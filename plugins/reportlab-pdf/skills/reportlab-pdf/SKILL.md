---
name: reportlab-pdf
description: >
  Generate professional, multi-page PDF documents using Python's ReportLab library
  and its Platypus layout engine. Use this skill whenever the user wants to create
  a PDF from structured content — CVs, reports, letters, invoices, or any document
  where you control the layout programmatically. Also use when the user asks for a
  PDF and ReportLab is already installed or is the natural tool choice. This skill
  covers document setup, paragraph styles, flowables, typography, colour, bullet
  points, horizontal rules, and pagination. It does NOT cover reading, merging,
  splitting, or form-filling existing PDFs — use the built-in pdf skill for those.
  Trigger on: "create a PDF", "generate a PDF", "build a PDF", "make a PDF from",
  "PDF report", "PDF CV", "PDF letter", "PDF invoice", "ReportLab", "Platypus",
  or any request to produce a professional-looking PDF document from data or text.
---

# PDF Generation with ReportLab Platypus

## When to use this skill

Use ReportLab Platypus when you need to **create** a PDF from structured content — CVs, reports, letters, invoices, or any document where you control the layout programmatically. Platypus handles pagination automatically, flowing content across pages without manual page breaks.

This skill is *not* for manipulating existing PDFs (use pypdf), extracting text (use pdfplumber), or filling forms (use pdf-lib). If you need those, use the built-in `pdf` skill instead.

## Installation

In a uv project:

```bash
uv add reportlab
```

For an ad-hoc script or environment without a project, use uv's pip-compatible interface (which avoids the `--break-system-packages` workaround needed by system pip on externally-managed environments):

```bash
uv pip install reportlab
```

ReportLab is pre-installed in most sandboxed environments. The built-in Helvetica family covers most professional documents without any font installation.

## Core architecture

Platypus works by building a list of **flowable** objects — paragraphs, horizontal rules, spacers, images, tables — and flowing them into a document template that handles pagination automatically. You build a `story` (a Python list), append flowables in order, and call `doc.build(story)`.

```python
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.platypus import SimpleDocTemplate, Paragraph, HRFlowable, Spacer, PageBreak
```

## Document setup

```python
doc = SimpleDocTemplate(
    "output.pdf",
    pagesize=A4,
    topMargin=18*mm,
    bottomMargin=18*mm,
    leftMargin=20*mm,
    rightMargin=20*mm,
)
```

For US Letter size, use `from reportlab.lib.pagesizes import letter` and `pagesize=letter`.

Margins of 18-20mm work well for professional documents. Going below 15mm starts to look cramped.

## Colours

Define colours as constants using `HexColor`:

```python
DARK = HexColor("#1a1a1a")      # Near-black for body text
ACCENT = HexColor("#2E5090")    # Blue for headings and name
GREY = HexColor("#555555")      # Mid-grey for secondary text
RULE = HexColor("#CCCCCC")      # Light grey for horizontal rules
```

## Paragraph styles

Start with the built-in stylesheet and add custom styles:

```python
styles = getSampleStyleSheet()
```

### Always set `leading` — this prevents overlapping text

The `leading` parameter controls line height in points. Without it, ReportLab's default is often too tight, causing lines to visually overlap — especially with larger font sizes. This is the single most common layout issue. Set `leading` to roughly 1.3× the `fontSize`:

| fontSize | Recommended leading |
|----------|-------------------|
| 9–9.5    | 12–13             |
| 10       | 13–14             |
| 11       | 15                |
| 12       | 16                |
| 20       | 26                |

### Style properties

Each `ParagraphStyle` takes these key properties:

```python
styles.add(ParagraphStyle(
    "StyleName",
    fontName="Helvetica",        # Font family
    fontSize=10,                 # Size in points
    leading=14,                  # Line height — ALWAYS SET THIS
    textColor=DARK,              # Text colour
    spaceAfter=4,                # Space below in points
    spaceBefore=0,               # Space above in points
    alignment=TA_JUSTIFY,        # TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
    leftIndent=0,                # Left indent in points
    bulletIndent=0,              # Indent for bullet character
))
```

### Available built-in fonts

These Helvetica variants are always available — no font installation needed:

- `Helvetica` — regular
- `Helvetica-Bold` — bold
- `Helvetica-Oblique` — italic
- `Helvetica-BoldOblique` — bold italic

Other built-in families: `Times-Roman`, `Courier`. For custom fonts, register TTF files with `pdfmetrics.registerFont()`.

### Reference style set for professional documents

This set has been tested and refined across multiple documents (CVs, letters, reports). Use it as a starting point and adapt as needed:

