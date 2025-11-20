import typer
from repo_tidier.scanner import scan_directory, calculate_statistics, PathError
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

app = typer.Typer(help="Repo tidier CLI")
console = Console()

@app.callback()
def callback():
    """Repo tidier - organize and clean up repositories."""
    pass

def format_size(size_bytes: int) -> str:
    """Format bytes into human-readable size."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"

@app.command()
def summary(
    path: str = typer.Argument(..., help="Path to the directory to scan"),
    exclude: list[str] = typer.Option(default=[], help="Additional patterns to exclude (e.g., .git, node_modules)"),
    only_files: bool = typer.Option(False, "--files-only", help="Show only files, exclude directories"),
    extensions: list[str] = typer.Option(default=[], help="Filter by file extensions (e.g., .py .js)"),
    sort_by: str = typer.Option("size", help="Sort by 'size' or 'name'"),
    reverse: bool = typer.Option(True, help="Sort in reverse order (largest first for size)"),
    limit: int = typer.Option(None, help="Limit number of results shown")
):
    """Generate a summary of the repository."""
    path = Path(path)
    
    try:
        # Build exclude patterns (combine defaults with user-provided)
        exclude_patterns = set(exclude) if exclude else None
        
        # Scan directory with filters and sorting
        files = scan_directory(
        path,
        exclude_patterns=exclude_patterns,
        only_files=only_files,
        extensions=extensions if extensions else None,
            sort_by=sort_by if sort_by else None,
            reverse=reverse
        )
    except PathError as e:
        console.print(f"[bold red]Error:[/bold red] {e}", style="red")
        raise typer.Exit(code=1)
    except PermissionError as e:
        console.print(f"[bold red]Permission Error:[/bold red] Cannot access {path}", style="red")
        console.print(f"[dim]{e}[/dim]")
        raise typer.Exit(code=1)
    
    # Calculate statistics
    stats = calculate_statistics(files)
    
    # Limit results for display
    display_files = files[:limit] if limit else files
    
    # Display summary in a panel with statistics
    total_text = f"{len(files)} total" if limit and len(files) > limit else f"{len(files)}"
    stats_lines = [
        f"Found [bold green]{total_text}[/bold green] files in [cyan]{path}[/cyan]",
        f"Total size: [bold yellow]{format_size(stats.total_size)}[/bold yellow]",
        f"Files: [cyan]{stats.total_files}[/cyan] | Avg size: [yellow]{format_size(int(stats.average_size))}[/yellow]"
    ]
    if stats.largest_file:
        stats_lines.append(f"Largest: [cyan]{stats.largest_file.path.name}[/cyan] ([yellow]{format_size(stats.largest_file.size)}[/yellow])")
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

def main():
    app()

if __name__ == "__main__":
    main()
