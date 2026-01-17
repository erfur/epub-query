"""Epub parsing functionality."""

from dataclasses import dataclass
from pathlib import Path

import ebooklib
from bs4 import BeautifulSoup
from ebooklib import epub


@dataclass
class Chapter:
    """Represents a chapter in an epub."""

    title: str
    content: str
    file_name: str


@dataclass
class EpubMetadata:
    """Metadata extracted from an epub file."""

    title: str | None
    author: str | None
    language: str | None
    identifier: str | None


class EpubParser:
    """Parser for epub files."""

    def __init__(self, epub_path: str | Path):
        self.path = Path(epub_path)
        if not self.path.exists():
            raise FileNotFoundError(f"Epub file not found: {self.path}")
        self._book: epub.EpubBook | None = None

    @property
    def book(self) -> epub.EpubBook:
        """Lazily load the epub book."""
        if self._book is None:
            self._book = epub.read_epub(str(self.path))
        return self._book

    def get_metadata(self) -> EpubMetadata:
        """Extract metadata from the epub."""
        title = self.book.get_metadata("DC", "title")
        author = self.book.get_metadata("DC", "creator")
        language = self.book.get_metadata("DC", "language")
        identifier = self.book.get_metadata("DC", "identifier")

        return EpubMetadata(
            title=title[0][0] if title else None,
            author=author[0][0] if author else None,
            language=language[0][0] if language else None,
            identifier=identifier[0][0] if identifier else None,
        )

    def get_chapters(self) -> list[Chapter]:
        """Extract all chapters from the epub."""
        chapters = []

        for item in self.book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
            content = item.get_content().decode("utf-8")
            soup = BeautifulSoup(content, "lxml")

            # Extract text content
            text = soup.get_text(separator="\n", strip=True)

            # Try to find chapter title
            title = ""
            for tag in ["h1", "h2", "h3", "title"]:
                heading = soup.find(tag)
                if heading:
                    title = heading.get_text(strip=True)
                    break

            if not title:
                title = item.get_name()

            chapters.append(
                Chapter(
                    title=title,
                    content=text,
                    file_name=item.get_name(),
                )
            )

        return chapters

    def get_full_text(self) -> str:
        """Get the full text content of the epub."""
        chapters = self.get_chapters()
        return "\n\n".join(chapter.content for chapter in chapters)
