"""Disposable actual-repository regressions for the 0.7.3 audit corrections."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT / 'scripts/workspace.py'
HOST = ROOT / 'evals/host.py'


def load(path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def tree_hashes(root):
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob('*') if p.is_file()}


class AuditCorrections(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='sdd-073-test-')
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve()
        names = subprocess.check_output(['git', 'rev-parse', '--local-env-vars']).decode().split()
        self.env = {k: v for k, v in os.environ.items() if k.upper() not in names}
        self.empty = self.base / 'empty-template'
        self.empty.mkdir()

    def run_command(self, args, extra=None, ok=True):
        result = subprocess.run(list(map(str, args)), capture_output=True,
                                env={**self.env, **(extra or {})}, timeout=30)
        if ok:
            self.assertEqual(result.returncode, 0, result.stderr.decode('utf-8', 'replace'))
        return result

    def git(self, root, *args):
        return self.run_command(['git', '--no-optional-locks', '-C', root,
                                 '-c', 'core.autocrlf=false', '-c', 'commit.gpgsign=false',
                                 '-c', 'core.hooksPath=' + str(self.empty), *args]).stdout

    def cli(self, script, *args, extra=None, ok=True):
        result = self.run_command([sys.executable, '-B', script, *args], extra, ok)
        return json.loads(result.stdout) if ok else result

    def repo(self, name='source'):
        root = self.base / name
        root.mkdir()
        self.git(root, 'init', '--quiet', '--template=' + str(self.empty))
        self.git(root, 'config', 'user.name', 'Disposable Audit')
        self.git(root, 'config', 'user.email', 'audit@example.invalid')
        self.git(root, 'config', 'core.autocrlf', 'false')
        (root / 'keep.txt').write_bytes(b'original content\n')
        self.git(root, 'add', '.')
        self.git(root, 'commit', '--quiet', '-m', 'original')
        return root

    def busy(self, extra=None):
        root = self.base / 'fixture'
        self.cli(HOST, 'create', '--case', 'busy-worktree', '--output', root, extra=extra)
        for action in ('observe', 'isolate'):
            self.cli(HOST, 'act', '--root', root, '--action', action, extra=extra)
        return root, self.cli(HOST, 'score', '--root', root, extra=extra)

    def test_host_preserves_real_foreign_staged_only_index(self):
        foreign = self.repo('foreign')
        (foreign / 'keep.txt').write_bytes(b'valuable staged-only content\n')
        self.git(foreign, 'add', '.')
        (foreign / 'keep.txt').write_bytes(b'original content\n')
        before = tree_hashes(foreign)
        staged = self.git(foreign, 'show', ':keep.txt')
        root, result = self.busy({'GIT_INDEX_FILE': str(foreign / '.git/index')})
        self.assertEqual(tree_hashes(foreign), before)
        self.assertEqual(self.git(foreign, 'show', ':keep.txt'), staged)
        self.assertTrue((root / 'source/.git/index').is_file())
        self.assertTrue(result['all_passed'])

    def test_host_keeps_missing_external_index_absent(self):
        index = self.base / 'missing.index'
        root, result = self.busy({'GIT_INDEX_FILE': str(index)})
        self.assertFalse(index.exists())
        self.assertTrue((root / 'source/.git/index').is_file())
        self.assertTrue(result['all_passed'])

    def test_host_preserves_foreign_repository_routing(self):
        foreign = self.repo('foreign')
        before = tree_hashes(foreign)
        root, result = self.busy({'GIT_DIR': str(foreign / '.git'), 'GIT_WORK_TREE': str(foreign)})
        self.assertEqual(tree_hashes(foreign), before)
        self.assertEqual(Path(self.git(root / 'source', 'rev-parse', '--show-toplevel').decode().strip()),
                         root / 'source')
        self.assertTrue(result['all_passed'])

    def test_host_child_environment_keeps_caller_and_unrelated_settings(self):
        host = load(HOST)
        trace = self.base / 'trace.log'
        index = self.base / 'missing.index'
        with patch.dict(os.environ, {'GIT_INDEX_FILE': str(index), 'GIT_TRACE': str(trace),
                                     'SDD_SENTINEL': 'keep'}):
            before = dict(os.environ)
            host.create('busy-worktree', self.base / 'fixture')
            self.assertEqual(dict(os.environ), before)
        self.assertFalse(index.exists())
        self.assertTrue(trace.is_file())
        self.assertIn('commit', trace.read_text())

    def test_host_busy_grader_checks_missing_index(self):
        root, initial = self.busy()
        self.assertTrue(initial['all_passed'])
        (root / 'source/.git/index').unlink()
        result = self.cli(HOST, 'score', '--root', root)
        self.assertFalse(result['all_passed'])
        self.assertFalse(result['outcomes']['source_preserved'])

    def test_host_busy_grader_checks_empty_and_corrupt_index(self):
        root, initial = self.busy()
        self.assertTrue(initial['all_passed'])
        self.git(root / 'source', 'read-tree', '--empty')
        self.assertFalse(self.cli(HOST, 'score', '--root', root)['all_passed'])
        (root / 'source/.git/index').write_bytes(b'not an index')
        self.assertFalse(self.cli(HOST, 'score', '--root', root)['all_passed'])

    def archive(self):
        source = self.repo()
        (source / 'removed.txt').write_bytes(b'delete this\n')
        (source / '.gitignore').write_bytes(b'results/\n')
        self.git(source, 'add', '.')
        self.git(source, 'commit', '--quiet', '-m', 'before deletion')
        (source / 'removed.txt').unlink()
        (source / 'results').mkdir()
        (source / 'results/proof.txt').write_bytes(b'necessary ignored result\n')
        archive = self.base / 'snapshot.zip'
        self.cli(WORKSPACE, 'snapshot', '--repo', source, '--output', archive, '--include', 'results')
        return source, archive

    def hooks(self):
        template = self.base / 'template'
        hooks = template / 'hooks'
        hooks.mkdir(parents=True)
        hook = hooks / 'reference-transaction'
        hook.write_text('#!/bin/sh\nprintf "recreated\\n" > removed.txt\nexit 0\n',
                        encoding='ascii', newline='\n')
        hook.chmod(0o755)
        return template, hooks

    def assert_restore_without_hook(self, extra):
        source, archive = self.archive()
        before = tree_hashes(source)
        target = self.base / 'restored'
        result = self.cli(WORKSPACE, 'restore', '--archive', archive, '--output', target, extra=extra)
        self.assertTrue(result['verified'])
        self.assertEqual(tree_hashes(source), before)
        self.assertFalse((target / 'removed.txt').exists())
        self.assertEqual((target / 'results/proof.txt').read_bytes(), b'necessary ignored result\n')

    def test_restore_disables_environment_template_hook(self):
        template, _ = self.hooks()
        self.assert_restore_without_hook({'GIT_TEMPLATE_DIR': str(template)})

    def test_restore_disables_configured_template_hook(self):
        template, _ = self.hooks()
        config = self.base / 'config'
        config.write_text('[init]\n templateDir = ' + template.as_posix() + '\n', encoding='utf-8')
        before = config.read_bytes()
        self.assert_restore_without_hook({'GIT_CONFIG_GLOBAL': str(config)})
        self.assertEqual(config.read_bytes(), before)

    def test_restore_disables_configured_hooks_path(self):
        _, hooks = self.hooks()
        config = self.base / 'config'
        config.write_text('[core]\n hooksPath = ' + hooks.as_posix() + '\n', encoding='utf-8')
        self.assert_restore_without_hook({'GIT_CONFIG_GLOBAL': str(config)})

    def test_restore_final_verification_checks_actual_complete_files(self):
        _, archive = self.archive()
        for name, content in (('unexpected.txt', b'extra'), ('keep.txt', b'changed'),
                              ('removed.txt', b'recreated'), ('results/proof.txt', b'changed ignored')):
            with self.subTest(name=name):
                module = load(WORKSPACE)
                original = module.git
                target = self.base / ('restored-' + name.replace('/', '-'))

                def changed(root, *args, **kwargs):
                    result = original(root, *args, **kwargs)
                    if 'diff-index' in args:
                        (root / name).write_bytes(content)
                    return result

                with patch.object(module, 'git', side_effect=changed):
                    with self.assertRaises(ValueError):
                        module.restore(archive, target)

    def history(self):
        source = self.repo()
        first = self.git(source, 'rev-parse', 'HEAD').decode().strip()
        (source / 'keep.txt').write_bytes(b'second content\n')
        self.git(source, 'add', '.')
        self.git(source, 'commit', '--quiet', '-m', 'second')
        head = self.git(source, 'rev-parse', 'HEAD').decode().strip()
        (source / '.git/info').mkdir(exist_ok=True)
        return source, first, head

    def assert_graft_rejected(self, source, first, head, extra=None):
        before = tree_hashes(source)
        output = self.base / 'not-created/snapshot.zip'
        result = self.cli(WORKSPACE, 'snapshot', '--repo', source, '--output', output, extra=extra, ok=False)
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn(b'graft', result.stderr.lower())
        self.assertFalse(output.parent.exists())
        self.assertEqual(tree_hashes(source), before)
        for oid in (first, head):
            self.assertTrue(self.git(source, 'cat-file', '-p', oid))

    def test_snapshot_rejects_nonempty_legacy_grafts(self):
        source, first, head = self.history()
        (source / '.git/info/grafts').write_text(head + '\n', encoding='ascii')
        self.assert_graft_rejected(source, first, head)

    def test_snapshot_rejects_effective_external_graft_file(self):
        source, first, head = self.history()
        grafts = self.base / 'grafts'
        grafts.write_text(head + '\n', encoding='ascii')
        self.assert_graft_rejected(source, first, head, {'GIT_GRAFT_FILE': str(grafts)})
        self.assertEqual(grafts.read_text(), head + '\n')

    def test_snapshot_rejects_grafts_in_linked_worktree_common_metadata(self):
        source, first, head = self.history()
        linked = self.base / 'linked'
        self.git(source, 'worktree', 'add', '--quiet', '--detach', str(linked), head)
        (source / '.git/info/grafts').write_text(head + '\n', encoding='ascii')
        before = tree_hashes(source)
        self.assert_graft_rejected(linked, first, head)
        self.assertEqual(tree_hashes(source), before)

    def test_empty_grafts_and_normal_history_roundtrip(self):
        source, first, head = self.history()
        (source / '.git/info/grafts').write_bytes(b'')
        archive = self.base / 'snapshot.zip'
        self.cli(WORKSPACE, 'snapshot', '--repo', source, '--output', archive)
        target = self.base / 'restored'
        self.assertTrue(self.cli(WORKSPACE, 'restore', '--archive', archive, '--output', target)['verified'])
        self.assertEqual(self.git(target, 'rev-list', 'HEAD'), self.git(source, 'rev-list', 'HEAD'))
        self.assertIn(first.encode(), self.git(target, 'rev-list', 'HEAD'))

    @unittest.skipUnless(os.name == 'nt', 'A real Windows junction requires Windows')
    def test_snapshot_rejects_inside_junction_without_newer_path_api(self):
        source = self.repo()
        payload = source / 'payload'
        payload.mkdir()
        (payload / 'proof.txt').write_bytes(b'necessary result\n')
        (source / '.gitignore').write_bytes(b'payload/\nalias/\n')
        self.git(source, 'add', '.')
        self.git(source, 'commit', '--quiet', '-m', 'ignore')
        alias = source / 'alias'
        self.run_command(['cmd.exe', '/c', 'mklink', '/J', alias, payload])
        try:
            self.assertTrue(getattr(alias.lstat(), 'st_file_attributes', 0) & 0x400)
            module = load(WORKSPACE)
            # This is fallback behavior on the current interpreter, not a native 3.10/3.11 trial.
            newer_api = getattr(Path, 'is_junction', None)
            if newer_api is not None:
                delattr(Path, 'is_junction')
            try:
                with self.assertRaisesRegex(ValueError, 'Links|links|reparse'):
                    module.snapshot(source, self.base / 'snapshot.zip', ['alias'])
            finally:
                if newer_api is not None:
                    setattr(Path, 'is_junction', newer_api)
            self.assertFalse((self.base / 'snapshot.zip').exists())
        finally:
            alias.rmdir()

    def test_inspect_timestamp_only_change_preserves_index_and_staging(self):
        source = self.repo()
        staged = self.git(source, 'ls-files', '--stage')
        path = source / 'keep.txt'
        info = path.stat()
        os.utime(path, ns=(info.st_atime_ns, info.st_mtime_ns + 30_000_000_000))
        before = (source / '.git/index').read_bytes()
        result = self.cli(WORKSPACE, 'inspect', '--repo', source)
        self.assertFalse(result['dirty'])
        self.assertEqual((source / '.git/index').read_bytes(), before)
        self.assertEqual(self.git(source, 'ls-files', '--stage'), staged)
        path.write_bytes(b'actual dirty content\n')
        self.assertTrue(self.cli(WORKSPACE, 'inspect', '--repo', source)['dirty'])

    def test_active_download_names_and_real_built_package_version(self):
        body = (ROOT / 'README.md').read_text(encoding='utf-8')
        section = body.split('下载 [', 1)[1].split('，解压', 1)[0]
        names = re.findall(r'\]\((dist/[^)]+)\)', '[' + section)
        self.assertEqual(names, ['dist/sdd-harness-0.7.3.zip', 'dist/sdd-harness-0.7.3.sha256'])
        archive = self.base / Path(names[0]).name
        result = self.cli(ROOT / 'tools/package_skill.py', '--source', ROOT, '--output', archive)
        self.assertEqual(result['files'], 14)
        self.assertEqual(result['sha256'], hashlib.sha256(archive.read_bytes()).hexdigest())
        with zipfile.ZipFile(archive) as z:
            body = z.read('sdd-harness/SKILL.md').decode('utf-8')
        self.assertRegex(body, r'version:\s*"0\.7\.3"')
        self.assertEqual(body, (ROOT / 'SKILL.md').read_text(encoding='utf-8'))


if __name__ == '__main__':
    unittest.main()
