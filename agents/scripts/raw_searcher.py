"""raw_searcher.py
Full-text search sobre obras de referência em raw/.
Retorna trechos com localização exata para citação com proveniência.

Uso básico:
    searcher = RawSearcher("raw")
    hits = searcher.search("δοῦλος prisoner Paul", siglas=["DPL2", "DLNT"])
    for h in hits:
        print(h.citation_tag)
        # → [Fonte: raw/dicionarios-enciclopedias/... | Obra: DPL2 | Nível: 3]
"""
import re
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

from distillation_manifest import build_raw_search_map


# Mapa sigla → (path relativo a raw/, nível de autoridade)
OBRA_MAP = build_raw_search_map("raw")

CONTEXT_LINES = 8   # linhas de contexto em torno do hit


@dataclass
class LoadedRawFile:
    obra_path: str
    file_name: str
    lines: list[str]


@dataclass
class SearchHit:
    sigla: str
    obra_path: str          # path relativo em raw/
    file_name: str
    line_number: int
    line_offset: int        # char offset dentro do arquivo
    matched_terms: list
    context: str            # trecho com contexto
    score: int              # número de termos encontrados
    nivel: int

    @property
    def citation_tag(self) -> str:
        return (
            f"[Fonte: raw/{self.obra_path}/{self.file_name} "
            f"| Obra: {self.sigla} | Nível: {self.nivel}]"
        )

    @property
    def obsidian_link(self) -> str:
        return f"[[raw/{self.obra_path}/{self.file_name}]]"


class RawSearcher:
    def __init__(self, raw_dir: str | Path):
        requested = Path(raw_dir)
        self.raw_root = self._normalize_raw_root(requested)
        self._index: dict[str, list[LoadedRawFile]] = {}

    def _normalize_raw_root(self, requested: Path) -> Path:
        """Aceita tanto raw/ quanto raw/dicionarios-enciclopedias/."""
        if requested.name == "dicionarios-enciclopedias":
            return requested.parent
        return requested

    def _entry(self, sigla: str) -> dict:
        if sigla not in OBRA_MAP:
            raise ValueError(f"Sigla '{sigla}' não cadastrada em OBRA_MAP.")
        return OBRA_MAP[sigla]

    def _resolve_candidates(self, sigla: str) -> list[Path]:
        entry = self._entry(sigla)
        target = self.raw_root / entry["path"]

        if target.is_file():
            return [target]
        if target.is_dir():
            return sorted(target.glob("*.txt"))

        raise FileNotFoundError(
            f"Nenhum arquivo encontrado para {sigla} em raw/{entry['path']}"
        )

    def _load(self, sigla: str) -> list[LoadedRawFile]:
        if sigla in self._index:
            return self._index[sigla]

        loaded: list[LoadedRawFile] = []
        for candidate in self._resolve_candidates(sigla):
            obra_path = str(candidate.parent.relative_to(self.raw_root)).replace("\\", "/")
            lines = candidate.read_text(encoding='utf-8', errors='replace').splitlines()
            loaded.append(LoadedRawFile(
                obra_path=obra_path,
                file_name=candidate.name,
                lines=lines,
            ))

        self._index[sigla] = loaded
        return loaded

    def search(
        self,
        query: str,
        siglas: Optional[list[str]] = None,
        max_hits: int = 10,
        min_score: int = 1,
    ) -> list[SearchHit]:
        """
        Busca `query` nas obras especificadas (ou em todas se siglas=None).
        Tokeniza a query, pontua hits por número de termos encontrados.
        """
        terms = [t.lower() for t in re.split(r'\s+', query.strip()) if len(t) > 2]
        targets = siglas if siglas else list(OBRA_MAP.keys())
        all_hits: list[SearchHit] = []

        for sigla in targets:
            try:
                raw_files = self._load(sigla)
            except (ValueError, FileNotFoundError):
                continue

            nivel = self._entry(sigla)["nivel"]

            for raw_file in raw_files:
                for i, line in enumerate(raw_file.lines):
                    line_lower = line.lower()
                    matched = [t for t in terms if t in line_lower]
                    if len(matched) < min_score:
                        continue

                    start = max(0, i - CONTEXT_LINES // 2)
                    end = min(len(raw_file.lines), i + CONTEXT_LINES // 2 + 1)
                    context = "\n".join(raw_file.lines[start:end])

                    all_hits.append(SearchHit(
                        sigla=sigla,
                        obra_path=raw_file.obra_path,
                        file_name=raw_file.file_name,
                        line_number=i + 1,
                        line_offset=sum(len(l) + 1 for l in raw_file.lines[:i]),
                        matched_terms=matched,
                        context=context,
                        score=len(matched),
                        nivel=nivel,
                    ))

        all_hits.sort(key=lambda h: (-h.score, h.file_name, h.line_number))
        return all_hits[:max_hits]

    def search_entry(
        self,
        entry_term: str,
        siglas: Optional[list[str]] = None,
        max_hits: int = 5,
    ) -> list[SearchHit]:
        """
        Busca um verbete específico (nome de artigo em dicionário).
        Procura linhas que parecem cabeçalhos de verbete (maiúsculas / padrão de entrada).
        """
        pattern = re.compile(
            rf'^\s*{re.escape(entry_term.upper())}[\s,.]',
            re.IGNORECASE | re.MULTILINE
        )
        targets = siglas if siglas else list(OBRA_MAP.keys())
        all_hits: list[SearchHit] = []

        for sigla in targets:
            try:
                raw_files = self._load(sigla)
            except Exception:
                continue

            nivel = self._entry(sigla)["nivel"]

            for raw_file in raw_files:
                full_text = "\n".join(raw_file.lines)
                for match in pattern.finditer(full_text):
                    line_num = full_text[:match.start()].count('\n') + 1
                    start = max(0, line_num - 2)
                    end = min(len(raw_file.lines), line_num + CONTEXT_LINES)
                    context = "\n".join(raw_file.lines[start:end])

                    all_hits.append(SearchHit(
                        sigla=sigla,
                        obra_path=raw_file.obra_path,
                        file_name=raw_file.file_name,
                        line_number=line_num,
                        line_offset=match.start(),
                        matched_terms=[entry_term],
                        context=context,
                        score=2,
                        nivel=nivel,
                    ))
                    if len(all_hits) >= max_hits:
                        return all_hits[:max_hits]

        return all_hits[:max_hits]

    def get_citation(self, sigla: str, line_number: int) -> str:
        """Gera tag de citação para uma sigla; line_number é mantido por compatibilidade."""
        del line_number
        if sigla not in OBRA_MAP:
            return f"[Fonte: raw/DESCONHECIDO/{sigla} | Obra: {sigla} | Nível: 5]"

        entry = self._entry(sigla)
        cited_path = entry["path"].replace("\\", "/")
        target = self.raw_root / entry["path"]
        if target.is_dir() and not cited_path.endswith("/"):
            cited_path += "/"

        return f"[Fonte: raw/{cited_path} | Obra: {sigla} | Nível: {entry['nivel']}]"
