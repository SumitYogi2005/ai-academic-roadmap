"""
Document text extraction service.
Handles PDF (text + scanned), DOCX, and image files.
"""
from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


# ── PDF extraction ────────────────────────────────────────────────────────────

def extract_text_from_pdf(path: Path) -> str:
    """Extract text from a PDF using PyMuPDF. Falls back to OCR for scanned pages."""
    try:
        import fitz  # PyMuPDF
    except ImportError:
        logger.warning("PyMuPDF not installed – returning empty text for PDF")
        return ""

    text_parts: list[str] = []
    with fitz.open(str(path)) as doc:
        for page_num, page in enumerate(doc, start=1):
            page_text = page.get_text("text").strip()
            if page_text:
                text_parts.append(f"[Page {page_num}]\n{page_text}")
            else:
                # Page appears to be scanned – try OCR
                ocr_text = _ocr_pdf_page(page, page_num)
                if ocr_text:
                    text_parts.append(f"[Page {page_num} - OCR]\n{ocr_text}")
    return "\n\n".join(text_parts)


def _ocr_pdf_page(page, page_num: int) -> str:
    """Render a PDF page to an image and run Tesseract OCR on it."""
    try:
        import pytesseract
        from PIL import Image
        import io

        mat = page.get_pixmap(dpi=200)
        img_bytes = mat.tobytes("png")
        img = Image.open(io.BytesIO(img_bytes))
        return pytesseract.image_to_string(img, lang="eng")
    except Exception as exc:
        logger.debug("OCR failed for PDF page %d: %s", page_num, exc)
        return ""


# ── DOCX extraction ───────────────────────────────────────────────────────────

def extract_text_from_docx(path: Path) -> str:
    """Extract text from a DOCX file using python-docx."""
    try:
        from docx import Document
    except ImportError:
        logger.warning("python-docx not installed – returning empty text for DOCX")
        return ""

    doc = Document(str(path))
    parts: list[str] = []

    for para in doc.paragraphs:
        if para.text.strip():
            parts.append(para.text.strip())

    # Include table content
    for table in doc.tables:
        for row in table.rows:
            row_text = " | ".join(cell.text.strip() for cell in row.cells if cell.text.strip())
            if row_text:
                parts.append(row_text)

    return "\n".join(parts)


# ── Image / scanned extraction ────────────────────────────────────────────────

def extract_text_from_image(path: Path) -> str:
    """Run Tesseract OCR on an image file."""
    try:
        import pytesseract
        from PIL import Image

        img = Image.open(str(path))
        # Convert to RGB if needed (handles PNG with alpha)
        if img.mode not in ("RGB", "L"):
            img = img.convert("RGB")
        return pytesseract.image_to_string(img, lang="eng")
    except ImportError:
        logger.warning("pytesseract / Pillow not installed – returning empty text for image")
        return ""
    except Exception as exc:
        logger.warning("Image OCR failed for %s: %s", path, exc)
        return ""


# ── Text normalisation ────────────────────────────────────────────────────────

_REPEATED_NEWLINES = re.compile(r"\n{3,}")
_TRAILING_WHITESPACE = re.compile(r"[ \t]+\n")


def normalize_text(raw: str) -> str:
    """Clean up raw extraction output for LLM consumption."""
    text = raw
    # Collapse runs of blank lines
    text = _REPEATED_NEWLINES.sub("\n\n", text)
    # Remove trailing whitespace on each line
    text = _TRAILING_WHITESPACE.sub("\n", text)
    # Strip surrounding whitespace
    text = text.strip()
    return text


# ── Dispatcher ────────────────────────────────────────────────────────────────

def extract_text(path: Path, mime_type: str) -> str:
    """
    Choose the right extractor based on *mime_type* and return normalised text.
    """
    mime = mime_type.lower()
    if mime == "application/pdf":
        raw = extract_text_from_pdf(path)
    elif mime == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        raw = extract_text_from_docx(path)
    elif mime.startswith("image/"):
        raw = extract_text_from_image(path)
    else:
        logger.warning("No extractor for MIME type %s – returning empty text", mime)
        raw = ""
    return normalize_text(raw)
