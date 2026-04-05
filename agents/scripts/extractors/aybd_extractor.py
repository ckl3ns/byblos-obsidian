"""aybd_extractor.py
Extrator para Anchor Yale Bible Dictionary (AYBD).
"""
import re
from pathlib import Path
from typing import Iterator

from .base_extractor import BaseExtractor, ExtractedEntry


class AYBDExtractor(BaseExtractor):
    """Extrator para arquivos AYBD."""
    
    # Padrão: verbetes geralmente começam com título em CAPS
    # Ex: "AARON (PERSON) [Heb 'ahărōn]"
    RE_ENTRY_START = re.compile(
        r'^([A-Z][A-Z0-9\s,\'-]+?)(?:\s*\([^)]+\))?\s*(?:\[|$)',
        re.MULTILINE
    )
    
    def __init__(self, source_path: Path):
        super().__init__(source_path, sigla="AYBD")
    
    def detect_entry_boundary(self, text: str) -> list[tuple[int, int]]:
        """Detecta início e fim de verbetes AYBD."""
        matches = list(self.RE_ENTRY_START.finditer(text))
        boundaries = []
        for i, match in enumerate(matches):
            start = match.start()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            boundaries.append((start, end))
        return boundaries
    
    def extract_entries(self) -> Iterator[ExtractedEntry]:
        """Extrai verbetes do arquivo AYBD."""
        text = self.read_full()
        text = self.clean_text(text)
        
        boundaries = self.detect_entry_boundary(text)
        
        for start, end in boundaries:
            entry_text = text[start:end].strip()
            if not entry_text:
                continue
            
            # Extrai título (primeira linha ou até [)
            lines = entry_text.split('\n', 1)
            title_line = lines[0].strip()
            
            # Remove parênteses e colchetes do título
            title = re.sub(r'\s*\([^)]*\)\s*', ' ', title_line)
            title = re.sub(r'\s*\[[^\]]*\]\s*', ' ', title)
            title = ' '.join(title.split()).strip()
            
            body = lines[1].strip() if len(lines) > 1 else ""
            
            yield ExtractedEntry(
                title=title,
                body=body,
                source_sigla=self.sigla,
                source_path=str(self.source_path),
                raw_offset=start,
            )
