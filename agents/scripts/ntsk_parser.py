"""ntsk_parser.py — Extrator estruturado do bloco NTSK (stateful + carryover).
Extrai: referências canônicas, símbolos semânticos, Strong numbers, notas inline.
Suporta carryover (e.g. "Mt 1:1. 2:3. 5." -> Mt 1:1, Mt 1:2, Mt 1:5).
Normaliza IDs para o padrão frontmatter: "Mt 1.1" (espaço, ponto).
"""
import re
from dataclasses import dataclass
from typing import Optional

# --- Mapeamento de sigla NTSK (EN) -> sigla vault (PT-BR) ---
# Fonte: ntsk_2_sigla.json (autoritativo)
BOOK_MAP: dict[str, str] = {
    # Pentateuco
    "Ge": "Gn", "Ex": "Ex", "Le": "Lv", "Nu": "Nm", "Dt": "Dt",
    # Históricos
    "Jsh": "Js", "Jos": "Js", "Jg": "Jz", "Jdg": "Jz", "Ru": "Rt",
    "1 S": "1Sm", "2 S": "2Sm",
    "1 K": "1Rs", "2 K": "2Rs",
    "1 Ch": "1Cr", "2 Ch": "2Cr",
    "Ezr": "Ed", "Ne": "Ne", "Est": "Et",
    # Poéticos
    "Jb": "Jo", "Ps": "Sl", "Pr": "Pv", "Ec": "Ec",
    "SS": "Ct", "Song": "Ct", "So": "Ct",
    # Profetas Maiores
    "Is": "Is", "Je": "Jr", "La": "Lm",
    "Eze": "Ez", "Ezk": "Ez", "Da": "Dn",
    # Profetas Menores
    "Ho": "Os", "Joel": "Jl", "Joe": "Jl", "Am": "Am", "Ob": "Ob",
    "Jon": "Jn", "Mi": "Mq", "Na": "Na", "Hab": "Hc",
    "Zp": "Sf", "Hg": "Ag", "Zc": "Zc", "Ml": "Ml",
    # NT
    "Mt": "Mt", "Mk": "Mc", "Lk": "Lc", "Jn": "Jo", "Ac": "At",
    "Ro": "Rm",
    "1 Co": "1Co", "2 Co": "2Co",
    "Ga": "Gl", "Ep": "Ef", "Ph": "Fp", "Col": "Cl",
    "1 Th": "1Ts", "2 Th": "2Ts",
    "1 T": "1Tm", "2 T": "2Tm", "T": "Tt",
    "Phm": "Fm", "Pm": "Fm",
    "He": "Hb", "Ja": "Tg",
    "1 P": "1Pe", "2 P": "2Pe",
    "1 J": "1Jo", "2 J": "2Jo", "3 J": "3Jo",
    "Ju": "Jd", "Re": "Ap",
}

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

# --- Regex compiladas ---
# Estrutura: [pre-syms] livro [mid-syms] cap [sep] vers_raw [post-syms]
# Onde post-syms é todo o texto após os dígitos do versículo.
# Vers: \d+(-\d+)* para ranges (23-38), decimal (?:\.(?=\d)) se seguido de dígito
# O lookahead (?=\d) só captura '.' se seguido imediatamente por dígito.
_VERS_PAT = r'(\d+(?:-\d+)*(?:\.(?=\d))?)'

_REF_WITH_BOOK = re.compile(
    r'([*+\u25d0=\u2a72\u25b6\u2721\u2225\u2021\u2713]*)'
    r'(\d+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?|[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)'
    r'\s*([*+\u25d0=\u2a72\u25b6\u2721\u2225\u2021\u2713]*)\s*'
    r'(\d+)[:\.]'
    r'\s*([*+\u25d0=\u2a72\u25b6\u2721\u2225\u2021\u2713]*)'
    + _VERS_PAT +
    r'(.*)',
    re.UNICODE | re.DOTALL
)

