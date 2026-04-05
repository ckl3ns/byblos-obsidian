"""ntsk_parser.py — Extrator estruturado do bloco NTSK (stateful + carryover).
Extrai: referências canônicas, símbolos semânticos, Strong numbers, notas inline.
Suporta carryover (e.g. "Mt 1:1. 2:3. 5." -> Mt 1:1, Mt 1:2, Mt 1:5).
Normaliza IDs para o padrão frontmatter: "Mt 1.1" (espaço, ponto).
"""
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

_ROOT_DIR = Path(__file__).resolve().parents[2]
_NTSK_DOCS_DIR = _ROOT_DIR / "docs" / "ntsk"


def _normalize_book_key(book: str) -> str:
    return re.sub(r"\s+", " ", book).strip().rstrip(".")


def _load_book_map() -> dict[str, str]:
    """Carrega aliases de livros com saída padronizada na sigla Logos."""
    bible_books = json.loads(
        (_NTSK_DOCS_DIR / "bible_books.json").read_text(encoding="utf-8")
    )
    ntsk_to_sigla = json.loads(
        (_NTSK_DOCS_DIR / "ntsk_2_sigla.json").read_text(encoding="utf-8")
    )

    alias_map: dict[str, str] = {}
    abbrev_owners: dict[str, set[str]] = {}

    for item in bible_books.values():
        logos = item["logos"]
        for alias in item.get("abreviaturas", []):
            key = _normalize_book_key(alias)
            if key:
                abbrev_owners.setdefault(key, set()).add(logos)

    # Prioridade 1: mapa autoritativo do NTSK -> Logos
    for raw_book, canonical in ntsk_to_sigla.items():
        alias_map[_normalize_book_key(raw_book)] = canonical

    # Prioridade 2: sigla TSK e sigla Logos explícitas
    for item in bible_books.values():
        logos = item["logos"]
        for explicit_alias in (item["tsk"], item["logos"]):
            key = _normalize_book_key(explicit_alias)
            alias_map.setdefault(key, logos)

    # Prioridade 3: abreviações extras apenas quando forem inequívocas
    for item in bible_books.values():
        logos = item["logos"]
        for alias in item.get("abreviaturas", []):
            key = _normalize_book_key(alias)
            if not key or key in alias_map:
                continue
            if len(abbrev_owners.get(key, set())) == 1:
                alias_map[key] = logos

    return alias_map


BOOK_MAP: dict[str, str] = _load_book_map()
_CANONICAL_BOOKS = sorted(set(BOOK_MAP.values()), key=lambda value: (-len(value), value))
_CANONICAL_BOOK_ALT = "|".join(re.escape(book) for book in _CANONICAL_BOOKS)
_INPUT_BOOKS = sorted(BOOK_MAP, key=lambda value: (-len(value), value))
_INPUT_BOOK_ALT = "|".join(re.escape(book) for book in _INPUT_BOOKS)

# --- Símbolos NTSK -> nome canônico e tipo de aresta ---
NTSK_SYMBOLS: dict[str, str] = {
    "*":    "especially_clear",
    "+":    "full_collection",
    "=":    "type_antitype",
    "\u25d0": "contrast",
    "\u2a72": "type_antitype_scriptural",
    "\u25b6": "ot_quote_in_nt",
    "\u2721": "fulfills_prophecy",
    "\u2225": "parallel_passage",
    "\u2021": "false_doctrine_proof",
    "\u2713": "critically_clear",
}

_SYMBOL_CHARS = "*+\u25d0=\u2a72\u25b6\u2721\u2225\u2021\u2713"

_BOOK_ALIAS_IN_REF = re.compile(
    rf"(?<![\w])(?P<book>{_INPUT_BOOK_ALT})(?=\s*(?:[{re.escape(_SYMBOL_CHARS)}]+\s*)*\d+[:.])",
    re.UNICODE,
)


def _canonicalize_reference_books(text: str) -> str:
    """Padroniza as siglas do texto bruto para a forma canônica do projeto."""

    def repl(match: re.Match[str]) -> str:
        raw_book = _normalize_book_key(match.group("book"))
        return BOOK_MAP.get(raw_book, match.group("book"))

    return _BOOK_ALIAS_IN_REF.sub(repl, text)

