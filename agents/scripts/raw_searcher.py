"""raw_searcher.py
Full-text search sobre obras de referência em raw/.
Retorna trechos com localização exata para citação com proveniência.

Uso básico:
    searcher = RawSearcher("vault/raw")
    hits = searcher.search("δοῦλος prisoner Paul", siglas=["DPL2", "DLNT"])
    for h in hits:
        print(h.citation_tag)
        # → [Fonte: raw/IVP-Black/DPL2.txt | Obra: DPL2 | Nível: 3]
"""
import re
import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional


# Mapa sigla → (path relativo, nível de autoridade)
OBRA_MAP = {
    "AYBD":   ("AYBD",        3),
    "DJG2":   ("IVP-Black",   3),
    "DPL2":   ("IVP-Black",   3),
    "DLNT":   ("IVP-Black",   3),
    "DNT-B":  ("IVP-Black",   3),
    "DOT-P":  ("IVP-Black",   3),
    "DOT-Pr": ("IVP-Black",   3),
    "DOT-W":  ("IVP-Black",   3),
    "NIDB":   ("NIDB",        3),
    "DDD":    ("especiais",   3),
    "EDT":    ("teologicos",  4),
    "EAC":    ("EAC",         3),
    "DTIB":   ("especiais",   4),
    "DBI-R":  ("especiais",   4),
}

CONTEXT_LINES = 8   # linhas de contexto em torno do hit


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
        self.raw_dir = Path(raw_dir)
        self._index: dict[str, list[str]] = {}   # sigla → linhas do arquivo

    def _load(self, sigla: str) -> list[str]:
        if sigla in self._index:
            return self._index[sigla]

        if sigla not in OBRA_MAP:
            raise ValueError(f"Sigla '{sigla}' não cadastrada em OBRA_MAP.")

        folder, _ = OBRA_MAP[sigla]
        candidates = list((self.raw_dir / folder).glob(f"*{sigla}*"))
        if not candidates:
            candidates = list((self.raw_dir / folder).glob("*.txt"))
        if not candidates:
            raise FileNotFoundError(
                f"Nenhum arquivo encontrado para {sigla} em raw/{folder}/"
            )

        # Carrega o primeiro candidato (em produção, indexar todos)
        lines = candidates[0].read_text(encoding='utf-8', errors='replace').splitlines()
        self._index[sigla] = lines
        return lines

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
                lines = self._load(sigla)
            except (ValueError, FileNotFoundError) as e:
                continue

            folder, nivel = OBRA_MAP[sigla]
            fname = Path(self._index.get(f"_path_{sigla}", sigla + ".txt")).name

            for i, line in enumerate(lines):
                line_lower = line.lower()
                matched = [t for t in terms if t in line_lower]
                if len(matched) < min_score:
                    continue

                # contexto: N linhas antes e depois
                start = max(0, i - CONTEXT_LINES // 2)
                end   = min(len(lines), i + CONTEXT_LINES // 2 + 1)
                context = "\n".join(lines[start:end])

                all_hits.append(SearchHit(
                    sigla=sigla,
                    obra_path=folder,
                    file_name=fname,
                    line_number=i + 1,
                    line_offset=sum(len(l)+1 for l in lines[:i]),
                    matched_terms=matched,
                    context=context,
                    score=len(matched),
                    nivel=nivel,
                ))

        # Ordenar por score desc, depois por linha asc
        all_hits.sort(key=lambda h: (-h.score, h.line_number))
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
        all_hits = []

        for sigla in targets:
            try:
                lines = self._load(sigla)
            except Exception:
                continue

            folder, nivel = OBRA_MAP[sigla]
            full_text = "\n".join(lines)

            for m in pattern.finditer(full_text):
                line_num = full_text[:m.start()].count('\n') + 1
                start = max(0, line_num - 2)
                end   = min(len(lines), line_num + CONTEXT_LINES)
                context = "\n".join(lines[start:end])
                fname = sigla + ".txt"

                all_hits.append(SearchHit(
                    sigla=sigla,
                    obra_path=folder,
                    file_name=fname,
                    line_number=line_num,
                    line_offset=m.start(),
                    matched_terms=[entry_term],
                    context=context,
                    score=2,   # verbetes têm score fixo maior
                    nivel=nivel,
                ))
                if len(all_hits) >= max_hits:
                    break

        return all_hits[:max_hits]

    def get_citation(self, sigla: str, line_number: int) -> str:
        """Gera tag de citação para uma linha específica."""
        if sigla not in OBRA_MAP:
            return f"[Fonte: raw/DESCONHECIDO/{sigla} | Obra: {sigla} | Nível: 5]"
        folder, nivel = OBRA_MAP[sigla]
        return f"[Fonte: raw/{folder}/{sigla}.txt | Obra: {sigla} | Nível: {nivel}]"
