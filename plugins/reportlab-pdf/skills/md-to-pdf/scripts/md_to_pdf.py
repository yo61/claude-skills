# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "mistune>=3.0",
#     "reportlab>=4.0",
# ]
# ///
"""Convert markdown to PDF using mistune (parsing) and ReportLab Platypus (layout).

Self-contained: no project-internal imports. Designed to be liftable into the
``reportlab-pdf`` skill as a drop-in helper.

Public API
----------
- ``write_pdf(source, output=None, **opts)`` — convenience: read a markdown
  file, write a styled PDF.
- ``render_markdown(md_text, *, styles=None, options=None)`` — return a list
  of Platypus ``Flowable`` objects suitable for embedding into a larger doc.
- ``PlatypusRenderer`` — walks a mistune AST and emits Flowables; subclass to
  customise.
- ``Palette`` / ``RenderOptions`` — colour palette and per-render switches.
- ``build_default_styles(palette)`` — produce the default stylesheet.

CLI
---
::

    python md_to_pdf.py input.md [-o output.pdf]
                                 [--show-link-urls]
                                 [--page-size {a4,letter}]
                                 [--margins-mm 20]

Supported markdown
------------------
ATX headings (``#``..``######``), paragraphs, bullet/ordered lists with
nesting, fenced code blocks, blockquotes, horizontal rules, inline bold,
italic, code, and links.

Not yet supported: tables, images, footnotes, definition lists. Tokens of an
unknown type fall back to a text paragraph rather than crashing.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from html import escape
from pathlib import Path
from typing import Any, cast

import mistune
from reportlab.lib.colors import Color, HexColor
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import ParagraphStyle, StyleSheet1, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Flowable,
    HRFlowable,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
)


@dataclass(frozen=True)
class Palette:
    """Colour palette used by the default stylesheet."""

    dark: Color = field(default_factory=lambda: HexColor("#1a1a1a"))
    accent: Color = field(default_factory=lambda: HexColor("#2E5090"))
    grey: Color = field(default_factory=lambda: HexColor("#555555"))
    rule: Color = field(default_factory=lambda: HexColor("#CCCCCC"))
    code_bg: Color = field(default_factory=lambda: HexColor("#F4F4F4"))
    link: Color = field(default_factory=lambda: HexColor("#2E5090"))


def _hex_markup(colour: Color) -> str:
    """Color -> '#RRGGBB' for use inside ReportLab paragraph markup."""
    return f"#{colour.hexval()[2:8]}"


DEFAULT_PALETTE = Palette()


@dataclass(frozen=True)
class RenderOptions:
    """Per-render switches that don't belong on styles."""

    show_link_urls: bool = False
    """When True, render each link as ``text (url)`` with the URL clickable.

    Useful for printable references lists. Off by default — bare hyperlinks
    are the standard convention.
    """

    max_list_depth: int = 4
    """Soft cap on nested list indentation. Items deeper than this still
    render but stop indenting further."""


def build_default_styles(palette: Palette = DEFAULT_PALETTE) -> StyleSheet1:
    """Return a stylesheet covering every style key the renderer expects."""
    styles = getSampleStyleSheet()

    def add(name: str, **kwargs: str | float | Color) -> None:
        styles.add(ParagraphStyle(name, **kwargs))

    add(
        "DocTitle",
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=26,
        textColor=palette.accent,
        spaceAfter=4,
    )
    add(
        "H2",
        fontName="Helvetica-Bold",
        fontSize=14,
        leading=18,
        textColor=palette.accent,
        spaceBefore=14,
        spaceAfter=6,
    )
    add(
        "H3",
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        textColor=palette.dark,
        spaceBefore=10,
        spaceAfter=4,
    )
    add(
        "H4",
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=13,
        textColor=palette.dark,
        spaceBefore=8,
        spaceAfter=3,
    )
    add(
        "H5",
        fontName="Helvetica-BoldOblique",
        fontSize=10,
        leading=13,
        textColor=palette.dark,
        spaceBefore=6,
        spaceAfter=3,
    )
    add(
        "H6",
        fontName="Helvetica-Oblique",
        fontSize=10,
        leading=13,
        textColor=palette.grey,
        spaceBefore=6,
        spaceAfter=3,
    )
    add(
        "Body",
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=palette.dark,
        spaceAfter=6,
        alignment=TA_JUSTIFY,
    )
    add(
        "Quote",
        fontName="Helvetica-Oblique",
        fontSize=10,
        leading=14,
        textColor=palette.grey,
        spaceAfter=6,
        leftIndent=14,
        rightIndent=14,
        borderPadding=4,
    )
    add(
        "CodeBlock",
        fontName="Courier",
        fontSize=9,
        leading=12,
        textColor=palette.dark,
        spaceAfter=6,
        leftIndent=12,
        backColor=palette.code_bg,
        borderPadding=6,
    )
    for depth in range(8):
        add(
            f"Bullet{depth}",
            fontName="Helvetica",
            fontSize=10,
            leading=14,
            textColor=palette.dark,
            spaceAfter=3,
            leftIndent=18 + depth * 14,
            bulletIndent=4 + depth * 14,
            alignment=TA_JUSTIFY,
        )
    return styles


