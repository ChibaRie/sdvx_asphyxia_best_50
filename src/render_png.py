"""Best 50 poster renderer for SDVX.

The output is a 1600 px "results terminal" poster:

* a cinematic hero with the official EXCEED GEAR key visual, player identity,
  total VOLFORCE and a deviation spectrum of all 50 tracks;
* the top three tracks as a staggered podium;
* ranks 04-50 as a dense, readable card grid;
* a real-data distribution panel that fills the last row.

Layout, hero and card components live in :mod:`b50_layout`,
:mod:`render_hero` and :mod:`render_cards`; this module owns the public API
and the final composition.
"""
from __future__ import annotations

import datetime
import os

from PIL import Image, ImageDraw

from b50_layout import (
    CANVAS_W,
    HERO_H,
    JPEG_QUALITY,
    MARGIN_X,
    RESAMPLE,
    build_stats,
    format_vf as format_vf,  # re-exported for tests and external callers
    layout_poster,
)
from render_cards import draw_podium, draw_runlist
from render_hero import draw_hero
from render_theme import (
    BG_DEEP,
    HAIRLINE,
    TEXT_FAINT,
    draw_hero_rule,
    draw_tracked,
    load_font,
    paint_page_background,
    px,
    set_cjk_font,
)

# Backwards-compatible aliases used by tests and external callers.
_layout = layout_poster
_build_stats = build_stats

__all__ = ["format_vf", "render_png"]


def _draw_footer(
    draw: ImageDraw.ImageDraw,
    y: float,
    date_label: str,
    source_label: str,
) -> None:
    draw.line(
        [(px(MARGIN_X), px(y)), (px(CANVAS_W - MARGIN_X), px(y))],
        fill=HAIRLINE,
        width=max(1, px(1)),
    )
    font = load_font("num-semi", px(8))
    draw_tracked(
        draw,
        (MARGIN_X, y + 9),
        "SDVX_B50  ·  BEST 50 GENERATOR",
        font,
        TEXT_FAINT,
        tracking=1.1,
    )
    draw_tracked(
        draw,
        (CANVAS_W / 2, y + 9),
        f"GENERATED {date_label}  ·  {source_label}",
        font,
        TEXT_FAINT,
        tracking=0.9,
        anchor="ma",
    )
    draw_tracked(
        draw,
        (CANVAS_W - MARGIN_X, y + 9),
        "KEY VISUAL & JACKETS © KONAMI AMUSEMENT / RIGHTS HOLDERS",
        font,
        TEXT_FAINT,
        tracking=0.7,
        anchor="ra",
    )


def render_png(
    rows: list[dict],
    player_name: str,
    total_vf: float,
    out_path: str,
    skill: str = "",
    font_path: str = "C:/Windows/Fonts/msyh.ttc",
    source_label: str = "LOCAL SAVE",
    background_path: str | None = None,
) -> None:
    """Render the Best 50 poster as a progressive JPEG at ``out_path``."""
    set_cjk_font(font_path)
    layout = layout_poster(len(rows))
    stats = build_stats(rows)
    date_label = datetime.date.today().isoformat()

    canvas = Image.new("RGB", (px(CANVAS_W), px(layout["total_h"])), BG_DEEP)
    paint_page_background(canvas, HERO_H, CANVAS_W, layout["total_h"])
    draw = ImageDraw.Draw(canvas)

    draw_hero(
        canvas,
        draw,
        rows,
        player_name,
        total_vf,
        skill,
        stats,
        source_label,
        background_path,
    )
    draw_hero_rule(canvas, HERO_H, CANVAS_W)
    draw_podium(canvas, draw, rows, stats, layout)
    if layout["run_rows"]:
        draw_runlist(canvas, draw, rows, stats, layout)
    _draw_footer(draw, layout["footer_y"], date_label, source_label)

    final = canvas.resize((CANVAS_W, layout["total_h"]), RESAMPLE)
    parent = os.path.dirname(out_path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    final.save(out_path, "JPEG", quality=JPEG_QUALITY, optimize=True, progressive=True)
