from collections import Counter
from dataclasses import dataclass
from pathlib import Path


@dataclass
class FileStat:
    path: Path
    size: int


@dataclass
class Statistics:
    total_files: int
    total_size: int
    largest_file: FileStat | None
    smallest_file: FileStat | None
    average_size: float
    files_by_extension: dict[str, int]


# Common directories/files to exclude by default
DEFAULT_EXCLUDES = {".git", ".venv", "__pycache__", "node_modules", ".pytest_cache", ".mypy_cache"}


class PathError(Exception):
    """Custom exception for path-related errors."""

    pass


def validate_path(path: Path) -> None:
    """
    Validate that a path exists and is a directory.

    Raises:
        PathError: If path doesn't exist or isn't a directory
    """
    if not path.exists():
        raise PathError(f"Path does not exist: {path}")
    if not path.is_dir():
        raise PathError(f"Path is not a directory: {path}")


def should_exclude(path: Path, exclude_patterns: set[str]) -> bool:
    """Check if a path should be excluded based on patterns."""
    # Check if any part of the path matches an exclude pattern
    parts = path.parts
    return any(part in exclude_patterns for part in parts)


def scan_directory(
    path: Path,
    exclude_patterns: set[str] | None = None,
    only_files: bool = False,
    extensions: list[str] | None = None,
    sort_by: str | None = None,
    reverse: bool = True,
) -> list[FileStat]:
    """
    Scan a directory and return a list of FileStat objects.

    Args:
        path: Directory to scan
        exclude_patterns: Set of directory/file names to exclude (defaults to common ones)
        only_files: If True, exclude directories
        extensions: List of file extensions to include (e.g., ['.py', '.js'])
        sort_by: Sort by 'size' or 'name' (None = no sorting)
        reverse: If True, sort descending (largest first for size, Z-A for name)

    Raises:
        PathError: If path doesn't exist or isn't a directory
        PermissionError: If we don't have permission to access the directory
    """
    validate_path(path)

    if exclude_patterns is None:
        exclude_patterns = DEFAULT_EXCLUDES

    files = []
    for item_path in path.glob("**/*"):
        # Skip if matches exclude pattern
        if should_exclude(item_path, exclude_patterns):
            continue

        # Skip directories if only_files is True
        if only_files and item_path.is_dir():
            continue

        # Filter by extension if specified
        if extensions and item_path.is_file():
            if item_path.suffix.lower() not in [ext.lower() for ext in extensions]:
                continue

        try:
            files.append(FileStat(path=item_path, size=item_path.stat().st_size))
        except PermissionError:
            # Skip files we don't have permission to access
            continue
        except OSError:
            # Skip files with other OS errors (e.g., broken symlinks)
            continue

    # Sort if requested
    if sort_by == "size":
        files.sort(key=lambda f: f.size, reverse=reverse)
    elif sort_by == "name":
        files.sort(key=lambda f: str(f.path).lower(), reverse=reverse)

    return files


def calculate_statistics(files: list[FileStat]) -> Statistics:
    """Calculate statistics from a list of FileStat objects."""
    if not files:
        return Statistics(
            total_files=0,
            total_size=0,
            largest_file=None,
            smallest_file=None,
            average_size=0.0,
            files_by_extension={},
        )

    # Filter to only files (exclude directories)
    file_stats = [f for f in files if f.path.is_file()]

    total_size = sum(f.size for f in file_stats)
    total_files = len(file_stats)

    # Find largest and smallest files
    largest_file = max(file_stats, key=lambda f: f.size) if file_stats else None
    smallest_file = min(file_stats, key=lambda f: f.size) if file_stats else None

    # Calculate average
    average_size = total_size / total_files if total_files > 0 else 0.0

    # Count files by extension
    extensions = Counter(f.path.suffix.lower() for f in file_stats if f.path.suffix)
    # Also count files with no extension
    no_ext_count = sum(1 for f in file_stats if not f.path.suffix)
    if no_ext_count > 0:
        extensions["(no extension)"] = no_ext_count

    return Statistics(
        total_files=total_files,
        total_size=total_size,
        largest_file=largest_file,
        smallest_file=smallest_file,
        average_size=average_size,
        files_by_extension=dict(extensions),
    )
