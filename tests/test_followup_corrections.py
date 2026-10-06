import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class LegacyJunctionTests(unittest.TestCase):
    def setUp(self):
        if os.name != 'nt':
            self.skipTest('Real Windows junction test requires Windows')
        self.temp = tempfile.TemporaryDirectory(prefix='sdd-071-junction-')
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.source = self.base / 'source'
        self.source.mkdir()
        shutil.copy2(ROOT / 'SKILL.md', self.source / 'SKILL.md')
        for name in ('scripts', 'references', 'assets'):
            shutil.copytree(ROOT / name, self.source / name)
        self.outside = self.base / 'outside'
        self.outside.mkdir()
        (self.outside / 'outside.txt').write_text('boundary sentinel', encoding='utf-8')

    def junction(self, path, destination=None):
        result = subprocess.run(['cmd', '/c', 'mklink', '/J', str(path), str(destination or self.outside)],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.addCleanup(os.rmdir, path)
        self.assertFalse(path.is_symlink())

    def legacy_run(self, script, *args):
        # Exercise the old API branch on the current interpreter, not a claimed 3.10 trial.
        code = "from pathlib import Path; import runpy,sys; " \
               "\nif hasattr(Path, 'is_junction'): delattr(Path, 'is_junction')\n" \
               "sys.argv=sys.argv[1:]; runpy.run_path(sys.argv[0], run_name='__main__')"
        return subprocess.run([sys.executable, '-B', '-c', code, str(script), *map(str, args)],
                              capture_output=True, text=True)

    def test_legacy_installer_rejects_nested_source_junction(self):
        self.junction(self.source / 'assets' / 'escape')
        target = self.base / 'installed'
        result = self.legacy_run(self.source / 'scripts' / 'install.py', '--into', target)
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn('links', result.stderr)
        self.assertFalse(target.exists())

    def test_legacy_installer_rejects_lexical_source_root_junction(self):
        linked_source = self.base / 'linked-source'
        self.junction(linked_source, self.source)
        target = self.base / 'installed'
        result = self.legacy_run(linked_source / 'scripts' / 'install.py', '--into', target)
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn('links', result.stderr)
        self.assertFalse(target.exists())

    def test_legacy_builder_rejects_lexical_source_root_junction(self):
        linked_source = self.base / 'linked-source'
        self.junction(linked_source, self.source)
        output = self.base / 'package.zip'
        result = self.legacy_run(ROOT / 'tools' / 'package_skill.py', '--source', linked_source, '--output', output)
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn('linked files', result.stderr)
        self.assertFalse(output.exists())

    def test_legacy_installer_rejects_top_level_source_junction(self):
        self.junction(self.source / 'agents')
        target = self.base / 'installed'
        result = self.legacy_run(self.source / 'scripts' / 'install.py', '--into', target)
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn('links', result.stderr)
        self.assertFalse(target.exists())

    def test_legacy_installer_rejects_existing_target_inventory_junction(self):
        target = self.base / 'installed'
        shutil.copytree(self.source, target / 'sdd-harness')
        self.junction(target / 'sdd-harness' / 'assets' / 'escape')
        result = self.legacy_run(self.source / 'scripts' / 'install.py', '--into', target)
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn('links', result.stderr)
        self.assertEqual((self.outside / 'outside.txt').read_text(), 'boundary sentinel')

    def test_legacy_installer_rejects_final_target_junction(self):
        target = self.base / 'installed'
        target.mkdir()
        self.junction(target / 'sdd-harness')
        result = self.legacy_run(self.source / 'scripts' / 'install.py', '--into', target)
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn('linked skill', result.stderr)
        self.assertEqual(list(self.outside.iterdir()), [self.outside / 'outside.txt'])

    def test_legacy_builder_rejects_nested_junction_before_output(self):
        self.junction(self.source / 'assets' / 'escape')
        output = self.base / 'package.zip'
        result = self.legacy_run(ROOT / 'tools' / 'package_skill.py', '--source', self.source, '--output', output)
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn('linked files', result.stderr)
        self.assertFalse(output.exists())


class RelocatedTemplateTests(unittest.TestCase):
    def test_all_templates_require_resolved_policy_before_save(self):
        with tempfile.TemporaryDirectory(prefix='sdd-071-record-') as temporary:
            project = Path(temporary)
            policy = project / 'instructions' / 'policy.md'
            policy.parent.mkdir()
            policy.write_text('Project writing policy.', encoding='utf-8')
            skill_policy = project / '.agents' / 'skills' / 'sdd-harness' / 'references' / 'writing.md'
            skill_policy.parent.mkdir(parents=True)
            shutil.copy2(ROOT / 'references' / 'writing.md', skill_policy)
            for template in ('change', 'handoff', 'release'):
                body = (ROOT / 'assets' / (template + '.md')).read_text(encoding='utf-8')
                with self.subTest(template=template):
                    self.assertIn('<accessible-writing-policy-reference>', body)
                    self.assertIn('Before saving', body)
                    self.assertNotIn('../references/writing.md', body)
                    for selected_policy in (policy, skill_policy):
                        record = project / 'arbitrary' / 'deep' / (template + '.md')
                        record.parent.mkdir(parents=True, exist_ok=True)
                        relative = Path(os.path.relpath(selected_policy, record.parent)).as_posix()
                        completed = body.replace('<accessible-writing-policy-reference>', '[writing policy](' + relative + ')')
                        record.write_text(completed, encoding='utf-8')
                        links = re.findall(r'\]\(([^)]+)\)', record.read_text(encoding='utf-8'))
                        self.assertTrue(links)
                        for link in links:
                            self.assertTrue((record.parent / link).is_file(), link)
                            self.assertEqual((record.parent / link).resolve(), selected_policy.resolve())


class InvocationBindingTests(unittest.TestCase):
    def test_new_native_inputs_bind_adaptation_and_observed_route(self):
        path = ROOT / 'evals' / 'results' / '0.7.1-native-requests.json'
        self.assertTrue(path.is_file(), 'Missing actual native invocation records')
        saved = json.loads(path.read_text(encoding='utf-8'))
        corpus = ROOT / saved['corpus_path']
        self.assertEqual(hashlib.sha256(corpus.read_bytes()).hexdigest(), saved['corpus_sha256'])
        cases = {c['id']: c for c in json.loads(corpus.read_text(encoding='utf-8'))['cases']}
        self.assertEqual(len(saved['requests']), 3)
        for record in saved['requests']:
            with self.subTest(request=record['request_id']):
                self.assertEqual(record['canonical_input'], cases[record['source_case_id']]['prompt'])
                self.assertEqual(record['input_sha256'], hashlib.sha256(record['actual_input'].encode('utf-8')).hexdigest())
                self.assertEqual(record['canonical_input_sha256'], hashlib.sha256(record['canonical_input'].encode('utf-8')).hexdigest())
                self.assertTrue(record['adaptation']['changed_facts'])
                self.assertEqual(record['observed_route'], record['expected_route'])
                self.assertEqual(record['expected_route'], cases[record['source_case_id']]['expected_route'])
                self.assertEqual(record['exit_code'], 0)
                self.assertEqual(record['before_files_sha256'], record['after_files_sha256'])
                self.assertEqual(len(record['portable_source_sha256']), 14)
                self.assertEqual(record['exact_corpus_coverage'], record['actual_input'] == record['canonical_input'])
                if record['expected_route'] is None:
                    self.assertEqual(record['raw_completed_commands'], [])
                    self.assertFalse(record['full_entry_output_observed'])
                else:
                    self.assertTrue(record['full_entry_output_observed'])
                    self.assertFalse(record['subagent_reference_output_observed'])

    def test_historical_correction_binds_actual_prompts_without_solo_coverage(self):
        correction_path = ROOT / 'evals' / 'results' / '0.7.0-invocation-errata.json'
        self.assertTrue(correction_path.is_file(), 'Missing dated historical invocation correction')
        correction = json.loads(correction_path.read_text(encoding='utf-8'))
        self.assertEqual(correction['original_commit'], 'd92ee047535d392c6d6f46096dda55060777ff2e')
        for path, expected in correction['original_artifact_sha256'].items():
            self.assertEqual(hashlib.sha256((ROOT / path).read_bytes()).hexdigest(), expected, path)
        prompts = json.loads((ROOT / 'evals' / 'results' / '0.7.0-native-prompts.json').read_text(encoding='utf-8'))
        for record in correction['executions']:
            self.assertEqual(record['input_sha256'], hashlib.sha256(prompts[record['original_prompt_key']].encode('utf-8')).hexdigest())
            self.assertIsNone(record['source_case_id'])
            self.assertFalse(record['exact_corpus_coverage'])
            self.assertIn('adaptation', record)
            self.assertIn('observed_route', record)
            if record['original_prompt_key'] in ('explicit', 'implicit'):
                self.assertEqual(record['expected_route'], 'subagents')
                self.assertEqual(record['observed_route'], 'subagents')


if __name__ == '__main__':
    unittest.main()
