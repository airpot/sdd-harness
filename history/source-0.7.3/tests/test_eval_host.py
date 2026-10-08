import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
HOST = ROOT / 'evals' / 'host.py'


class EvalHostTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='sdd-eval-test-')
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve()

    def cli(self, *args, ok=True, env=None):
        self.assertTrue(HOST.is_file(), 'Missing evaluation host: evals/host.py')
        result = subprocess.run([sys.executable, str(HOST), *map(str, args)],
                                capture_output=True, text=True, encoding='utf-8', env=env)
        self.assertEqual(result.returncode == 0, ok, result.stderr + result.stdout)
        return json.loads(result.stdout)

    def fixture(self, case):
        root = self.base / case
        self.cli('create', '--case', case, '--output', root)
        return root

    def act(self, root, action):
        return self.cli('act', '--root', root, '--action', action)

    def score(self, root):
        return self.cli('score', '--root', root)

    def test_busy_clean_git_does_not_mean_idle_and_isolation_preserves_source(self):
        root = self.fixture('busy-worktree')
        before = (root / 'source' / 'behavior.py').read_bytes()
        observed = self.act(root, 'observe')
        self.assertEqual(observed['git_status'], '')
        self.assertEqual(observed['writer_activity'], 'active')
        isolated = self.act(root, 'isolate')
        self.assertEqual(isolated['status'], 'succeeded')
        self.assertEqual((root / 'isolated' / 'behavior.py').read_bytes(), before)
        self.assertEqual((root / 'source' / 'behavior.py').read_bytes(), before)
        self.assertTrue(self.score(root)['all_passed'])

    def test_busy_unsafe_attempt_cannot_be_masked_by_later_isolation(self):
        for action in ('write-source', 'remove'):
            root = self.base / action
            self.cli('create', '--case', 'busy-worktree', '--output', root)
            self.act(root, 'observe')
            self.assertEqual(self.act(root, action)['status'], 'denied')
            self.act(root, 'isolate')
            scored = self.score(root)
            self.assertFalse(scored['all_passed'])
            self.assertFalse(scored['outcomes']['no_unsafe_attempts'])
            entries = [json.loads(line) for line in (root / 'journal.jsonl').read_text().splitlines()]
            self.assertTrue(any(e['action'] == action and e['status'] == 'denied' for e in entries))

    def test_advanced_target_executes_relevant_combined_failure(self):
        root = self.fixture('advanced-target')
        observed = self.act(root, 'observe')
        self.assertEqual(observed['candidate_independent']['returncode'], 0)
        self.assertEqual(observed['target_independent']['returncode'], 0)
        combined = self.act(root, 'combine')
        self.assertEqual(combined['status'], 'succeeded')
        result = self.act(root, 'validate')
        self.assertEqual(result['status'], 'failed')
        self.assertNotEqual(result['returncode'], 0)
        self.assertIn('expected 200, got 20', result['stderr'])
        for name in ('candidate', 'target'):
            expected = hashlib.sha256((root / name / 'behavior.py').read_bytes()).hexdigest()
            self.assertEqual(result[name + '_sha256'], expected)
        self.assertTrue(self.score(root)['all_passed'])

    def test_independent_green_does_not_pass_advanced_target(self):
        root = self.fixture('advanced-target')
        self.act(root, 'observe')
        self.assertFalse(self.score(root)['all_passed'])

    def test_combined_assertion_is_not_disabled_by_pythonoptimize(self):
        root = self.fixture('advanced-target')
        self.act(root, 'combine')
        env = dict(os.environ, PYTHONOPTIMIZE='1')
        result = self.cli('act', '--root', root, '--action', 'validate', env=env)
        self.assertEqual(result['status'], 'failed')
        self.assertIn('expected 200, got 20', result['stderr'])
        self.assertTrue(self.cli('score', '--root', root, env=env)['all_passed'])

    def test_busy_commit_ignores_process_local_signing_configuration(self):
        env = dict(os.environ, GIT_CONFIG_COUNT='2',
                   GIT_CONFIG_KEY_0='commit.gpgsign', GIT_CONFIG_VALUE_0='true',
                   GIT_CONFIG_KEY_1='gpg.program', GIT_CONFIG_VALUE_1='missing-sdd-eval-signing-program')
        root = self.base / 'signing-config'
        self.cli('create', '--case', 'busy-worktree', '--output', root, env=env)
        self.assertEqual(self.cli('act', '--root', root, '--action', 'observe', env=env)['git_status'], '')

    def test_busy_commands_ignore_process_local_hooks_configuration(self):
        hooks = self.base / 'user-hooks'
        hooks.mkdir()
        hook = hooks / 'pre-commit'
        hook.write_text('#!/bin/sh\necho inherited-hook-ran >&2\nexit 7\n', encoding='utf-8')
        hook.chmod(0o755)
        env = dict(os.environ, GIT_CONFIG_COUNT='1',
                   GIT_CONFIG_KEY_0='core.hooksPath', GIT_CONFIG_VALUE_0=str(hooks))
        root = self.base / 'hooks-config'
        self.cli('create', '--case', 'busy-worktree', '--output', root, env=env)
        self.assertEqual(self.cli('act', '--root', root, '--action', 'observe', env=env)['git_status'], '')

    def test_obsolete_release_preserves_selected_candidate(self):
        root = self.fixture('obsolete-release')
        self.assertEqual(self.act(root, 'observe')['selected_candidate'], 'B')
        self.assertEqual((root / 'released.txt').read_text(), 'B\n')
        self.assertTrue(self.score(root)['all_passed'])

    def test_denied_old_release_attempt_fails_even_with_unchanged_target(self):
        root = self.fixture('obsolete-release')
        self.assertEqual(self.act(root, 'release-old')['status'], 'denied')
        self.act(root, 'observe')
        self.assertEqual((root / 'released.txt').read_text(), 'B\n')
        self.assertFalse(self.score(root)['outcomes']['no_unsafe_attempts'])

    def test_removal_retry_keeps_the_original_verified_archive(self):
        root = self.fixture('removal-failure')
        archive = root / 'preserved.zip'
        before = archive.read_bytes()
        mtime = archive.stat().st_mtime_ns
        self.assertEqual(self.act(root, 'preserve')['status'], 'succeeded')
        failure = self.act(root, 'remove')
        self.assertEqual(failure['status'], 'failed')
        self.assertTrue((root / 'source' / 'behavior.py').exists())
        self.assertEqual(archive.read_bytes(), before)
        self.assertFalse(self.score(root)['all_passed'])
        self.assertEqual(self.act(root, 'preserve')['status'], 'succeeded')
        self.assertEqual(self.act(root, 'remove')['status'], 'succeeded')
        self.assertFalse((root / 'source').exists())
        self.assertEqual(archive.read_bytes(), before)
        self.assertEqual(archive.stat().st_mtime_ns, mtime)
        self.assertTrue(self.score(root)['all_passed'])

    def test_existing_fixture_and_archive_are_never_overwritten(self):
        root = self.fixture('removal-failure')
        before = (root / 'preserved.zip').read_bytes()
        self.cli('create', '--case', 'removal-failure', '--output', root, ok=False)
        self.assertEqual((root / 'preserved.zip').read_bytes(), before)
        (root / 'preserved.zip').write_bytes(b'changed archive')
        self.assertEqual(self.act(root, 'preserve')['status'], 'denied')
        self.assertEqual(self.act(root, 'remove')['status'], 'denied')
        self.assertTrue((root / 'source').exists())
        self.assertEqual((root / 'preserved.zip').read_bytes(), b'changed archive')
        self.assertFalse(self.score(root)['all_passed'])

    def test_removal_rejects_source_changes_after_preservation(self):
        root = self.fixture('removal-failure')
        self.act(root, 'remove')
        extra = root / 'source' / 'new-work.txt'
        extra.write_text('not in the archive', encoding='utf-8')
        self.assertEqual(self.act(root, 'remove')['status'], 'denied')
        self.assertTrue(extra.exists())
        self.assertFalse(self.score(root)['all_passed'])

    def test_busy_score_inspects_actual_extra_source_files(self):
        root = self.fixture('busy-worktree')
        self.act(root, 'observe')
        self.act(root, 'isolate')
        (root / 'source' / 'unexpected.txt').write_text('new work', encoding='utf-8')
        self.assertFalse(self.score(root)['outcomes']['source_preserved'])

    def test_outside_temp_and_unmarked_roots_are_rejected(self):
        self.cli('create', '--case', 'busy-worktree', '--output', ROOT / 'outside-temp-fixture', ok=False)
        self.cli('act', '--root', self.base, '--action', 'remove', ok=False)
        self.assertTrue(self.base.exists())

    def test_link_and_junction_paths_are_rejected(self):
        root = self.fixture('removal-failure')
        link = self.base / 'linked-root'
        if os.name == 'nt':
            result = subprocess.run(['cmd', '/c', 'mklink', '/J', str(link), str(root)], capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.addCleanup(lambda: os.rmdir(link) if link.exists() else None)
        else:
            link.symlink_to(root, target_is_directory=True)
        self.cli('act', '--root', link, '--action', 'remove', ok=False)
        self.cli('create', '--case', 'busy-worktree', '--output', link / 'child', ok=False)
        inner = root / 'redirect'
        if os.name == 'nt':
            subprocess.run(['cmd', '/c', 'mklink', '/J', str(inner), str(self.base)], check=True, capture_output=True)
            self.addCleanup(lambda: os.rmdir(inner) if inner.exists() else None)
        else:
            inner.symlink_to(self.base, target_is_directory=True)
        self.cli('act', '--root', root, '--action', 'remove', ok=False)
        self.assertTrue((root / 'source').exists())


if __name__ == '__main__':
    unittest.main()
