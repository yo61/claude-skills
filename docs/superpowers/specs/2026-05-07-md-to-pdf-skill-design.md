# `md-to-pdf` skill — design

Date: 2026-05-07
Status: approved (pending implementation plan)

## Summary

Add a new `md-to-pdf` skill to the existing `reportlab-pdf` plugin. The skill ships a self-contained Python script (`md_to_pdf.py`) that converts markdown files to styled PDFs via mistune + ReportLab Platypus. When triggered, the skill copies the script into the user's project, adds dependencies, and runs it on the input.

The script's canonical home becomes the skill repo. The existing copy under `~/Documents/Projects/Job Hunting 2026-04/internals/scripts/` becomes a downstream consumer that is synced from the skill.

## Motivation

The user has built a generic markdown-to-PDF tool inside a job-hunting project. The tool's docstring already declares it "designed to be liftable into the `reportlab-pdf` skill as a drop-in helper." Promoting it to a skill makes it reusable across any project Claude works on, while keeping the existing instructional `reportlab-pdf` skill intact for cases where layout is generated programmatically from data rather than from markdown.

## Decisions

### D1 — Two skills in one plugin

The new `md-to-pdf` skill lives alongside the existing `reportlab-pdf` skill under the same plugin. Both rely on ReportLab; one plugin is the right unit of installation.

**Trade-off accepted:** The two skills' descriptions must be tuned so they don't fight for the same triggers. Mitigation in D3.

### D2 — Plugin name unchanged

The plugin keeps the name `reportlab-pdf`. Renaming would force a reinstall on every existing user for no functional gain.

### D3 — Trigger boundary

- `md-to-pdf` matches on **markdown source or markdown intent**: `.md` files, pasted markdown, phrases like "convert markdown to PDF", "render this README as a PDF".
- `reportlab-pdf` matches on **structured/programmatic PDF generation**: data → layout, e.g. "PDF CV", "PDF invoice", "PDF report from this JSON".
- The existing `reportlab-pdf` SKILL.md gains a one-line note pointing at `md-to-pdf` for markdown input.

### D4 — Delivery model: copy into user's project

When the skill triggers, Claude copies the script into the user's repo. Each project owns its copy and can customise it (`Palette`, `RenderOptions`, `PlatypusRenderer` subclass, custom stylesheet) without affecting any other project.

The flow:

1. Detect project type — walk up from cwd looking for `pyproject.toml`, `requirements.txt`, or neither.
2. Pick destination path — default `scripts/md_to_pdf.py`. If `scripts/` is absent but `internals/scripts/`, `tools/`, or `bin/` exists, prefer that. If ambiguous, ask.
3. Copy the script verbatim from the skill's `scripts/md_to_pdf.py` to the chosen destination.
4. Add dependencies — `uv add mistune reportlab` (uv project), else `uv pip install mistune reportlab`. Skip if both are already declared.
5. Run the script on the user's input via its CLI entrypoint.

### D5 — PEP 723 inline metadata

Add PEP 723 inline metadata to the top of the script (commented `# /// script` block declaring `mistune` and `reportlab` as dependencies). This lets `uv run scripts/md_to_pdf.py input.md` work without project deps, which is useful for ad-hoc conversions in projects that should not have these libraries in their lockfile.

Step 4 of the delivery flow becomes optional: if the user asks for a one-shot conversion and the project doesn't already have the deps, Claude uses `uv run` instead of installing.

### D6 — SKILL.md content

Concise and procedural. Sections:

1. **When to use / when not to use** — markdown source vs. structured data; cross-link to `reportlab-pdf`.
2. **Setup procedure** — the 5-step flow from D4.
3. **Public API surface** — short reference for `write_pdf()`, `render_markdown()`, `Palette`, `RenderOptions`, `PlatypusRenderer`. Lifted from the script's docstring.
4. **Customisation recipe** — one worked example: pass a custom `Palette` to change the accent colour. One sentence each on subclassing `PlatypusRenderer` and supplying custom `StyleSheet1` instances. Defer deeper customisation to reading the source.
5. **Limitations** — tables, images, footnotes, definition lists not supported. Tells Claude not to promise them.
6. **Pitfalls** — mistune handles markdown escaping correctly; raw HTML in markdown is not passed through to the PDF.

### D7 — Source-of-truth: skill repo

The skill's `scripts/md_to_pdf.py` is canonical. The existing `internals/scripts/md_to_pdf.py` in the job-hunting repo becomes a downstream copy — the user (or Claude) syncs it from the skill when changes land.

## Layout

```
plugins/reportlab-pdf/
├── .claude-plugin/
│   └── plugin.json                   # version bump, description mentions both skills
├── README.md                          # add md-to-pdf section
└── skills/
    ├── reportlab-pdf/
    │   └── SKILL.md                   # one-line note pointing at md-to-pdf for .md input
    └── md-to-pdf/
        ├── SKILL.md                   # new — see D6
        └── scripts/
            └── md_to_pdf.py           # canonical copy of the script + PEP 723 header
```

`/.claude-plugin/marketplace.json` at repo root: update the `reportlab-pdf` entry's description and keywords to mention markdown. Plugin name and version handled in the plugin manifest.

## Out of scope

- Adding table, image, footnote, or definition-list support to the script. The current limitations stand and are advertised. Future work, not this skill.
- Publishing the script to PyPI as a standalone package. The skill ships it; that is enough.
- Any changes to the `contributory-factors` plugin.
- Migrating the job-hunting repo to consume the skill copy at install time. The user keeps a manual sync workflow.

## Verification

The skill is correct if:

1. A user with a `.md` file says "convert this to PDF" and Claude (a) picks `md-to-pdf`, (b) copies the script to a sensible path, (c) adds deps or uses `uv run`, (d) produces a PDF that opens and renders headings/lists/code/links.
2. A user with structured data says "build a PDF report" and Claude picks `reportlab-pdf`, not `md-to-pdf`.
3. The script in the skill repo is byte-identical to the one in `~/Documents/Projects/Job Hunting 2026-04/internals/scripts/md_to_pdf.py` at the time of import, except for the new PEP 723 header.
4. `marketplace.json`, plugin `plugin.json`, and the plugin `README.md` reflect the new skill.

## Open questions

None at design time. Implementation plan will surface details (exact PEP 723 block, exact wording of SKILL.md sections, version bump number).