```python
styles.add(ParagraphStyle("DocTitle",
    fontName="Helvetica-Bold", fontSize=20, leading=26,
    textColor=ACCENT, spaceAfter=6))

styles.add(ParagraphStyle("Subtitle",
    fontName="Helvetica", fontSize=11, leading=15,
    textColor=GREY, spaceAfter=4))

styles.add(ParagraphStyle("ContactInfo",
    fontName="Helvetica", fontSize=9, leading=13,
    textColor=GREY, spaceAfter=8))

styles.add(ParagraphStyle("SectionHeading",
    fontName="Helvetica-Bold", fontSize=12,
    textColor=ACCENT, spaceBefore=12, spaceAfter=4))

styles.add(ParagraphStyle("CompanyName",
    fontName="Helvetica-Bold", fontSize=11,
    textColor=DARK, spaceBefore=8, spaceAfter=1))

styles.add(ParagraphStyle("RoleTitle",
    fontName="Helvetica-BoldOblique", fontSize=10,
    textColor=DARK, spaceAfter=1))

styles.add(ParagraphStyle("DateRange",
    fontName="Helvetica", fontSize=9,
    textColor=GREY, spaceAfter=3))

styles.add(ParagraphStyle("Body",
    fontName="Helvetica", fontSize=9.5, leading=13,
    textColor=DARK, spaceAfter=4, alignment=TA_JUSTIFY))

styles.add(ParagraphStyle("Bullet",
    fontName="Helvetica", fontSize=9.5, leading=13,
    textColor=DARK, spaceAfter=3,
    leftIndent=14, bulletIndent=0, alignment=TA_JUSTIFY))

styles.add(ParagraphStyle("SkillLine",
    fontName="Helvetica", fontSize=9.5, leading=13,
    textColor=DARK, spaceAfter=4))

styles.add(ParagraphStyle("CompactLine",
    fontName="Helvetica", fontSize=9.5, leading=13,
    textColor=DARK, spaceAfter=2))
```

## Building the document

Create a list of flowables and append elements in order:

```python
story = []

# Title
story.append(Paragraph("Document Title", styles["DocTitle"]))
story.append(Paragraph("Subtitle or tagline", styles["Subtitle"]))

# Horizontal rule
story.append(HRFlowable(
    width="100%", thickness=1, color=RULE,
    spaceAfter=6, spaceBefore=2))

# Section heading
story.append(Paragraph("Section Name", styles["SectionHeading"]))

# Body text
story.append(Paragraph("Paragraph of body text here.", styles["Body"]))

# Bullet points
for bullet_text in ["First point.", "Second point.", "Third point."]:
    story.append(Paragraph(bullet_text, styles["Bullet"], bulletText="•"))

# Build the PDF
doc.build(story)
```

### Horizontal rules

Use `HRFlowable` for section dividers:

```python
# Thick rule (e.g. below header)
story.append(HRFlowable(width="100%", thickness=1, color=RULE, spaceAfter=6, spaceBefore=2))

# Thin rule (e.g. between sections)
story.append(HRFlowable(width="100%", thickness=0.5, color=RULE, spaceAfter=2, spaceBefore=8))
```

### Inline HTML markup

Paragraph text supports a subset of HTML tags for inline formatting:

- `<b>bold</b>`, `<i>italic</i>`, `<u>underline</u>`
- `<sub>subscript</sub>`, `<super>superscript</super>`
- `<a href="url">link</a>` (renders as blue underlined text)
- `<br/>` for line breaks

**Escape special characters** — paragraph text is parsed as XML:
- `&` → `&amp;`
- `<` → `&lt;`
- `>` → `&gt;`
- `'` → `&#39;`

Example with bold lead-in:

```python
story.append(Paragraph(
    "<b>Led the project</b> — delivered the platform on time and under budget.",
    styles["Bullet"], bulletText="•"))
```

**Never use Unicode subscript/superscript characters** (like `₂` or `²`) — Helvetica does not include these glyphs and they render as black boxes. Use `<sub>` and `<super>` tags instead.

### Bullet points

Bullets are paragraphs with `bulletText="•"` and a style that defines the indentation:

```python
styles.add(ParagraphStyle("Bullet",
    fontName="Helvetica", fontSize=9.5, leading=13,
    textColor=DARK, spaceAfter=3,
    leftIndent=14, bulletIndent=0, alignment=TA_JUSTIFY))

story.append(Paragraph("Bullet text here.", styles["Bullet"], bulletText="•"))
```

- `leftIndent=14` pushes paragraph text 14pt right
- `bulletIndent=0` places the bullet at the left margin
- The visual gap between bullet and text is `leftIndent - bulletIndent`

### Page breaks and spacers

```python
from reportlab.platypus import PageBreak, Spacer

story.append(PageBreak())       # Force new page
story.append(Spacer(1, 12))     # 12pt vertical space
```

Prefer `spaceAfter`/`spaceBefore` on styles over `Spacer` objects — it's cleaner.

