import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("updater", Path(__file__).with_name("update-cask.py"))
updater = importlib.util.module_from_spec(spec)
spec.loader.exec_module(updater)


class CaskUpdateTests(unittest.TestCase):
    def original(self):
        return '  version "1.0.0"\n  sha256 arm:   "' + 'a' * 64 + '",\n         intel: "' + 'b' * 64 + '"\n\n  app "DayEdge.app"\n'

    def test_version_and_both_hashes_change_together(self):
        updated = updater.update_text(self.original(), "1.0.1", {"arm": "c" * 64, "intel": "d" * 64})
        self.assertIn('version "1.0.1"', updated)
        self.assertIn('arm:   "' + 'c' * 64, updated)
        self.assertIn('intel: "' + 'd' * 64, updated)
        self.assertTrue(updated.endswith('  app "DayEdge.app"\n'))

    def test_both_checksums_are_required(self):
        with self.assertRaises(ValueError):
            updater.update_text(self.original(), "1.0.1", {"arm": "c" * 64})

    def test_downgrade_is_rejected(self):
        with self.assertRaises(ValueError):
            updater.update_text(self.original(), "0.9.0", {"arm": "c" * 64, "intel": "d" * 64})

    def test_missing_checksum_stanza_is_rejected(self):
        with self.assertRaises(ValueError):
            updater.update_text('  version "1.0.0"\n', "1.0.1", {"arm": "c" * 64, "intel": "d" * 64})

    def test_malformed_checksum_is_rejected(self):
        with self.assertRaises(ValueError):
            updater.checksum('not-a-checksum', 'DayEdge-1.0.1-arm64.zip')

    def test_checksum_must_name_the_correct_archive(self):
        with self.assertRaises(ValueError):
            updater.checksum('a' * 64 + '  other.zip', 'DayEdge-1.0.1-arm64.zip')

    def test_valid_checksum_accepts_shasum_format(self):
        self.assertEqual(updater.checksum('A' * 64 + '  DayEdge-1.0.1-arm64.zip\n', 'DayEdge-1.0.1-arm64.zip'), 'a' * 64)

    def test_draft_release_is_rejected(self):
        with self.assertRaises(ValueError):
            updater.release_version({"tag_name": "v1.0.1", "draft": True, "published_at": "2026-10-11"})

    def test_prerelease_is_rejected(self):
        with self.assertRaises(ValueError):
            updater.release_version({"tag_name": "v1.0.1", "prerelease": True, "published_at": "2026-10-11"})

    def test_missing_intel_asset_prevents_all_downloads(self):
        with patch.object(updater, 'request') as request:
            with self.assertRaises(ValueError):
                updater.verified_checksums({"assets": [
                    {"name": "DayEdge-1.0.1-arm64.zip" + suffix, "state": "uploaded"}
                    for suffix in ("", ".sha256")
                ]}, "1.0.1")
            request.assert_not_called()

    def test_mismatched_zip_is_rejected(self):
        import io
        def response(url):
            if url.endswith('.sha256'):
                return io.BytesIO(('a' * 64 + '  DayEdge-1.0.1-arm64.zip\n').encode())
            return io.BytesIO(b'wrong archive')
        assets = [{"name": f"DayEdge-1.0.1-{arch}.zip{suffix}", "state": "uploaded"}
                  for arch in ('arm64', 'x86_64') for suffix in ('', '.sha256')]
        with patch.object(updater, 'request', side_effect=response):
            with self.assertRaisesRegex(ValueError, 'does not match'):
                updater.verified_checksums({"assets": assets}, "1.0.1")


if __name__ == '__main__':
    unittest.main()
