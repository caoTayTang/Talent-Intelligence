import re

from app.tools.llm import LLMError, chat_json
from app.tools.scoring import extract_skills
from app.tools.web_search import extract_public_urls

SECTION_PATTERN = re.compile(r"^#{0,3}\s*([A-Za-z][A-Za-z /&+-]{1,40}):?$")
ITEM_START_PATTERN = re.compile(r"^(?:[-*]\s+|\d+[.)]\s+)")
DATE_RANGE_PATTERN = re.compile(
    r"((?:20\d{2}|19\d{2})\s*(?:-|to)\s*(?:present|current|20\d{2}|19\d{2}))",
    re.IGNORECASE,
)


def sectionize(text: str) -> dict[str, list[str]]:
    sections: dict[str, list[str]] = {"other": []}
    active = "other"
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        match = SECTION_PATTERN.match(line.strip("# "))
        if match and len(line.split()) <= 6:
            active = match.group(1).strip().lower()
            sections.setdefault(active, [])
            continue
        sections.setdefault(active, []).append(line)
    return sections


def split_items(lines: list[str]) -> list[str]:
    items: list[str] = []
    current: list[str] = []

    def flush() -> None:
        nonlocal current
        text = " ".join(current).strip()
        if text:
            items.append(text)
        current = []

    for line in lines:
        starts_item = bool(ITEM_START_PATTERN.match(line))
        looks_heading = (
            not starts_item
            and len(line) <= 140
            and len(line.split()) <= 16
            and not line.endswith(".")
        )
        if starts_item or looks_heading:
            if current:
                flush()
            current = [line]
            continue
        current.append(line)
    flush()
    return items


def clean_item_title(text: str) -> str:
    title = ITEM_START_PATTERN.sub("", text).strip()
    title = re.split(r"\s[-|:]\s", title, maxsplit=1)[0].strip()
    title = DATE_RANGE_PATTERN.sub("", title).strip(" -|:")
    return title[:100]


def extract_date_range(text: str) -> str | None:
    match = DATE_RANGE_PATTERN.search(text)
    return match.group(1) if match else None


def deterministic_cv_profile(cv_text: str) -> dict:
    sections = sectionize(cv_text)
    links = [
        {"type": item.get("kind", "other"), "url": item.get("label")}
        for item in extract_public_urls(cv_text)
    ]
    skills = extract_skills(cv_text)

    project_lines = sections.get("projects", []) + sections.get("project", [])
    experience_lines = (
        sections.get("experience", [])
        + sections.get("work experience", [])
        + sections.get("employment", [])
    )

    projects = []
    for item in split_items(project_lines):
        projects.append(
            {
                "name": clean_item_title(item),
                "date_range": extract_date_range(item),
                "description": item,
                "skills": extract_skills(item),
                "links": [link for link in links if link.get("url") and link["url"] in item],
            }
        )

    experience = []
    for item in split_items(experience_lines):
        parts = re.split(r"\s[-|:]\s", item, maxsplit=1)
        company_title = parts[0].strip()
        experience.append(
            {
                "company": clean_item_title(company_title),
                "title": None,
                "date_range": extract_date_range(item),
                "description": item,
                "skills": extract_skills(item),
            }
        )

    return {
        "candidate_name": None,
        "links": links,
        "skills": skills,
        "projects": projects,
        "experience": experience,
        "education": split_items(sections.get("education", [])),
        "raw_claims": projects + experience,
        "extraction_source": "deterministic",
    }


def llm_refine_cv_profile(cv_text: str, fallback_profile: dict) -> dict:
    prompt = {
        "task": "Refine a parsed CV profile. Return JSON only. Preserve facts from the CV; do not invent.",
        "schema": {
            "candidate_name": None,
            "links": [{"type": "github|linkedin|portfolio|other", "url": "..."}],
            "skills": ["..."],
            "projects": [
                {
                    "name": "...",
                    "date_range": None,
                    "description": "...",
                    "skills": ["..."],
                    "links": [],
                }
            ],
            "experience": [
                {
                    "company": "...",
                    "title": None,
                    "date_range": None,
                    "description": "...",
                    "skills": ["..."],
                }
            ],
            "education": [],
            "raw_claims": [],
        },
        "fallback_profile": fallback_profile,
        "cv_excerpt": cv_text[:7000],
    }
    refined = chat_json(
        [
            {"role": "system", "content": "Return a valid JSON object only."},
            {"role": "user", "content": str(prompt)},
        ],
        temperature=0.0,
    )
    for key, value in fallback_profile.items():
        refined.setdefault(key, value)
    refined["extraction_source"] = "llm_refined"
    return refined


def extract_cv_profile(cv_text: str) -> tuple[dict, str | None]:
    fallback = deterministic_cv_profile(cv_text)
    try:
        return llm_refine_cv_profile(cv_text, fallback), None
    except (LLMError, Exception) as exc:
        fallback["extraction_source"] = "deterministic_fallback"
        return fallback, str(exc)
