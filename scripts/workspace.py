#!/usr/bin/env python3
"""Observe Git workspaces and preserve portable file snapshots. Never delete sources."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import zipfile


def git(root: Path, *args: str, optional: bool = False) -> bytes:
    result = subprocess.run(['git', '-C', str(root), *args], capture_output=True)
    if result.returncode and not optional:
        raise ValueError(result.stderr.decode('utf-8', 'replace').strip())
    return result.stdout if not result.returncode else b''


def text(data: bytes) -> str:
    return data.decode('utf-8', 'surrogateescape').strip()


def root_of(path: Path) -> Path:
    return Path(text(git(path.resolve(), 'rev-parse', '--show-toplevel'))).resolve()


def inspect(path: Path) -> dict:
    root = root_of(path)
    status = git(root, 'status', '--porcelain=v1', '-z', '--untracked-files=all')
    common = Path(text(git(root, 'rev-parse', '--git-common-dir')))
    if not common.is_absolute():
        common = root / common
    git_dir = Path(text(git(root, 'rev-parse', '--git-dir')))
    if not git_dir.is_absolute():
        git_dir = root / git_dir
    head = text(git(root, 'rev-parse', '--verify', 'HEAD', optional=True)) or None
    object_format = text(git(root, 'rev-parse', '--show-object-format', optional=True))
    if object_format not in ('sha1', 'sha256'):
        object_format = 'sha256' if head and len(head) == 64 else 'sha1'
    return {
        'root': str(root), 'head': head, 'object_format': object_format,
        'branch': text(git(root, 'symbolic-ref', '--quiet', '--short', 'HEAD', optional=True)) or None,
        'git_common_dir': str(common.resolve()), 'linked_worktree': git_dir.resolve() != common.resolve(),
        'dirty': bool(status), 'status': [text(item) for item in status.split(b'\0') if item],
        'activity': 'unknown', 'write_authorized': False, 'safe_to_remove': False,
    }


def safe_name(name: str) -> str:
    if not isinstance(name, str) or not name or '\\' in name or ':' in name or '\x00' in name:
        raise ValueError(f'Unsupported relative path: {name!r}')
    path = PurePosixPath(name)
    if path.is_absolute() or any(p in ('', '.', '..') or p.rstrip(' .').casefold() == '.git'
                                 or re.fullmatch(r'git~[0-9]+', p.rstrip(' .'), re.IGNORECASE)
                                 for p in name.split('/')):
        raise ValueError(f'Unsafe relative path: {name!r}')
    return name


def local_file(root: Path, name: str) -> Path:
    path = root / safe_name(name)
    current = root
    for part in PurePosixPath(name).parts:
        current = current / part
        if current.is_symlink() or (hasattr(current, 'is_junction') and current.is_junction()):
            raise ValueError(f'Links require a native snapshot tool: {name}')
    resolved = path.resolve()
    if not resolved.is_relative_to(root):
        raise ValueError(f'Path leaves repository: {name}')
    metadata = (root / '.git').resolve()
    if resolved == metadata or resolved.is_relative_to(metadata):
        raise ValueError(f'Path resolves into Git metadata: {name}')
    return path


def inventory(root: Path, includes: list[str]) -> tuple[list[str], list[str]]:
    tracked = []
    for entry in git(root, 'ls-files', '--stage', '-z').split(b'\0'):
        if not entry:
            continue
        info, name = entry.split(b'\t', 1)
        mode, _oid, stage = info.split()
        if mode not in (b'100644', b'100755') or stage != b'0':
            raise ValueError('Symlinks, gitlinks and unmerged indexes require a native snapshot tool')
        tracked.append(name.decode('utf-8', 'surrogateescape'))
    selected = set(tracked)
    selected.update(p.decode('utf-8', 'surrogateescape') for p in
                    git(root, 'ls-files', '--others', '--exclude-standard', '-z').split(b'\0') if p)
    for name in includes:
        path = local_file(root, name)
        if not path.exists():
            raise ValueError(f'Explicit include does not exist: {name}')
        if path.is_dir():
            for child in path.rglob('*'):
                rel = child.relative_to(root).as_posix()
                candidate = local_file(root, rel)
                if candidate.is_file():
                    selected.add(rel)
                elif not candidate.is_dir():
                    raise ValueError(f'Unsupported file: {rel}')
        else:
            selected.add(name)
    present, missing = [], []
    for name in sorted(selected):
        path = local_file(root, name)
        if path.is_file():
            present.append(name)
        elif not path.exists() and name in tracked:
            missing.append(name)
        else:
            raise ValueError(f'Unsupported repository entry: {name}')
    return present, missing


def digest(stream) -> tuple[str, int]:
    h, size = hashlib.sha256(), 0
    while chunk := stream.read(1024 * 1024):
        h.update(chunk)
        size += len(chunk)
    return h.hexdigest(), size


def add_file(z: zipfile.ZipFile, source: Path, name: str) -> dict:
    h, size = hashlib.sha256(), 0
    with source.open('rb') as src, z.open(name, 'w') as dst:
        while chunk := src.read(1024 * 1024):
            dst.write(chunk)
            h.update(chunk)
            size += len(chunk)
    return {'sha256': h.hexdigest(), 'size': size}


def snapshot(repo: Path, output: Path, includes: list[str]) -> dict:
    root = root_of(repo)
    output = output.expanduser().resolve()
    if output.is_relative_to(root):
        raise ValueError('Snapshot output must be outside the source worktree')
    if output.exists():
        raise ValueError('Refusing to overwrite an existing snapshot')
    if text(git(root, 'rev-parse', '--is-shallow-repository')) == 'true':
        raise ValueError('Shallow repositories require complete history or a native preservation tool; preserve the source')
    before = inspect(root)
    paths, missing = inventory(root, includes)
    manifest = {'format': 1, 'source': before, 'files': [], 'deleted': missing,
                'bundle': None, 'included_ignored': includes,
                'stability': 'observed-only; not proof of stopped writers'}
    output.parent.mkdir(parents=True, exist_ok=True)
    created = False
    try:
        with tempfile.TemporaryDirectory(prefix='sdd-bundle-') as staging:
            bundle = Path(staging) / 'history.bundle'
            if before['head']:
                git(root, 'bundle', 'create', str(bundle), 'HEAD')
                git(root, 'bundle', 'verify', str(bundle))
            with zipfile.ZipFile(output, 'x', compression=zipfile.ZIP_DEFLATED) as z:
                created = True
                if before['head']:
                    manifest['bundle'] = add_file(z, bundle, 'history.bundle')
                for name in paths:
                    source = local_file(root, name)
                    entry = {'path': name, 'mode': stat.S_IMODE(source.stat().st_mode)}
                    entry.update(add_file(z, source, 'files/' + name))
                    manifest['files'].append(entry)
                if inspect(root) != before or inventory(root, includes) != (paths, missing):
                    raise ValueError('Source changed during snapshot; preserve the worktree and retry after stopping writers')
                for entry in manifest['files']:
                    with local_file(root, entry['path']).open('rb') as src:
                        if digest(src) != (entry['sha256'], entry['size']):
                            raise ValueError('File changed during snapshot; do not remove the worktree')
                z.writestr('manifest.json', json.dumps(manifest, ensure_ascii=True, indent=2))
        verify(output)
    except Exception:
        if created:
            output.unlink(missing_ok=True)
        raise
    with output.open('rb') as src:
        archive_hash, _size = digest(src)
    return {'archive': str(output), 'sha256': archive_hash, 'files': len(paths),
            'head': before['head'], 'verified': True, 'safe_to_remove': False}


def verify(archive: Path) -> dict:
    with zipfile.ZipFile(archive) as z:
        names = z.namelist()
        if len(names) != len(set(names)) or 'manifest.json' not in names:
            raise ValueError('Duplicate members or missing manifest')
        if z.getinfo('manifest.json').file_size > 16 * 1024 * 1024:
            raise ValueError('Manifest is too large')
        manifest = json.loads(z.read('manifest.json'))
        if manifest['format'] != 1:
            raise ValueError('Unsupported snapshot format')
        head = manifest['source']['head']
        object_format = manifest['source'].get('object_format', 'sha256' if head and len(head) == 64 else 'sha1')
        if object_format not in ('sha1', 'sha256') or (head and len(head) != {'sha1': 40, 'sha256': 64}[object_format]):
            raise ValueError('Inconsistent Git object format')
        manifest['source']['object_format'] = object_format
        expected = {'manifest.json'}
        checks = []
        if manifest['source']['head']:
            if not re.fullmatch(r'[0-9a-f]{40}|[0-9a-f]{64}', manifest['source']['head']):
                raise ValueError('Invalid HEAD')
            checks.append(('history.bundle', manifest['bundle']))
            expected.add('history.bundle')
        elif manifest['bundle'] is not None:
            raise ValueError('Unexpected bundle without HEAD')
        deleted = [safe_name(name) for name in manifest['deleted']]
        if len(deleted) != len(set(deleted)):
            raise ValueError('Duplicate deleted path')
        for entry in manifest['files']:
            name = 'files/' + safe_name(entry['path'])
            if name in expected or entry['path'] in deleted:
                raise ValueError('Duplicate or contradictory file path')
            if type(entry['mode']) is not int or not 0 <= entry['mode'] <= 0o777:
                raise ValueError('Invalid file mode')
            expected.add(name)
            checks.append((name, entry))
        if set(names) != expected:
            raise ValueError('Archive members do not match the manifest')
        for name, entry in checks:
            info = z.getinfo(name)
            if stat.S_ISLNK(info.external_attr >> 16) or type(entry['size']) is not int or entry['size'] < 0:
                raise ValueError('Unsupported member metadata')
            with z.open(name) as src:
                if digest(src) != (entry['sha256'], entry['size']):
                    raise ValueError(f'Content checksum mismatch: {name}')
        return manifest


def restore(archive: Path, output: Path) -> dict:
    manifest = verify(archive)
    output = output.expanduser().resolve()
    if output.exists():
        raise ValueError('Restore requires a new, nonexistent directory')
    output.mkdir(parents=True)
    git(output, 'init', '--quiet', '--object-format=' + manifest['source']['object_format'])
    with zipfile.ZipFile(archive) as z, tempfile.TemporaryDirectory(prefix='sdd-restore-') as staging:
        if manifest['source']['head']:
            bundle = Path(staging) / 'history.bundle'
            with z.open('history.bundle') as src, bundle.open('wb') as dst:
                shutil.copyfileobj(src, dst)
            git(output, 'fetch', '--quiet', str(bundle), 'HEAD')
            head = manifest['source']['head']
            git(output, 'update-ref', '--no-deref', 'HEAD', head)
            # Load the original index without checking out potentially historical links.
            git(output, 'read-tree', head)
        for entry in manifest['files']:
            target = local_file(output, entry['path'])
            target.parent.mkdir(parents=True, exist_ok=True)
            with z.open('files/' + entry['path']) as src, target.open('xb') as dst:
                shutil.copyfileobj(src, dst)
            target.chmod(entry['mode'])
            with target.open('rb') as restored:
                if digest(restored) != (entry['sha256'], entry['size']):
                    raise ValueError(f'Restored file mismatch: {entry["path"]}')
    return {'restored': str(output), 'head': manifest['source']['head'],
            'files': len(manifest['files']), 'verified': True, 'write_authorized': False}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    p = commands.add_parser('inspect', help='Read-only Git facts; does not establish activity or authority')
    p.add_argument('--repo', type=Path, required=True)
    p = commands.add_parser('snapshot', help='Save HEAD history and current regular files, without removing source')
    p.add_argument('--repo', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--include', action='append', default=[], help='Explicit necessary ignored path within worktree')
    p = commands.add_parser('verify', help='Check snapshot inventory and content hashes')
    p.add_argument('--archive', type=Path, required=True)
    p = commands.add_parser('restore', help='Restore files and HEAD into a new directory')
    p.add_argument('--archive', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.command == 'inspect':
            result = inspect(args.repo)
        elif args.command == 'snapshot':
            result = snapshot(args.repo, args.output, args.include)
        elif args.command == 'verify':
            manifest = verify(args.archive)
            result = {'verified': True, 'files': len(manifest['files']), 'safe_to_remove': False}
        else:
            result = restore(args.archive, args.output)
        print(json.dumps(result, ensure_ascii=True))
        return 0
    except (OSError, ValueError, KeyError, TypeError, zipfile.BadZipFile) as exc:
        print(json.dumps({'error': str(exc)}, ensure_ascii=True), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
