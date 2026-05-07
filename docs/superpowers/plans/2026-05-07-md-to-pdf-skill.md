# `md-to-pdf` Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a new `md-to-pdf` skill alongside the existing `reportlab-pdf` skill in the same plugin. The skill ships a self-contained markdown-to-PDF script (mistune + ReportLab Platypus) that Claude copies into the user's project and invokes when triggered.

**Architecture:** Two skills under one plugin. The new skill bundles `md_to_pdf.py` (lifted from `~/Documents/Projects/Job Hunting 2026-04/internals/scripts/md_to_pdf.py`) plus PEP 723 inline metadata so it can run via `uv run` without project-level deps. The existing `reportlab-pdf` skill gains a one-line cross-reference so the two cooperate on triggers. The plugin's manifest, README, and the marketplace manifest are updated to describe both skills. Plugin version 1.0.0 → 1.1.0.

**Tech Stack:** Python 3.10+, `uv` for dependency / runner management, `mistune` 3.x, `reportlab` 4.x, Claude Code plugin / skill format (`SKILL.md` with YAML frontmatter, `plugin.json`, marketplace `marketplace.json`).

**Working branch:** `add-md-to-pdf-skill` (already created and contains the design spec).

**Spec:** `docs/superpowers/specs/2026-05-07-md-to-pdf-skill-design.md`

**Source script (canonical input):** `/Users/robin/Documents/Projects/Job Hunting 2026-04/internals/scripts/md_to_pdf.py` (413 lines).

---

## File Structure

After this plan completes, the plugin tree looks like:

```
plugins/reportlab-pdf/
├── .claude-plugin/
│   └── plugin.json                    # MODIFIED — version 1.1.0, description
├── README.md                           # MODIFIED — add md-to-pdf section
└── skills/
    ├── reportlab-pdf/
    │   └── SKILL.md                    # MODIFIED — cross-reference note
    └── md-to-pdf/                      # NEW
        ├── SKILL.md                    # NEW
        └── scripts/
            └── md_to_pdf.py            # NEW (lifted, with PEP 723 header)
```

Top-level files modified:

```
.claude-plugin/marketplace.json         # MODIFIED — reportlab-pdf entry
README.md                               # MODIFIED — table row description
```

Each file has one clear responsibility:
- `scripts/md_to_pdf.py` — the conversion logic. Self-contained, no project-internal imports.
- `md-to-pdf/SKILL.md` — instructions for Claude on when, how, and where to use the script.
- `reportlab-pdf/SKILL.md` — instructions for direct Platypus use (existing); gains one cross-reference paragraph.
- `plugin.json`, plugin `README.md` — plugin-level metadata and human docs.
- `marketplace.json`, top-level `README.md` — marketplace-level metadata and human docs.

---

## Task 1: Bundle the script with PEP 723 metadata

Lift `md_to_pdf.py` into the skill, prepend a PEP 723 inline metadata block so `uv run` can resolve dependencies without a project, and verify it produces a PDF from a sample markdown input.

**Files:**
- Create: `plugins/reportlab-pdf/skills/md-to-pdf/scripts/md_to_pdf.py`
- Source: `/Users/robin/Documents/Projects/Job Hunting 2026-04/internals/scripts/md_to_pdf.py`

- [ ] **Step 1: Write the failing smoke test (a sample fixture + expected command)**

Create a fixture markdown file in `/tmp/` for the smoke test:

```bash
cat > /tmp/md_to_pdf_smoke.md <<'EOF'
# Smoke Test

A short paragraph with **bold**, *italic*, `code`, and a [link](https://example.com).

## Lists

- top-level item
  - nested item
    - deeper nested item
- second top-level

1. ordered one
2. ordered two

## Code

```python
def hello():
    return "world"
```

> A blockquote line.

---

End of fixture.
EOF
```

- [ ] **Step 2: Run the smoke test and confirm it fails**

