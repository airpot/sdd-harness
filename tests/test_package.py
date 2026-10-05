import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile


ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / 'tools' / 'package_skill.py'
SOURCE = ROOT / 'skills' / 'sdd-harness'


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


if __name__ == '__main__':
    unittest.main()
