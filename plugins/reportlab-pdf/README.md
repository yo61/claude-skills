# reportlab-pdf

A Claude skill for generating professional, multi-page PDF documents using
Python's [ReportLab](https://www.reportlab.com/) library and its
[Platypus](https://docs.reportlab.com/reportlab/userguide/ch5_platypus/) layout
engine.

When this plugin is active, Claude can:

- Set up `SimpleDocTemplate` with sensible margins and page sizes (A4, Letter).
- Build documents from a list of flowables (paragraphs, horizontal rules,
  spacers, page breaks) that paginate automatically.
- Define and apply `ParagraphStyle` definitions with correct `leading` to
  prevent overlapping text — the most common ReportLab layout bug.
- Use the built-in Helvetica / Times / Courier families without installing
  fonts, and register TTF files when custom fonts are needed.
- Apply colour, bullet points, justified text, inline HTML markup
  (`<b>`, `<i>`, `<sub>`, `<super>`, `<a>`), and horizontal rules.
- Avoid common pitfalls (XML escaping of `&`, `<`, `>`, `'`; Unicode
  super/subscript glyphs missing from Helvetica; duplicate style names).

## Scope

This skill covers **creating** PDFs from structured content — CVs, reports,
letters, invoices, and similar documents where the layout is generated
programmatically. It does **not** cover reading, merging, splitting, or
form-filling existing PDFs; for those, use Claude Code's built-in `pdf` skill.

## Installation

From the [`yo61/claude-skills`](https://github.com/yo61/claude-skills)
marketplace:

```text
/plugin marketplace add yo61/claude-skills
/plugin install reportlab-pdf@yo61-skills
```

ReportLab itself is installed per the user's Python tooling. Following the
project's standards, prefer `uv`:

```bash
uv add reportlab          # in a uv project
uv pip install reportlab  # ad-hoc / no project
```

## What's in the plugin

```
reportlab-pdf/
├── .claude-plugin/
│   └── plugin.json
└── skills/
    └── reportlab-pdf/
        └── SKILL.md   # the skill itself
```

`SKILL.md` is loaded into Claude's context when the skill triggers.

## License

[MIT](../../LICENSE)
