#!/usr/bin/env python3
"""Read Git workspace data. Keep portable file snapshots. Do not remove sources."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import zipfile


def git(root: Path, *args: str, optional: bool = False, env: dict | None = None,
        hooks: Path | None = None) -> bytes:
    options = ['-c', 'core.hooksPath=' + str(hooks), '-c', 'core.fsmonitor='] if hooks is not None else []
    result = subprocess.run(['git', '-C', str(root), *options, *args], capture_output=True, env=env)
    if result.returncode and not optional:
        raise ValueError(result.stderr.decode('utf-8', 'replace').strip())
    return result.stdout if not result.returncode else b''


def restore_environment() -> dict:
    env = os.environ.copy()
    # Git documentation tells you to remove these variables from commands for a different repository.
    result = subprocess.run(['git', 'rev-parse', '--local-env-vars'], capture_output=True, env=env)
    if result.returncode:
        raise ValueError('Cannot find the Git environment variables for this repository')
    local = {name.upper() for name in result.stdout.decode('ascii').split()}
    return {name: value for name, value in env.items() if name.upper() not in local}


def restore_index(root: Path, env: dict, hooks: Path | None = None) -> Path:
    metadata = root / '.git'
    actual = Path(text(git(root, 'rev-parse', '--absolute-git-dir', env=env, hooks=hooks))).resolve()
    common = Path(text(git(root, 'rev-parse', '--git-common-dir', env=env, hooks=hooks)))
    index = Path(text(git(root, 'rev-parse', '--git-path', 'index', env=env, hooks=hooks)))
    common = common if common.is_absolute() else root / common
    index = index if index.is_absolute() else root / index
    top = Path(text(git(root, 'rev-parse', '--show-toplevel', env=env, hooks=hooks))).resolve()
    if (not metadata.is_dir() or metadata.is_symlink() or actual != metadata or
            common.resolve() != metadata or top != root or index.resolve() != metadata / 'index'):
        raise ValueError('Restore can use only the Git metadata of the new output directory')
    return index


def text(data: bytes) -> str:
    return data.decode('utf-8', 'surrogateescape').removesuffix('\n')


def root_of(path: Path) -> Path:
    return Path(text(git(path.resolve(), 'rev-parse', '--show-toplevel'))).resolve()


def inspect(path: Path) -> dict:
    root = root_of(path)
    status = git(root, '--no-optional-locks', 'status', '--porcelain=v1', '-z', '--untracked-files=all')
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
        'dirty': bool(status), 'status': [item.decode('utf-8', 'surrogateescape')
                                        for item in status.split(b'\0') if item],
        'activity': 'unknown', 'write_authorized': False, 'safe_to_remove': False,
    }


def safe_name(name: str) -> str:
    if not isinstance(name, str) or not name or '\\' in name or ':' in name or '\x00' in name:
        raise ValueError(f'Cannot use this relative path: {name!r}')
    path = PurePosixPath(name)
    if path.is_absolute() or any(p in ('', '.', '..') or p.rstrip(' .').casefold() == '.git'
                                 or re.fullmatch(r'git~[0-9]+', p.rstrip(' .'), re.IGNORECASE)
                                 for p in name.split('/')):
        raise ValueError(f'Cannot use this relative path: {name!r}')
    return name


def local_file(root: Path, name: str) -> Path:
    path = root / safe_name(name)
    current = root
    for part in PurePosixPath(name).parts:
        current = current / part
        try:
            info = current.lstat()
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(info.st_mode) or (
                getattr(info, 'st_file_attributes', 0) & getattr(stat, 'FILE_ATTRIBUTE_REPARSE_POINT', 0x400)):
            raise ValueError(f'Links must have a native snapshot tool: {name}')
        # A regular file cannot have descendants.
        if stat.S_ISREG(info.st_mode) and current != path:
            break
    resolved = path.resolve()
    if not resolved.is_relative_to(root):
        raise ValueError(f'Path is not in the repository: {name}')
    metadata = (root / '.git').resolve()
    if resolved == metadata or resolved.is_relative_to(metadata):
        raise ValueError(f'Path is a Git metadata location: {name}')
    return path


def inventory(root: Path, includes: list[str]) -> tuple[list[str], list[str]]:
    tracked = []
    for entry in git(root, 'ls-files', '--stage', '-z').split(b'\0'):
        if not entry:
            continue
        info, name = entry.split(b'\t', 1)
        mode, _oid, stage = info.split()
        if mode not in (b'100644', b'100755') or stage != b'0':
            raise ValueError('Symlinks, gitlinks and indexes with merge conflicts must have a native snapshot tool')
        tracked.append(name.decode('utf-8', 'surrogateescape'))
    selected = set(tracked)
    selected.update(p.decode('utf-8', 'surrogateescape') for p in
                    git(root, 'ls-files', '--others', '--exclude-standard', '-z').split(b'\0') if p)
    for name in includes:
        path = local_file(root, name)
        if not path.exists():
            raise ValueError(f'Include path is missing: {name}')
        if path.is_dir():
            for child in path.rglob('*'):
                rel = child.relative_to(root).as_posix()
                candidate = local_file(root, rel)
                if candidate.is_file():
                    selected.add(rel)
                elif not candidate.is_dir():
                    raise ValueError(f'Cannot use this file: {rel}')
        else:
            selected.add(name)
    present, missing = [], []
    for name in sorted(selected):
        path = local_file(root, name)
        if path.is_file():
            present.append(name)
        elif name in tracked and (not path.exists() or path.is_dir()):
            missing.append(name)
        else:
            raise ValueError(f'Cannot use this repository entry: {name}')
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
    git_dir = Path(text(git(root, 'rev-parse', '--absolute-git-dir'))).resolve()
    common = Path(text(git(root, 'rev-parse', '--git-common-dir')))
    common = (common if common.is_absolute() else root / common).resolve()
    if any(output.is_relative_to(path) for path in (root, git_dir, common)):
        raise ValueError('Snapshot output must not be in the source worktree or Git metadata')
    if output.exists():
        raise ValueError('Cannot replace the snapshot at the output location')
    if text(git(root, 'rev-parse', '--is-shallow-repository')) == 'true':
        raise ValueError('Shallow repositories must have all history or a native preservation tool. Keep the source')
    # --git-path gives common metadata paths for linked worktrees and GIT_GRAFT_FILE.
    grafts = Path(text(git(root, 'rev-parse', '--git-path', 'info/grafts')))
    grafts = grafts if grafts.is_absolute() else root / grafts
    if grafts.is_file() and any(line.strip() and not line.lstrip().startswith(b'#')
                               for line in grafts.read_bytes().splitlines()):
        raise ValueError('Legacy graft history must have a native preservation tool. Keep the source')
    before = inspect(root)
    paths, missing = inventory(root, includes)
    manifest = {'format': 1, 'source': before, 'files': [], 'deleted': missing,
                'bundle': None, 'included_ignored': includes,
                'stability': 'The results show only file and Git state from checks. They do not show that writers stopped.'}
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
                    raise ValueError('Source changed during snapshot. Keep the worktree. After writers stop, try again')
                for entry in manifest['files']:
                    with local_file(root, entry['path']).open('rb') as src:
                        if digest(src) != (entry['sha256'], entry['size']):
                            raise ValueError('File changed during snapshot. Do not remove the worktree')
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
            raise ValueError('Cannot use this snapshot format')
        head = manifest['source']['head']
        object_format = manifest['source'].get('object_format', 'sha256' if head and len(head) == 64 else 'sha1')
        if object_format not in ('sha1', 'sha256') or (head and len(head) != {'sha1': 40, 'sha256': 64}[object_format]):
            raise ValueError('Git object format does not agree with the HEAD identity')
        manifest['source']['object_format'] = object_format
        expected = {'manifest.json'}
        checks = []
        if manifest['source']['head']:
            if not re.fullmatch(r'[0-9a-f]{40}|[0-9a-f]{64}', manifest['source']['head']):
                raise ValueError('Incorrect HEAD identity')
            checks.append(('history.bundle', manifest['bundle']))
            expected.add('history.bundle')
        elif manifest['bundle'] is not None:
            raise ValueError('A bundle must have a HEAD identity')
        deleted = [safe_name(name) for name in manifest['deleted']]
        if len(deleted) != len(set(deleted)):
            raise ValueError('Duplicate path in the deletion inventory')
        for entry in manifest['files']:
            name = 'files/' + safe_name(entry['path'])
            if name in expected or entry['path'] in deleted:
                raise ValueError('File path has a duplicate or a conflict')
            if type(entry['mode']) is not int or not 0 <= entry['mode'] <= 0o777:
                raise ValueError('Incorrect file mode')
            expected.add(name)
            checks.append((name, entry))
        present = {entry['path'] for entry in manifest['files']}
        if any(parent.as_posix() in present for name in present
               for parent in PurePosixPath(name).parents):
            raise ValueError('Regular-file paths in the inventory have an ancestor conflict')
        if set(names) != expected:
            raise ValueError('Archive members do not agree with the manifest')
        for name, entry in checks:
            info = z.getinfo(name)
            if stat.S_ISLNK(info.external_attr >> 16) or type(entry['size']) is not int or entry['size'] < 0:
                raise ValueError('Cannot use this member metadata')
            with z.open(name) as src:
                if digest(src) != (entry['sha256'], entry['size']):
                    raise ValueError(f'Incorrect content checksum: {name}')
        return manifest


def verify_restored_files(root: Path, manifest: dict) -> None:
    expected = {entry['path']: entry for entry in manifest['files']}
    actual = set()
    for current, dirs, files in os.walk(root, followlinks=False):
        if Path(current) == root:
            dirs[:] = [name for name in dirs if name != '.git']
        for name in dirs + files:
            relative = (Path(current) / name).relative_to(root).as_posix()
            path = local_file(root, relative)
            if name in dirs:
                continue
            if not stat.S_ISREG(path.lstat().st_mode) or relative not in expected:
                raise ValueError(f'Restored file is not in the expected inventory or is not a regular file: {relative}')
            actual.add(relative)
            entry = expected[relative]
            with path.open('rb') as stream:
                if digest(stream) != (entry['sha256'], entry['size']):
                    raise ValueError(f'Restored file does not agree with the snapshot: {relative}')
    if actual != set(expected):
        raise ValueError('Restored file inventory does not agree with the snapshot')
    for name in manifest['deleted']:
        path = local_file(root, name)
        if path.exists() and not (
                path.is_dir() and any(saved.startswith(name + '/') for saved in expected)):
            raise ValueError(f'Restored results contain a path from the deletion inventory: {name}')


def restore(archive: Path, output: Path) -> dict:
    manifest = verify(archive)
    output = output.expanduser().resolve()
    if output.exists():
        raise ValueError('Restore must use an output directory that is not there before restore starts')
    env = restore_environment()
    with zipfile.ZipFile(archive) as z, tempfile.TemporaryDirectory(prefix='sdd-restore-') as staging:
        # Overrides for each command prevent templates and hooks from the host configuration during restore.
        empty = Path(staging) / 'empty'
        empty.mkdir()

        def run(*args, optional=False):
            return git(output, *args, optional=optional, env=env, hooks=empty)

        output.mkdir(parents=True)
        run('init', '--quiet', '--template=' + str(empty),
            '--object-format=' + manifest['source']['object_format'])
        restore_index(output, env, empty)
        if manifest['source']['head']:
            bundle = Path(staging) / 'history.bundle'
            with z.open('history.bundle') as src, bundle.open('wb') as dst:
                shutil.copyfileobj(src, dst)
            run('fetch', '--quiet', str(bundle), 'HEAD')
            head = manifest['source']['head']
            run('update-ref', '--no-deref', 'HEAD', head)
            # Read the index from the snapshot HEAD without a checkout of links from its history.
            run('read-tree', head)
        else:
            run('read-tree', '--empty')
        for entry in manifest['files']:
            target = local_file(output, entry['path'])
            target.parent.mkdir(parents=True, exist_ok=True)
            with z.open('files/' + entry['path']) as src, target.open('xb') as dst:
                shutil.copyfileobj(src, dst)
            target.chmod(entry['mode'])
            with target.open('rb') as restored:
                if digest(restored) != (entry['sha256'], entry['size']):
                    raise ValueError(f'Restored file does not agree with the snapshot: {entry["path"]}')
        if not restore_index(output, env, empty).is_file():
            raise ValueError('Restore did not make the output repository index')
        head = text(run('rev-parse', '--verify', 'HEAD', optional=True)) or None
        if head != manifest['source']['head']:
            raise ValueError('Restored HEAD does not agree with the snapshot')
        if head:
            run('diff-index', '--cached', '--quiet', head, '--')
        elif run('ls-files', '--stage', '-z'):
            raise ValueError('Restore without an initial commit must have an empty index')
        # Index validation can change metadata. Read HEAD after all other Git commands.
        if not restore_index(output, env, empty).is_file():
            raise ValueError('Restore did not make the output repository index')
        head = text(run('rev-parse', '--verify', 'HEAD', optional=True)) or None
        if head != manifest['source']['head']:
            raise ValueError('Restored HEAD does not agree with the snapshot')
        verify_restored_files(output, manifest)
    return {'restored': str(output), 'head': head, 'files': len(manifest['files']),
            'verified': True, 'write_authorized': False, 'safe_to_remove': False}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    p = commands.add_parser('inspect', help='Read Git data without changes. The data give no activity proof or authority')
    p.add_argument('--repo', type=Path, required=True)
    p = commands.add_parser('snapshot', help='Keep HEAD history and regular files at snapshot time. Do not remove source')
    p.add_argument('--repo', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--include', action='append', default=[], help='A necessary ignored path that you supply from the worktree')
    p = commands.add_parser('verify', help='Make sure that snapshot inventory and content hashes agree')
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
