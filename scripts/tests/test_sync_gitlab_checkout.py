import hashlib
import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location("sync_checkout", Path(__file__).parents[1]/"sync_gitlab_checkout.py")
m = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(m)
PIN = 'c52b987fc1cde38c2e94a8a6286556ccd8999f02'


class CheckoutSyncTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.target = self.root/'nps-26-009-datacards'
        self.target.mkdir()
        self.git('init', '-b', 'master')
        self.git('config', 'user.email', 'test@example.invalid')
        self.git('config', 'user.name', 'Test')
        self.git('remote', 'add', 'origin', 'ssh://git@gitlab.cern.ch:7999/cms-analysis/nps/nps-26-009/datacards.git')
        self.git('update-index', '--add', '--cacheinfo', '160000', PIN, 'systematics')
        (self.target/'README.md').write_text('previous submitted README')
        (self.target/'.gitignore').write_text('*.root\n')
        (self.target/'review_validation').mkdir()
        (self.target/'review_validation/old.log').write_text('unique old fit log')
        self.git('add', 'README.md', '.gitignore', 'review_validation/old.log')
        self.git('commit', '-m', 'initial submitted version')
        (self.target/'systematics').mkdir()
        (self.target/'systematics/keep.txt').write_text('do not touch submodule work tree')
        # A previously staged user edit must remain staged as it was.
        (self.target/'README.md').write_text('partially staged user README')
        self.git('add', 'README.md')
        self.index_before = self.git('rev-parse', ':README.md')
        (self.target/'README.md').write_text('unique unstaged user README')
        self.package = self.root/'package'
        self.package.mkdir()
        (self.package/'README.md').write_text('current compact README')
        (self.package/'input').mkdir()
        (self.package/'input/datacard_M20_Run2Run3.txt').write_text('current card')
        manifest = {'source_repository': 'https://github.com/joonblee/combine_review',
                    'source_commit': 'a'*40, 'systematics_submodule_commit': PIN,
                    'files': {n: {'source_path': n, 'sha256': m.digest(self.package/n)}
                              for n in ('README.md', 'input/datacard_M20_Run2Run3.txt')},
                    'generated_files': {}}
        (self.package/'preservation').mkdir()
        (self.package/'preservation/submission_manifest.json').write_text(json.dumps(manifest))
        self.manifest, self.desired = m.validate_export(self.package)

    def git(self, *args):
        return subprocess.check_output(['git', '-C', str(self.target), *args], stderr=subprocess.PIPE).decode().strip()

    def test_export_checksums_are_required(self):
        (self.package/'input/datacard_M20_Run2Run3.txt').write_text('corrupted')
        with self.assertRaisesRegex(RuntimeError, 'Export checksum mismatch'):
            m.validate_export(self.package)

    def test_plan_is_read_only_and_reports_obsolete_results(self):
        before = m.inventory(self.target, m.PROTECTED)
        changed, retired = m.plan(self.target, self.desired)
        self.assertIn('README.md', changed)
        self.assertIn('review_validation/old.log', retired)
        self.assertEqual(before, m.inventory(self.target, m.PROTECTED))

    def test_install_preserves_git_settings_index_submodule_and_original_edits(self):
        previous = m.check_checkout(self.target, PIN)
        origin = self.git('remote', 'get-url', 'origin')
        backup = m.install(self.target, self.package, self.desired, self.manifest)
        self.assertEqual(m.inventory(self.target, m.PROTECTED), self.desired)
        self.assertEqual(self.git('rev-parse', 'HEAD'), previous['head'])
        self.assertEqual(self.git('branch', '--show-current'), 'master')
        self.assertEqual(self.git('remote', 'get-url', 'origin'), origin)
        self.assertEqual(self.git('rev-parse', ':README.md'), self.index_before)
        self.assertEqual((self.target/'.gitignore').read_text(), '*.root\n')
        self.assertEqual((self.target/'systematics/keep.txt').read_text(), 'do not touch submodule work tree')
        self.assertEqual((backup/'README.md').read_text(), 'unique unstaged user README')
        self.assertEqual((backup/'review_validation/old.log').read_text(), 'unique old fit log')
        self.assertTrue((backup/'sync_receipt.json').is_file())
        self.assertEqual(m.plan(self.target, self.desired), ([], []))

    def test_corruption_after_install_restores_original_checkout(self):
        original_inventory = m.inventory
        calls = []
        def check(root, exclude=()):
            if root == self.target:
                calls.append(True)
                return {'corrupted': 'unexpected'}
            return original_inventory(root, exclude)
        with patch.object(m, 'inventory', side_effect=check):
            with self.assertRaisesRegex(RuntimeError, 'does not match export'):
                m.install(self.target, self.package, self.desired, self.manifest)
        self.assertTrue(calls)
        self.assertEqual((self.target/'README.md').read_text(), 'unique unstaged user README')
        self.assertEqual((self.target/'review_validation/old.log').read_text(), 'unique old fit log')
        self.assertFalse((self.target/'input').exists())
        self.assertEqual(self.git('rev-parse', ':README.md'), self.index_before)

    def test_mismatched_submodule_pin_stops_before_any_install(self):
        with self.assertRaisesRegex(RuntimeError, 'Expected existing systematics gitlink'):
            m.check_checkout(self.target, 'b'*40)
        self.assertEqual((self.target/'README.md').read_text(), 'unique unstaged user README')

    def test_undeclared_files_are_rejected(self):
        (self.package/'unreviewed.txt').write_text('not declared')
        with self.assertRaisesRegex(RuntimeError, 'undeclared'):
            m.validate_export(self.package)


if __name__ == '__main__':
    unittest.main()
