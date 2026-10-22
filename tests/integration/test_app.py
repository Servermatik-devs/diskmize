"""Headless integration tests for DiskMize filesystem scanning."""

from pathlib import Path

from diskmize.scanner import largest_files, scan_files, top_folders


def test_scan_finds_files(tmp_path: Path) -> None:
    (tmp_path / "one.bin").write_bytes(b"x" * 500)
    (tmp_path / "two.bin").write_bytes(b"y" * 1000)

    result = scan_files(tmp_path)

    sizes = {entry.name: entry.size for entry in result.entries}
    assert sizes["one.bin"] == 500
    assert sizes["two.bin"] == 1000


def test_largest_files_respects_limit(tmp_path: Path) -> None:
    (tmp_path / "small.bin").write_bytes(b"x" * 500)
    (tmp_path / "large.bin").write_bytes(b"y" * 1000)

    result = largest_files(tmp_path, limit=1)

    assert len(result.entries) == 1
    assert result.entries[0].name == "large.bin"
    assert result.entries[0].size == 1000


def test_top_folders_returns_folder_sizes(tmp_path: Path) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"
    first.mkdir()
    second.mkdir()
    (first / "data.bin").write_bytes(b"x" * 100)
    (second / "data.bin").write_bytes(b"y" * 300)

    result = top_folders(tmp_path)

    sizes = {entry.name: entry.size for entry in result.entries}
    assert sizes["first"] == 100
    assert sizes["second"] == 300
