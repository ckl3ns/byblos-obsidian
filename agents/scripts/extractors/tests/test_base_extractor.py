"""Testes para BaseExtractor."""
import pytest
from pathlib import Path
from ..base_extractor import BaseExtractor, ExtractedEntry


class ConcreteExtractor(BaseExtractor):
    """Implementação concreta para testes."""
    
    def extract_entries(self):
        yield ExtractedEntry(title="Test", body="Body", source_sigla=self.sigla)
    
    def detect_entry_boundary(self, text):
        return [(0, len(text))]


class TestBaseExtractor:
    
    def test_clean_text_hyphen_break(self):
        ext = ConcreteExtractor(Path("."), "TEST")
        text = "theo-\nlogical"
        assert ext.clean_text(text) == "theological"
    
    def test_clean_text_page_numbers(self):
        ext = ConcreteExtractor(Path("."), "TEST")
        text = "Some text\n\n123\n\nMore text"
        cleaned = ext.clean_text(text)
        assert "123" not in cleaned
        assert "Some text" in cleaned
        assert "More text" in cleaned
    
    def test_clean_text_multiple_newlines(self):
        ext = ConcreteExtractor(Path("."), "TEST")
        text = "Line 1\n\n\n\n\nLine 2"
        cleaned = ext.clean_text(text)
        assert cleaned == "Line 1\n\nLine 2"
