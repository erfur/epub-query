# epub-query

A command-line tool for querying and searching epub files.

## Installation

```bash
pip install .
```

Or with uv:

```bash
uv pip install .
```

## Usage

```bash
# Display metadata and info about an epub file
epub-query info book.epub

# List all chapters
epub-query chapters book.epub

# Search for a pattern (case-insensitive by default)
epub-query search book.epub "search term"

# Search with regex
epub-query search book.epub "pattern.*here" --regex

# Show word count statistics
epub-query stats book.epub

# Extract full text to a file
epub-query extract book.epub output.txt

# Extract a specific chapter (by number or title)
epub-query chapter book.epub 1
epub-query chapter book.epub "Introduction" -o intro.txt
```

## Requirements

- Python 3.10+
