"""Real disposable regressions for restore routing and portable inventories."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT / 'scripts' / 'workspace.py'
BUILDER = ROOT / 'tools' / 'package_skill.py'


def hashes(root):
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob('*') if p.is_file()}


def load(path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CorrectionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='sdd-072-test-')
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)

    def run_command(self, args, env=None):
        result = subprocess.run(list(map(str, args)), capture_output=True, env=env)
        self.assertEqual(result.returncode, 0, result.stderr.decode('utf-8', 'replace'))
        return result.stdout

    def git(self, repo, *args):
        return self.run_command(['git', '-C', repo, *args])

    def cli(self, script, *args, env=None):
        return json.loads(self.run_command([sys.executable, '-B', script, *args], env=env))

    def archive_fixture(self, unborn=False):
        source = self.base / 'source'
        source.mkdir()
        self.git(source, 'init', '--quiet')
        self.git(source, 'config', 'user.name', 'Disposable Correction')
        self.git(source, 'config', 'user.email', 'correction@example.invalid')
        self.git(source, 'config', 'core.autocrlf', 'false')
        (source / 'accepted.txt').write_bytes(b'accepted HEAD\n')
        if not unborn:
            self.git(source, 'add', '.')
            self.git(source, 'commit', '--quiet', '-m', 'archived base')
        archive = self.base / 'snapshot.zip'
        self.cli(WORKSPACE, 'snapshot', '--repo', source, '--output', archive)
        if not unborn:
            (source / 'accepted.txt').write_bytes(b'later source HEAD\n')
            self.git(source, 'add', '.')
            self.git(source, 'commit', '--quiet', '-m', 'later source')
        (source / 'accepted.txt').write_bytes(b'unique staged source content\n')
        self.git(source, 'add', '.')
        return source, archive

    def assert_restore_isolated(self, overrides, unborn=False):
        source, archive = self.archive_fixture(unborn)
        before = hashes(source)
        branch = self.git(source, 'symbolic-ref', 'HEAD')
        source_head = None if unborn else self.git(source, 'rev-parse', 'HEAD')
        env = {**os.environ, **overrides(source)}
        target = self.base / 'restored'
        result = self.cli(WORKSPACE, 'restore', '--archive', archive, '--output', target, env=env)
        self.assertEqual(hashes(source), before, 'Restore changed the existing source')
        self.assertEqual(self.git(source, 'symbolic-ref', 'HEAD'), branch)
        if source_head:
            self.assertEqual(self.git(source, 'rev-parse', 'HEAD'), source_head)
        self.assertTrue(result['verified'])
        self.assertTrue((target / '.git').is_dir(), 'Restore omitted its own Git directory')
        self.assertEqual(Path(self.git(target, 'rev-parse', '--absolute-git-dir').decode().strip()),
                         target / '.git')
        self.assertTrue((target / '.git' / 'index').is_file(), 'Restore omitted its own index')
        self.assertEqual((target / 'accepted.txt').read_bytes(), b'accepted HEAD\n')
        if unborn:
            self.assertIsNone(result['head'])
            self.assertEqual(self.git(target, 'ls-files', '--stage'), b'')
            head = subprocess.run(['git', '-C', str(target), 'rev-parse', '--verify', 'HEAD'],
                                  capture_output=True)
            self.assertNotEqual(head.returncode, 0)
        else:
            self.assertEqual(self.git(target, 'rev-parse', 'HEAD').decode().strip(), result['head'])
            self.assertEqual(self.git(target, 'show', ':accepted.txt'), b'accepted HEAD\n')

    def test_restore_preserves_foreign_staged_index(self):
        self.assert_restore_isolated(lambda source: {'GIT_INDEX_FILE': str(source / '.git/index')})

    def test_restore_preserves_foreign_head_and_branch(self):
        self.assert_restore_isolated(lambda source: {
            'GIT_DIR': str(source / '.git'), 'GIT_WORK_TREE': str(source)})

    def test_restore_isolates_foreign_common_and_object_directories(self):
        self.assert_restore_isolated(lambda source: {
            'GIT_COMMON_DIR': str(source / '.git'),
            'GIT_OBJECT_DIRECTORY': str(source / '.git/objects'),
            'GIT_ALTERNATE_OBJECT_DIRECTORIES': str(source / '.git/objects')})

    def test_unborn_restore_has_own_empty_index_under_foreign_overrides(self):
        self.assert_restore_isolated(lambda source: {
            'GIT_DIR': str(source / '.git'), 'GIT_WORK_TREE': str(source),
            'GIT_INDEX_FILE': str(source / '.git/index')}, unborn=True)

    def test_restore_preserves_caller_environment_and_unrelated_settings(self):
        source, archive = self.archive_fixture()
        module = load(WORKSPACE)
        before = hashes(source)
        trace = self.base / 'git-trace.log'
        with patch.dict(os.environ, {'GIT_INDEX_FILE': str(source / '.git/index'),
                                     'GIT_TRACE': str(trace), 'SDD_TEST_SENTINEL': 'keep'}):
            original = dict(os.environ)
            module.restore(archive, self.base / 'restored')
            self.assertEqual(dict(os.environ), original)
        self.assertEqual(hashes(source), before)
        self.assertTrue(trace.is_file(), 'Unrelated GIT_TRACE setting was removed')
        self.assertIn('read-tree', trace.read_text(encoding='utf-8'))

    def portable_fixture(self, parent):
        source = parent / 'sdd-harness'
        source.mkdir(parents=True)
        shutil.copy2(ROOT / 'SKILL.md', source / 'SKILL.md')
        for name in ('scripts', 'references', 'assets'):
            shutil.copytree(ROOT / name, source / name,
                            ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        self.assertEqual(len(hashes(source)), 14)
        return source

    def assert_package_and_install(self, source, parent):
        expected = hashes(source)
        internal = source / 'scripts' / '__pycache__'
        internal.mkdir()
        (internal / 'cached.pyc').write_bytes(b'cache')
        (internal / 'not-bytecode.txt').write_bytes(b'internal cache')
        (source / 'assets' / 'cached.pyc').write_bytes(b'bytecode')
        archive = self.base / 'skill.zip'
        package = self.cli(BUILDER, '--source', source, '--output', archive)
        self.assertEqual(package['files'], 14)
        with zipfile.ZipFile(archive) as z:
            actual = {name.removeprefix('sdd-harness/'): hashlib.sha256(z.read(name)).hexdigest()
                      for name in z.namelist()}
            self.assertEqual(actual, expected)
        installed = self.cli(source / 'scripts/install.py', '--into', parent)
        self.assertEqual(installed['files'], 14)
        self.assertEqual(hashes(parent / 'sdd-harness'), expected)
        repeated = self.cli(source / 'scripts/install.py', '--into', parent)
        self.assertEqual(repeated['status'], 'already-installed')
        changed = parent / 'sdd-harness' / 'SKILL.md'
        changed.write_bytes(changed.read_bytes() + b'\nlocal change\n')
        before = hashes(parent / 'sdd-harness')
        refusal = subprocess.run([sys.executable, '-B', str(source / 'scripts/install.py'),
                                  '--into', str(parent)], capture_output=True)
        self.assertNotEqual(refusal.returncode, 0)
        self.assertEqual(hashes(parent / 'sdd-harness'), before)

    def test_cache_named_source_ancestor_preserves_portable_inventory(self):
        source = self.portable_fixture(self.base / '__pycache__' / 'download')
        self.assert_package_and_install(source, self.base / 'installed')

    def test_cache_named_target_ancestor_preserves_portable_inventory(self):
        source = self.portable_fixture(self.base / 'download')
        self.assert_package_and_install(source, self.base / '__pycache__' / 'project' / '.dsh/skills')

    def test_empty_package_inventory_is_rejected_before_output_creation(self):
        source = self.portable_fixture(self.base / 'download')
        module = load(BUILDER)
        output = self.base / 'not-created' / 'empty.zip'
        with patch.object(module, 'checked_entries', return_value=iter(())):
            with self.assertRaisesRegex(ValueError, 'empty|Empty'):
                module.package(source, output)
        self.assertFalse(output.parent.exists())

    def test_empty_install_inventory_is_rejected_before_parent_creation(self):
        source = self.portable_fixture(self.base / 'download')
        module = load(source / 'scripts/install.py')
        parent = self.base / 'not-created'
        with patch.object(module, 'skill_files', return_value=[]):
            with self.assertRaises((OSError, ValueError)) as caught:
                module.install(parent)
        self.assertIsInstance(caught.exception, ValueError)
        self.assertRegex(str(caught.exception), 'empty|Empty')
        self.assertFalse(parent.exists())


if __name__ == '__main__':
    unittest.main()
