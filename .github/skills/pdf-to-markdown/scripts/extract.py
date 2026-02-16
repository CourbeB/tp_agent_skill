#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "pymupdf>=1.24.0",
#   "pdfplumber>=0.11.0",
# ]
# ///
"""
PDF to Markdown extractor.

Extracts text and tables from a PDF file and converts them to clean Markdown.

Usage:
    uv run scripts/extract.py <pdf_path> [options]

See SKILL.md for full documentation.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def parse_pages(pages_arg: str, total: int) -> list[int]:
    """Parse a page range string like '1-5' or '1,3,5' into a 0-based list."""
    result: set[int] = set()
    for part in pages_arg.split(","):
        part = part.strip()
        if "-" in part:
            start_s, end_s = part.split("-", 1)
            start, end = int(start_s.strip()), int(end_s.strip())
            result.update(range(start - 1, end))  # convert to 0-based
        else:
            result.add(int(part) - 1)
    return sorted(p for p in result if 0 <= p < total)


def bbox_overlap(bbox_a: tuple, bbox_b: tuple, threshold: float = 0.3) -> bool:
    """Return True if two bounding boxes overlap beyond a threshold (ratio of bbox_a area)."""
    ax0, ay0, ax1, ay1 = bbox_a
    bx0, by0, bx1, by1 = bbox_b
    ix0 = max(ax0, bx0)
    iy0 = max(ay0, by0)
    ix1 = min(ax1, bx1)
    iy1 = min(ay1, by1)
    if ix1 <= ix0 or iy1 <= iy0:
        return False
    intersection = (ix1 - ix0) * (iy1 - iy0)
    area_a = (ax1 - ax0) * (ay1 - ay0)
    return area_a > 0 and (intersection / area_a) >= threshold


def clean_cell(value) -> str:
    """Sanitize a table cell value for Markdown output."""
    if value is None:
        return ""
    return str(value).replace("\n", " ").replace("|", "\\|").strip()


def table_to_markdown(table: list[list]) -> str:
    """Convert a pdfplumber table (list of rows) to a Markdown table string."""
    if not table or not table[0]:
        return ""

    # Normalise all rows to the same number of columns
    n_cols = max(len(row) for row in table)
    rows = [[clean_cell(cell) for cell in row] + [""] * (n_cols - len(row)) for row in table]

    header = rows[0]
    separator = ["---"] * n_cols
    body = rows[1:] if len(rows) > 1 else []

    lines = [
        "| " + " | ".join(header) + " |",
        "| " + " | ".join(separator) + " |",
    ]
    for row in body:
        lines.append("| " + " | ".join(row) + " |")

    return "\n".join(lines)


def detect_heading_level(span_size: float, body_size: float) -> int | None:
    """
    Heuristic: map font size ratio to heading level (1-3).
    Returns None if the span is considered body text.
    """
    ratio = span_size / body_size if body_size else 1.0
    if ratio >= 1.6:
        return 1
    if ratio >= 1.35:
        return 2
    if ratio >= 1.15:
        return 3
    return None


# ---------------------------------------------------------------------------
# Core extraction
# ---------------------------------------------------------------------------

def extract_page(
    fitz_page,
    plumber_page,
    use_tables: bool,
    verbose: bool,
) -> str:
    """
    Extract content from a single page and return a Markdown string.

    Strategy:
    1. Use pdfplumber to detect tables and their bounding boxes.
    2. Use pymupdf to get text blocks sorted in reading order.
    3. For each text block, check if it falls inside a table bbox — if so, skip it.
    4. Insert Markdown tables at the position of the first skipped block.
    """
    import fitz  # pymupdf

    page_md_parts: list[tuple[float, str]] = []  # (y_position, markdown_snippet)

    # --- Table extraction via pdfplumber ---
    tables_md: list[tuple[tuple, str]] = []  # (bbox, markdown)
    table_bboxes: list[tuple] = []

    if use_tables and plumber_page is not None:
        for table in plumber_page.extract_tables():
            if not table:
                continue
            md = table_to_markdown(table)
            if not md:
                continue
            # pdfplumber uses top-based coordinates; convert to fitz (bottom-based) if needed
            # Actually both use top-left origin in their default modes; we keep pdfplumber coords.
            bbox = plumber_page.find_tables()[len(table_bboxes)].bbox  # (x0, top, x1, bottom)
            table_bboxes.append(bbox)
            tables_md.append((bbox, md))
            if verbose:
                print(f"    [table] detected at bbox {bbox}")

    # --- Text extraction via pymupdf ---
    body_size = 11.0  # fallback

    # First pass: estimate dominant (body) font size
    size_counts: dict[float, int] = {}
    for block in fitz_page.get_text("dict", flags=fitz.TEXT_PRESERVE_WHITESPACE)["blocks"]:
        if block.get("type") != 0:
            continue
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                s = round(span.get("size", 0), 1)
                size_counts[s] = size_counts.get(s, 0) + len(span.get("text", ""))
    if size_counts:
        body_size = max(size_counts, key=lambda k: size_counts[k])

    # Second pass: build markdown from text blocks
    inserted_tables: set[int] = set()

    for block in fitz_page.get_text("dict", flags=fitz.TEXT_PRESERVE_WHITESPACE)["blocks"]:
        if block.get("type") != 0:  # skip image blocks
            continue

        bx0, by0, bx1, by1 = block["bbox"]
        block_center_y = (by0 + by1) / 2

        # Check if this block is inside a table bbox
        inside_table_idx = None
        for i, (tbbox, _) in enumerate(tables_md):
            tx0, ty0, tx1, ty1 = tbbox
            if bbox_overlap((bx0, by0, bx1, by1), (tx0, ty0, tx1, ty1)):
                inside_table_idx = i
                break

        if inside_table_idx is not None:
            # Insert the table markdown once, at the y-position of its first text block
            if inside_table_idx not in inserted_tables:
                inserted_tables.add(inside_table_idx)
                _, tmd = tables_md[inside_table_idx]
                page_md_parts.append((by0, "\n" + tmd + "\n"))
            continue  # skip text that is part of a table

        # Build markdown for this text block
        block_lines: list[str] = []
        for line in block.get("lines", []):
            line_text_parts: list[str] = []
            dominant_size = body_size

            for span in line.get("spans", []):
                text = span.get("text", "").strip()
                if not text:
                    continue
                size = span.get("size", body_size)
                flags = span.get("flags", 0)
                is_bold = bool(flags & 2**4)
                is_italic = bool(flags & 2**1)

                if is_bold and is_italic:
                    text = f"***{text}***"
                elif is_bold:
                    text = f"**{text}**"
                elif is_italic:
                    text = f"*{text}*"

                dominant_size = size
                line_text_parts.append(text)

            line_text = " ".join(line_text_parts).strip()
            if not line_text:
                continue

            heading_level = detect_heading_level(dominant_size, body_size)
            if heading_level:
                # Strip any bold markers inside headings — headings are already prominent
                clean = line_text.replace("**", "").replace("*", "")
                block_lines.append("#" * heading_level + " " + clean)
            else:
                block_lines.append(line_text)

        if block_lines:
            block_text = "\n".join(block_lines)
            page_md_parts.append((block_center_y, block_text))

    # Append any tables that were not matched to a text block (e.g. image-only pages)
    for i, (_, tmd) in enumerate(tables_md):
        if i not in inserted_tables:
            page_md_parts.append((float("inf"), "\n" + tmd + "\n"))

    # Sort all parts by vertical position
    page_md_parts.sort(key=lambda x: x[0])
    return "\n\n".join(part for _, part in page_md_parts)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract text and tables from a PDF and convert to Markdown.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("pdf_path", type=Path, help="Path to the input PDF file")
    parser.add_argument(
        "--output", "-o", type=Path, default=None,
        help="Output Markdown file path (default: <pdf_name>.md)",
    )
    parser.add_argument(
        "--pages", type=str, default=None,
        help="Pages to extract, e.g. '1-5' or '1,3,5' (default: all)",
    )
    parser.add_argument(
        "--password", type=str, default=None,
        help="Password for encrypted PDFs",
    )
    parser.add_argument(
        "--no-tables", dest="no_tables", action="store_true",
        help="Disable table detection (plain text only)",
    )
    parser.add_argument(
        "--verbose", action="store_true",
        help="Print progress details",
    )

    args = parser.parse_args()

    pdf_path: Path = args.pdf_path.resolve()
    if not pdf_path.exists():
        print(f"Error: file not found: {pdf_path}", file=sys.stderr)
        sys.exit(1)
    if pdf_path.suffix.lower() != ".pdf":
        print(f"Warning: file does not have a .pdf extension: {pdf_path}", file=sys.stderr)

    output_path: Path = args.output or pdf_path.with_suffix(".md")

    # --- Open with pymupdf ---
    try:
        import fitz  # pymupdf
    except ImportError:
        print("Error: pymupdf is not installed. Run: uv run scripts/extract.py ...", file=sys.stderr)
        sys.exit(1)

    try:
        doc = fitz.open(str(pdf_path))
    except Exception as e:
        print(f"Error opening PDF: {e}", file=sys.stderr)
        sys.exit(1)

    if doc.is_encrypted:
        if args.password is None:
            print(
                "Error: PDF is encrypted. Provide the password with --password <PASSWORD>",
                file=sys.stderr,
            )
            sys.exit(1)
        if not doc.authenticate(args.password):
            print("Error: incorrect password.", file=sys.stderr)
            sys.exit(1)

    total_pages = len(doc)
    page_indices = parse_pages(args.pages, total_pages) if args.pages else list(range(total_pages))

    if verbose := args.verbose:
        print(f"PDF: {pdf_path.name}  ({total_pages} pages total)")
        print(f"Extracting pages: {[p + 1 for p in page_indices]}")
        print(f"Table detection: {'disabled' if args.no_tables else 'enabled'}")

    # --- Open with pdfplumber (for tables) ---
    plumber_doc = None
    if not args.no_tables:
        try:
            import pdfplumber
            plumber_doc = pdfplumber.open(str(pdf_path), password=args.password or "")
        except Exception as e:
            print(f"Warning: could not open PDF with pdfplumber ({e}). Tables will be skipped.", file=sys.stderr)

    # --- Extract pages ---
    md_pages: list[str] = []
    scanned_pages: list[int] = []

    for idx in page_indices:
        fitz_page = doc.load_page(idx)
        plumber_page = plumber_doc.pages[idx] if plumber_doc else None

        if verbose:
            print(f"  Processing page {idx + 1}/{total_pages}...")

        # Detect scanned (image-only) pages
        text_check = fitz_page.get_text("text").strip()
        if not text_check:
            scanned_pages.append(idx + 1)
            md_pages.append(f"# Page {idx + 1}\n\n> ⚠️ This page appears to be a scanned image with no selectable text. Consider using `ocrmypdf` to add a text layer before extraction.")
            continue

        page_md = extract_page(
            fitz_page=fitz_page,
            plumber_page=plumber_page,
            use_tables=not args.no_tables,
            verbose=verbose,
        )
        md_pages.append(f"# Page {idx + 1}\n\n{page_md}")

    doc.close()
    if plumber_doc:
        plumber_doc.close()

    # --- Write output ---
    output_path.parent.mkdir(parents=True, exist_ok=True)
    full_md = "\n\n---\n\n".join(md_pages)
    output_path.write_text(full_md, encoding="utf-8")

    print(f"\n✅ Done! Markdown written to: {output_path}")
    print(f"   Pages processed : {len(page_indices)}")
    if scanned_pages:
        print(f"   ⚠️  Scanned pages  : {scanned_pages} (no text layer — consider ocrmypdf)")


if __name__ == "__main__":
    main()