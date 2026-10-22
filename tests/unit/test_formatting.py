"""Unit tests for DiskMize formatting and resource paths."""

import unittest

from diskmize.formatting import datetime_from_timestamp, format_size
from diskmize.paths import icon_ico, icon_png


class TestFormatting(unittest.TestCase):
    def test_format_size_small(self) -> None:
        self.assertEqual(format_size(1536), "1.50 KB")

    def test_format_size_large(self) -> None:
        self.assertEqual(format_size(5 * 1024**4), "5.00 TB")

    def test_datetime_from_timestamp(self) -> None:
        dt = datetime_from_timestamp(1609459200.0)
        self.assertEqual(dt.year, 2021)

    def test_format_size_negative_raises(self) -> None:
        with self.assertRaises(ValueError):
            format_size(-100)

    def test_format_size_bool_raises(self) -> None:
        with self.assertRaises(TypeError):
            format_size(True)

    def test_asset_paths_exist(self) -> None:
        self.assertTrue(icon_png().is_file())
        self.assertTrue(icon_ico().is_file())


if __name__ == "__main__":
    unittest.main()
