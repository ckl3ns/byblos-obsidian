"""Indexador piloto de verbetes baseado em headings."""
from __future__ import annotations

import re
from pathlib import Path

from distillation_models import DistilledEntry, SourceManifestItem


_GENERIC_HEADING_RE = re.compile(r"^[A-Z0-9][A-Z0-9\s'&.,()/:-]{1,}$")
_PAREN_ALIAS_RE = re.compile(r"^\s*([A-Z0-9][A-Z0-9\s'&.,:-]*?)\s*\(([^)]+)\)\s*$")
_SEE_ALSO_RE = re.compile(r"^\s*see\s+also\b[:\s]+(.+)", re.IGNORECASE)
_BIBLIOGRAPHY_RE = re.compile(r"bibliograph", re.IGNORECASE)
_ROMAN_SECTION_RE = re.compile(r"^[IVXLCDM]+\.\s")
_ALPHABET_MARKER_RE = re.compile(r"^[A-Z]$")
_AUTHOR_BYLINE_RE = re.compile(
    r"^(?:[A-Z]\.\s*){1,4}"
    r"(?:[A-Z][A-Z'’`\-]+|VAN|DER|DE|DI|DA|DEL|DU|LA|LE|TEN|TER|DEN|VON|Y|&)"
    r"(?:\s+(?:[A-Z][A-Z'’`\-]+|VAN|DER|DE|DI|DA|DEL|DU|LA|LE|TEN|TER|DEN|VON|Y|&))*$"
)
_ALLOWED_TITLE_PUNCTUATION = set(" '&.,()/;:-")


def index_source_entries(item: SourceManifestItem, text_path: str | Path) -> list[DistilledEntry]:
    path = Path(text_path)
    files = [path] if path.is_file() else sorted(p for p in path.rglob("*.txt") if p.is_file())

    entries: list[DistilledEntry] = []
    for file_path in files:
        if item.sigla == "DDD":
            entries.extend(_index_ddd_text_file(item, file_path))
        else:
            entries.extend(_index_generic_text_file(item, file_path))

    return sorted(entries, key=lambda entry: (entry.raw_path, entry.start_anchor, entry.title))


def _index_generic_text_file(item: SourceManifestItem, file_path: Path) -> list[DistilledEntry]:
    lines = file_path.read_text(encoding="utf-8", errors="replace").splitlines()
    heading_starts = _find_generic_heading_starts(lines)
    if not heading_starts:
        return []

    return _build_entries(item, file_path, lines, heading_starts, _parse_generic_heading)


def _index_ddd_text_file(item: SourceManifestItem, file_path: Path) -> list[DistilledEntry]:
    lines = file_path.read_text(encoding="utf-8", errors="replace").splitlines()
    heading_starts = _find_ddd_heading_starts(lines)
    if not heading_starts:
        return []
    return _build_entries(item, file_path, lines, heading_starts, _parse_ddd_heading)


def _build_entries(
    item: SourceManifestItem,
    file_path: Path,
    lines: list[str],
    heading_starts: list[int],
    parser,
) -> list[DistilledEntry]:
    entries: list[DistilledEntry] = []
    raw_path = _raw_path_for(item, file_path)
    for index, start_line in enumerate(heading_starts):
        end_line = heading_starts[index + 1] - 1 if index + 1 < len(heading_starts) else len(lines)
        block = lines[start_line - 1 : end_line]
        if item.sigla == "DDD":
            block = _trim_ddd_block(block)
        heading_line = block[0].strip()
        title, aliases, heading_see_also = parser(heading_line)
        content_lines = block[1:]
        see_also = _merge_unique(heading_see_also, _extract_see_also(content_lines))
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


def _find_generic_heading_starts(lines: list[str]) -> list[int]:
    starts: list[int] = []
    for line_number, line in enumerate(lines, start=1):
        stripped = line.strip()
        if _looks_like_generic_heading(stripped):
            starts.append(line_number)
    return starts


def _find_ddd_heading_starts(lines: list[str]) -> list[int]:
    lexicon_start = _find_ddd_lexicon_start(lines)
    starts: list[int] = []
    for line_number, line in enumerate(lines, start=1):
        if line_number < lexicon_start:
            continue
        stripped = line.strip()
        if _is_ddd_entry_heading(lines, line_number, stripped):
            starts.append(line_number)
    return starts


def _find_ddd_lexicon_start(lines: list[str]) -> int:
    for index, line in enumerate(lines, start=1):
        if not _is_alphabet_marker(line.strip()):
            continue
        window = [candidate.strip() for candidate in lines[index : index + 12] if candidate.strip()]
        entry_like = [candidate for candidate in window if _looks_like_ddd_heading(candidate)]
        if len(entry_like) >= 2:
            return index + 1
    return 1


def _looks_like_generic_heading(line: str) -> bool:
    if not line:
        return False
    if line.lower().startswith("bibliography"):
        return False
    if _PAREN_ALIAS_RE.match(line):
        return True
    if not _GENERIC_HEADING_RE.match(line):
        return False
    letters = [char for char in line if char.isalpha()]
    return bool(letters) and all(char.isupper() for char in letters)


