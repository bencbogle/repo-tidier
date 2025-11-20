# repo-tidier

A command-line tool to analyse and summarise repository file structures with beautiful, formatted output.

## Features

- 📊 **Rich statistics**: Total size, file counts, largest/smallest files, average size
- 🔍 **Smart filtering**: Filter by file extensions, exclude common directories (`.git`, `.venv`, `__pycache__`, etc.)
- 📈 **Sorting & limiting**: Sort by size or name, limit results
- 🎨 **Beautiful output**: Rich-formatted tables and panels with colours
- ✅ **Error handling**: Clear error messages for invalid paths

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

## Options

- `--files-only`: Show only files, exclude directories
- `--extensions`: Filter by file extensions (e.g., `.py .js`)
- `--exclude`: Additional patterns to exclude
- `--sort-by`: Sort by `size` or `name` (default: `size`)
- `--reverse` / `--no-reverse`: Sort order (default: reverse)
- `--limit`: Limit number of results shown

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

