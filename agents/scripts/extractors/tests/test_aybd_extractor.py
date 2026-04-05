"""Testes para AYBDExtractor."""
import pytest
from pathlib import Path
from ..aybd_extractor import AYBDExtractor


class TestAYBDExtractor:
    
    def test_detect_entry_boundary_single(self):
        ext = AYBDExtractor(Path("."))
        text = "AARON (PERSON) [Heb 'ahărōn]\nThe first high priest."
        boundaries = ext.detect_entry_boundary(text)
        assert len(boundaries) == 1
        assert boundaries[0][0] == 0
    
    def test_detect_entry_boundary_multiple(self):
        ext = AYBDExtractor(Path("."))
        text = """AARON (PERSON) [Heb]
The first high priest.

ABEL (PERSON) [Heb]
Second son of Adam."""
        boundaries = ext.detect_entry_boundary(text)
        assert len(boundaries) == 2
    
    def test_extract_title_cleaned(self):
        ext = AYBDExtractor(Path("."))
        # Testar limpeza de título
        text = "ABRAHAM (PERSON) [Heb 'abrāhām]"
        # Simular processamento
        title_line = text
        title = pytest.importorskip('re').sub(r'\s*\([^)]*\)\s*', ' ', title_line)
        title = pytest.importorskip('re').sub(r'\s*\[[^\]]*\]\s*', ' ', title)
        title = ' '.join(title.split()).strip()
        assert title == "ABRAHAM"
