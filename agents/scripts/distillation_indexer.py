"""Indexador piloto de verbetes baseado em headings."""
from __future__ import annotations

import re
from pathlib import Path

from distillation_models import DistilledEntry, SourceManifestItem


_HEADING_RE = re.compile(r"^[A-Z0-9][A-Z0-9\s'&.,()/:-]{1,}$")
_PAREN_ALIAS_RE = re.compile(r"^\s*([A-Z0-9][A-Z0-9\s'&.,:-]*?)\s*\(([^)]+)\)\s*$")
_SEE_ALSO_RE = re.compile(r"see also[:\s]+(.+)", re.IGNORECASE)
_BIBLIOGRAPHY_RE = re.compile(r"bibliograph", re.IGNORECASE)


def index_source_entries(item: SourceManifestItem, text_path: str | Path) -> list[DistilledEntry]:
    path = Path(text_path)
    files = [path] if path.is_file() else sorted(p for p in path.rglob("*.txt") if p.is_file())

    entries: list[DistilledEntry] = []
    for file_path in files:
        entries.extend(_index_text_file(item, file_path))

    return sorted(entries, key=lambda entry: (entry.raw_path, entry.start_anchor, entry.title))


def _index_text_file(item: SourceManifestItem, file_path: Path) -> list[DistilledEntry]:
    lines = file_path.read_text(encoding="utf-8", errors="replace").splitlines()
    heading_starts = _find_heading_starts(lines)
    if not heading_starts:
        return []

    entries: list[DistilledEntry] = []
    raw_path = _raw_path_for(item, file_path)
    for index, start_line in enumerate(heading_starts):
        end_line = heading_starts[index + 1] - 1 if index + 1 < len(heading_starts) else len(lines)
        block = lines[start_line - 1 : end_line]
        heading_line = block[0].strip()
        title, aliases = _parse_heading(heading_line)
        content_lines = block[1:]
        see_also = _extract_see_also(content_lines)
        bibliography_present = any(_BIBLIOGRAPHY_RE.search(line) for line in block)
        confidence = _score_entry(heading_line, aliases, see_also, bibliography_present, content_lines)

        entries.append(
            DistilledEntry(
                unit_id=f"{item.sigla}:{_slugify(title)}",
                unit_type=_infer_unit_type(item, title),
                title=title,
                aliases=aliases,
                sigla=item.sigla,
                nivel=item.nivel,
                independence_group=item.independence_group,
                tradition=item.tradition,
                target_surface=item.target_surface,
                target_domain=item.target_domain,
                raw_path=raw_path,
                start_anchor=start_line,
                end_anchor=end_line,
                see_also=see_also,
                bibliography_present=bibliography_present,
                confidence=confidence,
                content="\n".join(block).strip(),
            )
        )

    return entries


def _find_heading_starts(lines: list[str]) -> list[int]:
    starts: list[int] = []
    for line_number, line in enumerate(lines, start=1):
        stripped = line.strip()
        if _looks_like_heading(stripped):
            starts.append(line_number)
    return starts


def _looks_like_heading(line: str) -> bool:
    if not line:
        return False
    if line.lower().startswith("bibliography"):
        return False
    if _PAREN_ALIAS_RE.match(line):
        return True
    if not _HEADING_RE.match(line):
        return False
    letters = [char for char in line if char.isalpha()]
    return bool(letters) and all(char.isupper() for char in letters)


def _parse_heading(line: str) -> tuple[str, tuple[str, ...]]:
    match = _PAREN_ALIAS_RE.match(line)
    if match:
        title = _normalize_heading_text(match.group(1))
        aliases = tuple(
            alias
            for alias in (_normalize_heading_text(part) for part in re.split(r"[;,/]", match.group(2)))
            if alias and alias != title
        )
        return title, aliases
    return _normalize_heading_text(line), ()


def _normalize_heading_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip()).upper()


def _extract_see_also(lines: list[str]) -> tuple[str, ...]:
    seen: list[str] = []
    for line in lines:
        match = _SEE_ALSO_RE.search(line)
        if not match:
            continue
        for candidate in re.split(r"[;,]", match.group(1)):
            cleaned = _normalize_heading_text(candidate).rstrip(".")
            if cleaned and cleaned not in seen:
                seen.append(cleaned)
    return tuple(seen)


def _score_entry(
    heading_line: str,
    aliases: tuple[str, ...],
    see_also: tuple[str, ...],
    bibliography_present: bool,
    content_lines: list[str],
) -> float:
    score = 0.5
    if heading_line.isupper():
        score += 0.15
    if aliases:
        score += 0.1
    if see_also:
        score += 0.1
    if bibliography_present:
        score += 0.1
    if any(line.strip() for line in content_lines):
        score += 0.05
    return min(score, 0.99)


def _infer_unit_type(item: SourceManifestItem, title: str) -> str:
    if "altar" in title.lower():
        return "historical_context"
    return item.expected_unit_types[0]


def _slugify(text: str) -> str:
    return re.sub(r"[^A-Z0-9]+", "-", text.upper()).strip("-") or "ENTRY"


def _raw_path_for(item: SourceManifestItem, file_path: Path) -> str:
    item_parts = Path(item.path).parts
    path_parts = file_path.parts
    for start in range(len(path_parts) - len(item_parts) + 1):
        if path_parts[start : start + len(item_parts)] == item_parts:
            return Path(*path_parts[start:]).as_posix()
    return file_path.as_posix().replace("\\", "/")