class PlatypusRenderer:
    """Walk a mistune AST and emit ReportLab Platypus Flowables.

    Block tokens dispatch to ``_block_<type>`` methods that return a list of
    Flowables. Inline tokens dispatch to ``_inline_<type>`` methods that
    return ReportLab markup strings. Unknown tokens fall back gracefully.

    Subclass and override individual methods to customise output. The split
    between block (Flowable) and inline (string) maps directly onto the
    Platypus model: blocks become page elements, inline content becomes
    markup inside a Paragraph.
    """

    def __init__(
        self,
        styles: StyleSheet1 | None = None,
        *,
        palette: Palette = DEFAULT_PALETTE,
        options: RenderOptions | None = None,
    ) -> None:
        """Build a renderer with an optional stylesheet, palette, and options."""
        self.styles = styles if styles is not None else build_default_styles(palette)
        self.palette = palette
        self.options = options or RenderOptions()

    def render(self, tokens: list[dict[str, Any]]) -> list[Flowable]:
        """Walk a list of mistune block tokens and return Platypus flowables."""
        out: list[Flowable] = []
        for tok in tokens:
            out.extend(self._block(tok))
        return out

    # --- block dispatch -------------------------------------------------

    def _block(self, tok: dict[str, Any]) -> list[Flowable]:
        method = getattr(self, f"_block_{tok['type']}", self._block_unknown)
        return method(tok)

    def _block_blank_line(self, _: dict[str, Any]) -> list[Flowable]:
        return []

    def _block_heading(self, tok: dict[str, Any]) -> list[Flowable]:
        level = tok["attrs"]["level"]
        style_name = "DocTitle" if level == 1 else f"H{min(level, 6)}"
        return [Paragraph(self._inline(tok["children"]), self.styles[style_name])]

    def _block_paragraph(self, tok: dict[str, Any]) -> list[Flowable]:
        return [Paragraph(self._inline(tok["children"]), self.styles["Body"])]

    def _block_thematic_break(self, _: dict[str, Any]) -> list[Flowable]:
        return [
            Spacer(1, 4),
            HRFlowable(
                width="100%", thickness=0.5, color=self.palette.rule, spaceBefore=2, spaceAfter=6
            ),
        ]

    def _block_block_code(self, tok: dict[str, Any]) -> list[Flowable]:
        return [Preformatted(tok["raw"].rstrip("\n"), self.styles["CodeBlock"])]

    def _block_block_quote(self, tok: dict[str, Any]) -> list[Flowable]:
        out: list[Flowable] = []
        for child in tok.get("children", []):
            if child["type"] == "paragraph":
                out.append(Paragraph(self._inline(child["children"]), self.styles["Quote"]))
            else:
                out.extend(self._block(child))
        return out

    def _block_list(self, tok: dict[str, Any]) -> list[Flowable]:
        return list(self._iter_list(tok, depth=0))

    def _iter_list(self, tok: dict[str, Any], *, depth: int) -> list[Flowable]:
        clamped = min(depth, self.options.max_list_depth)
        style = self.styles[f"Bullet{clamped}"]
        ordered = tok["attrs"]["ordered"]
        out: list[Flowable] = []
        for index, item in enumerate(tok.get("children", []), start=1):
            bullet = f"{index}." if ordered else "•"
            out.extend(self._render_list_item(item, bullet, style, depth))
        return out

    def _render_list_item(
        self,
        item: dict[str, Any],
        bullet: str,
        style: ParagraphStyle,
        depth: int,
    ) -> list[Flowable]:
        out: list[Flowable] = []
        first = True
        for child in item.get("children", []):
            ct = child["type"]
            if ct in ("block_text", "paragraph"):
                text = self._inline(child.get("children", []))
                out.append(Paragraph(text, style, bulletText=bullet if first else ""))
                first = False
            elif ct == "list":
                out.extend(self._iter_list(child, depth=depth + 1))
            else:
                out.extend(self._block(child))
        return out

    def _block_unknown(self, tok: dict[str, Any]) -> list[Flowable]:
        text = self._inline(tok.get("children", [])) or escape(tok.get("raw", ""))
        return [Paragraph(text, self.styles["Body"])] if text else []

    # --- inline dispatch ------------------------------------------------

    def _inline(self, children: list[dict[str, Any]]) -> str:
        return "".join(self._inline_one(c) for c in children)

    def _inline_one(self, tok: dict[str, Any]) -> str:
        method = getattr(self, f"_inline_{tok['type']}", None)
        if method is None:
            return escape(tok.get("raw", ""))
        return method(tok)

    def _inline_text(self, tok: dict[str, Any]) -> str:
        return escape(tok["raw"])

    def _inline_strong(self, tok: dict[str, Any]) -> str:
        return f"<b>{self._inline(tok['children'])}</b>"

    def _inline_emphasis(self, tok: dict[str, Any]) -> str:
        return f"<i>{self._inline(tok['children'])}</i>"

    def _inline_codespan(self, tok: dict[str, Any]) -> str:
        return f'<font name="Courier">{escape(tok["raw"])}</font>'

    def _inline_link(self, tok: dict[str, Any]) -> str:
        text = self._inline(tok.get("children", []))
        url = escape(tok["attrs"]["url"], quote=True)
        colour = _hex_markup(self.palette.link)
        link = f'<link href="{url}" color="{colour}">{text}</link>'
        if not self.options.show_link_urls:
            return link
        url_link = f'<link href="{url}" color="{colour}">{escape(tok["attrs"]["url"])}</link>'
        return f"{text} ({url_link})"

    def _inline_softbreak(self, _: dict[str, Any]) -> str:
        return " "

    def _inline_linebreak(self, _: dict[str, Any]) -> str:
        return "<br/>"


