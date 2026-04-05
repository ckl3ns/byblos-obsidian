"""Pipeline de extração de dicionários teológicos."""

from .base_extractor import BaseExtractor, ExtractedEntry
from .aybd_extractor import AYBDExtractor

__all__ = ['BaseExtractor', 'ExtractedEntry', 'AYBDExtractor']
