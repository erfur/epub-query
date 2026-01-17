"""Command-line interface for epub-query."""

import click

from epub_query.parser import EpubParser
from epub_query.query import EpubQuery


@click.group()
@click.version_option()
def main():
    """Query and search epub files."""
    pass


@main.command()
@click.argument("epub_file", type=click.Path(exists=True))
def info(epub_file: str):
    """Display metadata and info about an epub file."""
    parser = EpubParser(epub_file)
    meta = parser.get_metadata()
    chapters = parser.get_chapters()

    click.echo(f"Title:      {meta.title or 'Unknown'}")
    click.echo(f"Author:     {meta.author or 'Unknown'}")
    click.echo(f"Language:   {meta.language or 'Unknown'}")
    click.echo(f"Identifier: {meta.identifier or 'Unknown'}")
    click.echo(f"Chapters:   {len(chapters)}")


@main.command()
@click.argument("epub_file", type=click.Path(exists=True))
def chapters(epub_file: str):
    """List all chapters in an epub file."""
    query = EpubQuery(epub_file)
    for i, title in enumerate(query.list_chapters(), 1):
        click.echo(f"{i}. {title}")


@main.command()
@click.argument("epub_file", type=click.Path(exists=True))
@click.argument("pattern")
@click.option("-i", "--ignore-case/--case-sensitive", default=True, help="Case sensitivity")
@click.option("-r", "--regex", is_flag=True, help="Treat pattern as regex")
@click.option("-c", "--context", default=1, help="Lines of context around matches")
def search(epub_file: str, pattern: str, ignore_case: bool, regex: bool, context: int):
    """Search for a pattern in an epub file."""
    query = EpubQuery(epub_file)
    results = query.search(
        pattern,
        case_sensitive=not ignore_case,
        regex=regex,
        context_lines=context,
    )

    if not results:
        click.echo("No matches found.")
        return

    click.echo(f"Found {len(results)} match(es):\n")

    for result in results:
        click.echo(f"--- {result.chapter_title} (line {result.line_number}) ---")
        click.echo(result.context)
        click.echo()


@main.command()
@click.argument("epub_file", type=click.Path(exists=True))
def stats(epub_file: str):
    """Show word count statistics for an epub file."""
    query = EpubQuery(epub_file)
    counts = query.word_count()

    click.echo(f"Total words: {counts['total']:,}")
    click.echo("\nBy chapter:")
    for title, count in counts["by_chapter"].items():
        click.echo(f"  {title}: {count:,}")


@main.command()
@click.argument("epub_file", type=click.Path(exists=True))
@click.argument("output_file", type=click.Path())
def extract(epub_file: str, output_file: str):
    """Extract full text content to a file."""
    parser = EpubParser(epub_file)
    text = parser.get_full_text()

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(text)

    click.echo(f"Extracted text to {output_file}")


@main.command()
@click.argument("epub_file", type=click.Path(exists=True))
@click.argument("chapter")
@click.option("-o", "--output", type=click.Path(), help="Output file (prints to stdout if not set)")
def chapter(epub_file: str, chapter: str, output: str | None):
    """Extract a specific chapter by number or title.

    CHAPTER can be a number (1-based index) or a title substring.
    """
    query = EpubQuery(epub_file)
    chapters = query.chapters

    content = None
    chapter_title = None

    # Try as number first
    if chapter.isdigit():
        idx = int(chapter) - 1
        if 0 <= idx < len(chapters):
            content = chapters[idx].content
            chapter_title = chapters[idx].title

    # Try as title match
    if content is None:
        for ch in chapters:
            if chapter.lower() in ch.title.lower():
                content = ch.content
                chapter_title = ch.title
                break

    if content is None:
        click.echo(f"Chapter not found: {chapter}", err=True)
        click.echo("Use 'epub-query chapters <file>' to list available chapters.", err=True)
        raise SystemExit(1)

    if output:
        with open(output, "w", encoding="utf-8") as f:
            f.write(content)
        click.echo(f"Extracted '{chapter_title}' to {output}")
    else:
        click.echo(content)


if __name__ == "__main__":
    main()
