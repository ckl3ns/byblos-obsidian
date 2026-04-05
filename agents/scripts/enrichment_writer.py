"""enrichment_writer.py
Appenda seções de enriquecimento em nós de versículo do vault.
Regras absolutas (espelho do AGENTS.md):
  - NUNCA modifica frontmatter, textos KJV/BKJ, breadcrumb ou navegação
  - NUNCA escreve afirmação factual sem [Fonte: ... | Obra: ... | Nível: N]
  - NUNCA coloca inferência fora da seção "Lacunas Identificadas"
  - Seções são adicionadas APENAS após o bloco NTSK
  - Seções seguem ordem obrigatória definida em ALLOWED_SECTIONS
"""
import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional


ALLOWED_SECTIONS = [
    "Léxico",
    "Contexto Histórico-Cultural",
    "Posições Exegéticas",
    "Conexões no Grafo",
    "Lacunas Identificadas",
]

SOURCE_TAG_RE   = re.compile(r'\[Fonte:\s*.+?\|\s*Obra:\s*.+?\|\s*Nível:\s*[1-5]\]')
INFERENCE_RE    = re.compile(r'\[INFERÊNCIA DO AGENTE\]')
NTSK_BLOCK_RE   = re.compile(
    r'(##\s+🔗\s+\*\*Referências Cruzadas \(NTSK\)\*\*\s*\n\n`.*?`\s*\n\n\[\[Glossário do NTSK\]\])',
    re.DOTALL
)
EXISTING_ENRICH = re.compile(r'^##\s+(Léxico|Contexto|Posições|Conexões|Lacunas)', re.MULTILINE)


@dataclass
class EnrichmentSection:
    title: str        # deve estar em ALLOWED_SECTIONS
    content: str      # conteúdo Markdown da seção


class EnrichmentValidationError(Exception):
    pass


def validate_section(section: EnrichmentSection) -> list[str]:
    """Retorna lista de erros de validação (vazia = ok)."""
    errors = []

    if section.title not in ALLOWED_SECTIONS:
        errors.append(
            f"Seção '{section.title}' não permitida. "
            f"Permitidas: {ALLOWED_SECTIONS}"
        )

    # Seções factuais (não-Lacunas) devem ter pelo menos uma tag de fonte
    if section.title != "Lacunas Identificadas":
        if section.content.strip() and not SOURCE_TAG_RE.search(section.content):
            errors.append(
                f"Seção '{section.title}' contém conteúdo sem "
                f"[Fonte: ... | Obra: ... | Nível: N]. Adicione proveniência."
            )

    # Inferências fora de Lacunas são proibidas
    if section.title != "Lacunas Identificadas":
        if INFERENCE_RE.search(section.content):
            errors.append(
                f"[INFERÊNCIA DO AGENTE] encontrada em '{section.title}'. "
                f"Inferências só podem estar em 'Lacunas Identificadas'."
            )

    return errors


def append_enrichment(
    file_path: str | Path,
    sections: list[EnrichmentSection],
    dry_run: bool = False,
) -> dict:
    """
    Appenda seções ao nó. Retorna dict com resultado.
    dry_run=True: valida e retorna diff sem gravar.
    """
    path = Path(file_path)
    content = path.read_text(encoding='utf-8')
    result = {
        'file': str(path),
        'success': False,
        'errors': [],
        'warnings': [],
        'sections_added': [],
        'sections_skipped': [],
        'diff_preview': '',
    }

    # Verificar que é um nó de versículo (tem bloco NTSK)
    if not NTSK_BLOCK_RE.search(content):
        result['errors'].append(
            "Arquivo não contém bloco NTSK. "
            "Enriquecimento só é permitido em nós de versículo."
        )
        return result

    # Detectar seções já existentes
    existing = set(EXISTING_ENRICH.findall(content))

    # Validar e filtrar seções
    sections_to_add = []
    for sec in sections:
        # Verificar se já existe
        if any(sec.title.startswith(e) for e in existing):
            result['sections_skipped'].append(sec.title)
            result['warnings'].append(
                f"Seção '{sec.title}' já existe — ignorada (use update_section para editar)."
            )
            continue

        errs = validate_section(sec)
        if errs:
            result['errors'].extend(errs)
        else:
            sections_to_add.append(sec)

    if result['errors']:
        return result

    if not sections_to_add:
        result['success'] = True
        result['warnings'].append("Nenhuma seção nova para adicionar.")
        return result

    # Ordenar seções pela ordem obrigatória
    order_map = {s: i for i, s in enumerate(ALLOWED_SECTIONS)}
    sections_to_add.sort(key=lambda s: order_map.get(s.title, 99))

    # Montar bloco a adicionar
    new_block = "\n\n" + "\n\n".join(
        f"## {s.title}\n\n{s.content.strip()}"
        for s in sections_to_add
    )

    new_content = content.rstrip() + new_block + "\n"
    result['diff_preview'] = new_block
    result['sections_added'] = [s.title for s in sections_to_add]

    if not dry_run:
        path.write_text(new_content, encoding='utf-8')

    result['success'] = True
    return result


def update_section(
    file_path: str | Path,
    section: EnrichmentSection,
    dry_run: bool = False,
) -> dict:
    """Atualiza uma seção de enriquecimento já existente."""
    path = Path(file_path)
    content = path.read_text(encoding='utf-8')

    errs = validate_section(section)
    if errs:
        return {'success': False, 'errors': errs}

    # Regex para encontrar e substituir a seção existente
    sec_re = re.compile(
        rf'^(##\s+{re.escape(section.title)})\s*\n(.*?)(?=^##\s|\Z)',
        re.MULTILINE | re.DOTALL
    )
    match = sec_re.search(content)
    if not match:
        return {'success': False, 'errors': [f"Seção '{section.title}' não encontrada."]}

    new_content = sec_re.sub(
        f"## {section.title}\n\n{section.content.strip()}\n\n",
        content
    )

    if not dry_run:
        path.write_text(new_content, encoding='utf-8')

    return {
        'success': True,
        'errors': [],
        'section_updated': section.title,
        'file': str(path),
    }
