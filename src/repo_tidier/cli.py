from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from repo_tidier.scanner import PathError, calculate_statistics, scan_directory

app = typer.Typer(help="Repo tidier CLI")
console = Console()


@app.callback()
def callback():
    """Repo tidier - organize and clean up repositories."""
    pass


def format_size(size_bytes: int) -> str:
    """Format bytes into human-readable size."""
    size = float(size_bytes)  # Convert to float for division
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} PB"


@app.command()
def summary(
    path: str = typer.Argument(..., help="Path to the directory to scan"),
    exclude: list[str] = typer.Option(
        default=[], help="Additional patterns to exclude (e.g., .git, node_modules)"
    ),
    only_files: bool = typer.Option(
        False, "--files-only", help="Show only files, exclude directories"
    ),
    extensions: list[str] = typer.Option(
        default=[], help="Filter by file extensions (e.g., .py .js)"
    ),
    sort_by: str = typer.Option("size", help="Sort by 'size' or 'name'"),
    reverse: bool = typer.Option(True, help="Sort in reverse order (largest first for size)"),
    limit: int = typer.Option(None, help="Limit number of results shown"),
):
    """Generate a summary of the repository."""
    path_obj = Path(path)

    try:
        # Build exclude patterns (combine defaults with user-provided)
        exclude_patterns = set(exclude) if exclude else None

        # Scan directory with filters and sorting
        files = scan_directory(
            path_obj,
            exclude_patterns=exclude_patterns,
            only_files=only_files,
            extensions=extensions if extensions else None,
            sort_by=sort_by if sort_by else None,
            reverse=reverse,
        )
    except PathError as e:
        console.print(f"[bold red]Error:[/bold red] {e}", style="red")
        raise typer.Exit(code=1)
    except PermissionError as e:
        console.print(
            f"[bold red]Permission Error:[/bold red] Cannot access {path_obj}", style="red"
        )
        console.print(f"[dim]{e}[/dim]")
        raise typer.Exit(code=1)

    # Calculate statistics
    stats = calculate_statistics(files)

    # Limit results for display
    display_files = files[:limit] if limit else files

    # Display summary in a panel with statistics
    total_text = f"{len(files)} total" if limit and len(files) > limit else f"{len(files)}"
    stats_lines = [
        f"Found [bold green]{total_text}[/bold green] files in [cyan]{path_obj}[/cyan]",
        f"Total size: [bold yellow]{format_size(stats.total_size)}[/bold yellow]",
        (
            f"Files: [cyan]{stats.total_files}[/cyan] | "
            f"Avg size: [yellow]{format_size(int(stats.average_size))}[/yellow]"
        ),
    ]
    if stats.largest_file:
        largest_name = stats.largest_file.path.name
        largest_size = format_size(stats.largest_file.size)
        stats_lines.append(
            f"Largest: [cyan]{largest_name}[/cyan] ([yellow]{largest_size}[/yellow])"
        )
    summary_text = "\n".join(stats_lines)
    console.print(Panel(summary_text, title="Summary", border_style="green"))

    # Display file type breakdown if we have extensions
    if stats.files_by_extension:
        ext_lines = []
        # Sort by count descending, show top 5
        sorted_exts = sorted(stats.files_by_extension.items(), key=lambda x: x[1], reverse=True)[:5]
        for ext, count in sorted_exts:
            ext_lines.append(f"{ext}: [bold]{count}[/bold]")
        if len(stats.files_by_extension) > 5:
            ext_lines.append(f"... and {len(stats.files_by_extension) - 5} more")
        console.print(Panel("\n".join(ext_lines), title="File Types", border_style="blue"))

    # Display files in a table
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Path", style="cyan")
    table.add_column("Size", justify="right", style="yellow")

    for file in display_files:
        table.add_row(str(file.path), format_size(file.size))

    console.print(table)


@app.command()
def types(
    path: str = typer.Argument(..., help="Path to the directory to scan"),
    exclude: list[str] = typer.Option(
        default=[], help="Additional patterns to exclude (e.g., .git, node_modules)"
    ),
    top: int = typer.Option(None, "--top", help="Show only the top N file types"),
    summary_only: bool = typer.Option(
        False, "--summary", help="Show only the count of unique file types"
    ),
):
    """Show unique file extensions and their counts."""
    path_obj = Path(path)

    try:
        # Build exclude patterns (combine defaults with user-provided)
        exclude_patterns = set(exclude) if exclude else None

        # Scan directory with filters - always files only for types command
        files = scan_directory(
            path_obj,
            exclude_patterns=exclude_patterns,
            only_files=True,  # File types only make sense for files
            extensions=None,  # We want all extensions for types
            sort_by=None,  # No need to sort files for types command
            reverse=False,
        )
    except PathError as e:
        console.print(f"[bold red]Error:[/bold red] {e}", style="red")
        raise typer.Exit(code=1)
    except PermissionError as e:
        console.print(
            f"[bold red]Permission Error:[/bold red] Cannot access {path_obj}", style="red"
        )
        console.print(f"[dim]{e}[/dim]")
        raise typer.Exit(code=1)

    # Calculate statistics to get file types
    stats = calculate_statistics(files)

    if not stats.files_by_extension:
        console.print(f"[yellow]No file types found in {path_obj}[/yellow]")
        return

    # Sort by count descending
    sorted_exts = sorted(stats.files_by_extension.items(), key=lambda x: x[1], reverse=True)

    # Limit to top N if specified
    if top:
        sorted_exts = sorted_exts[:top]

    # Summary only mode
    if summary_only:
        total_types = len(stats.files_by_extension)
        console.print(
            Panel(
                f"[bold green]{total_types}[/bold green] unique file types",
                title="File Types Summary",
                border_style="blue",
            )
        )
        return

    # Display in a Rich table
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Extension", style="cyan", width=20)
    table.add_column("Count", justify="right", style="yellow")

    for ext, count in sorted_exts:
        # Format extension display
        ext_display = ext if ext else "(no extension)"
        # Pluralize "file" vs "files"
        file_word = "file" if count == 1 else "files"
        table.add_row(ext_display, f"{count} {file_word}")

    # Header with total count
    total_types = len(stats.files_by_extension)
    header_text = (
        f"Found [bold green]{total_types}[/bold green] file type"
        f"{'s' if total_types != 1 else ''} in [cyan]{path_obj}[/cyan]"
    )
    if top and top < total_types:
        header_text += f" (showing top [bold]{top}[/bold])"

    console.print(Panel(header_text, border_style="blue"))
    console.print(table)


def main():
    app()


if __name__ == "__main__":
    main()
