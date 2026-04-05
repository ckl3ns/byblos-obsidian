"""ntsk_parser.py — Extrator estruturado do bloco NTSK.
Extrai: referências canônicas, símbolos semânticos, Strong numbers, notas inline.
"""
import re
from dataclasses import dataclass
from typing import Optional

BOOK_MAP = {
    "Ge":"Gn","Ex":"Ex","Le":"Lv","Nu":"Nm","Dt":"Dt",
    "Jsh":"Js","Jg":"Jz","Ru":"Rt",
    "1 S":"1Sm","2 S":"2Sm","1S":"1Sm","2S":"2Sm",
    "1 K":"1Rs","2 K":"2Rs","1K":"1Rs","2K":"2Rs",
    "1 Ch":"1Cr","2 Ch":"2Cr","1Ch":"1Cr","2Ch":"2Cr",
    "Ezr":"Ed","Ne":"Ne","Es":"Et",
    "Jb":"Jó","Ps":"Sl","Pr":"Pv","Ec":"Ec","Song":"Ct",
    "Is":"Is","Je":"Jr","La":"Lm","Ez":"Ez","Da":"Dn",
    "Ho":"Os","Joe":"Jl","Am":"Am","Ob":"Ob",
    "Jon":"Jn","Mi":"Mq","Na":"Na","Hab":"Hc",
    "Zp":"Sf","Hg":"Ag","Zc":"Zc","Ml":"Ml",
    "Mt":"Mt","Mk":"Mc","Lk":"Lc","Jn":"Jo","Ac":"At","Ro":"Rm",
    "1 Co":"1Co","2 Co":"2Co","1Co":"1Co","2Co":"2Co",
    "Ga":"Gl","Ep":"Ef","Ph":"Fp","Col":"Col",
    "1 Th":"1Ts","2 Th":"2Ts","1Th":"1Ts","2Th":"2Ts",
    "1 Ti":"1Tm","2 Ti":"2Tm","1Ti":"1Tm","2Ti":"2Tm",
    "Tt":"Tt","Phm":"Fm","He":"Hb","Ja":"Tg",
    "1 P":"1Pe","2 P":"2Pe","1P":"1Pe","2P":"2Pe",
    "1 J":"1Jo","2 J":"2Jo","3 J":"3Jo","1J":"1Jo","2J":"2Jo","3J":"3Jo",
    "Jude":"Jd","Re":"Ap",
}

NTSK_SYMBOLS = {
    "*":"ref_clara","\u2713":"ref_critica","+":"colecao_completa",
    "\u25d0":"contraste","=":"tipo_antitipo","\u2a72":"tipo_antitipo_escritural",
    "\u25b6":"citacao_at_nt","\u2721":"cumprimento_profecia",
    "\u2225":"passagem_paralela","\u2021":"doutrina_falsa",
}

_REF = re.compile(
    r'([*\u2713+\u25d0=\u2a72\u25b6\u2721\u2225\u2021]*)'
    r'(\d\s+)?([A-Z][a-z]+(?:\s[A-Z][a-z]+)?)\s+(\d+)[:.](\d+(?:,\s*\d+)*)[a-z]?'
)
_SH = re.compile(r'\u2745S#(\d+h)')
_SG = re.compile(r'\u2763S#(\d+g)|(?:S#(\d+g))')
_NT = re.compile(r'i\.e\.\s+[^.]+|Heb\.\s+[^.]+|or,\s+[^.]+|\([^)]+\)')

@dataclass
class NTSKRef:
    raw: str
    book_abbr: str
    book_vault: Optional[str]
    chapter: str
    verses: list
    symbols: list
    symbol_meanings: list

def parse_ntsk_block(ntsk_raw: str, source_ref: str = "") -> dict:
    refs = []
    for m in _REF.finditer(ntsk_raw):
        syms  = m.group(1)
        pre   = (m.group(2) or "").strip()
        book  = m.group(3).strip()
        bkey  = f"{pre} {book}" if pre else book
        bv    = BOOK_MAP.get(bkey) or BOOK_MAP.get(book)
        dec   = [s for s in NTSK_SYMBOLS if s in syms]
        refs.append(NTSKRef(
            raw=m.group(0), book_abbr=bkey, book_vault=bv,
            chapter=m.group(4), verses=[v.strip() for v in m.group(5).split(",")],
            symbols=dec, symbol_meanings=[NTSK_SYMBOLS[s] for s in dec],
        ))
    return {
        "source": source_ref, "total_refs": len(refs), "refs": refs,
        "strong_h": _SH.findall(ntsk_raw),
        "strong_g": [a or b for a,b in _SG.findall(ntsk_raw)],
        "inline_notes": _NT.findall(ntsk_raw),
        "prophetic_refs": [r for r in refs if "\u2721" in r.symbols],
        "at_nt_refs":    [r for r in refs if "\u25b6" in r.symbols],
        "contrast_refs": [r for r in refs if "\u25d0" in r.symbols],
    }