def render_markdown(
    md_text: str,
    *,
    renderer: PlatypusRenderer | None = None,
    styles: StyleSheet1 | None = None,
    palette: Palette = DEFAULT_PALETTE,
    options: RenderOptions | None = None,
) -> list[Flowable]:
    """Parse markdown text and return a list of Platypus Flowables.

    When ``renderer`` is provided the ``styles``/``palette``/``options`` args
    are ignored — the caller has already configured them on the renderer.
    """
    parser = mistune.create_markdown(renderer=None)
    tokens = cast("list[dict[str, Any]]", parser(md_text))
    if renderer is None:
        renderer = PlatypusRenderer(styles=styles, palette=palette, options=options)
    return renderer.render(tokens)


def write_pdf(
    source: Path,
    output: Path | None = None,
    *,
    renderer: PlatypusRenderer | None = None,
    page_size: tuple[float, float] = A4,
    margins_mm: float = 20.0,
    palette: Palette = DEFAULT_PALETTE,
    options: RenderOptions | None = None,
) -> Path:
    """Read a markdown file and write a styled PDF; return the output path.

    Pass ``renderer`` to use a custom subclass (e.g. for domain-specific
    layouts); otherwise the default ``PlatypusRenderer`` is used.
    """
    md = source.read_text(encoding="utf-8")
    out = output if output is not None else source.with_suffix(".pdf")
    doc = SimpleDocTemplate(
        str(out),
        pagesize=page_size,
        topMargin=margins_mm * mm,
        bottomMargin=margins_mm * mm,
        leftMargin=margins_mm * mm,
        rightMargin=margins_mm * mm,
    )
    flowables = render_markdown(
        md,
        renderer=renderer,
        palette=palette,
        options=options,
    )
    doc.build(flowables)
    return out


_PAGE_SIZES = {"a4": A4, "letter": letter}


def main() -> None:
    """Parse CLI arguments and write a PDF from the source markdown file."""
    ap = argparse.ArgumentParser(description="Render a markdown file to PDF")
    ap.add_argument("source", type=Path, help="Markdown input file")
    ap.add_argument("-o", "--output", type=Path, help="PDF output path")
    ap.add_argument(
        "--show-link-urls",
        action="store_true",
        help="Render links as 'text (url)' for printable references",
    )
    ap.add_argument("--page-size", choices=_PAGE_SIZES.keys(), default="a4")
    ap.add_argument("--margins-mm", type=float, default=20.0)
    args = ap.parse_args()

    out = write_pdf(
        args.source,
        args.output,
        page_size=_PAGE_SIZES[args.page_size],
        margins_mm=args.margins_mm,
        options=RenderOptions(show_link_urls=args.show_link_urls),
    )
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
