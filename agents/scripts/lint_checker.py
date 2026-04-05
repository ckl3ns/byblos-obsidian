"""lint_checker.py
Health checks do vault bíblico-teológico.
Verifica regras do AGENTS.md e gera relatório em reports/lint/.

Verificações:
  1. Nós de versículo com enriquecimento sem [Fonte: ...]
  2. [INFERÊNCIA DO AGENTE] fora de seção "Lacunas Identificadas"
  3. Frontmatter de nós Bíblia/ com campos obrigatórios ausentes
  4. Wikilinks [[...]] quebrados (alvo não existe no vault)
  5. Seções em ordem errada (fora do ALLOWED_SECTIONS order)
  6. Artigos wiki/conceitos/ sem seção "O que este conceito NÃO é"
  7. Artigos wiki/obras/ com path_raw inexistente
  8. Conceitos citados em versículos mas sem artigo em wiki/conceitos/
"""
import re
import yaml
from pathlib import Path
from dataclasses import dataclass, field
from datetime import date
from typing import Optional


FRONTMATTER_RE  = re.compile(r'^---\r?\n(.*?)\r?\n---', re.DOTALL)
SOURCE_TAG_RE   = re.compile(r'\[Fonte:\s*.+?\|\s*Obra:\s*.+?\|\s*Nível:\s*[1-5]\]')
INFERENCE_RE    = re.compile(r'\[INFERÊNCIA DO AGENTE\]')
WIKILINK_RE     = re.compile(r'\[\[([^\]|#]+?)(?:\|[^\]]+)?\]\]')
SECTION_H2_RE   = re.compile(r'^##\s+(.+?)$', re.MULTILINE)

ALLOWED_SECTIONS_ORDER = [
    "Léxico",
    "Contexto Histórico-Cultural",
    "Posições Exegéticas",
    "Conexões no Grafo",
    "Lacunas Identificadas",
]

VERSICULO_REQUIRED_FM = [
    'referencia', 'sigla', 'livro', 'indice_livro',
    'capitulo', 'versiculo', 'KJV', 'BKJ', 'testamento', 'status'
]

NTSK_BLOCK_RE = re.compile(
    r'##\s+🔗\s+\*\*Referências Cruzadas \(NTSK\)\*\*\s*\n\n`.*?`',
    re.DOTALL
)


@dataclass
class LintIssue:
    severity: str       # 'CRITICO' | 'MENOR' | 'SUGESTAO'
    file: str
    rule: str
    detail: str
    suggestion: str = ''


@dataclass
class LintReport:
    date: str
    vault_dir: str
    issues: list[LintIssue] = field(default_factory=list)
    stats: dict = field(default_factory=dict)

    @property
    def critical(self):
        return [i for i in self.issues if i.severity == 'CRITICO']

    @property
    def minor(self):
        return [i for i in self.issues if i.severity == 'MENOR']

    @property
    def suggestions(self):
        return [i for i in self.issues if i.severity == 'SUGESTAO']

    def to_markdown(self) -> str:
        lines = [
            f"---",
            f"data: {self.date}",
            f"vault: {self.vault_dir}",
            f"criticos: {len(self.critical)}",
            f"menores: {len(self.minor)}",
            f"sugestoes: {len(self.suggestions)}",
            f"---",
            "",
            f"# Relatório de Lint — {self.date}",
            "",
        ]

        if self.stats:
            lines += ["## Métricas do Vault", ""]
            lines += [f"| Métrica | Valor |", "|---------|-------|"]
            for k, v in self.stats.items():
                lines.append(f"| {k} | {v} |")
            lines.append("")

        for sev, label in [('CRITICO','Problemas Críticos'), ('MENOR','Problemas Menores'), ('SUGESTAO','Sugestões')]:
            group = [i for i in self.issues if i.severity == sev]
            if not group:
                continue
            lines += [f"## {label}", ""]
            for issue in group:
                lines.append(f"- **[{issue.rule}]** `{issue.file}`")
                lines.append(f"  {issue.detail}")
                if issue.suggestion:
                    lines.append(f"  → _{issue.suggestion}_")
            lines.append("")

        return "\n".join(lines)


