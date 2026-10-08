import hashlib
import json
import shutil
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile


ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / 'tools' / 'package_skill.py'
SOURCE = ROOT


class PackageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='sdd-package-test-')
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)

    def build(self, output, ok=True):
        self.assertTrue(BUILD.exists(), 'Missing distribution builder')
        result = subprocess.run([sys.executable, str(BUILD), '--source', str(SOURCE),
                                 '--output', str(output)], capture_output=True, text=True)
        if ok:
            self.assertEqual(result.returncode, 0, result.stderr)
            return json.loads(result.stdout)
        self.assertNotEqual(result.returncode, 0)

    def test_distribution_installs_after_extraction(self):
        archive = self.base / 'skill.zip'
        result = self.build(archive)
        self.assertEqual(result['sha256'], hashlib.sha256(archive.read_bytes()).hexdigest())
        extracted = self.base / 'extract'
        with zipfile.ZipFile(archive) as z:
            self.assertIsNone(z.testzip())
            self.assertIn('sdd-harness/SKILL.md', z.namelist())
            self.assertFalse(any('/tests/' in name or '/docs/' in name or '__pycache__' in name for name in z.namelist()))
            z.extractall(extracted)
        script = extracted / 'sdd-harness' / 'scripts' / 'install.py'
        result = subprocess.run([sys.executable, str(script), '--into', str(self.base / 'installed')],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        installed = self.base / 'installed' / 'sdd-harness'
        self.assertTrue((installed / 'references' / 'install.md').is_file())
        self.assertEqual((installed / 'SKILL.md').read_bytes(), (SOURCE / 'SKILL.md').read_bytes())

    def test_existing_distribution_is_not_overwritten(self):
        target = self.base / 'existing.zip'
        target.write_bytes(b'preserve')
        self.build(target, ok=False)
        self.assertEqual(target.read_bytes(), b'preserve')

    def test_distribution_inside_source_is_rejected(self):
        target = SOURCE / 'distribution-test.zip'
        self.build(target, ok=False)
        self.assertFalse(target.exists())

    def repository_fixture(self):
        repo = self.base / 'checkout-with-another-name'
        repo.mkdir()
        shutil.copy2(SOURCE / 'SKILL.md', repo / 'SKILL.md')
        for name in ('scripts', 'references', 'assets'):
            shutil.copytree(SOURCE / name, repo / name)
        (repo / 'README.md').write_text('Repository documentation', encoding='utf-8')
        (repo / 'evals').mkdir()
        (repo / 'evals' / 'fixture.json').write_text('{}', encoding='utf-8')
        return repo

    def test_root_repository_installer_excludes_development_files(self):
        repo = self.repository_fixture()
        result = subprocess.run([sys.executable, str(repo / 'scripts' / 'install.py'),
                                 '--into', str(self.base / 'root-installed')],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        installed = self.base / 'root-installed' / 'sdd-harness'
        self.assertFalse((installed / 'README.md').exists())
        self.assertFalse((installed / 'evals').exists())
        self.assertTrue((installed / 'references' / 'install.md').exists())

    def test_root_repository_package_uses_frontmatter_name(self):
        repo = self.repository_fixture()
        output = self.base / 'root.zip'
        result = subprocess.run([sys.executable, str(BUILD), '--source', str(repo),
                                 '--output', str(output)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        with zipfile.ZipFile(output) as z:
            self.assertIn('sdd-harness/SKILL.md', z.namelist())
            self.assertFalse(any('/evals/' in n or n.endswith('README.md') for n in z.namelist()))

    def test_root_repository_can_build_into_dist(self):
        repo = self.repository_fixture()
        output = repo / 'dist' / 'release.zip'
        result = subprocess.run([sys.executable, str(BUILD), '--source', str(repo),
                                 '--output', str(output)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(output.is_file())

    def test_package_rejects_link_to_excluded_repository_file(self):
        repo = self.repository_fixture()
        entry = repo / 'SKILL.md'
        entry.write_text(entry.read_text(encoding='utf-8') + '\n[Development](README.md)\n', encoding='utf-8')
        result = subprocess.run([sys.executable, str(BUILD), '--source', str(repo),
                                 '--output', str(self.base / 'broken-link.zip')],
                                capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.base / 'broken-link.zip').exists())


if __name__ == '__main__':
    unittest.main()
