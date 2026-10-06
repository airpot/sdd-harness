import json
import hashlib
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT
WORKSPACE = SKILL / 'scripts' / 'workspace.py'
INSTALL = SKILL / 'scripts' / 'install.py'


class SkillToolsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='sdd-harness-test-')
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.repo = self.base / '项目 with spaces'
        self.repo.mkdir()
        self.git('init', '--quiet')
        self.git('config', 'user.name', 'Skill Test')
        self.git('config', 'user.email', 'skill-test@example.invalid')
        (self.repo / '.gitignore').write_text('required.bin\n', encoding='utf-8')
        (self.repo / '代码.txt').write_text('original\n', encoding='utf-8')
        self.git('add', '.')
        self.git('commit', '--quiet', '-m', 'fixture')

    def git(self, *args, cwd=None):
        return subprocess.run(['git', '-C', str(cwd or self.repo), *args],
                              check=True, capture_output=True).stdout

    def cli(self, script, *args, ok=True, env=None):
        self.assertTrue(script.is_file(), f'Missing required helper: {script.name}')
        result = subprocess.run([sys.executable, str(script), *map(str, args)],
                                capture_output=True, text=True, encoding='utf-8', env=env)
        if ok:
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            return json.loads(result.stdout)
        self.assertNotEqual(result.returncode, 0, result.stdout)
        return result

    def snapshot(self, *extra):
        archive = self.base / 'snapshot.zip'
        result = self.cli(WORKSPACE, 'snapshot', '--repo', self.repo,
                          '--output', archive, *extra)
        self.assertTrue(self.repo.exists())
        self.assertFalse(result['safe_to_remove'])
        return archive

    def test_clean_repository_does_not_grant_write_or_delete(self):
        result = self.cli(WORKSPACE, 'inspect', '--repo', self.repo)
        self.assertFalse(result['dirty'])
        self.assertEqual(result['activity'], 'unknown')
        self.assertFalse(result['safe_to_remove'])
        self.assertFalse(result['write_authorized'])

    def test_inspect_from_subdirectory_finds_root(self):
        child = self.repo / 'child'
        child.mkdir()
        result = self.cli(WORKSPACE, 'inspect', '--repo', child)
        self.assertEqual(Path(result['root']), self.repo.resolve())

    def test_dirty_untracked_and_explicit_ignored_files_restore(self):
        (self.repo / '代码.txt').write_text('changed\n', encoding='utf-8')
        (self.repo / 'new.txt').write_text('new\n', encoding='utf-8')
        (self.repo / 'required.bin').write_bytes(b'necessary\x00data')
        archive = self.snapshot('--include', 'required.bin')
        self.cli(WORKSPACE, 'verify', '--archive', archive)
        restored = self.base / 'restored'
        self.cli(WORKSPACE, 'restore', '--archive', archive, '--output', restored)
        for name in ['代码.txt', 'new.txt', 'required.bin']:
            self.assertEqual((restored / name).read_bytes(), (self.repo / name).read_bytes())
        self.assertEqual(self.git('rev-parse', 'HEAD'), self.git('rev-parse', 'HEAD', cwd=restored))

    def test_deleted_tracked_file_remains_deleted_after_restore(self):
        (self.repo / '代码.txt').unlink()
        archive = self.snapshot()
        restored = self.base / 'restored'
        self.cli(WORKSPACE, 'restore', '--archive', archive, '--output', restored)
        self.assertFalse((restored / '代码.txt').exists())

    def test_unpushed_commit_is_in_restore(self):
        (self.repo / '代码.txt').write_text('second commit\n', encoding='utf-8')
        self.git('add', '.')
        self.git('commit', '--quiet', '-m', 'not pushed')
        archive = self.snapshot()
        restored = self.base / 'restored'
        self.cli(WORKSPACE, 'restore', '--archive', archive, '--output', restored)
        self.assertEqual(self.git('rev-parse', 'HEAD'), self.git('rev-parse', 'HEAD', cwd=restored))

    def test_sha256_repository_restores_with_original_object_format(self):
        self.repo = self.base / 'sha256'
        self.repo.mkdir()
        self.git('init', '--quiet', '--object-format=sha256')
        self.git('config', 'user.name', 'Skill Test')
        self.git('config', 'user.email', 'skill-test@example.invalid')
        (self.repo / 'file.txt').write_text('sha256 content', encoding='utf-8')
        self.git('add', '.')
        self.git('commit', '--quiet', '-m', 'sha256 fixture')
        archive = self.snapshot()
        target = self.base / 'restored'
        self.cli(WORKSPACE, 'restore', '--archive', archive, '--output', target)
        self.assertEqual(self.git('rev-parse', '--show-object-format', cwd=target).strip(), b'sha256')
        self.assertEqual(self.git('rev-parse', 'HEAD'), self.git('rev-parse', 'HEAD', cwd=target))

    def test_unborn_sha256_repository_preserves_object_format(self):
        self.repo = self.base / 'sha256-unborn'
        self.repo.mkdir()
        self.git('init', '--quiet', '--object-format=sha256')
        (self.repo / 'file.txt').write_text('not committed', encoding='utf-8')
        archive = self.snapshot()
        target = self.base / 'restored'
        self.cli(WORKSPACE, 'restore', '--archive', archive, '--output', target)
        self.assertEqual(self.git('rev-parse', '--show-object-format', cwd=target).strip(), b'sha256')

    def test_restore_uses_source_format_despite_different_environment_default(self):
        self.assertEqual(self.git('rev-parse', '--show-object-format').strip(), b'sha1')
        archive = self.snapshot()
        target = self.base / 'restored'
        self.cli(WORKSPACE, 'restore', '--archive', archive, '--output', target,
                 env={**os.environ, 'GIT_DEFAULT_HASH': 'sha256'})
        self.assertEqual(self.git('rev-parse', '--show-object-format', cwd=target).strip(), b'sha1')

    def test_ignored_files_are_not_collected_implicitly(self):
        (self.repo / 'required.bin').write_bytes(b'private')
        archive = self.snapshot()
        with zipfile.ZipFile(archive) as z:
            self.assertNotIn('files/required.bin', z.namelist())

    def test_snapshot_inside_source_is_rejected(self):
        self.cli(WORKSPACE, 'snapshot', '--repo', self.repo,
                 '--output', self.repo / 'bad.zip', ok=False)
        self.assertFalse((self.repo / 'bad.zip').exists())

    def test_include_outside_root_is_rejected(self):
        outside = self.base / 'outside.txt'
        outside.write_text('outside', encoding='utf-8')
        self.cli(WORKSPACE, 'snapshot', '--repo', self.repo,
                 '--output', self.base / 'bad.zip', '--include', '../outside.txt', ok=False)

    def test_archive_is_not_overwritten(self):
        archive = self.base / 'existing.zip'
        archive.write_bytes(b'unique backup')
        self.cli(WORKSPACE, 'snapshot', '--repo', self.repo, '--output', archive, ok=False)
        self.assertEqual(archive.read_bytes(), b'unique backup')

    def test_restore_never_overwrites_existing_directory(self):
        archive = self.snapshot()
        target = self.base / 'existing'
        target.mkdir()
        (target / 'keep.txt').write_text('keep', encoding='utf-8')
        self.cli(WORKSPACE, 'restore', '--archive', archive, '--output', target, ok=False)
        self.assertEqual((target / 'keep.txt').read_text(encoding='utf-8'), 'keep')

    def test_tampered_payload_is_rejected(self):
        archive = self.snapshot()
        altered = self.base / 'tampered.zip'
        with zipfile.ZipFile(archive) as original, zipfile.ZipFile(altered, 'w') as dest:
            for entry in original.infolist():
                data = original.read(entry.filename)
                dest.writestr(entry, b'tampered' if entry.filename == 'files/代码.txt' else data)
        self.cli(WORKSPACE, 'verify', '--archive', altered, ok=False)

    def test_unlisted_traversal_entry_is_rejected_before_restore(self):
        archive = self.snapshot()
        with zipfile.ZipFile(archive, 'a') as z:
            z.writestr('files/../../escape.txt', 'escape')
        target = self.base / 'restored'
        self.cli(WORKSPACE, 'restore', '--archive', archive, '--output', target, ok=False)
        self.assertFalse(target.exists())
        self.assertFalse((self.base / 'escape.txt').exists())

    def test_git_metadata_is_rejected_case_insensitively(self):
        archive = self.snapshot()
        forged = self.base / 'git-metadata.zip'
        with zipfile.ZipFile(archive) as original, zipfile.ZipFile(forged, 'w') as dest:
            manifest = json.loads(original.read('manifest.json'))
            for entry in manifest['files']:
                if entry['path'] == '代码.txt':
                    entry['path'] = '.GIT/config'
            for name in original.namelist():
                if name == 'manifest.json':
                    dest.writestr(name, json.dumps(manifest))
                else:
                    dest.writestr('files/.GIT/config' if name == 'files/代码.txt' else name, original.read(name))
        self.cli(WORKSPACE, 'verify', '--archive', forged, ok=False)

    def test_windows_short_name_cannot_write_git_metadata(self):
        forged = self.base / 'short-name.zip'
        payload = b'# harmless metadata injection fixture\n'
        name = 'GIT~1/hooks/post-checkout'
        manifest = {'format': 1, 'source': {'head': None}, 'bundle': None, 'deleted': [],
                    'files': [{'path': name, 'mode': 0o644, 'size': len(payload),
                               'sha256': hashlib.sha256(payload).hexdigest()}]}
        with zipfile.ZipFile(forged, 'w') as z:
            z.writestr('manifest.json', json.dumps(manifest))
            z.writestr('files/' + name, payload)
        target = self.base / 'restored'
        self.cli(WORKSPACE, 'restore', '--archive', forged, '--output', target, ok=False)
        self.assertFalse(target.exists())

    def test_born_repository_without_commits_restores(self):
        empty = self.base / 'unborn'
        empty.mkdir()
        self.git('init', '--quiet', cwd=empty)
        (empty / 'first.txt').write_text('first', encoding='utf-8')
        archive = self.base / 'unborn.zip'
        self.cli(WORKSPACE, 'snapshot', '--repo', empty, '--output', archive)
        target = self.base / 'restored'
        self.cli(WORKSPACE, 'restore', '--archive', archive, '--output', target)
        self.assertEqual((target / 'first.txt').read_text(encoding='utf-8'), 'first')

    def test_git_symlink_mode_is_rejected_even_on_windows(self):
        blob = self.git('hash-object', '-w', '--stdin').decode().strip()
        self.git('update-index', '--add', '--cacheinfo', f'120000,{blob},link')
        self.cli(WORKSPACE, 'snapshot', '--repo', self.repo,
                 '--output', self.base / 'unsupported.zip', ok=False)

    def test_install_relocation_and_idempotency(self):
        target = self.base / 'agent-skills'
        first = self.cli(INSTALL, '--into', target)
        installed = Path(first['installed'])
        self.assertTrue((installed / 'SKILL.md').is_file())
        second = self.cli(installed / 'scripts' / 'install.py', '--into', target)
        self.assertEqual(second['status'], 'already-installed')
        self.cli(installed / 'scripts' / 'workspace.py', 'inspect', '--repo', self.repo)

    def test_install_refuses_changed_existing_skill(self):
        target = self.base / 'agent-skills'
        first = self.cli(INSTALL, '--into', target)
        existing = Path(first['installed']) / 'SKILL.md'
        existing.write_text('local customization', encoding='utf-8')
        self.cli(INSTALL, '--into', target, ok=False)
        self.assertEqual(existing.read_text(encoding='utf-8'), 'local customization')

    def test_install_inside_source_is_rejected(self):
        target = SKILL / 'nested-install-test'
        self.cli(INSTALL, '--into', target, ok=False)
        self.assertFalse(target.exists())


if __name__ == '__main__':
    unittest.main()
