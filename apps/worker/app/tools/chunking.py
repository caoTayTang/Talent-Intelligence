import re

MAX_CHUNK_CHARS = 1400
SECTION_ALIASES = {
    "summary": "summary",
    "profile": "summary",
    "objective": "summary",
    "skills": "skills",
    "technical skills": "skills",
    "experience": "experience",
    "work experience": "experience",
    "employment": "experience",
    "projects": "projects",
    "project": "projects",
    "education": "education",
    "certifications": "certifications",
    "certification": "certifications",
    "awards": "awards",
}
ITEMIZED_SECTIONS = {"experience", "projects", "education", "certifications", "awards"}
ITEM_START_PATTERN = re.compile(r"^(?:[-*]\s+|\d+[.)]\s+)")


def normalize_space(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def detect_section(line: str, current: str) -> str:
    candidate = line.strip().lower().rstrip(":")
    if candidate.startswith("#"):
        candidate = candidate.lstrip("#").strip().rstrip(":")
    if len(candidate) > 40:
        return current

    return SECTION_ALIASES.get(candidate, current)


def extract_subsection_title(line: str) -> str:
    title = ITEM_START_PATTERN.sub("", line).strip(" -:|")
    title = re.split(r"\s[-|:]\s", title, maxsplit=1)[0].strip()
    return title[:100]


def split_long_text(text: str, max_chars: int = MAX_CHUNK_CHARS) -> list[str]:
    paragraphs = [p.strip() for p in re.split(r"\n{2,}", text) if p.strip()]
    chunks: list[str] = []
    current = ""

    for paragraph in paragraphs or [text]:
        paragraph = paragraph.strip()
        if not paragraph:
            continue

        if len(current) + len(paragraph) + 2 <= max_chars:
            current = f"{current}\n\n{paragraph}".strip()
            continue

        if current:
            chunks.append(current)
            current = ""

        while len(paragraph) > max_chars:
            chunks.append(paragraph[:max_chars].strip())
            paragraph = paragraph[max_chars:].strip()

        current = paragraph

    if current:
        chunks.append(current)

    return chunks


def split_itemized_block(section_name: str, lines: list[str]) -> list[tuple[str | None, str]]:
    if section_name not in ITEMIZED_SECTIONS:
        return [(None, "\n".join(lines).strip())]

    items: list[tuple[str | None, list[str]]] = []
    current_title: str | None = None
    current_lines: list[str] = []

    def flush() -> None:
        nonlocal current_title, current_lines
        text = "\n".join(current_lines).strip()
        if text:
            items.append((current_title, current_lines))
        current_title = None
        current_lines = []

    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue

        starts_item = bool(ITEM_START_PATTERN.match(line))
        has_inline_title_delimiter = bool(re.search(r"\s[-|:]\s", line))
        looks_heading = (
            not starts_item
            and len(line) <= 140
            and len(line.split()) <= 16
            and (not line.endswith(".") or has_inline_title_delimiter)
        )

        if starts_item or looks_heading:
            if current_lines:
                flush()
            current_title = extract_subsection_title(line)
            current_lines.append(line)
            continue

        current_lines.append(line)

    flush()
    if not items:
        return [(None, "\n".join(lines).strip())]

    return [(title, "\n".join(item_lines).strip()) for title, item_lines in items]


def chunk_document(text: str, source: str) -> list[dict]:
    """
    Split parsed CV/JD text into section-labeled chunks for embedding.
    """
    cleaned = text.strip()
    if not cleaned:
        return []

    section = "other"
    section_blocks: list[tuple[str, list[str]]] = [(section, [])]

    for raw_line in cleaned.splitlines():
        line = raw_line.strip()
        if not line:
            if section_blocks[-1][1]:
                section_blocks[-1][1].append("")
            continue

        next_section = detect_section(line, section)
        if next_section != section:
            section = next_section
            section_blocks.append((section, []))
            continue

        section_blocks[-1][1].append(line)

    chunks: list[dict] = []
    for section_name, lines in section_blocks:
        blocks = split_itemized_block(section_name, lines)
        for subsection, block in blocks:
            if not block:
                continue

            for part_index, chunk_text in enumerate(split_long_text(block), start=1):
                normalized = normalize_space(chunk_text)
                if not normalized:
                    continue
                chunks.append(
                    {
                        "source": source,
                        "section": section_name,
                        "text": normalized,
                        "metadata": {"part": part_index, "subsection": subsection},
                    }
                )

    return chunks

