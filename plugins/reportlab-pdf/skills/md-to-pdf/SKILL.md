---
name: md-to-pdf
description: >
  Convert markdown files (or markdown text) into styled, multi-page PDFs using
  mistune for parsing and ReportLab Platypus for layout. Use this skill whenever
  the user has markdown as input and wants a PDF as output — e.g. "render this
  README as a PDF", "convert notes.md to PDF", "make a printable PDF from this
  markdown". The skill copies a self-contained, customisable script into the
  user's project, adds dependencies if needed, and runs it. For PDFs built
  programmatically from structured data (CVs, invoices, reports from a dict or
  JSON), use the `reportlab-pdf` skill instead. Trigger on: ".md to PDF",
  "markdown to PDF", "convert markdown", "render this README as PDF",
  "print this markdown".
---

# Markdown to PDF

## When to use

Use this skill when the source is **markdown** — a `.md` file, a markdown
string, or pasted markdown text — and the output is a styled PDF. The skill
ships `md_to_pdf.py`, a self-contained renderer that handles ATX headings,
paragraphs, nested bullet/ordered lists, fenced code blocks, blockquotes,
horizontal rules, and inline bold / italic / code / links.

For PDFs assembled programmatically from data — a CV from a dict, an invoice
from line items, a report from query results — use the `reportlab-pdf` skill
instead. That skill teaches the Platypus API directly so you can control
layout flowable-by-flowable.

## Setup procedure

When triggered, do this in order:

1. **Detect project type.** Walk up from the user's input file looking for
   `pyproject.toml` (uv-managed), `requirements.txt` (pip-managed), or
   neither (ad-hoc).

2. **Pick a destination path** for `md_to_pdf.py`:
   - If `scripts/` exists, use `scripts/md_to_pdf.py`.
   - Else if any of `internals/scripts/`, `tools/`, `bin/` exists, use that.
   - Else create `scripts/` and use `scripts/md_to_pdf.py`.
   - If multiple candidates exist, ask the user.

3. **Copy the script verbatim** from this skill's
   `scripts/md_to_pdf.py` to the chosen destination. Do not edit it on
   the way through — future updates need to be a clean copy-over.

4. **Add dependencies** if the project will use them long-term:
   - uv project: `uv add mistune reportlab`
   - pip project: `uv pip install mistune reportlab`
   - Skip if both are already declared.

   If the user only wants a one-shot conversion, you may skip step 4 — the
   script's PEP 723 inline metadata makes
   `uv run --no-project scripts/md_to_pdf.py input.md` self-contained.

5. **Run the script** on the user's input:

   ```bash
   uv run scripts/md_to_pdf.py input.md -o output.pdf
   ```

   Report the output path back to the user.

## Public API

`md_to_pdf.py` exposes (full docstrings in the file):

- `write_pdf(source, output=None, *, page_size, margins_mm, palette, options)`
  — read a markdown file, write a styled PDF, return the output path.
- `render_markdown(md_text, *, styles, palette, options)` — parse markdown
  text and return a list of Platypus `Flowable`s for embedding into a larger
  document.
- `PlatypusRenderer` — walks a mistune AST and emits Flowables; subclass to
  customise output.
- `Palette` — colour palette with fields `dark`, `accent`, `grey`, `rule`,
  `code_bg`, `link`.
- `RenderOptions` — per-render switches (`show_link_urls`, `max_list_depth`).
- `build_default_styles(palette)` — produce the default stylesheet.

## CLI options

```text
python md_to_pdf.py input.md [-o output.pdf]
                             [--show-link-urls]
                             [--page-size {a4,letter}]
                             [--margins-mm 20]
```

## Customisation

Most users only need a colour change. Pass a custom `Palette`:

```python
from pathlib import Path
from reportlab.lib.colors import HexColor
from md_to_pdf import Palette, write_pdf

write_pdf(
    Path("input.md"),
    Path("output.pdf"),
    palette=Palette(accent=HexColor("#B22222")),
)
```

For style-level changes (font sizes, leading, indentation), call
`build_default_styles(palette)`, mutate the returned `StyleSheet1`, and
pass it to `render_markdown(..., styles=...)`.

For deeper changes (custom block types, frontmatter handling, table
support), subclass `PlatypusRenderer` and override the relevant
`_block_<type>` or `_inline_<type>` methods.

## Limitations

The script does **not** support tables, images, footnotes, or definition
lists. Don't promise these to the user. Tokens of an unknown type fall
back to a plain paragraph rather than crashing.

Raw HTML embedded in markdown is **not** passed through — mistune is
configured without the HTML plugin. If the user needs HTML pass-through,
this skill is the wrong tool.

## Pitfalls

- Mistune handles markdown escaping correctly — you don't need to escape
  `&`, `<`, `>`, or `'` in the markdown source the way you would in raw
  ReportLab paragraph text.
- Helvetica lacks Unicode subscript/superscript glyphs (e.g. `₂`, `²`);
  these render as black boxes in the PDF. The script does not currently
  translate them. Warn the user if their markdown contains these.
- The script writes to `source.with_suffix(".pdf")` by default. Pass `-o`
  to override.