# --- Regex compiladas ---
# Estrutura: [pre-syms] livro [mid-syms] cap [sep] vers_raw [post-syms]
# Onde post-syms é todo o texto após os dígitos do versículo.
# Vers: \d+(-\d+)* para ranges (23-38), decimal (?:\.(?=\d)) se seguido de dígito
# O lookahead (?=\d) só captura '.' se seguido imediatamente por dígito.
_VERS_PAT = r'(\d+(?:-\d+)*(?:\.(?=\d))?)'

_REF_WITH_BOOK = re.compile(
    r'([*+\u25d0=\u2a72\u25b6\u2721\u2225\u2021\u2713]*)'
    rf'({_CANONICAL_BOOK_ALT})'
    r'\s*([*+\u25d0=\u2a72\u25b6\u2721\u2225\u2021\u2713]*)\s*'
    r'(\d+)[:\.]'
    r'\s*([*+\u25d0=\u2a72\u25b6\u2721\u2225\u2021\u2713]*)'
    + _VERS_PAT +
    r'(.*)',
    re.UNICODE | re.DOTALL
)

_REF_WITH_BOOK_LETTER = _REF_WITH_BOOK

_REF_NO_BOOK = re.compile(
    r'([*+\u25d0=\u2a72\u25b6\u2721\u2225\u2021\u2713]*)'
    r'\s*'
    r'(\d+)[:\.]'
    r'\s*([*+\u25d0=\u2a72\u25b6\u2721\u2225\u2021\u2713]*)'
    + _VERS_PAT +
    r'(.*)',
    re.UNICODE | re.DOTALL
)

_STRONG_H = re.compile(r'\u2758S#(\d+h)')
_STRONG_G = re.compile(r'\u2723S#(\d+g)')
_INLINE_NOTE = re.compile(
    r'i\.e\.\s+[^.]+|Heb\.\s+[^.]+|or,\s+[^.]+|\([^)]+\)'
)
_VERSE_QUALIFIER = re.compile(r'(?<=\d)(mg|n|g|h|[abc])$', re.IGNORECASE)
_BOOK_CHANGE_START = re.compile(
    rf'^\.\s*({_CANONICAL_BOOK_ALT})(?=\s+\d+[:.])',
    re.UNICODE,
)
_BOOK_CHANGE_AFTER_DOT = re.compile(
    rf'\.\s+({_CANONICAL_BOOK_ALT})(?=\s+\d+[:.])',
    re.UNICODE,
)


@dataclass
class NTSKRef:
    raw: str
    book_abbr: str
    book_vault: Optional[str]
    chapter: str
    verses: list
    symbols: list
    symbol_names: list

    def target_id(self) -> str:
        v = self.verses[0] if self.verses else "?"
        return f"{self.book_vault} {self.chapter}.{v}"


