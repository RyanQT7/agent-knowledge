# Local research tools

## PDF inspection

Use the lightweight `paper-pdf` command to inspect local academic PDFs. Its source is [`paper_pdf.py`](paper_pdf.py); the user-level launcher is `/home/xieqitong/.local/bin/paper-pdf`.

### Private Python environment

The tool does not alter system Python. It uses:

```text
Python: /usr/bin/python3.10 (3.10.12)
uv: 0.11.33
venv: /home/xieqitong/.local/share/agent-knowledge/venv/
launcher: /home/xieqitong/.local/bin/paper-pdf
```

Installed direct dependencies:

| Package | Version |
| --- | ---: |
| PyMuPDF | 1.28.2 |
| pdfplumber | 0.11.10 |
| Pillow | 12.3.0 |
| beautifulsoup4 | 4.15.0 |
| NumPy | 2.2.6 |
| SciPy | 1.15.3 |
| pandas | 2.3.3 |
| matplotlib | 3.10.9 |

Recreate the environment with the existing user-level `uv`:

```bash
uv venv --python /usr/bin/python3.10 /home/xieqitong/.local/share/agent-knowledge/venv
uv pip install --python /home/xieqitong/.local/share/agent-knowledge/venv/bin/python \
  PyMuPDF==1.28.2 pdfplumber==0.11.10 Pillow==12.3.0 \
  beautifulsoup4==4.15.0 numpy==2.2.6 scipy==1.15.3 \
  pandas==2.3.3 matplotlib==3.10.9
```

If the launcher is missing, recreate it with:

```sh
cat > /home/xieqitong/.local/bin/paper-pdf <<'EOF'
#!/bin/sh
exec /home/xieqitong/.local/share/agent-knowledge/venv/bin/python /home/xieqitong/agent-knowledge/scripts/research/paper_pdf.py "$@"
EOF
chmod 755 /home/xieqitong/.local/bin/paper-pdf
```

### Commands

All page selectors use **1-based physical PDF pages**, not printed page numbers. The output labels retain physical page numbers; after visually checking a page, record its printed number separately when useful.

```bash
/home/xieqitong/.local/bin/paper-pdf info sources/papers/example.pdf
/home/xieqitong/.local/bin/paper-pdf extract sources/papers/example.pdf \
  --pages 2,5-7 --mode layout --format md --output /tmp/example-pages.md
/home/xieqitong/.local/bin/paper-pdf search sources/papers/example.pdf \
  --query 'Figure 3' --context-chars 180
/home/xieqitong/.local/bin/paper-pdf render sources/papers/example.pdf \
  --pages 4,8 --dpi 200 --output-dir /home/xieqitong/.cache/agent-knowledge/paper-pdf/example
/home/xieqitong/.local/bin/paper-pdf render sources/papers/example.pdf \
  --pages 8 --dpi 220 --crop 100,80,510,300
/home/xieqitong/.local/bin/paper-pdf tables sources/papers/example.pdf \
  --pages 8 --backend auto --format json --output /tmp/example-tables.json
```

`extract` accepts `plain` or block-sorted `layout` text, keeps a boundary for each selected page, and supports Markdown or text output. It writes to stdout unless `--output` is supplied. Existing output files are not replaced unless `--force` is explicit.

`render` writes PNG files outside the repository by default under `~/.cache/agent-knowledge/paper-pdf/<pdf-stem>/`. `--crop` coordinates are `x0,y0,x1,y1` in PDF points. Render only the relevant pages; do not render every page by default.

`tables` supports Markdown, JSON, and long-form CSV. `auto` tries PyMuPDF table detection and falls back to pdfplumber if it finds none; `--backend` can select either extractor directly.

### Reading and extraction boundaries

- PyMuPDF handles local PDF metadata, page text, rendering, and image crops; no Poppler dependency is needed here. This server does not have `pdfinfo`, `pdftotext`, or `pdftoppm`.
- Text extraction reads embedded text; it does not OCR scanned pages. Column order, ligatures, equations, footnotes, and table cell order may be wrong. The `layout` mode is a block-order aid, not a promise of perfect two-column reconstruction.
- Automatic table extraction can miss borderless tables or mistake plot axes/legends for table cells. For example, neither extractor recovered NetArena Table 1 reliably, and pdfplumber emitted chart fragments for Figure 3. Treat extraction as a search aid, not the authoritative source.
- For a key score, figure/text contradiction, or ambiguous table, search/extract the relevant page, render it, and inspect the PNG. The current Codex environment exposes a local image viewer; this workflow actually used it on NetArena physical pages 3, 7, and 9. If a future session has no image tool, keep the PNG and open it in VS Code; do not claim visual verification.
- Record both the PDF physical page used by the command and any visible printed page number. Do not silently equate PDF pages with printed pagination.

## Base command availability

Already available and reused: Git 2.34.1, curl 7.81.0, wget 1.21.2, ripgrep 15.2.0, Python 3.10.12, and uv 0.11.33. `jq`, `pdfinfo`, `pdftotext`, and `pdftoppm` are not installed; no system package or Poppler installation was needed.
