import base64
import json
import re
from io import BytesIO
from typing import Any

import fitz
import httpx
import pdfplumber

from app.config import settings


FIGURE_WORDS = re.compile(
    r"\b(figure|fig\.|diagram|graph|plot|chart|architecture|flowchart|below|above|"
    r"following|image|screenshot|visualize|visualise|drawn)\b",
    re.IGNORECASE,
)


class VisionDocumentError(RuntimeError):
    pass


def _bbox_from_object(obj: dict) -> list[float] | None:
    if all(key in obj for key in ("x0", "top", "x1", "bottom")):
        return [float(obj["x0"]), float(obj["top"]), float(obj["x1"]), float(obj["bottom"])]
    return None


def _bbox_center(bbox: list[float]) -> tuple[float, float]:
    return ((bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2)


def _center_inside(inner: list[float], outer: list[float]) -> bool:
    x, y = _bbox_center(inner)
    return outer[0] <= x <= outer[2] and outer[1] <= y <= outer[3]


def _in_header_or_footer(bbox: list[float], page_height: float, margin_ratio: float = 0.1) -> bool:
    _, y = _bbox_center(bbox)
    top_limit = page_height * margin_ratio
    bottom_limit = page_height * (1 - margin_ratio)
    return y <= top_limit or y >= bottom_limit


def _inside_any_table(bbox: list[float], table_bboxes: list[list[float]]) -> bool:
    return any(_center_inside(bbox, table_bbox) for table_bbox in table_bboxes)


def _sort_key_from_bbox(bbox: list[float] | None) -> tuple[float, float]:
    if not bbox:
        return (999999.0, 999999.0)
    return (round(float(bbox[1]), 1), round(float(bbox[0]), 1))


def _body_objects(page: Any, objects: list[dict], table_bboxes: list[list[float]]) -> list[dict]:
    kept = []
    for obj in objects:
        bbox = _bbox_from_object(obj)
        if bbox is None:
            continue
        if _in_header_or_footer(bbox, float(page.height)):
            continue
        if _inside_any_table(bbox, table_bboxes):
            continue
        kept.append(obj)
    return kept


def _extract_text_blocks(page: Any, table_bboxes: list[list[float]], y_tolerance: float = 4.0) -> list[dict]:
    """
    Extract positioned text lines in top-to-bottom, left-to-right order.
    Text inside detected table regions is skipped because tables are emitted as
    their own structured blocks.
    """
    words = []
    for word in page.extract_words(use_text_flow=False) or []:
        bbox = [
            float(word["x0"]),
            float(word["top"]),
            float(word["x1"]),
            float(word["bottom"]),
        ]
        if _inside_any_table(bbox, table_bboxes):
            continue
        words.append({**word, "bbox": bbox})

    words = sorted(words, key=lambda item: (float(item["top"]), float(item["x0"])))
    lines: list[list[dict]] = []
    for word in words:
        if not lines:
            lines.append([word])
            continue

        current_line = lines[-1]
        current_top = sum(float(item["top"]) for item in current_line) / len(current_line)
        if abs(float(word["top"]) - current_top) <= y_tolerance:
            current_line.append(word)
        else:
            lines.append([word])

    blocks = []
    for line_index, line in enumerate(lines, start=1):
        ordered_line = sorted(line, key=lambda item: float(item["x0"]))
        text = " ".join(item["text"] for item in ordered_line).strip()
        if not text:
            continue

        bbox = [
            min(item["bbox"][0] for item in ordered_line),
            min(item["bbox"][1] for item in ordered_line),
            max(item["bbox"][2] for item in ordered_line),
            max(item["bbox"][3] for item in ordered_line),
        ]
        blocks.append(
            {
                "id": f"p{page.page_number}_text_{line_index}",
                "type": "text",
                "bbox": bbox,
                "content": text,
            }
        )

    return blocks


def _table_rows(table: Any) -> list[list[str]]:
    rows = table.extract() or []
    return [[cell.strip() if cell else "" for cell in row] for row in rows]


def _table_quality(rows: list[list[str]]) -> str:
    if not rows:
        return "empty"
    non_empty = sum(1 for row in rows for cell in row if cell)
    cell_count = sum(len(row) for row in rows)
    if cell_count == 0:
        return "empty"
    fill_ratio = non_empty / cell_count
    if len(rows) >= 2 and fill_ratio >= 0.4:
        return "good"
    return "weak"


def extract_pdf_layout(file_bytes: bytes) -> dict:
    """
    Extract page text, tables, geometry signals, and VLM need scores.
    Coordinates use PDF points with origin near the top-left, matching pdfplumber.
    """
    pages = []
    with pdfplumber.open(BytesIO(file_bytes)) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            tables = []
            table_bboxes = []
            for table_index, table in enumerate(page.find_tables(), start=1):
                bbox = [float(value) for value in table.bbox]
                rows = _table_rows(table)
                table_bboxes.append(bbox)
                tables.append(
                    {
                        "id": f"p{page_number}_t{table_index}",
                        "type": "table",
                        "order": table_index,
                        "bbox": bbox,
                        "rows": rows,
                        "quality": _table_quality(rows),
                    }
                )

            text_blocks = _extract_text_blocks(page, table_bboxes)
            body_images = _body_objects(page, page.images, table_bboxes)
            body_lines = _body_objects(page, page.lines, table_bboxes)
            body_rects = _body_objects(page, page.rects, table_bboxes)
            body_curves = _body_objects(page, page.curves, table_bboxes)
            figure_word_hits = len(FIGURE_WORDS.findall(text))
            weak_tables = sum(1 for table in tables if table["quality"] != "good")
            geometry_count = len(body_lines) + len(body_rects) + len(body_curves)
            low_text_high_geometry = len(text.strip()) < 250 and geometry_count > 0

            visual_score = (
                len(body_images) * 5
                + len(body_curves) * 3
                + min(geometry_count, 20)
                + figure_word_hits * 4
                + weak_tables * 2
                + (6 if low_text_high_geometry else 0)
            )

            needs_vlm = bool(
                body_images
                or body_curves
                or figure_word_hits
                or weak_tables
                or low_text_high_geometry
                or geometry_count > 0
            )

            pages.append(
                {
                    "page": page_number,
                    "width": float(page.width),
                    "height": float(page.height),
                    "text": text,
                    "text_blocks": text_blocks,
                    "tables": tables,
                    "layout_signals": {
                        "body_images": len(body_images),
                        "body_lines": len(body_lines),
                        "body_rects": len(body_rects),
                        "body_curves": len(body_curves),
                        "figure_word_hits": figure_word_hits,
                        "weak_tables": weak_tables,
                        "visual_score": visual_score,
                        "needs_vlm": needs_vlm,
                    },
                }
            )
    return {"pages": pages}


def _vlm_mode(mode: str | None = None) -> str:
    selected = (mode or settings.vlm_mode or "auto").lower()
    if selected not in {"fast", "auto", "rich"}:
        raise VisionDocumentError("VLM mode must be one of: fast, auto, rich")
    return selected


def select_vlm_pages(layout: dict, mode: str | None = None, max_pages: int | None = None) -> list[int]:
    selected_mode = _vlm_mode(mode)
    if selected_mode == "fast":
        return []

    pages = layout["pages"]
    if selected_mode == "rich":
        selected = pages
    else:
        selected = [
            page for page in pages
            if page["layout_signals"]["needs_vlm"]
        ]
        selected = sorted(
            selected,
            key=lambda page: page["layout_signals"]["visual_score"],
            reverse=True,
        )

    page_limit = max_pages if max_pages is not None else settings.vlm_max_pages
    return [page["page"] for page in selected[:page_limit]]


def render_pdf_pages(file_bytes: bytes, page_numbers: list[int], dpi: int = 150) -> list[dict]:
    rendered = []
    pdf = fitz.open(stream=file_bytes, filetype="pdf")
    try:
        for page_number in page_numbers:
            page = pdf.load_page(page_number - 1)
            pixmap = page.get_pixmap(dpi=dpi, alpha=False)
            image_bytes = pixmap.tobytes("png")
            rendered.append(
                {
                    "page": page_number,
                    "mime_type": "image/png",
                    "base64": base64.b64encode(image_bytes).decode("ascii"),
                }
            )
    finally:
        pdf.close()
    return rendered


def _parse_json_object(content: str) -> dict:
    cleaned = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL).strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?", "", cleaned).strip()
        cleaned = re.sub(r"```$", "", cleaned).strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise
        return json.loads(cleaned[start : end + 1])