class NTSKParser:
    """Parser stateful com suporte a carryover de livro/capítulo."""

    def __init__(self, ntsk_raw: str, source_ref: str = ""):
        self.ntsk_raw = _canonicalize_reference_books(ntsk_raw)
        self.source_ref = source_ref
        self._curr_book_ntsk: Optional[str] = None
        self._curr_book_vault: Optional[str] = None
        self._curr_chapter: Optional[str] = None
        self._carryover_cap: Optional[str] = None  # capítulo em carryover (não muda durante expansão)
        self.refs: list[NTSKRef] = []
        self.strong_h: list = _STRONG_H.findall(ntsk_raw)
        self.strong_g: list = [g for g in _STRONG_G.findall(ntsk_raw) if g]
        self.inline_notes: list = _INLINE_NOTE.findall(ntsk_raw)

    def _resolve_book(self, raw_book: str) -> Optional[str]:
        if vault := BOOK_MAP.get(_normalize_book_key(raw_book)):
            return vault
        return None

    def _extract_symbols(self, text: str) -> tuple[str, str]:
        """Extrai símbolos NTSK de uma string e devolve (símbolos_como_string, resto)."""
        sym_chars = [c for c in NTSK_SYMBOLS if c in text]
        syms_str = "".join(sym_chars)
        remaining = "".join(c for c in text if c not in NTSK_SYMBOLS).strip()
        return syms_str, remaining

    def _expand_verses(self, verses_raw: str) -> list[str]:
        """Expande '23-38', '23-38.', '1, 2, 3', '2:3' (carryover), '1. 2. 3' em lista de versículos.

        carryover ':' significa "dois versículos separados" (ex: '2:3' -> ['2', '3']).
        '. ' é separator de refs encadeadas (ex: '1. 2:3. 5' -> ['1', '2', '3', '5']).
        vírgula separa versículos na mesma ref (ex: '1, 2, 3' -> ['1', '2', '3']).
        """
        verses: list[str] = []

        def append_token(token: str) -> None:
            cleaned = token.strip().rstrip(').,;')
            cleaned = _VERSE_QUALIFIER.sub('', cleaned).strip()
            if not cleaned:
                return

            cap_range_m = re.match(r'^(\d+)\.(\d+)-(\d+)$', cleaned)
            if cap_range_m:
                try:
                    start_v = int(cap_range_m.group(2))
                    end_v = int(cap_range_m.group(3))
                    verses.extend(str(v) for v in range(start_v, end_v + 1))
                    return
                except ValueError:
                    return

            range_m = re.match(r'^(\d+)-(\d+)$', cleaned)
            if range_m:
                try:
                    start_v = int(range_m.group(1))
                    end_v = int(range_m.group(2))
                    verses.extend(str(v) for v in range(start_v, end_v + 1))
                    return
                except ValueError:
                    return

            if cleaned.isdigit():
                verses.append(cleaned)
                return

            verses.append(cleaned)

        # Divide por '. ' (separator de refs encadeadas como "1. 2:3. 5")
        sub_parts = re.split(r'\.\s+', verses_raw)
        for sp in sub_parts:
            sp = sp.strip()
            if not sp:
                continue
            # Strip trailing dot if present (but not decimal like "1.2")
            if sp.endswith('.') and not re.match(r'^\d+\.\d+$', sp):
                sp = sp[:-1]
            s_clean = sp.strip(', \t')
            if s_clean and not s_clean[0].isdigit():
                break
            if not sp:
                continue
            # Carryover separator: '2:3' means verse 2 and verse 3 of the SAME chapter
            if ':' in sp and re.fullmatch(r'\d+(?:\s*:\s*\d+)+', sp):
                for p in sp.split(':'):
                    append_token(p)
                continue
            for token in sp.split(','):
                append_token(token)
        return verses

    def _make_ref(
        self, raw: str, book_ntsk: str, chapter: str,
        verses_raw: str, pre_syms: str, post_syms: str,
        vers_raw: str = "",
    ) -> list[NTSKRef]:
        """Constrói uma ou mais NTSKRef a partir de grupos regex.

        Para carryover chain (e.g. "Mt 1:1. 2:3. 5."), retorna múltiplas refs.
        Para ref simples, retorna uma única NTSKRef.

        verses_raw: full verses string (pre_syms + mid_syms + pre_vers from regex).
        vers_raw: the raw verse number/range captured by the regex group.
        """
        book_vault = self._resolve_book(book_ntsk)
        if not book_vault:
            return []
        post_syms_str, verses_clean = self._extract_symbols(post_syms)
        all_syms = pre_syms + post_syms_str
        sym_chars = [c for c in NTSK_SYMBOLS if c in all_syms]

        # Fix: se vers_raw é só um dígito e verses_clean começa com ", X" (vírgula + dígito),
        # então a vírgula faz parte da lista de versículos e devemos combinar.
        # Ex: "1, 2, 3" -> vers_raw='1', verses_clean=', 2, 3' -> combined='1, 2, 3'
        combined_vers = None
        if vers_raw and verses_clean:
            # verses_clean starts with comma/digit pattern like ", 2, 3" or ",2,3"
            if re.match(r'^,\s*\d', verses_clean):
                # Mantém a string inteira para preservar ranges e possíveis chains.
                combined_vers = vers_raw + verses_clean
                verses_clean = ''  # signals that we used combined_vers

        verses_stripped = verses_clean.strip() if verses_clean else (combined_vers or "")

        # Chain detection: verses_clean com leading '. ' indica carryover
        # Ex: ". 2:3. 5" -> split -> ["2:3", "5"], cria uma ref por parte
        chain_source = None
        if verses_clean.startswith('. '):
            chain_source = vers_raw + verses_clean
        elif combined_vers and re.search(r'\.\s+\d', combined_vers):
            chain_source = combined_vers
        is_chain = bool(
            chain_source and
            chain_source.strip() not in ('.',)
        )
        if is_chain:
            parts = re.split(r'\.\s+', chain_source)
            results: list[NTSKRef] = []
            carried_chapter = chapter
            carried_book_ntsk = book_ntsk
            carried_book_vault = book_vault
            for idx, part in enumerate(parts):
                part = part.strip()
                if not part:
                    continue
                # Remove trailing dot if present
                if part.endswith('.'):
                    part = part[:-1].strip()
                if not part:
                    continue
                if _REF_WITH_BOOK.match(part):
                    # Book-change detected — STOP chain processing.
                    # The outer parse loop will restart from this book-change position!
                    break

                if not part[0].isdigit():
                    # Explanatory text, not a cross-reference. (e.g. "This is a...")
                    # STOP chain processing.
                    break

                # Check if part has digit:digit pattern — chapter:verse vs verse carryover
                # "2:3" (first < 5, both small) -> verse carryover SPLIT into 2 refs
                # "5:1" (first >= 5) -> chapter change
                # "37:2" (first >= 10) -> chapter change
                # NOTE: first part (idx==0) with chapter:verse should NOT be carryover even if first<5
                vers_split = part.split(':')
                if len(vers_split) == 2 and vers_split[0].strip().isdigit():
                    first_num = int(vers_split[0].strip())
                    second_num_str = vers_split[1].strip()
                    is_first_part = (idx == 0)
                    if is_first_part or first_num >= 5:
                        # First part always uses explicit chapter (no carryover), OR
                        # Chapter change: "5:1" (chapter 5) or "37:2" (chapter 37)
                        carried_chapter = str(first_num)
                        part_verses = self._expand_verses(second_num_str) if second_num_str else [str(first_num)]
                    else:
                        # Verse carryover: "2:3" -> SPLIT into separate refs for each verse
                        carry_verses = [str(first_num)]
                        if second_num_str:
                            carry_verses.extend(self._expand_verses(second_num_str))
                        for v in carry_verses:
                            results.append(NTSKRef(
                                raw=raw, book_abbr=carried_book_ntsk, book_vault=carried_book_vault,
                                chapter=carried_chapter, verses=[v],
                                symbols=sym_chars,
                                symbol_names=[NTSK_SYMBOLS[s] for s in sym_chars],
                            ))
                        continue
                else:
                    # No ':' -> just verses (possibly range or comma-separated)
                    part_verses = self._expand_verses(part)
                if not part_verses:
                    part_verses = [part]
                results.append(NTSKRef(
                    raw=raw, book_abbr=carried_book_ntsk, book_vault=carried_book_vault,
                    chapter=carried_chapter, verses=part_verses,
                    symbols=sym_chars,
                    symbol_names=[NTSK_SYMBOLS[s] for s in sym_chars],
                ))
            return results if results else []

        # Non-chain: single ref
        # verses_stripped starting with '.' followed by LETTER is a book-change pattern
        # e.g. ". Lk 1:1." -> verses_stripped = ". Lk 1:1." (dot preserved by strip)
        # We detect this by checking if verses_stripped matches ". LETTER"
        book_change_pattern = _BOOK_CHANGE_START.match(verses_stripped)
        if book_change_pattern:
            # ". Lk 1:1." pattern — this is a book-change, not verses.
            # Return just the first ref (vers_raw) and signal parse loop to restart.
            first_verses = self._expand_verses(vers_raw) if vers_raw else [chapter]
            return [NTSKRef(
                raw=raw, book_abbr=book_ntsk, book_vault=book_vault,
                chapter=chapter, verses=first_verses,
                symbols=sym_chars,
                symbol_names=[NTSK_SYMBOLS[s] for s in sym_chars],
            )]
        if verses_stripped and verses_stripped not in ('.',):
            verses = self._expand_verses(verses_stripped)
            if not verses and vers_raw:
                verses = self._expand_verses(vers_raw)
        elif verses_raw.strip():
            verses = self._expand_verses(verses_raw.strip())
        elif vers_raw:
            verses = self._expand_verses(vers_raw)
        else:
            verses = []

        return [NTSKRef(
            raw=raw, book_abbr=book_ntsk, book_vault=book_vault,
            chapter=chapter, verses=verses,
            symbols=sym_chars,
            symbol_names=[NTSK_SYMBOLS[s] for s in sym_chars],
        )]

    def _carryover_expand(self, chapter: str, verses: list[str], raw: str) -> list[NTSKRef]:
        """Expande refs de carryover que usam 'cap.vers' contra a convenção NTSK.
        
        Em NTSK carryover, '2:3' após 'Mt 1:1' significa: vers 2 e vers 3 do cap 1.
        O ':' em carryover é SEPARADOR de versos, não 'cap:vers'.
        """
        result: list[NTSKRef] = []
        carried_chapter = self._curr_chapter or chapter
        
        for v in verses:
            parts = v.split(':')
            for p in parts:
                p = p.strip()
                if p.isdigit():
                    result.append(NTSKRef(
                        raw=raw, book_abbr=self._curr_book_ntsk or "",
                        book_vault=self._curr_book_vault,
                        chapter=carried_chapter,
                        verses=[p],
                        symbols=[], symbol_names=[],
                    ))
        return result

    def parse(self) -> "NTSKParser":
        text = self.ntsk_raw.strip()
        i = 0
        while i < len(text):
            m = _REF_WITH_BOOK.match(text, i)
            if m:
                pre_syms  = m.group(1) or ""
                book_ntsk = m.group(2).strip()
                mid_syms  = m.group(3) or ""
                chapter   = m.group(4)
                pre_vers  = m.group(5) or ""
                vers_raw  = m.group(6)
                post_syms = m.group(7) or ""
                self._curr_book_ntsk = book_ntsk
                self._curr_book_vault = self._resolve_book(book_ntsk)
                self._curr_chapter = chapter
                self._carryover_cap = chapter
                refs = self._make_ref(
                    m.group(0), book_ntsk, chapter, vers_raw,
                    pre_syms + mid_syms + pre_vers, post_syms,
                    vers_raw=vers_raw,
                )
                self.refs.extend(refs)
                # Check if post_syms has a book-change pattern (. LETTER)
                # If so, find the book position and continue from there
                book_m = _BOOK_CHANGE_AFTER_DOT.search(post_syms)
                if book_m:
                    post_syms_start = m.end() - len(post_syms)
                    book_abs_pos = post_syms_start + book_m.start(1)
                    i = book_abs_pos
                else:
                    i = m.end()
                continue
            if self._curr_book_vault:
                m = _REF_NO_BOOK.match(text, i)
                if m:
                    chapter = m.group(2)
                    if chapter.isdigit():
                        # Chapter-only reference (carryover/new chapter within same book)
                        pre_syms  = m.group(1) or ""
                        mid_syms  = m.group(3) or ""
                        vers_raw  = m.group(4)
                        post_syms = m.group(5) or ""
                        try:
                            cap_int = int(chapter)
                            prev_cap = int(self._curr_chapter) if self._curr_chapter else 0
                            carry_cap = int(self._carryover_cap) if self._carryover_cap else prev_cap
                            if cap_int != prev_cap:
                                next_cap = self._peek_next_cap(post_syms)
                                is_carryover = (
                                    next_cap is not None and
                                    next_cap < carry_cap
                                )
                                if is_carryover:
                                    carry_refs = self._carryover_expand(
                                        self._carryover_cap or chapter,
                                        [chapter, vers_raw.replace('.', '')],
                                        m.group(0),
                                    )
                                    self.refs.extend(carry_refs)
                                    i = m.end()
                                    continue
                        except ValueError:
                            pass
                        self._curr_chapter = chapter
                        self._carryover_cap = chapter
                        refs = self._make_ref(
                            m.group(0), self._curr_book_ntsk or "",
                            chapter, vers_raw,
                            pre_syms + mid_syms, post_syms,
                            vers_raw=vers_raw,
                        )
                        self.refs.extend(refs)
                        i = m.end()
                        continue
                    else:
                        # Non-digit chapter from _REF_NO_BOOK (e.g. space before book name)
                        i = m.end()
                        continue
            # Book change: _REF_NO_BOOK failed or matched non-digit chapter
            # Try _REF_WITH_BOOK if we're at a letter (new book)
            if text[i:i+1].isalpha():
                m = _REF_WITH_BOOK.match(text, i)
                if not m:
                    # Try single-letter book pattern (e.g. "1 S", "2 K", "1 Ch")
                    m = _REF_WITH_BOOK_LETTER.match(text, i)
            else:
                # Text doesn't start with letter - try _REF_WITH_BOOK_LETTER anyway
                # for cases like "1 S 1:1." where book name starts with digit
                m = _REF_WITH_BOOK_LETTER.match(text, i)
                if not m:
                    m = _REF_WITH_BOOK.match(text, i)
            if m:
                pre_syms  = m.group(1) or ""
                book_ntsk = m.group(2).strip()
                mid_syms  = m.group(3) or ""
                chapter   = m.group(4)
                pre_vers  = m.group(5) or ""
                vers_raw  = m.group(6)
                post_syms = m.group(7) or ""
                self._curr_book_ntsk = book_ntsk
                self._curr_book_vault = self._resolve_book(book_ntsk)
                self._curr_chapter = chapter
                self._carryover_cap = chapter
                refs = self._make_ref(
                    m.group(0), book_ntsk, chapter, vers_raw,
                    pre_syms + mid_syms + pre_vers, post_syms,
                    vers_raw=vers_raw,
                )
                self.refs.extend(refs)
                i = m.end()
                continue
            # Caso especial: "5." sozinho no fim da string → próximo vers do cap carryover
            if (self._carryover_cap and
                i + 2 <= len(text) and
                text[i].isdigit() and text[i + 1] == '.' and
                (i + 2 == len(text) or text[i + 2] in ' \t')):
                verses = self._expand_verses(text[i])
                self.refs.append(NTSKRef(
                    raw=text[i], book_abbr=self._curr_book_ntsk or "",
                    book_vault=self._curr_book_vault,
                    chapter=self._carryover_cap,
                    verses=verses,
                    symbols=[], symbol_names=[],
                ))
                i += 2
                continue
            i += 1
        return self

    def _peek_next_cap(self, post_syms: str) -> Optional[int]:
        """Extrai o próximo número de capítulo do post_syms (se existir)."""
        m = re.match(r'\s*(\d+)', post_syms.lstrip())
        if m:
            return int(m.group(1))
        return None

    def to_dict(self) -> dict:
        return {
            "source":         self.source_ref,
            "total_refs":     len(self.refs),
            "refs":           self.refs,
            "strong_h":       self.strong_h,
            "strong_g":       self.strong_g,
            "inline_notes":   self.inline_notes,
            "prophetic_refs": [r for r in self.refs if "\u2721" in r.symbols],
            "at_nt_refs":     [r for r in self.refs if "\u25b6" in r.symbols],
            "contrast_refs":  [r for r in self.refs if "\u25d0" in r.symbols],
            "full_coll_refs": [r for r in self.refs if "+" in r.symbols],
        }


def parse_ntsk_block(ntsk_raw: str, source_ref: str = "") -> dict:
    """API pública: mantém assinatura original para compatibilidade."""
    return NTSKParser(ntsk_raw, source_ref).parse().to_dict()
