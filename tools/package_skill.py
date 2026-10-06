#!/usr/bin/env python3
"""Build a standalone skill ZIP containing only its portable installation tree."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import stat
import sys
import zipfile


def checked_entries(root):
    try:
        info = root.lstat()
    except FileNotFoundError:
        return
    if stat.S_ISLNK(info.st_mode) or (
            getattr(info, 'st_file_attributes', 0) & getattr(stat, 'FILE_ATTRIBUTE_REPARSE_POINT', 0x400)):
        raise ValueError('Distribution cannot contain linked files')
    yield root
    if root.is_dir():
        for entry in root.iterdir():
            yield from checked_entries(entry)


def package(source, output):
    source_path = Path(source)
    # Check the root before resolve() can hide a linked source.
    next(checked_entries(source_path), None)
    source, output = Path(source).resolve(), Path(output).resolve()
    if not (source / 'SKILL.md').is_file():
        raise ValueError('Source must contain SKILL.md')
    if output.is_relative_to(source) and not output.is_relative_to(source / 'dist'):
        raise ValueError('Output inside the repository must be under dist')
    body = (source / 'SKILL.md').read_text(encoding='utf-8')
    match = re.search(r'^name:\s*([a-z0-9-]+)\s*$', body, re.MULTILINE)
    if not match:
        raise ValueError('Skill frontmatter must contain a valid name')
    name = match.group(1)
    files = []
    entries = list(checked_entries(source / 'SKILL.md'))
    for directory in ('scripts', 'references', 'assets', 'agents'):
        entry = source / directory
        entries.extend(checked_entries(entry))
    for path in sorted(entries):
        if path.is_file() and '__pycache__' not in path.parts and path.suffix != '.pyc':
            files.append(path)
    included = set(files)
    for path in files:
        if path.suffix == '.md':
            for target in re.findall(r'\]\(([^)]+)\)', path.read_text(encoding='utf-8')):
                if target.startswith(('https://', 'http://', '#')):
                    continue
                resolved = (path.parent / target.split('#', 1)[0]).resolve()
                if resolved not in included:
                    raise ValueError(f'Invalid portable link in {path.name}: {target}')
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, 'x', compression=zipfile.ZIP_DEFLATED) as z:
        for path in files:
            z.write(path, name + '/' + path.relative_to(source).as_posix())
    with zipfile.ZipFile(output) as z:
        if z.testzip() is not None:
            raise ValueError('Distribution integrity check failed')
    h = hashlib.sha256()
    with output.open('rb') as stream:
        while chunk := stream.read(1024 * 1024):
            h.update(chunk)
    return {'archive': str(output), 'files': len(files), 'sha256': h.hexdigest()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    try:
        print(json.dumps(package(args.source, args.output)))
        return 0
    except (OSError, ValueError, zipfile.BadZipFile) as exc:
        print(json.dumps({'error': str(exc)}), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