```bash
cd /Users/robin/code/github/yo61/claude-skills
uv run --no-project plugins/reportlab-pdf/skills/md-to-pdf/scripts/md_to_pdf.py /tmp/md_to_pdf_smoke.md -o /tmp/md_to_pdf_smoke.pdf
```

Expected: FAIL with "No such file or directory" (script does not exist yet).

- [ ] **Step 3: Create the script directory**

```bash
mkdir -p /Users/robin/code/github/yo61/claude-skills/plugins/reportlab-pdf/skills/md-to-pdf/scripts
```

- [ ] **Step 4: Copy the source script verbatim**

```bash
cp "/Users/robin/Documents/Projects/Job Hunting 2026-04/internals/scripts/md_to_pdf.py" \
   /Users/robin/code/github/yo61/claude-skills/plugins/reportlab-pdf/skills/md-to-pdf/scripts/md_to_pdf.py
```

Verify identical:

```bash
diff "/Users/robin/Documents/Projects/Job Hunting 2026-04/internals/scripts/md_to_pdf.py" \
     /Users/robin/code/github/yo61/claude-skills/plugins/reportlab-pdf/skills/md-to-pdf/scripts/md_to_pdf.py
```

Expected: no output (files identical).

- [ ] **Step 5: Prepend PEP 723 inline metadata**

Edit `plugins/reportlab-pdf/skills/md-to-pdf/scripts/md_to_pdf.py` and insert this block as the very first lines of the file, before the existing module docstring:

```python
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "mistune>=3.0",
#     "reportlab>=4.0",
# ]
# ///
```

The file should now begin:

```python
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "mistune>=3.0",
#     "reportlab>=4.0",
# ]
# ///
"""Convert markdown to PDF using mistune (parsing) and ReportLab Platypus (layout).
...
```

- [ ] **Step 6: Run the smoke test and confirm it now passes**

```bash
uv run --no-project /Users/robin/code/github/yo61/claude-skills/plugins/reportlab-pdf/skills/md-to-pdf/scripts/md_to_pdf.py /tmp/md_to_pdf_smoke.md -o /tmp/md_to_pdf_smoke.pdf
```

Expected: prints `Wrote /tmp/md_to_pdf_smoke.pdf`. Then:

```bash
test -s /tmp/md_to_pdf_smoke.pdf && file /tmp/md_to_pdf_smoke.pdf
```

Expected: file exists, non-zero size, output contains `PDF document`.

- [ ] **Step 7: Optional — visually inspect the PDF**

```bash
open /tmp/md_to_pdf_smoke.pdf
```

Expected: heading, lists with nesting, code block, blockquote, horizontal rule, link all rendered.

- [ ] **Step 8: Clean up the fixture**

```bash
rm /tmp/md_to_pdf_smoke.md /tmp/md_to_pdf_smoke.pdf
```

- [ ] **Step 9: Commit**

```bash
cd /Users/robin/code/github/yo61/claude-skills
git add plugins/reportlab-pdf/skills/md-to-pdf/scripts/md_to_pdf.py
git commit -m "Bundle md_to_pdf.py script with PEP 723 metadata"
```

---

## Task 2: Write the new skill's SKILL.md

Author the instructional document Claude reads when the skill triggers. The frontmatter description controls trigger matching; the body teaches the setup procedure, public API, customisation, and limitations.

**Files:**
- Create: `plugins/reportlab-pdf/skills/md-to-pdf/SKILL.md`

- [ ] **Step 1: Write the SKILL.md file**

Create `plugins/reportlab-pdf/skills/md-to-pdf/SKILL.md` with this exact content:

````markdown
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
````

- [ ] **Step 2: Sanity-check the YAML frontmatter parses**

```bash
cd /Users/robin/code/github/yo61/claude-skills
uv run --no-project --with pyyaml python -c "
import yaml, pathlib
text = pathlib.Path('plugins/reportlab-pdf/skills/md-to-pdf/SKILL.md').read_text()
front = text.split('---', 2)[1]
data = yaml.safe_load(front)
assert data['name'] == 'md-to-pdf', data
assert 'markdown' in data['description'].lower()
print('frontmatter OK:', data['name'])
"
```

