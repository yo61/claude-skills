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