def _parse_generic_heading(line: str) -> tuple[str, tuple[str, ...], tuple[str, ...]]:
    match = _PAREN_ALIAS_RE.match(line)
    if match:
        title = _normalize_heading_text(match.group(1))
        aliases = tuple(
            alias
            for alias in (_normalize_heading_text(part) for part in re.split(r"[;,/]", match.group(2)))
            if alias and alias != title
        )
        return title, aliases, ()
    return _normalize_heading_text(line), (), ()


def _is_ddd_entry_heading(lines: list[str], line_number: int, line: str) -> bool:
    if not _looks_like_ddd_heading(line):
        return False
    if line_number > 1 and lines[line_number - 2].strip():
        return False

    next_non_empty = _next_non_empty_line(lines, line_number)
    if not next_non_empty:
        return False
    if _looks_like_ddd_redirect_heading(line):
        return _looks_like_ddd_heading(next_non_empty) or _ROMAN_SECTION_RE.match(next_non_empty) is not None
    return _ROMAN_SECTION_RE.match(next_non_empty) is not None


def _looks_like_ddd_heading(line: str) -> bool:
    if not line:
        return False
    if _is_alphabet_marker(line):
        return False
    if _is_author_byline(line):
        return False
    if line.lower().startswith("bibliography"):
        return False
    if _ROMAN_SECTION_RE.match(line):
        return False
    if _looks_like_ddd_redirect_heading(line):
        return True
    return any(character.isalpha() for character in line) and len(line) <= 120


def _parse_ddd_heading(line: str) -> tuple[str, tuple[str, ...], tuple[str, ...]]:
    redirect = _parse_ddd_redirect_heading(line)
    if redirect:
        return redirect

    match = _PAREN_ALIAS_RE.match(line)
    if match:
        title = _normalize_heading_text(match.group(1))
        aliases = tuple(
            alias
            for alias in (_normalize_heading_text(part) for part in re.split(r"[;,/]", match.group(2)))
            if alias and alias != title
        )
        return title, aliases, ()

    title, tail = _split_title_and_tail(line)
    if not title:
        if any(character.isalpha() for character in line):
            return _normalize_heading_text(line), (), ()
        return "", (), ()
    if tail and not _has_ascii_lowercase(tail):
        return _normalize_heading_text(line), (), ()
    aliases = (_normalize_heading_text(tail),) if tail else ()
    return _normalize_heading_text(title), aliases, ()


def _parse_ddd_redirect_heading(line: str) -> tuple[str, tuple[str, ...], tuple[str, ...]] | None:
    if "→" not in line:
        return None
    left, right = (part.strip() for part in line.split("→", maxsplit=1))
    if not left or not right:
        return None

    title, tail = _split_title_and_tail(left)
    if not title:
        title = _normalize_heading_text(left)
    elif tail:
        return None
    targets = tuple(
        candidate
        for candidate in (_normalize_heading_text(part).rstrip(".") for part in re.split(r"[;,/]", right))
        if candidate
    )
    if not targets or any(any("a" <= char <= "z" for char in target) for target in targets):
        return None
    return _normalize_heading_text(title), (), targets


def _split_title_and_tail(line: str) -> tuple[str, str]:
    consumed: list[str] = []
    for character in line:
        if character in _ALLOWED_TITLE_PUNCTUATION or character.isdigit():
            consumed.append(character)
            continue
        if _is_upper_heading_letter(character):
            consumed.append(character)
            continue
        break

    title = "".join(consumed).strip()
    tail = line[len("".join(consumed)) :].strip()
    if not title:
        return "", ""
    if tail and any("a" <= char <= "z" for char in tail):
        return "", ""
    return title, tail


def _is_upper_heading_letter(character: str) -> bool:
    return "A" <= character <= "Z"


def _has_ascii_lowercase(text: str) -> bool:
    return any("a" <= character <= "z" for character in text)


def _looks_like_ddd_redirect_heading(line: str) -> bool:
    return _parse_ddd_redirect_heading(line) is not None


def _next_non_empty_line(lines: list[str], line_number: int) -> str:
    for candidate in lines[line_number:]:
        stripped = candidate.strip()
        if stripped:
            return stripped
    return ""


def _normalize_heading_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip()).upper()


def _extract_see_also(lines: list[str]) -> tuple[str, ...]:
    seen: list[str] = []
    for line in lines:
        match = _SEE_ALSO_RE.search(line)
        if not match:
            continue
        for candidate in re.split(r"[;,/]", match.group(1)):
            cleaned = _normalize_heading_text(candidate).rstrip(".")
            if cleaned and cleaned not in seen:
                seen.append(cleaned)
    return tuple(seen)


def _merge_unique(*groups: tuple[str, ...]) -> tuple[str, ...]:
    merged: list[str] = []
    for group in groups:
        for candidate in group:
            if candidate and candidate not in merged:
                merged.append(candidate)
    return tuple(merged)


def _trim_ddd_block(block: list[str]) -> list[str]:
    trimmed = list(block)
    while trimmed and not trimmed[-1].strip():
        trimmed.pop()
    if len(trimmed) > 1 and _is_author_byline(trimmed[-1].strip()):
        trimmed.pop()
    while trimmed and not trimmed[-1].strip():
        trimmed.pop()
    return trimmed


def _is_alphabet_marker(line: str) -> bool:
    return bool(_ALPHABET_MARKER_RE.match(line))


def _is_author_byline(line: str) -> bool:
    return bool(_AUTHOR_BYLINE_RE.match(line))


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