def _vlm_url() -> str:
    base_url = settings.vlm_base_url or settings.llm_base_url
    return base_url.rstrip("/") + "/chat/completions"


def _vlm_api_key() -> str:
    return settings.vlm_api_key or settings.llm_api_key


def _vlm_model_name() -> str:
    return settings.vlm_model_name or settings.model_name


def describe_pdf_page_images(
    rendered_pages: list[dict],
    layout_pages: list[dict],
    batch_size: int | None = None,
) -> dict:
    """
    Ask an OpenAI-compatible VLM to describe diagrams, plots, charts, figures,
    and visual context in small page batches.
    """
    if not rendered_pages:
        return {"pages": []}
    if not _vlm_api_key():
        raise VisionDocumentError("VLM_API_KEY or LLM_API_KEY is not configured")
    if not _vlm_model_name():
        raise VisionDocumentError("VLM_MODEL_NAME or MODEL_NAME is not configured")

    layout_by_page = {page["page"]: page for page in layout_pages}
    page_batch_size = batch_size or settings.vlm_pages_per_batch
    described_pages = []

    for start in range(0, len(rendered_pages), page_batch_size):
        batch = rendered_pages[start : start + page_batch_size]
        layout_excerpt = [
            {
                "page": item["page"],
                "text_excerpt": (layout_by_page[item["page"]]["text"] or "")[:1800],
                "tables": [
                    {
                        "id": table["id"],
                        "bbox": table["bbox"],
                        "quality": table["quality"],
                        "rows_preview": table["rows"][:4],
                    }
                    for table in layout_by_page[item["page"]]["tables"][:4]
                ],
                "layout_signals": layout_by_page[item["page"]]["layout_signals"],
            }
            for item in batch
        ]

        content: list[dict] = [
            {
                "type": "text",
                "text": (
                    "Analyze the attached PDF page images for visual information only. "
                    "Return valid JSON. Describe diagrams, graphs, plots, charts, equations, "
                    "screenshots, and visually meaningful layouts. Ignore logos, headers, "
                    "footers, page numbers, and decorative lines. If a visible table is already "
                    "represented in the provided table data, only add visual notes when the table "
                    "meaning cannot be recovered from text. Coordinates may be approximate.\n\n"
                    "Required JSON shape:\n"
                    '{"pages":[{"page":1,"visuals":[{"visual_type":"plot|graph_diagram|'
                    'architecture_diagram|equation|screenshot|image|table_like_visual|other",'
                    '"approx_bbox":[x1,y1,x2,y2],"nearby_text":"",'
                    '"description":"","structured_data":{},"question_relevance":""}]}]}\n\n'
                    f"Text/table/layout context:\n{json.dumps(layout_excerpt, ensure_ascii=False)}"
                ),
            }
        ]
        for page in batch:
            content.append({"type": "text", "text": f"Rendered image for PDF page {page['page']}:"})
            content.append(
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{page['mime_type']};base64,{page['base64']}"
                    },
                }
            )

        response = httpx.post(
            _vlm_url(),
            headers={
                "Authorization": f"Bearer {_vlm_api_key()}",
                "Content-Type": "application/json",
            },
            json={
                "model": _vlm_model_name(),
                "messages": [{"role": "user", "content": content}],
                "temperature": 0.1,
            },
            timeout=90,
        )
        if response.status_code >= 400:
            raise VisionDocumentError(
                f"VLM request failed with HTTP {response.status_code}: {response.text[:300]}"
            )

        parsed = _parse_json_object(response.json()["choices"][0]["message"]["content"])
        described_pages.extend(parsed.get("pages", []))

    return {"pages": described_pages}