Expected: prints `frontmatter OK: md-to-pdf`.

- [ ] **Step 3: Commit**

```bash
git add plugins/reportlab-pdf/skills/md-to-pdf/SKILL.md
git commit -m "Add SKILL.md for md-to-pdf"
```

---

## Task 3: Add cross-reference to the existing reportlab-pdf SKILL.md

Insert one paragraph in the existing skill's "When to use this skill" section so it points users with markdown input at the new skill, and tightens its own scope to programmatic / data-driven generation.

**Files:**
- Modify: `plugins/reportlab-pdf/skills/reportlab-pdf/SKILL.md` (around line 19–24, the existing "When to use this skill" section)

- [ ] **Step 1: Read the section to confirm current text**

The current section (lines ~19–24 of `plugins/reportlab-pdf/skills/reportlab-pdf/SKILL.md`) reads:

```markdown
## When to use this skill

Use ReportLab Platypus when you need to **create** a PDF from structured content — CVs, reports, letters, invoices, or any document where you control the layout programmatically. Platypus handles pagination automatically, flowing content across pages without manual page breaks.

This skill is *not* for manipulating existing PDFs (use pypdf), extracting text (use pdfplumber), or filling forms (use pdf-lib). If you need those, use the built-in `pdf` skill instead.
```

- [ ] **Step 2: Insert a cross-reference paragraph**

After the second paragraph (the one starting "This skill is *not* for manipulating existing PDFs"), append a third paragraph so the section reads:

```markdown
## When to use this skill

Use ReportLab Platypus when you need to **create** a PDF from structured content — CVs, reports, letters, invoices, or any document where you control the layout programmatically. Platypus handles pagination automatically, flowing content across pages without manual page breaks.

This skill is *not* for manipulating existing PDFs (use pypdf), extracting text (use pdfplumber), or filling forms (use pdf-lib). If you need those, use the built-in `pdf` skill instead.

If the source is **markdown** (a `.md` file, a markdown string, or pasted markdown text) and the user wants a styled PDF, prefer the `md-to-pdf` skill in this plugin — it ships an end-to-end renderer (mistune + Platypus) and handles parsing, styling, and pagination for you. Use this skill directly when you're building PDFs programmatically from data (a dict, JSON, query results) and need fine-grained layout control beyond what markdown can express.
```

- [ ] **Step 3: Commit**

```bash
git add plugins/reportlab-pdf/skills/reportlab-pdf/SKILL.md
git commit -m "Cross-reference md-to-pdf from reportlab-pdf SKILL.md"
```

---

## Task 4: Update the plugin manifest and plugin README

Bump the plugin version, refresh the description, and document the new skill in the plugin's README so the human-facing entry points reflect the two-skill structure.

**Files:**
- Modify: `plugins/reportlab-pdf/.claude-plugin/plugin.json`
- Modify: `plugins/reportlab-pdf/README.md`

- [ ] **Step 1: Update `plugin.json`**

Replace the entire content of `plugins/reportlab-pdf/.claude-plugin/plugin.json` with:

```json
{
  "name": "reportlab-pdf",
  "version": "1.1.0",
  "description": "ReportLab-based PDF generation. Includes the reportlab-pdf skill (programmatic Platypus PDFs) and the md-to-pdf skill (markdown files → styled PDFs via mistune + Platypus).",
  "author": {
    "name": "Robin Bowes",
    "email": "robin@yo61.com"
  },
  "license": "MIT",
  "homepage": "https://github.com/yo61/claude-skills",
  "repository": "https://github.com/yo61/claude-skills"
}
```

- [ ] **Step 2: Verify the JSON parses**

```bash
cd /Users/robin/code/github/yo61/claude-skills
python -c "
import json, pathlib
data = json.loads(pathlib.Path('plugins/reportlab-pdf/.claude-plugin/plugin.json').read_text())
assert data['version'] == '1.1.0', data
assert 'md-to-pdf' in data['description']
print('plugin.json OK:', data['version'])
"
```