## Common pitfalls

### Text overlapping
Missing or insufficient `leading`. A 20pt font with default leading will overlap adjacent elements. Always set `leading` to at least 1.3× `fontSize`, and use `spaceAfter` for breathing room.

### XML parsing errors from ampersands
Paragraph text is parsed as XML. Bare `&` breaks the parser. Always use `&amp;` in text content.

```python
# Wrong — will crash
Paragraph("Leadership & Management", style)

# Right
Paragraph("Leadership &amp; Management", style)
```

### Apostrophes near HTML tags
Use `&#39;` when apostrophes appear near markup:

```python
Paragraph("the platform&#39;s future", style)
```

### Duplicate style names
`styles.add()` raises an error if the name already exists (including built-in names like "Normal", "Title", "Heading1"). Use unique names for custom styles.

### Missing alignment import
If using `TA_JUSTIFY` or other alignment constants:

```python
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER, TA_RIGHT
```

## Complete working example

```python
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.platypus import SimpleDocTemplate, Paragraph, HRFlowable

output_path = "example.pdf"
doc = SimpleDocTemplate(output_path, pagesize=A4,
    topMargin=18*mm, bottomMargin=18*mm,
    leftMargin=20*mm, rightMargin=20*mm)

DARK = HexColor("#1a1a1a")
ACCENT = HexColor("#2E5090")
GREY = HexColor("#555555")
RULE = HexColor("#CCCCCC")

styles = getSampleStyleSheet()
styles.add(ParagraphStyle("DocTitle",
    fontName="Helvetica-Bold", fontSize=20, leading=26,
    textColor=ACCENT, spaceAfter=6))
styles.add(ParagraphStyle("Subtitle",
    fontName="Helvetica", fontSize=11, leading=15,
    textColor=GREY, spaceAfter=4))
styles.add(ParagraphStyle("Contact",
    fontName="Helvetica", fontSize=9, leading=13,
    textColor=GREY, spaceAfter=8))
styles.add(ParagraphStyle("Section",
    fontName="Helvetica-Bold", fontSize=12,
    textColor=ACCENT, spaceBefore=12, spaceAfter=4))
styles.add(ParagraphStyle("Body",
    fontName="Helvetica", fontSize=9.5, leading=13,
    textColor=DARK, spaceAfter=4, alignment=TA_JUSTIFY))
styles.add(ParagraphStyle("Bullet",
    fontName="Helvetica", fontSize=9.5, leading=13,
    textColor=DARK, spaceAfter=3,
    leftIndent=14, bulletIndent=0, alignment=TA_JUSTIFY))
styles.add(ParagraphStyle("SkillLine",
    fontName="Helvetica", fontSize=9.5, leading=13,
    textColor=DARK, spaceAfter=4))

story = []

# Header
story.append(Paragraph("Person Name", styles["DocTitle"]))
story.append(Paragraph("Role Title  |  Specialism", styles["Subtitle"]))
story.append(Paragraph("Location  |  Phone  |  Email", styles["Contact"]))
story.append(HRFlowable(width="100%", thickness=1, color=RULE,
    spaceAfter=6, spaceBefore=2))

# Summary section
story.append(Paragraph("Summary", styles["Section"]))
story.append(Paragraph("Summary paragraph goes here.", styles["Body"]))

# Divider
story.append(HRFlowable(width="100%", thickness=0.5, color=RULE,
    spaceAfter=2, spaceBefore=4))

# Experience section with bullets
story.append(Paragraph("Experience", styles["Section"]))
story.append(Paragraph("Body text describing the role.", styles["Body"]))

for b in [
    "<b>Led something</b> — details of what was achieved.",
    "<b>Built something</b> — more details here.",
]:
    story.append(Paragraph(b, styles["Bullet"], bulletText="•"))

# Skills section
story.append(HRFlowable(width="100%", thickness=0.5, color=RULE,
    spaceAfter=2, spaceBefore=8))
story.append(Paragraph("Skills", styles["Section"]))

for cat, body in [
    ("<b>Category:</b>", "Skill 1, Skill 2, Skill 3."),
]:
    story.append(Paragraph(f"{cat} {body}", styles["SkillLine"]))

doc.build(story)
print("PDF created successfully")
```

## Tips for good results

- **Body text**: 9–9.5pt for dense documents (CVs); 10–11pt for letters and reports.
- **Justified text**: Use `alignment=TA_JUSTIFY` for body and bullets to get clean right margins.
- **Spacing via styles**: Prefer `spaceAfter` on styles over inserting `Spacer` objects.
- **Section separation**: `spaceBefore=12` on section headings gives natural visual breaks.
- **Test with real content**: Pagination issues only surface with enough text to overflow a page.
- **Output path**: Point the output to the user's workspace folder so they can access it via a `computer://` link.