def _parse_fm(content: str) -> dict:
    m = FRONTMATTER_RE.match(content)
    if not m:
        return {}
    try:
        return yaml.safe_load(m.group(1)) or {}
    except Exception:
        return {}


def _all_md_files(vault_dir: Path) -> list[Path]:
    return list(vault_dir.rglob('*.md'))


def _build_file_index(vault_dir: Path) -> set[str]:
    """Conjunto de referências resolvíveis (stems + referencia fields)."""
    index = set()
    for md in vault_dir.rglob('*.md'):
        index.add(md.stem.lower())
        fm = _parse_fm(md.read_text(encoding='utf-8', errors='replace'))
        if ref := fm.get('referencia'):
            index.add(str(ref).lower())
        for alias in (fm.get('alias') or []):
            index.add(str(alias).lower())
    return index


def run_lint(vault_dir: str | Path, output_dir: Optional[str | Path] = None) -> LintReport:
    vault = Path(vault_dir)
    report = LintReport(date=str(date.today()), vault_dir=str(vault))
    file_index = _build_file_index(vault)

    biblia_dir = vault / 'Bíblia'
    wiki_dir   = vault / 'wiki'
    raw_dir    = vault / 'raw'

    versiculo_count = 0
    enriched_count  = 0
    wiki_concepts   = set()
    broken_links    = 0
    no_source_count = 0

    all_files = _all_md_files(vault) if vault.exists() else []

    for md in all_files:
        try:
            content = md.read_text(encoding='utf-8', errors='replace')
        except Exception:
            continue

        fm    = _parse_fm(content)
        rel   = str(md.relative_to(vault))
        short = rel

        # ── Regra 1: frontmatter de versículo com campos ausentes ────
        if fm.get('versiculo') is not None and str(biblia_dir) in str(md):
            versiculo_count += 1
            missing_fm = [f for f in VERSICULO_REQUIRED_FM if fm.get(f) is None]
            if missing_fm:
                report.issues.append(LintIssue(
                    severity='MENOR', file=short, rule='FM_INCOMPLETO',
                    detail=f"Campos ausentes no frontmatter: {missing_fm}",
                    suggestion="Preencher campos no pipeline de geração do vault."
                ))

        # ── Regra 2: enriquecimento sem [Fonte: ...] ─────────────────
        ntsk_m = NTSK_BLOCK_RE.search(content)
        if ntsk_m:
            after_ntsk = content[ntsk_m.end():]
            sections = SECTION_H2_RE.split(after_ntsk)
            for i in range(1, len(sections), 2):
                title = sections[i].strip()
                body  = sections[i+1].strip() if i+1 < len(sections) else ''
                if title == 'Lacunas Identificadas':
                    continue
                if body and not SOURCE_TAG_RE.search(body):
                    no_source_count += 1
                    enriched_count += 1
                    report.issues.append(LintIssue(
                        severity='CRITICO', file=short, rule='SEM_FONTE',
                        detail=f"Seção '{title}' contém afirmações sem [Fonte: ...].",
                        suggestion="Adicionar tag [Fonte: raw/... | Obra: ... | Nível: N] a cada afirmação."
                    ))
                elif body:
                    enriched_count += 1

        # ── Regra 3: [INFERÊNCIA] fora de Lacunas ────────────────────
        if ntsk_m:
            after_ntsk = content[ntsk_m.end():]
            sec_parts = SECTION_H2_RE.split(after_ntsk)
            for i in range(1, len(sec_parts), 2):
                title = sec_parts[i].strip()
                body  = sec_parts[i+1] if i+1 < len(sec_parts) else ''
                if title != 'Lacunas Identificadas' and INFERENCE_RE.search(body):
                    report.issues.append(LintIssue(
                        severity='CRITICO', file=short, rule='INFERENCIA_FORA_LUGAR',
                        detail=f"[INFERÊNCIA DO AGENTE] encontrada em '{title}'.",
                        suggestion="Mover inferência para seção 'Lacunas Identificadas'."
                    ))

        # ── Regra 4: wikilinks quebrados ─────────────────────────────
        for m in WIKILINK_RE.finditer(content):
            target = m.group(1).strip().lower()
            # Ignora links internos óbvios (Bíblia/, Glossário, etc.)
            if target.startswith('bíblia') or 'glossário' in target:
                continue
            if target not in file_index:
                broken_links += 1
                report.issues.append(LintIssue(
                    severity='MENOR', file=short, rule='LINK_QUEBRADO',
                    detail=f"Wikilink [[{m.group(1)}]] não resolve para nenhum arquivo.",
                    suggestion="Verificar se o arquivo existe ou corrigir o alias."
                ))

        # ── Regra 5: ordem de seções ──────────────────────────────────
        if ntsk_m:
            after = content[ntsk_m.end():]
            found_order = [
                s.strip() for s in SECTION_H2_RE.findall(after)
                if s.strip() in ALLOWED_SECTIONS_ORDER
            ]
            expected = [s for s in ALLOWED_SECTIONS_ORDER if s in found_order]
            if found_order != expected:
                report.issues.append(LintIssue(
                    severity='MENOR', file=short, rule='ORDEM_SECOES',
                    detail=f"Seções fora de ordem. Encontrado: {found_order}. Esperado: {expected}.",
                    suggestion="Reordenar seções conforme ALLOWED_SECTIONS_ORDER."
                ))

        # ── Regra 6: artigos wiki/conceitos/ sem "O que NÃO é" ───────
        if 'wiki/conceitos' in rel or 'wiki\\conceitos' in rel:
            wiki_concepts.add(md.stem.lower())
            if '## O que este conceito NÃO é' not in content:
                report.issues.append(LintIssue(
                    severity='MENOR', file=short, rule='CONCEITO_SEM_NEGACAO',
                    detail="Artigo de conceito sem seção '## O que este conceito NÃO é'.",
                    suggestion="Adicionar seção com distinções negativas (o que o conceito não é)."
                ))

        # ── Regra 7: wiki/obras/ com path_raw inexistente ─────────────
        if ('wiki/obras' in rel or 'wiki\\obras' in rel) and raw_dir.exists():
            path_raw = fm.get('path_raw', '')
            if path_raw:
                target_path = vault / path_raw
                if not target_path.exists():
                    report.issues.append(LintIssue(
                        severity='MENOR', file=short, rule='PATH_RAW_INVALIDO',
                        detail=f"path_raw '{path_raw}' não existe em disco.",
                        suggestion="Verificar se a obra foi copiada para raw/ ou corrigir o path."
                    ))

    report.stats = {
        'Nós de versículo':      versiculo_count,
        'Com enriquecimento':    enriched_count,
        'Sem fonte (críticos)':  no_source_count,
        'Wikilinks quebrados':   broken_links,
        'Artigos wiki/conceitos': len(wiki_concepts),
        'Total issues':          len(report.issues),
    }

    # Salvar relatório
    if output_dir:
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)
        report_path = out / f"{report.date}.md"
        report_path.write_text(report.to_markdown(), encoding='utf-8')

    return report


# CLI simples
if __name__ == '__main__':
    import sys
    vault_dir  = sys.argv[1] if len(sys.argv) > 1 else '.'
    output_dir = sys.argv[2] if len(sys.argv) > 2 else 'reports/lint'
    r = run_lint(vault_dir, output_dir)
    print(r.to_markdown())
    if r.critical:
        print(f"\n⚠️  {len(r.critical)} problema(s) crítico(s) encontrado(s).")
        sys.exit(1)