def ordered_page_blocks(layout_page: dict, visual_page: dict | None = None) -> list[dict]:
    blocks = []
    blocks.extend(layout_page.get("text_blocks", []))

    for table in layout_page.get("tables", []):
        blocks.append(table)

    for index, visual in enumerate((visual_page or {}).get("visuals", []), start=1):
        blocks.append(
            {
                "id": f"p{layout_page['page']}_v{index}",
                "type": "visual",
                "bbox": visual.get("approx_bbox"),
                **visual,
            }
        )

    ordered_blocks = sorted(
        blocks,
        key=lambda block: _sort_key_from_bbox(block.get("bbox") or block.get("approx_bbox")),
    )
    for order, block in enumerate(ordered_blocks, start=1):
        block["order"] = order
    return ordered_blocks


def extract_rich_pdf_document(
    file_bytes: bytes,
    object_key: str | None = None,
    mode: str | None = None,
) -> dict:
    """
    Build an ordered document JSON with text, tables, and optional VLM visuals.
    """
    layout = extract_pdf_layout(file_bytes)
    page_numbers = select_vlm_pages(layout, mode=mode)
    rendered_pages = render_pdf_pages(file_bytes, page_numbers) if page_numbers else []
    visual_result = describe_pdf_page_images(rendered_pages, layout["pages"]) if rendered_pages else {"pages": []}
    visuals_by_page = {page["page"]: page for page in visual_result["pages"]}

    pages = []
    for layout_page in layout["pages"]:
        pages.append(
            {
                "page": layout_page["page"],
                "width": layout_page["width"],
                "height": layout_page["height"],
                "layout_signals": layout_page["layout_signals"],
                "blocks": ordered_page_blocks(
                    layout_page,
                    visuals_by_page.get(layout_page["page"]),
                ),
            }
        )

    return {
        "document_type": "pdf",
        "object_key": object_key,
        "vlm_mode": _vlm_mode(mode),
        "vlm_pages": page_numbers,
        "pages": pages,
    }
