import unittest

from three_user_datasets_audit import ROOT, safe_member_path


class SafeZipPathTests(unittest.TestCase):
    def test_normal_member_stays_inside_destination(self):
        destination = ROOT / "safe-path-test-root"
        self.assertEqual(safe_member_path("folder/data.csv", destination),
                         (destination / "folder/data.csv").resolve())

    def test_traversal_and_drive_paths_rejected(self):
        destination = ROOT / "safe-path-test-root"
        for name in ("../data.csv", "/data.csv", "C:/data.csv", "folder/../../data.csv"):
            with self.subTest(name=name), self.assertRaises(ValueError):
                safe_member_path(name, destination)


if __name__ == "__main__":
    unittest.main()
