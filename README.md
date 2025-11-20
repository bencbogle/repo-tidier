# repo-tidier

A command-line tool to analyse and summarise repository file structures with beautiful, formatted output.

## Features

- 📊 **Rich statistics**: Total size, file counts, largest/smallest files, average size
- 🔍 **Smart filtering**: Filter by file extensions, exclude common directories (`.git`, `.venv`, `__pycache__`, etc.)
- 📈 **Sorting & limiting**: Sort by size or name, limit results
- 📋 **File type analysis**: Discover all file types in your repository with counts
- 🎨 **Beautiful output**: Rich-formatted tables and panels with colours
- ✅ **Error handling**: Clear error messages for invalid paths

## Quickstart

Get started in seconds:

```bash
# Install dependencies
uv sync

# Get a quick summary of your repo
uv run repo-tidier summary .
```

**More examples**:
```bash
# See what file types are in your repo
uv run repo-tidier types .

# Find the top 5 most common file types
uv run repo-tidier types . --top 5

# Discover what's taking up space
uv run repo-tidier summary . --sort-by size --limit 5

# Check only Python files
uv run repo-tidier summary . --extensions .py
```

## Installation

```bash
# Clone the repository
git clone https://github.com/bencbogle/repo-tidier.git
cd repo-tidier

# Install dependencies
uv sync

# Run the tool
uv run repo-tidier summary <path>
```

## Usage

### Basic summary

```bash
uv run repo-tidier summary .
```

### Filter by file extension

```bash
uv run repo-tidier summary src --extensions .py .js
```

### Show only files (exclude directories)

```bash
uv run repo-tidier summary . --files-only
```

### Sort and limit results

```bash
uv run repo-tidier summary . --sort-by size --limit 10
```

### Exclude additional patterns

```bash
uv run repo-tidier summary . --exclude node_modules --exclude dist
```

### File types analysis

Show all unique file extensions and their counts:

```bash
uv run repo-tidier types .
```

Show only the top 5 file types:

```bash
uv run repo-tidier types . --top 5
```

Get a quick count of unique file types:

```bash
uv run repo-tidier types . --summary
```

## Commands

### `summary`

Generate a comprehensive summary of the repository structure.

**Options:**
- `--files-only`: Show only files, exclude directories
- `--extensions`: Filter by file extensions (e.g., `.py .js`)
- `--exclude`: Additional patterns to exclude
- `--sort-by`: Sort by `size` or `name` (default: `size`)
- `--reverse` / `--no-reverse`: Sort order (default: reverse)
- `--limit`: Limit number of results shown

### `types`

Show unique file extensions and their counts in the repository.

**Options:**
- `--top`: Show only the top N file types
- `--summary`: Show only the count of unique file types
- `--exclude`: Additional patterns to exclude (e.g., `.git`, `node_modules`)

## Example Output

```
╭────────────────────────────────── Summary ───────────────────────────────────╮
│ Found 18 files in .                                                         │
│ Total size: 18.4 KB                                                         │
│ Files: 15 | Avg size: 1.2 KB                                                 │
│ Largest: uv.lock (9.8 KB)                                                    │
╰──────────────────────────────────────────────────────────────────────────────╯
╭───────────────────────────────── File Types ─────────────────────────────────╮
│ .txt: 5                                                                      │
│ .py: 4                                                                       │
│ (no extension): 3                                                            │
╰──────────────────────────────────────────────────────────────────────────────╯
```

## Requirements

- Python 3.13+
- [uv](https://github.com/astral-sh/uv) for package management

## Development

This project uses:

- **[ruff](https://github.com/astral-sh/ruff)** for linting and code formatting
- **[mypy](https://mypy.readthedocs.io/)** for static type checking
- **[pytest](https://pytest.org/)** for testing

### Running checks

```bash
# Run linting
uv run ruff check src/

# Run type checking
uv run mypy src/

# Run tests
uv run pytest tests/
```

Pre-commit hooks are configured to automatically run `ruff` and `ruff-format` before each commit.

