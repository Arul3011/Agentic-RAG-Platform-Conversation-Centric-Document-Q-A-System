from typing import List, Dict, Any
from app.core.logging import get_logger

logger = get_logger(__name__)


def _extract_with_ocr(path: str) -> List[Dict[str, Any]]:
    """Extract text from scanned/image-based PDFs using OCR."""
    import pytesseract
    from pdf2image import convert_from_path

    pages = []
    images = convert_from_path(path, dpi=300)
    logger.info(f"OCR: converted PDF to {len(images)} images")

    for i, img in enumerate(images, start=1):
        text = pytesseract.image_to_string(img) or ""
        char_count = len(text.strip())
        logger.debug(f"OCR Page {i}: {char_count} characters extracted")
        pages.append({"page_number": i, "text": text.strip()})

    return pages


def _extract_with_pdfplumber(path: str) -> List[Dict[str, Any]]:
    """Try extracting text using pdfplumber (more robust)."""
    import pdfplumber

    pages = []
    with pdfplumber.open(path) as pdf:
        logger.info(f"pdfplumber: opened PDF with {len(pdf.pages)} pages")
        for i, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            # Also try extracting tables if no text found
            if not text.strip():
                tables = page.extract_tables()
                if tables:
                    text = "\n".join(
                        " | ".join(str(cell or "") for cell in row)
                        for table in tables
                        for row in table
                    )
            char_count = len(text.strip())
            logger.debug(f"Page {i}: {char_count} characters extracted")
            pages.append({"page_number": i, "text": text.strip()})
    return pages


def _extract_with_pypdf(path: str) -> List[Dict[str, Any]]:
    """Fallback: extract using pypdf."""
    import pypdf

    pages = []
    with open(path, "rb") as f:
        reader = pypdf.PdfReader(f)
        logger.info(f"pypdf: opened PDF with {len(reader.pages)} pages")
        for i, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            char_count = len(text.strip())
            logger.debug(f"Page {i}: {char_count} characters extracted")
            pages.append({"page_number": i, "text": text.strip()})
    return pages


def extract_pdf(path: str) -> List[Dict[str, Any]]:
    """Return list of {page_number, text} dicts. Tries pdfplumber first, falls back to pypdf."""
    logger.info(f"Starting PDF extraction: {path}")

    try:
        pages = _extract_with_pdfplumber(path)
        total_chars = sum(len(p["text"]) for p in pages)
        non_empty = sum(1 for p in pages if p["text"])

        if total_chars > 10:
            logger.info(
                f"PDF extracted (pdfplumber): {len(pages)} pages, "
                f"{non_empty} pages with text, {total_chars} total characters"
            )
            return pages

        logger.warning(
            f"pdfplumber extracted only {total_chars} chars from {len(pages)} pages, "
            f"trying pypdf fallback"
        )
    except Exception as e:
        logger.warning(f"pdfplumber failed: {e}, trying pypdf fallback")

    try:
        pages = _extract_with_pypdf(path)
        total_chars = sum(len(p["text"]) for p in pages)
        non_empty = sum(1 for p in pages if p["text"])

        logger.info(
            f"PDF extracted (pypdf fallback): {len(pages)} pages, "
            f"{non_empty} pages with text, {total_chars} total characters"
        )

        if total_chars > 10:
            return pages
    except Exception as e:
        logger.warning(f"pypdf failed: {e}, trying OCR fallback")

    try:
        logger.info("Attempting OCR extraction for scanned/image-based PDF...")
        pages = _extract_with_ocr(path)
        total_chars = sum(len(p["text"]) for p in pages)
        non_empty = sum(1 for p in pages if p["text"])

        logger.info(
            f"PDF extracted (OCR): {len(pages)} pages, "
            f"{non_empty} pages with text, {total_chars} total characters"
        )

        if total_chars < 10:
            logger.warning(
                f"OCR extraction yielded minimal text. "
                f"The PDF may be empty or password-protected."
            )

        return pages
    except ImportError:
        logger.error(
            "OCR dependencies not installed. "
            "Install with: pip install pytesseract pdf2image "
            "and install Tesseract OCR engine on your system."
        )
        # Return empty pages so pipeline can continue
        return pages if "pages" in dir() else [{"page_number": 1, "text": ""}]
    except Exception as e:
        logger.error(f"OCR extraction failed: {e}")
        raise
