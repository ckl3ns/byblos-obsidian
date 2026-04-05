"""base_extractor.py
Classe abstrata e utilitários para extração de dicionários em raw/.
"""
import re
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Iterator, Optional
from dataclasses import dataclass


@dataclass
class ExtractedEntry:
    """Verbete extraído de uma fonte."""
    title: str                    # Título do verbete (em inglês)
    body: str                     # Corpo do verbete (limpo)
    author: Optional[str] = None  # Autor do verbete
    bibliography: Optional[str] = None  # Bibliografia
    source_sigla: str = ""        # Sigla da obra (AYBD, EDT, etc.)
    source_path: str = ""         # Path do arquivo fonte
    raw_offset: int = 0           # Offset no arquivo original


class BaseExtractor(ABC):
    """Classe base para extratores de dicionários."""
    
    # Regex para limpeza
    RE_HYPHEN_BREAK = re.compile(r'(\w)-\n(\w)')  # theo-\nlogical -> theological
    RE_PAGE_NUMBER = re.compile(r'^\s*\d+\s*$', re.MULTILINE)  # Números de página isolados
    RE_MULTIPLE_NEWLINES = re.compile(r'\n{3,}')  # Múltiplas linhas vazias
    RE_TRAILING_SPACES = re.compile(r'[ \t]+$', re.MULTILINE)
    
    def __init__(self, source_path: Path, sigla: str, chunk_size: int = 1024 * 1024):
        self.source_path = source_path
        self.sigla = sigla
        self.chunk_size = chunk_size  # 1MB por chunk
    
    def read_chunks(self) -> Iterator[str]:
        """Lê arquivo em chunks para economizar memória."""
        with open(self.source_path, 'r', encoding='utf-8', errors='replace') as f:
            while True:
                chunk = f.read(self.chunk_size)
                if not chunk:
                    break
                yield chunk
    
    def read_full(self) -> str:
        """Lê arquivo completo (cuidado com arquivos grandes)."""
        return self.source_path.read_text(encoding='utf-8', errors='replace')
    
    def clean_text(self, text: str) -> str:
        """Aplica limpezas básicas ao texto."""
        # Reconstrói palavras quebradas por hífen
        text = self.RE_HYPHEN_BREAK.sub(r'\1\2', text)
        # Remove números de página isolados
        text = self.RE_PAGE_NUMBER.sub('', text)
        # Normaliza múltiplas linhas vazias
        text = self.RE_MULTIPLE_NEWLINES.sub('\n\n', text)
        # Remove espaços em branco no final das linhas
        text = self.RE_TRAILING_SPACES.sub('', text)
        return text.strip()
    
    @abstractmethod
    def extract_entries(self) -> Iterator[ExtractedEntry]:
        """Extrai verbetes do arquivo. Implementar em subclasses."""
        pass
    
    @abstractmethod
    def detect_entry_boundary(self, text: str) -> list[tuple[int, int]]:
        """Detecta início e fim de verbetes no texto. Implementar em subclasses."""
        pass
