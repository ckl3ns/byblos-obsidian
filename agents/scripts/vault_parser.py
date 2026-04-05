"""vault_parser.py — Parse de nós do vault Bíblico-Teológico.
Suporta tipos: versiculo, capitulo, livro.
SOMENTE LEITURA — não modifica nenhum arquivo.
"""
import re, yaml
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class VaultNode:
    node_type: str
    raw_frontmatter: dict
    breadcrumb: str
    nav_prev: Optional[str]
    nav_next: Optional[str]
    referencia: Optional[str] = None
    sigla: Optional[str] = None
    livro: Optional[str] = None
    indice_livro: Optional[int] = None
    capitulo: Optional[int] = None
    versiculo: Optional[int] = None
    kjv: Optional[str] = None
    bkj: Optional[str] = None
    testamento: Optional[str] = None
    canon_judaico: Optional[str] = None
    canon_cristao: Optional[str] = None
    ntsk_raw: Optional[str] = None
    enrichment_sections: dict = field(default_factory=dict)
    dataview_query: Optional[str] = None

_FM   = re.compile(r'^---\r?\n(.*?)\r?\n---', re.DOTALL)
_BC   = re.compile(r'(\[\[Bíblia\]\].*)', re.MULTILINE)
_NAV  = re.compile(r'\[\[([^\]|]+?)(?:\|Voltar)?\]\]\s*❮.*?❯\s*\[\[([^\]|]+?)(?:\|Avançar)?\]\]')
_NTSK = re.compile(r'##\s+🔗\s+\*\*Referências Cruzadas \(NTSK\)\*\*\s*\n\n`(.*?)`', re.DOTALL)
_SEC  = re.compile(r'^##\s+(.+?)$', re.MULTILINE)
_DV   = re.compile(r'```dataview\n(.*?)```', re.DOTALL)

def parse_node(filename: str, content: str) -> VaultNode:
    fm_m = _FM.match(content)
    fm   = yaml.safe_load(fm_m.group(1)) if fm_m else {}
    if fm.get('versiculo') is not None:
        ntype = 'versiculo'
    elif fm.get('capitulo') is not None:
        ntype = 'capitulo'
    else:
        ntype = 'livro'
    bc   = _BC.search(content)
    nav  = _NAV.search(content)
    ntsk = _NTSK.search(content)
    dv   = _DV.search(content)
    enrich = {}
    if ntsk:
        parts = _SEC.split(content[ntsk.end():])
        for i in range(1, len(parts), 2):
            enrich[parts[i].strip()] = parts[i+1].strip() if i+1 < len(parts) else ''
    return VaultNode(
        node_type=ntype, raw_frontmatter=fm,
        breadcrumb=bc.group(1).strip() if bc else '',
        nav_prev=nav.group(1) if nav else None,
        nav_next=nav.group(2) if nav else None,
        referencia=fm.get('referencia'), sigla=fm.get('sigla'),
        livro=fm.get('livro'), indice_livro=fm.get('indice_livro'),
        capitulo=fm.get('capitulo'), versiculo=fm.get('versiculo'),
        kjv=fm.get('KJV','').strip() if fm.get('KJV') else None,
        bkj=fm.get('BKJ','').strip() if fm.get('BKJ') else None,
        testamento=fm.get('testamento'), canon_judaico=fm.get('canon_judaico'),
        canon_cristao=fm.get('canon_cristao'),
        ntsk_raw=ntsk.group(1).strip() if ntsk else None,
        enrichment_sections=enrich,
        dataview_query=dv.group(1).strip() if dv else None,
    )

def parse_file(path) -> VaultNode:
    p = Path(path)
    return parse_node(p.name, p.read_text(encoding='utf-8'))

def parse_vault(vault_dir) -> list:
    """Parseia todos os .md de um diretório recursivamente."""
    results = []
    for md in Path(vault_dir).rglob('*.md'):
        try:
            results.append(parse_file(md))
        except Exception as e:
            print(f"[WARN] {md}: {e}")
    return results
