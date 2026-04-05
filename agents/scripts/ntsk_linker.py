#!/usr/bin/env python3
"""
ntsk_linker.py
==============
Converte blocos NTSK raw (entre backticks) em wikilinks Obsidian
nos arquivos .md do vault bíblico.

Uso:
    # Modo preview (não altera arquivos):
    python ntsk_linker.py --vault /caminho/vault --dry-run

    # Modo real (altera arquivos in-place):
    python ntsk_linker.py --vault /caminho/vault

    # Processar arquivo único:
    python ntsk_linker.py --file /caminho/Mt-1.1.md

    # Gerar relatório CSV:
    python ntsk_linker.py --vault /caminho/vault --dry-run --report resultado.csv
"""

import re
import os
import csv
import argparse
from pathlib import Path

try:
    import yaml
except ImportError:
    print("Instale pyyaml: pip install pyyaml")
    raise

# ==========================================
# MAPEAMENTO: sigla NTSK (EN) → sigla vault (PT-BR)
# ==========================================
NTSK_TO_VAULT = {
    # Pentateuco
    "Ge": "Gn", "Ex": "Ex", "Le": "Lv", "Lv": "Lv", "Nu": "Nm", "Dt": "Dt",
    # Históricos
    "Jsh": "Js", "Jos": "Js", "Jg": "Jz", "Jdg": "Jz", "Ru": "Rt",
    "1 S": "1Sm", "2 S": "2Sm", "1 K": "1Rs", "2 K": "2Rs",
    "1 Ch": "1Cr", "2 Ch": "2Cr", "Ezr": "Ed", "Ne": "Ne", "Es": "Et",
    # Poéticos
    "Jb": "Jó", "Ps": "Sl", "Pr": "Pv", "Ec": "Ec", "SS": "Ct", "So": "Ct",
    # Profetas Maiores
    "Is": "Is", "Je": "Jr", "La": "Lm", "Eze": "Ez", "Ezk": "Ez", "Da": "Dn",
    # Profetas Menores
    "Ho": "Os", "Jl": "Jl", "Am": "Am", "Ob": "Ob", "Jon": "Jn",
    "Mi": "Mq", "Na": "Na", "Hab": "Hc", "Zp": "Sf", "Hg": "Ag",
    "Zc": "Zc", "Ml": "Ml",
    # NT
    "Mt": "Mt", "Mk": "Mc", "Lk": "Lc", "Jn": "Jo", "Ac": "At",
    "Ro": "Rm", "1 Co": "1Co", "2 Co": "2Co", "Ga": "Gl", "Ep": "Ef",
    "Ph": "Fp", "Col": "Cl", "1 Th": "1Ts", "2 Th": "2Ts",
    "1 Ti": "1Tm", "2 Ti": "2Tm", "Tit": "Tt", "Tt": "Tt",
    "Phm": "Fm", "Pm": "Fm",
    "He": "Hb", "Ja": "Tg",
    "1 Pe": "1Pe", "2 Pe": "2Pe", "1 Jn": "1Jo", "2 Jn": "2Jo", "3 Jn": "3Jo",
    "Ju": "Jd", "Re": "Ap",
}

# Build regex de siglas (ordenado por tamanho desc para evitar match parcial)
_siglas_sorted = sorted(NTSK_TO_VAULT.keys(), key=len, reverse=True)
SIGLA_RE = '|'.join(re.escape(s) for s in _siglas_sorted)

SYM_CHARS = r'[*\u2713+\u2721\u25b6\u25d0=\u2A72\u2225\u2021?\u2723\u25d0\u25b6\U0001D4AB]'
SYMS      = SYM_CHARS + '+'

REF_WITH_BOOK = re.compile(
    r'(?P<pre_syms>' + SYMS + r')?\ *'
    r'(?P<book>' + SIGLA_RE + r')\ +'
    r'(?P<mid_syms>' + SYMS + r')?\ *'
    r'(?P<chap>\d+):(?P<post_syms>' + SYMS + r')?\ *(?P<vers>\d+)'
    r'(?:-(?P<vers_end>\d+))?',
    re.UNICODE
)

REF_NO_BOOK = re.compile(
    r'(?P<pre_syms>' + SYMS + r')?\ *'
    r'(?P<chap>\d+):(?P<post_syms>' + SYMS + r')?\ *(?P<vers>\d+)'
    r'(?:-(?P<vers_end>\d+))?',
    re.UNICODE
)

COMMA_VERS = re.compile(
    r',\ *(?P<post_syms>' + SYMS + r')?\ *(?P<vers>\d+)(?:-(?P<vers_end>\d+))?',
    re.UNICODE
)

VER_RE = re.compile(r'ver\.\s*(?P<v>\d+(?:,\s*\d+)*)')

NTSK_BLOCK_RE = re.compile(
    r'(## 🔗 \*\*Referências Cruzadas \(NTSK\)\*\*\s*\n+)`([^`]+)`'
)


def make_link(vault_sig, chap, vers, vers_end=None, symbols=''):
    if vers_end:
        return f"{symbols}[[{vault_sig}-{chap}.{vers}|{vault_sig} {chap}:{vers}-{vers_end}]]"
    return f"{symbols}[[{vault_sig}-{chap}.{vers}]]"