# Livros de letra única (e.g. "S" em "1 S"):
# O padrão [A-Z][a-z]+ exige 2+ letras. Aqui capturamos "S", "Ch", etc.
_REF_WITH_BOOK_LETTER = re.compile(
    r'([*+\u25d0=\u2a72\u25b6\u2721\u2225\u2021\u2713]*)'
    r'(\d+\s+[A-Z][a-z]*|\d+\s+[A-Z])'
    r'\s*([*+\u25d0=\u2a72\u25b6\u2721\u2225\u2021\u2713]*)\s*'
    r'(\d+)[:\.]'
    r'\s*([*+\u25d0=\u2a72\u25b6\u2721\u2225\u2021\u2713]*)'
    + _VERS_PAT +
    r'(.*)',
    re.UNICODE | re.DOTALL
)

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
        self.ntsk_raw = ntsk_raw
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
        if vault := BOOK_MAP.get(raw_book):
            return vault
        collapsed = re.sub(r'\s+', ' ', raw_book).strip()
        if vault := BOOK_MAP.get(collapsed):
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
        # Divide por '. ' (separator de refs encadeadas como "1. 2:3. 5")
        sub_parts = re.split(r'\.\s+', verses_raw)
        for sp in sub_parts:
            sp = sp.strip()
            if not sp:
                continue
            s_clean = sp.strip(', \t')
            if s_clean and not s_clean[0].isdigit():
                break
            # Strip trailing dot if present (but not decimal like "1.2")
            if sp.endswith('.') and not re.match(r'^\d+\.\d+$', sp):
                sp = sp[:-1]
            if not sp:
                continue
            # Carryover separator: '2:3' means verse 2 and verse 3 of the SAME chapter
            if ':' in sp:
                for p in sp.split(':'):
                    p = p.strip()
                    if p.isdigit():
                        verses.append(p)
                continue
            # Comma-separated verses: '1, 2, 3' -> ['1', '2', '3']
            if ',' in sp:
                for p in sp.split(','):
                    p = p.strip()
                    if p:
                        verses.append(p)
                continue
            # Range expansion: '23-38' -> 16 verses
            if '-' in sp:
                range_m = re.match(r'^(\d+)-(\d+)$', sp)
                if range_m:
                    try:
                        verses.extend(str(v) for v in range(int(range_m.group(1)), int(range_m.group(2)) + 1))
                        continue
                    except ValueError:
                        pass
            verses.append(sp)
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
        post_syms_str, verses_clean = self._extract_symbols(post_syms)
        all_syms = pre_syms + post_syms_str
        sym_chars = [c for c in NTSK_SYMBOLS if c in all_syms]

        # Fix: se vers_raw é só um dígito e verses_clean começa com ", X" (vírgula + dígito),
        # então a vírgula faz parte da lista de versículos e devemos combinar.
        # Ex: "1, 2, 3" -> vers_raw='1', verses_clean=', 2, 3' -> combined='1, 2, 3'
        combined_vers = None
        if vers_raw and vers_raw.isdigit() and verses_clean:
            # verses_clean starts with comma/digit pattern like ", 2, 3" or ",2,3"
            if re.match(r'^,\s*\d', verses_clean):
                # Extract the comma-separated part and combine with vers_raw
                comma_part = verses_clean[1:].strip()  # remove leading comma
                combined_vers = vers_raw + ', ' + comma_part
                verses_clean = ''  # signals that we used combined_vers

        verses_stripped = verses_clean.strip() if verses_clean else (combined_vers or "")

        # Chain detection: verses_clean com leading '. ' indica carryover
        # Ex: ". 2:3. 5" -> split -> ["2:3", "5"], cria uma ref por parte
        is_chain = (
            verses_stripped and
            verses_stripped not in ('.',) and
            verses_clean.startswith('. ')
        )
        if is_chain:
            # Chain: verses_clean = ". 2:3. 5" (starts with '. '), use directly
            # Prepend vers_raw (the first verse) to get full chain
            chain_str = vers_raw + verses_clean
            parts = re.split(r'\.\s+', chain_str)
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
                # Check if part is a book-change pattern: "Lk 1:1" or "1 Co 1"
                part_space = part.split(' ')
                new_book_ntsk = ""
                if len(part_space) >= 2 and self._resolve_book(part_space[0] + " " + part_space[1]):
                    new_book_ntsk = part_space[0] + " " + part_space[1]
                elif len(part_space) >= 1 and self._resolve_book(part_space[0]):
                    new_book_ntsk = part_space[0]

                if new_book_ntsk:
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
                        for v in part.split(':'):
                            v = v.strip()
                            if v.isdigit():
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
        import re as _re
        book_change_pattern = _re.match(r'\.\s*[A-Za-z]', verses_stripped)
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
                import re as _re
                book_m = _re.search(r'\.\s+([A-Za-z])', post_syms)
                if book_m:
                    # book_m matches ". L" where . is separator and L is first letter of book
                    # book_m.group(0) = ". L" (separator . + letter)
                    # The letter starts AFTER the separator in post_syms
                    # Separator length = len(book_m.group(0)) - 1 (the letter is not part of separator)
                    # = 3 - 1 = 2 for ". L", = 1 for ".L"
                    post_syms_start = m.end() - len(post_syms)
                    sep_len = len(book_m.group(0)) - 1
                    book_abs_pos = post_syms_start + book_m.start() + sep_len
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
