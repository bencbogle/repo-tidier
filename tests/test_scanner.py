"""
Tests for the scanner module.

This demonstrates:
- Using pytest fixtures to create temporary test directories
- Golden path tests (happy path scenarios)
- Edge case tests (error conditions, empty dirs, etc.)
"""

from pathlib import Path

import pytest

from repo_tidier.scanner import (
    PathError,
    calculate_statistics,
    scan_directory,
    validate_path,
)


@pytest.fixture
def temp_dir(tmp_path):
    """
    Fixture that creates a temporary directory with test files.

    Fixtures are reusable test data/setup. This one creates:
    - A main directory
    - Some test files with different sizes
    - A subdirectory with more files
    - Common directories to exclude (.git, __pycache__)

    `tmp_path` is a built-in pytest fixture that gives us a temporary directory.
    """
    # Create test files
    (tmp_path / "file1.txt").write_text("content")
    (tmp_path / "file2.py").write_text("print('hello')")
    (tmp_path / "large_file.txt").write_text("x" * 1000)  # 1000 bytes

    # Create a subdirectory
    subdir = tmp_path / "subdir"
    subdir.mkdir()
    (subdir / "file3.js").write_text("console.log('test')")

    # Create directories that should be excluded
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "config").write_text("git config")
    (tmp_path / "__pycache__").mkdir()
    (tmp_path / "__pycache__" / "file.pyc").write_text("bytecode")

    return tmp_path


# ============ GOLDEN PATH TESTS ============
# These test the happy path - normal, expected usage


def test_scan_directory_basic(temp_dir):
    """Golden path: Scan a directory and get all files."""
    files = scan_directory(temp_dir)

    # Should find files but exclude .git and __pycache__
    assert len(files) > 0
    # Check that excluded directories aren't included
    paths = [str(f.path) for f in files]
    assert not any(".git" in p for p in paths)
    assert not any("__pycache__" in p for p in paths)


def test_scan_directory_only_files(temp_dir):
    """Golden path: Scan with --files-only flag."""
    files = scan_directory(temp_dir, only_files=True)

    # All results should be files, not directories
    assert all(f.path.is_file() for f in files)


def test_scan_directory_filter_extensions(temp_dir):
    """Golden path: Filter by file extension."""
    files = scan_directory(temp_dir, extensions=[".py"], only_files=True)

    # Should only return .py files (directories excluded with only_files=True)
    assert all(f.path.suffix == ".py" for f in files)
    assert len(files) == 1  # Only file2.py


def test_scan_directory_sort_by_size(temp_dir):
    """Golden path: Sort files by size."""
    files = scan_directory(temp_dir, sort_by="size", reverse=True)

    # Should be sorted largest first
    sizes = [f.size for f in files]
    assert sizes == sorted(sizes, reverse=True)


def test_calculate_statistics_basic(temp_dir):
    """Golden path: Calculate statistics from files."""
    files = scan_directory(temp_dir, only_files=True)
    stats = calculate_statistics(files)

    # Should have calculated stats
    assert stats.total_files > 0
    assert stats.total_size > 0
    assert stats.largest_file is not None
    assert stats.smallest_file is not None
    assert stats.average_size > 0


# ============ EDGE CASE TESTS ============
# These test error conditions, empty inputs, boundaries, etc.


def test_scan_directory_empty_directory(tmp_path):
    """Edge case: Scan an empty directory."""
    files = scan_directory(tmp_path)

    # Should return empty list, not crash
    assert files == []


def test_scan_directory_nonexistent_path():
    """Edge case: Try to scan a path that doesn't exist."""
    fake_path = Path("/nonexistent/path/12345")

    # Should raise PathError
    with pytest.raises(PathError, match="does not exist"):
        scan_directory(fake_path)


def test_scan_directory_file_not_directory(tmp_path):
    """Edge case: Try to scan a file instead of a directory."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("content")

    # Should raise PathError
    with pytest.raises(PathError, match="not a directory"):
        scan_directory(test_file)


def test_calculate_statistics_empty_list():
    """Edge case: Calculate stats from empty file list."""
    stats = calculate_statistics([])

    # Should return zero stats, not crash
    assert stats.total_files == 0
    assert stats.total_size == 0
    assert stats.largest_file is None
    assert stats.smallest_file is None
    assert stats.average_size == 0.0
    assert stats.files_by_extension == {}


def test_scan_directory_only_excluded_files(temp_dir):
    """Edge case: Directory only contains excluded files."""
    # Create a directory with only excluded patterns
    excluded_dir = temp_dir / "node_modules"
    excluded_dir.mkdir()
    (excluded_dir / "package.json").write_text("{}")

    files = scan_directory(temp_dir, exclude_patterns={".git", "__pycache__", "node_modules"})

    # node_modules should be excluded
    paths = [str(f.path) for f in files]
    assert not any("node_modules" in p for p in paths)


def test_validate_path_nonexistent():
    """Edge case: Validate a path that doesn't exist."""
    fake_path = Path("/fake/path/12345")

    with pytest.raises(PathError):
        validate_path(fake_path)


def test_validate_path_file_not_dir(tmp_path):
    """Edge case: Validate a file when expecting a directory."""
    test_file = tmp_path / "file.txt"
    test_file.write_text("content")

    with pytest.raises(PathError):
        validate_path(test_file)


def test_scan_directory_no_matching_extensions(temp_dir):
    """Edge case: Filter by extension that doesn't exist."""
    files = scan_directory(temp_dir, extensions=[".nonexistent"], only_files=True)

    # Should return empty list (no files match, directories excluded)
    assert files == []


def test_calculate_statistics_with_directories(temp_dir):
    """Edge case: Calculate stats including directories."""
    # Get all files including directories
    files = scan_directory(temp_dir, only_files=False)
    stats = calculate_statistics(files)

    # Statistics should only count actual files, not directories
    # So total_files should be less than total items scanned
    file_count = sum(1 for f in files if f.path.is_file())
    assert stats.total_files == file_count