Expected: prints `plugin.json OK: 1.1.0`.

- [ ] **Step 3: Replace the plugin README**

Replace the entire content of `plugins/reportlab-pdf/README.md` with:

````markdown
# reportlab-pdf

A Claude Code plugin for generating PDFs with Python's
[ReportLab](https://www.reportlab.com/) library and its
[Platypus](https://docs.reportlab.com/reportlab/userguide/ch5_platypus/)
layout engine. The plugin contains two skills:

| Skill | Purpose |
| ----- | ------- |
| `reportlab-pdf` | Programmatic PDF generation — Claude writes ReportLab code directly to lay out a CV, invoice, report, or letter from structured data. |
| `md-to-pdf` | Markdown → PDF — Claude copies a self-contained renderer (mistune + Platypus) into your project and converts a `.md` file to a styled PDF. |

## When each skill triggers

- `md-to-pdf` triggers on **markdown input or markdown intent** —
  `.md` files, pasted markdown, phrases like "convert markdown to PDF" or
  "render this README as a PDF".
- `reportlab-pdf` triggers on **programmatic PDF generation** — phrases
  like "build a PDF CV", "generate a PDF invoice from this data",
  "make a PDF report from this JSON".

## Scope

This plugin covers **creating** PDFs from structured content (markdown or
data). It does **not** cover reading, merging, splitting, or form-filling
existing PDFs; for those, use Claude Code's built-in `pdf` skill.

## Installation

From the [`yo61/claude-skills`](https://github.com/yo61/claude-skills)
marketplace:

```text
/plugin marketplace add yo61/claude-skills
/plugin install reportlab-pdf@yo61-skills
```

ReportLab and (for `md-to-pdf`) mistune are installed per the user's
Python tooling. Following the project's standards, prefer `uv`:

```bash
uv add reportlab mistune          # in a uv project
uv pip install reportlab mistune  # ad-hoc / no project
```

For one-shot markdown conversions, you can skip installation entirely —
the bundled `md_to_pdf.py` carries
[PEP 723](https://peps.python.org/pep-0723/) inline metadata and runs
under `uv run --no-project`.

## What's in the plugin

```
reportlab-pdf/
├── .claude-plugin/
│   └── plugin.json
├── README.md
└── skills/
    ├── reportlab-pdf/
    │   └── SKILL.md
    └── md-to-pdf/
        ├── SKILL.md
        └── scripts/
            └── md_to_pdf.py
```

## License

[MIT](../../LICENSE)
````

- [ ] **Step 4: Commit**

```bash
git add plugins/reportlab-pdf/.claude-plugin/plugin.json plugins/reportlab-pdf/README.md
git commit -m "Bump reportlab-pdf plugin to 1.1.0 and document md-to-pdf"
```

---

## Task 5: Update marketplace.json

Refresh the `reportlab-pdf` entry in the top-level marketplace manifest to reflect the new version, expanded scope, and additional keywords.

**Files:**
- Modify: `.claude-plugin/marketplace.json`

- [ ] **Step 1: Read current entry**

Confirm the current `reportlab-pdf` block in `.claude-plugin/marketplace.json` matches what was observed during planning:

```json
{
  "name": "reportlab-pdf",
  "source": "./plugins/reportlab-pdf",
  "description": "Generate professional, multi-page PDF documents using Python's ReportLab Platypus layout engine.",
  "version": "1.0.0",
  "category": "document-generation",
  "keywords": [
    "pdf",
    "reportlab",
    "platypus",
    "document",
    "cv",
    "report",
    "letter",
    "invoice",
    "typography"
  ]
}
```

- [ ] **Step 2: Replace the block**

Replace the `reportlab-pdf` block in `.claude-plugin/marketplace.json` with:

```json
{
  "name": "reportlab-pdf",
  "source": "./plugins/reportlab-pdf",
  "description": "ReportLab-based PDF generation. Two skills: programmatic Platypus PDFs (CVs, invoices, reports) and a markdown-to-PDF renderer (mistune + Platypus).",
  "version": "1.1.0",
  "category": "document-generation",
  "keywords": [
    "pdf",
    "reportlab",
    "platypus",
    "markdown",
    "mistune",
    "md-to-pdf",
    "document",
    "cv",
    "report",
    "letter",
    "invoice",
    "typography"
  ]
}
```

Leave the `contributory-factors` block untouched.

- [ ] **Step 3: Verify the JSON parses and the version moved**

```bash
python -c "
import json, pathlib
data = json.loads(pathlib.Path('.claude-plugin/marketplace.json').read_text())
entry = next(p for p in data['plugins'] if p['name'] == 'reportlab-pdf')
assert entry['version'] == '1.1.0', entry
assert 'markdown' in entry['keywords']
assert 'mistune' in entry['keywords']
print('marketplace OK:', entry['version'])
"
```

Expected: prints `marketplace OK: 1.1.0`.

- [ ] **Step 4: Commit**

```bash
git add .claude-plugin/marketplace.json
git commit -m "Update marketplace entry for reportlab-pdf 1.1.0"
```

---

## Task 6: Update top-level README

Refresh the description in the marketplace's top-level README so the plugins table reflects both skills.

**Files:**
- Modify: `README.md` (the table row for `reportlab-pdf`)

- [ ] **Step 1: Replace the reportlab-pdf row**

In `README.md`, locate the table row:

```markdown
| [`reportlab-pdf`](plugins/reportlab-pdf) | Generate professional, multi-page PDF documents using Python's ReportLab Platypus layout engine. |
```

Replace it with:

```markdown
| [`reportlab-pdf`](plugins/reportlab-pdf) | ReportLab-based PDF generation. Two skills: programmatic Platypus PDFs (CVs, invoices, reports) and markdown-to-PDF (`md-to-pdf`, via mistune + Platypus). |
```

Leave the `contributory-factors` row and the rest of the README untouched.

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "Document md-to-pdf skill in top-level README"
```

---

## Task 7: End-to-end verification

Run a clean smoke test against the now-bundled script using the same path Claude would use after install, and verify the JSON manifests are still well-formed as a set.

- [ ] **Step 1: Re-create the smoke fixture**

```bash
cat > /tmp/md_to_pdf_e2e.md <<'EOF'
# End-to-End Verification

This document exercises every supported markdown construct.

## Inline formatting

A paragraph with **bold**, *italic*, `inline code`, and a
[link to example](https://example.com).

## Lists

- top-level
  - nested
    - deeper
- second

1. ordered one
2. ordered two

## Code block

```python
from md_to_pdf import write_pdf
write_pdf(Path("input.md"), Path("output.pdf"))
```

## Blockquote

> Mistune handles markdown escaping correctly &
> you don't need to escape ampersands.

---

End.
EOF
```

- [ ] **Step 2: Run via the bundled path**

```bash
cd /Users/robin/code/github/yo61/claude-skills
uv run --no-project plugins/reportlab-pdf/skills/md-to-pdf/scripts/md_to_pdf.py /tmp/md_to_pdf_e2e.md -o /tmp/md_to_pdf_e2e.pdf
test -s /tmp/md_to_pdf_e2e.pdf && file /tmp/md_to_pdf_e2e.pdf
```

Expected: prints `Wrote /tmp/md_to_pdf_e2e.pdf`; `file` reports `PDF document, version 1.x`.

- [ ] **Step 3: Verify all manifests parse together**

```bash
python -c "
import json, pathlib
root = pathlib.Path('.')
mp = json.loads((root / '.claude-plugin/marketplace.json').read_text())
plugin = json.loads((root / 'plugins/reportlab-pdf/.claude-plugin/plugin.json').read_text())
mp_entry = next(p for p in mp['plugins'] if p['name'] == 'reportlab-pdf')
assert mp_entry['version'] == plugin['version'] == '1.1.0', (mp_entry, plugin)
print('versions aligned:', plugin['version'])
"
```

Expected: prints `versions aligned: 1.1.0`.

- [ ] **Step 4: Verify the SKILL.md files are present and frontmatter is valid**

```bash
uv run --no-project --with pyyaml python <<'PY'
import yaml, pathlib
for path in [
    "plugins/reportlab-pdf/skills/reportlab-pdf/SKILL.md",
    "plugins/reportlab-pdf/skills/md-to-pdf/SKILL.md",
]:
    text = pathlib.Path(path).read_text()
    front = text.split("---", 2)[1]
    data = yaml.safe_load(front)
    print(path, "->", data["name"])
PY
```

Expected: two lines, ending in `-> reportlab-pdf` and `-> md-to-pdf` respectively.

- [ ] **Step 5: Confirm git working tree is clean**

```bash
git status
git log --oneline add-md-to-pdf-skill ^main
```

Expected: working tree clean; six new commits on top of the design-spec commit (one per implementation task).

- [ ] **Step 6: Clean up fixtures**

```bash
rm /tmp/md_to_pdf_e2e.md /tmp/md_to_pdf_e2e.pdf
```

- [ ] **Step 7: Push the branch and open a PR**

Confirm with the user before pushing. If approved:

```bash
git push -u origin add-md-to-pdf-skill
gh pr create --title "Add md-to-pdf skill alongside reportlab-pdf" --body "$(cat <<'EOF'
## Summary
- Adds a new `md-to-pdf` skill in the `reportlab-pdf` plugin that ships a self-contained markdown-to-PDF script (mistune + Platypus) with PEP 723 inline metadata.
- Updates the existing `reportlab-pdf` skill with a cross-reference so the two skills cooperate on triggers.
- Bumps plugin version to 1.1.0 and refreshes plugin / marketplace metadata.

## Test plan
- [x] Smoke-test the bundled script via `uv run --no-project` against a sample markdown fixture covering every supported construct.
- [x] Validate JSON manifests (`marketplace.json`, `plugin.json`) parse and report version 1.1.0 consistently.
- [x] Validate YAML frontmatter on both `SKILL.md` files.
- [ ] Visual inspection of the rendered PDF (reviewer).

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

---

## Self-review

Spec coverage check:
- D1 (two skills, one plugin): Tasks 1, 2, 4 create/wire the new skill into the existing plugin.
- D2 (plugin name unchanged): No rename anywhere.
- D3 (trigger boundary): Task 2 frontmatter + Task 3 cross-reference paragraph.
- D4 (copy-into-project delivery): Task 2's "Setup procedure" section codifies the 5-step flow.
- D5 (PEP 723): Task 1 step 5 prepends the metadata block.
- D6 (SKILL.md content): Task 2 step 1 contains the full prose.
- D7 (skill repo canonical): No code-level enforcement; documented in spec, reinforced by Task 1 step 4 (verbatim copy from job-hunting source) and Task 2 step 1 (instruction to copy verbatim, not edit on the way through).
- Verification clauses 1–4 from the spec: covered by Task 7 steps 2–4.

Placeholder scan: No "TBD", no "implement later", every code/edit step has the actual content. Two prose-only files (`SKILL.md` for md-to-pdf, plugin `README.md`) are quoted in full. JSON files are quoted in full.

Type / name consistency: `md-to-pdf` slug used everywhere. Plugin version `1.1.0` matches across `plugin.json` and `marketplace.json`. `mistune>=3.0` and `reportlab>=4.0` declared in PEP 723 and referenced in both READMEs.

Risks flagged:
- The smoke test in Task 1 step 6 depends on a working `uv` install with network access to fetch `mistune` and `reportlab` into uv's PEP 723 cache. If offline, this step fails — note for the executor.
- `uv run --no-project` is the syntax for running outside any pyproject; if the working directory has its own `pyproject.toml` (the marketplace repo's root currently has none), no flag is strictly required, but `--no-project` is explicit and safer.