def parse_ntsk(ntsk_raw, host_vault_sigla, host_chapter):
    text   = ntsk_raw.strip()
    out    = []
    missing = []
    resolved = 0
    current_book_vault = None
    current_chap = None
    i = 0

    while i < len(text):
        # ver. N
        m = VER_RE.match(text, i)
        if m:
            for v in [x.strip() for x in m.group('v').split(',')]:
                out.append(make_link(host_vault_sigla, host_chapter, v))
                resolved += 1
            i = m.end(); continue

        # Ref COM sigla
        m = REF_WITH_BOOK.match(text, i)
        if m:
            syms = ((m.group('pre_syms') or '') + (m.group('mid_syms') or '') + (m.group('post_syms') or '')).strip()
            book_ntsk = m.group('book')
            chap = m.group('chap'); vers = m.group('vers'); ve = m.group('vers_end')
            vault_sig = NTSK_TO_VAULT.get(book_ntsk)
            if vault_sig:
                current_book_vault = vault_sig
                current_chap = chap
                out.append(' ' + make_link(vault_sig, chap, vers, ve, syms))
                resolved += 1
                j = m.end()
                while j < len(text):
                    cm = COMMA_VERS.match(text, j)
                    if cm:
                        ps = (cm.group('post_syms') or '').strip()
                        out.append(' ' + make_link(vault_sig, chap, cm.group('vers'), cm.group('vers_end'), ps))
                        resolved += 1; j = cm.end()
                    else: break
                i = j
            else:
                out.append(m.group(0)); missing.append(book_ntsk); i = m.end()
            continue

        # Ref SEM sigla (carryover)
        if current_book_vault:
            m = REF_NO_BOOK.match(text, i)
            if m:
                syms = ((m.group('pre_syms') or '') + (m.group('post_syms') or '')).strip()
                chap = m.group('chap'); vers = m.group('vers'); ve = m.group('vers_end')
                current_chap = chap
                out.append(' ' + make_link(current_book_vault, chap, vers, ve, syms))
                resolved += 1
                j = m.end()
                while j < len(text):
                    cm = COMMA_VERS.match(text, j)
                    if cm:
                        ps = (cm.group('post_syms') or '').strip()
                        out.append(' ' + make_link(current_book_vault, chap, cm.group('vers'), cm.group('vers_end'), ps))
                        resolved += 1; j = cm.end()
                    else: break
                i = j; continue

        out.append(text[i]); i += 1

    return ''.join(out).strip(), {'resolved': resolved, 'missing': missing}


def extract_frontmatter(content):
    if not content.startswith('---'): return {}, content
    end = content.find('\n---', 3)
    if end == -1: return {}, content
    try: fm = yaml.safe_load(content[3:end]) or {}
    except: fm = {}
    return fm, content[end+4:]


def process_file(file_path, dry_run=True):
    content = Path(file_path).read_text(encoding='utf-8')
    fm, _ = extract_frontmatter(content)
    vault_sigla = fm.get('sigla', '')
    chapter     = fm.get('capitulo', 0)
    versiculo   = fm.get('versiculo', 0)

    if not versiculo or not vault_sigla or not chapter:
        return {'file': file_path, 'status': 'skipped', 'reason': 'not_verse'}

    m = NTSK_BLOCK_RE.search(content)
    if not m:
        return {'file': file_path, 'status': 'skipped', 'reason': 'no_ntsk_block'}

    linked_text, stats = parse_ntsk(m.group(2), vault_sigla, int(chapter))
    if stats['resolved'] == 0:
        return {'file': file_path, 'status': 'skipped', 'reason': 'zero_refs'}

    new_block   = m.group(1) + linked_text
    new_content = content[:m.start()] + new_block + content[m.end():]

    if not dry_run:
        Path(file_path).write_text(new_content, encoding='utf-8')

    return {
        'file': str(file_path),
        'status': 'ok',
        'ref': f"{vault_sigla} {chapter}:{versiculo}",
        'resolved': stats['resolved'],
        'missing': '|'.join(stats['missing']) if stats['missing'] else '',
    }


def process_vault(vault_path, dry_run=True, report_path=None):
    results = []
    md_files = list(Path(vault_path).rglob('*.md'))
    print(f"Encontrados {len(md_files)} arquivos .md")

    for fp in md_files:
        r = process_file(fp, dry_run=dry_run)
        results.append(r)
        if r['status'] == 'ok':
            missing_warn = f" | MISSING: {r['missing']}" if r['missing'] else ""
            print(f"  ✓ {r['ref']} — {r['resolved']} refs{missing_warn}")

    ok      = [r for r in results if r['status'] == 'ok']
    skipped = [r for r in results if r['status'] == 'skipped']
    total_resolved = sum(r.get('resolved', 0) for r in ok)

    print(f"\n=== RESUMO ===")
    print(f"Processados: {len(ok)} | Ignorados: {len(skipped)} | Total refs: {total_resolved}")
    if dry_run:
        print("(DRY RUN — nenhum arquivo alterado)")

    if report_path:
        with open(report_path, 'w', newline='', encoding='utf-8') as f:
            w = csv.DictWriter(f, fieldnames=['file','status','reason','ref','resolved','missing'])
            w.writeheader()
            for r in results:
                w.writerow({k: r.get(k,'') for k in w.fieldnames})
        print(f"Relatório salvo: {report_path}")

    return results


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Converte blocos NTSK em wikilinks Obsidian')
    parser.add_argument('--vault',  help='Caminho do vault Obsidian')
    parser.add_argument('--file',   help='Processar arquivo único')
    parser.add_argument('--dry-run', action='store_true', default=True,
                        help='Não alterar arquivos (padrão: True)')
    parser.add_argument('--run',    action='store_true',
                        help='Realmente alterar arquivos (sobrescreve --dry-run)')
    parser.add_argument('--report', help='Salvar relatório CSV')
    args = parser.parse_args()

    dry = not args.run

    if args.file:
        r = process_file(args.file, dry_run=dry)
        print(r)
    elif args.vault:
        process_vault(args.vault, dry_run=dry, report_path=args.report)
    else:
        print("Use --vault ou --file. Veja --help")
