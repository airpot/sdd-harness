#!/usr/bin/env python3
"""Copy the complete skill into a selected agent skills directory; never overwrite."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import stat
import sys
import tempfile


def is_link(path):
    try:
        info = path.lstat()
    except FileNotFoundError:
        return False
    return stat.S_ISLNK(info.st_mode) or bool(
        getattr(info, 'st_file_attributes', 0) & getattr(stat, 'FILE_ATTRIBUTE_REPARSE_POINT', 0x400))


def checked_entries(root):
    if is_link(root):
        raise ValueError('Skill directories must not contain links')
    yield root
    if root.is_dir():
        for entry in root.iterdir():
            yield from checked_entries(entry)


def skill_files(root):
    if is_link(root):
        raise ValueError('Skill directories must not contain links')
    files = [root / 'SKILL.md']
    for name in ('scripts', 'references', 'assets', 'agents'):
        entry = root / name
        files.extend(checked_entries(entry))
    result = []
    for path in files:
        if is_link(path):
            raise ValueError('Skill directories must not contain links')
        if path.is_file() and '__pycache__' not in path.parts and path.suffix != '.pyc':
            result.append(path)
    return sorted(result)


def contents(root):
    result = {}
    for path in checked_entries(root):
        if path.is_file() and '__pycache__' not in path.parts and path.suffix != '.pyc':
            result[path.relative_to(root).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def install(parent):
    source = Path(__file__).absolute().parents[1]
    if is_link(source):
        raise ValueError('Skill directories must not contain links')
    source = source.resolve()
    parent = Path(parent).expanduser().resolve()
    target = parent / 'sdd-harness'
    if parent.is_relative_to(source):
        raise ValueError('Installation directory must be outside the source skill')
    if not (source / 'SKILL.md').is_file():
        raise ValueError('Missing SKILL.md; copy the complete distribution')
    files = skill_files(source)
    expected = {p.relative_to(source).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    if is_link(target):
        raise ValueError('Refusing to replace a linked skill')
    if target.exists():
        if target.is_dir() and contents(target) == expected:
            return {'status': 'already-installed', 'installed': str(target)}
        raise ValueError('Existing skill differs; preserve it as a backup before installing')
    parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.sdd-install-', dir=parent) as temporary:
        staged = Path(temporary) / 'sdd-harness'
        for path in files:
            copied = staged / path.relative_to(source)
            copied.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, copied)
        if contents(staged) != expected:
            raise ValueError('Source changed or copy verification failed')
        if is_link(target) or target.exists():
            raise ValueError('Target appeared during installation; preserve it and retry')
        staged.rename(target)
    return {'status': 'installed', 'installed': str(target), 'files': len(expected)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--into', required=True, help='Parent skills directory, not the final skill folder')
    args = parser.parse_args()
    try:
        print(json.dumps(install(args.into), ensure_ascii=True))
        return 0
    except (OSError, ValueError) as exc:
        print(json.dumps({'error': str(exc)}, ensure_ascii=True), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
