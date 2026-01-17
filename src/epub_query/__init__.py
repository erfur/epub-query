"""Epub Query - A tool for querying and searching epub files."""

__version__ = "0.1.0"

from epub_query.parser import EpubParser
from epub_query.query import EpubQuery

__all__ = ["EpubParser", "EpubQuery"]
