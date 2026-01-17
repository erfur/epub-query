"""Query functionality for epub files."""

import re
from dataclasses import dataclass
from pathlib import Path

from epub_query.parser import Chapter, EpubParser


@dataclass
class SearchResult:
    """A search result with context."""

    chapter_title: str
    file_name: str
    match: str
    context: str
    line_number: int


class EpubQuery:
    """Query interface for epub files."""

    def __init__(self, epub_path: str | Path):
        self.parser = EpubParser(epub_path)
        self._chapters: list[Chapter] | None = None

    @property
    def chapters(self) -> list[Chapter]:
        """Lazily load chapters."""
        if self._chapters is None:
            self._chapters = self.parser.get_chapters()
        return self._chapters

    def search(
        self,
        pattern: str,
        *,
        case_sensitive: bool = False,
        context_lines: int = 1,
        regex: bool = False,
    ) -> list[SearchResult]:
        """Search for a pattern across all chapters.

        Args:
            pattern: The search pattern (string or regex)
            case_sensitive: Whether the search is case-sensitive
            context_lines: Number of lines of context around matches
            regex: Whether to treat pattern as a regular expression

        Returns:
            List of SearchResult objects
        """
        results = []
        flags = 0 if case_sensitive else re.IGNORECASE

        if not regex:
            pattern = re.escape(pattern)

        compiled = re.compile(pattern, flags)

        for chapter in self.chapters:
            lines = chapter.content.split("\n")

            for i, line in enumerate(lines):
                matches = compiled.findall(line)
                if matches:
                    # Build context
                    start = max(0, i - context_lines)
                    end = min(len(lines), i + context_lines + 1)
                    context = "\n".join(lines[start:end])

                    for match in matches:
                        results.append(
                            SearchResult(
                                chapter_title=chapter.title,
                                file_name=chapter.file_name,
                                match=match if isinstance(match, str) else match[0],
                                context=context,
                                line_number=i + 1,
                            )
                        )

        return results

    def list_chapters(self) -> list[str]:
        """List all chapter titles."""
        return [chapter.title for chapter in self.chapters]

    def get_chapter_content(self, title: str) -> str | None:
        """Get the content of a specific chapter by title."""
        for chapter in self.chapters:
            if chapter.title == title:
                return chapter.content
        return None

    def word_count(self) -> dict[str, int]:
        """Get word count statistics."""
        total = 0
        by_chapter = {}

        for chapter in self.chapters:
            words = len(chapter.content.split())
            by_chapter[chapter.title] = words
            total += words

        return {"total": total, "by_chapter": by_chapter}
