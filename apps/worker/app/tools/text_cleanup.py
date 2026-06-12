import re

URL_PLACEHOLDER = "__URL_PLACEHOLDER_{}__"


def clean_document_text(text: str) -> str:
    """
    Normalize parsed PDF/DOCX text while preserving URLs and section boundaries.
    """
    if not text:
        return ""

    urls: list[str] = []

    def stash_url(match: re.Match) -> str:
        urls.append(match.group(0))
        return URL_PLACEHOLDER.format(len(urls) - 1)

    cleaned = re.sub(r"https?://\S+|(?:github|linkedin)\.com/\S+", stash_url, text)
    cleaned = cleaned.replace("\u00a0", " ")
    cleaned = cleaned.replace("•", "-")
    cleaned = cleaned.replace("–", "-").replace("—", "-")
    cleaned = re.sub(r"([A-Za-z])-\s+([A-Za-z])", r"\1\2", cleaned)
    cleaned = re.sub(r"[ \t]+", " ", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    cleaned = "\n".join(line.strip() for line in cleaned.splitlines())

    for index, url in enumerate(urls):
        cleaned = cleaned.replace(URL_PLACEHOLDER.format(index), url.rstrip(".,;)]"))

    return cleaned.strip()
