---
name: pdf-to-markdown
description: Extracts text and tables from PDF files and converts them to clean Markdown. Use when the user wants to read, parse, convert or extract content from a PDF document, or when working with PDF reports, papers, invoices, or any document in PDF format.
license: Apache-2.0
compatibility: Requires Python 3.11+ and uv (https://docs.astral.sh/uv/). Internet access needed for first-time dependency installation.
metadata:
  author: baptiste
  version: "1.0"
---

# PDF to Markdown

This skill extracts text and tables from PDF files and converts the content to clean, structured Markdown. It uses `pdfplumber` for accurate table detection and `pymupdf` for reliable text extraction.

## Setup

The script uses `uv` with inline dependency metadata — no manual `pip install` needed.

Make sure `uv` is installed:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Usage

```bash
uv run scripts/extract.py <path-to-pdf> [options]
```

### Arguments

| Argument | Description |
|---|---|
| `pdf_path` | Path to the input PDF file (required) |
| `--output`, `-o` | Output `.md` file path. Defaults to `<pdf_name>.md` next to the PDF |
| `--pages` | Page range to extract, e.g. `1-5` or `2,4,7`. Default: all pages |
| `--no-tables` | Disable table detection (faster, plain text only) |
| `--verbose` | Print progress details |

### Examples

```bash
# Convert full PDF to Markdown
uv run scripts/extract.py report.pdf

# Convert with custom output path
uv run scripts/extract.py report.pdf --output output/report.md

# Extract only pages 1 to 10
uv run scripts/extract.py report.pdf --pages 1-10

# Extract specific pages
uv run scripts/extract.py report.pdf --pages 1,3,5

# Skip table detection
uv run scripts/extract.py report.pdf --no-tables
```

## How it works

1. **Text extraction** — `pymupdf` extracts text block by block, preserving reading order and detecting headings by font size.
2. **Table detection** — `pdfplumber` identifies table regions per page and renders them as Markdown tables (`| col | col |`).
3. **Merge** — Text and tables are merged in page order. Table regions in the text stream are replaced by the Markdown table to avoid duplication.
4. **Output** — A single `.md` file is written with page separators (`---`) between pages.

## Output format

```markdown
# Page 1

Some extracted paragraph text here...

| Column A | Column B | Column C |
|----------|----------|----------|
| value 1  | value 2  | value 3  |

More text after the table...

---

# Page 2

...
```

## Common edge cases

- **Scanned PDFs** (image-only): the script detects when a page has no selectable text and warns the user. For OCR, point them to `ocrmypdf` as a pre-processing step.
- **Multi-column layouts**: text blocks are sorted left-to-right, top-to-bottom. Complex multi-column PDFs may require manual review.
- **Password-protected PDFs**: the script exits with a clear error message asking the user to provide the password via `--password`.
- **Large PDFs**: use `--pages` to process in chunks if memory is a concern.

## Script location

`scripts/extract.py`