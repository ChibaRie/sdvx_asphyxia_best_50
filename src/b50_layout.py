"""Layout constants, statistics and shared card primitives for the B50 poster.

Keeping these out of :mod:`render_png` lets the hero and card modules share a
single source of truth without circular imports.
"""
from __future__ import annotations

import math
import os
from collections import Counter
from typing import Any

from PIL import Image, ImageDraw

from render_theme import (
    COPPER,
    CYAN,
    GOLD,
    GRADE_STYLES,
    HAIRLINE,
    ICE,
    LAMP_STYLES,
    SS,
    TEXT,
    TEXT_MUTED,
    difficulty_color,
    draw_text,
    draw_tracked,
    hex_to_rgb,
    load_font,
    px,
    text_width,
)

# ---------------------------------------------------------------------------
# Layout constants (logical pixels)
# ---------------------------------------------------------------------------
CANVAS_W = 1600
MARGIN_X = 28
HERO_H = 360

PODIUM_LABEL_Y = 382
PODIUM_TOP = 408
RUNLIST_LABEL_Y = 688
RUNLIST_TOP = 716

CARD_W = 298
CARD_H = 128
CARD_GAP_X = 13
CARD_GAP_Y = 12
COLS = 5
GRID_X = (CANVAS_W - (COLS * CARD_W + (COLS - 1) * CARD_GAP_X)) // 2

JPEG_QUALITY = 90
TOP3_ACCENTS = (GOLD, ICE, COPPER)
TOP3_LABELS = ("CHAMPION", "RUNNER-UP", "THIRD PLACE")
TOP3_FILLS = ((26, 22, 12), (16, 22, 32), (26, 19, 14))

GRADE_ORDER = ("S", "AAA+", "AAA", "AA+", "AA", "A+", "A", "B", "C", "D")
DIFF_LABEL_COLORS: dict[str, tuple[int, int, int]] = {
    "NOV": hex_to_rgb(difficulty_color(0)),
    "ADV": hex_to_rgb(difficulty_color(1)),
    "EXH": hex_to_rgb(difficulty_color(2)),
    "INF": hex_to_rgb(difficulty_color(3)),
    "GRV": hex_to_rgb(difficulty_color(3)),
    "HVN": hex_to_rgb(difficulty_color(3)),
    "VVD": hex_to_rgb(difficulty_color(3)),
    "XCD": hex_to_rgb(difficulty_color(3)),
    "NBL": hex_to_rgb(difficulty_color(3)),
    "MXM": hex_to_rgb(difficulty_color(4)),
    "ULT": hex_to_rgb(difficulty_color(5)),
}

try:
    RESAMPLE = Image.Resampling.LANCZOS
except AttributeError:  # pragma: no cover
    RESAMPLE = Image.LANCZOS


# ---------------------------------------------------------------------------
# Text / number helpers
# ---------------------------------------------------------------------------
def format_vf(vf: float, pct: float) -> str:
    """Format a VF value plus its share of total VOLFORCE."""
    return f"{vf} ·{pct:.4f}%"


def lw(draw: ImageDraw.ImageDraw, text: str, font) -> float:
    """Logical text width (the drawing surface is supersampled)."""
    return text_width(draw, text, font) / SS


def fmt_vf(value: Any) -> str:
    try:
        return f"{float(value):.1f}"
    except (TypeError, ValueError):
        return "—"


def fmt_pct(value: Any) -> str:
    try:
        return f"{float(value):.4f}%"
    except (TypeError, ValueError):
        return "—"


# ---------------------------------------------------------------------------
# Jackets
# ---------------------------------------------------------------------------
def load_or_create_cover(
    cover_path: str | None,
    side: float,
    mtype: int,
    label: str,
    font,
) -> Image.Image:
    """Load a jacket or draw the procedural SDVX prism fallback."""
    side_px = px(side)
    if cover_path and os.path.isfile(cover_path):
        try:
            with Image.open(cover_path) as source:
                return source.convert("RGB").resize((side_px, side_px), RESAMPLE)
        except (OSError, ValueError):
            pass
    return make_procedural_cover(side_px, mtype, label, font)


def make_procedural_cover(side: int, mtype: int, label: str, font) -> Image.Image:
    """Original cyber-prism jacket used when a cover file is missing."""
    img = Image.new("RGB", (side, side), (13, 18, 29))
    draw = ImageDraw.Draw(img)
    diff = hex_to_rgb(difficulty_color(mtype))

    for offset in range(-side, side * 2, max(2, px(7))):
        draw.line([(offset, 0), (0, offset)], fill=(20, 28, 42), width=max(1, px(0.7)))
    draw.line([(0, side * 0.72), (side * 0.72, 0)], fill=diff, width=max(1, px(1)))
    draw.line([(0, side * 0.80), (side * 0.80, 0)], fill=diff, width=max(1, px(0.6)))

    cx, cy = side // 2, side // 2
    r = side * 0.24
    draw.polygon(
        [(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)],
        fill=(19, 27, 42),
        outline=diff,
    )
    inner = r * 0.46
    draw.polygon(
        [(cx, cy - inner), (cx + inner, cy), (cx, cy + inner), (cx - inner, cy)],
        fill=diff,
    )

    label_font = load_font("num-bold", max(px(7), int(side * 0.11)))
    text = label or "SDVX"
    tw = text_width(draw, text, label_font)
    draw.text((cx - tw / 2, side - side * 0.16), text, font=label_font, fill=diff)
    return img


# ---------------------------------------------------------------------------
# Statistics
# ---------------------------------------------------------------------------
def build_stats(rows: list[dict]) -> dict[str, Any]:
    count = len(rows)
    vf_values = [float(r.get("volforce", 0.0) or 0.0) for r in rows]
    vf_sum = sum(vf_values)
    pct_values = [float(r.get("vf_pct", 0.0) or 0.0) for r in rows]
    if vf_sum > 0:
        # Derive a missing share from the real VF values instead of leaving a
        # zero bar. This is the same definition used by b50data.build_rows.
        pct_values = [
            pct if pct > 0 else value / vf_sum * 100.0
            for pct, value in zip(pct_values, vf_values)
        ]
    top_vf = vf_values[0] if vf_values else 0.0
    avg_vf = vf_sum / count if count else 0.0
    grade_counts = Counter(str(r.get("grade_name") or "—") for r in rows)
    diff_counts = Counter(str(r.get("label") or "?") for r in rows)
    top3_share = (sum(vf_values[:3]) / vf_sum * 100.0) if vf_sum > 0 else 0.0
    return {
        "count": count,
        "top_vf": top_vf,
        "avg_vf": avg_vf,
        "s_count": grade_counts.get("S", 0),
        "grade_counts": grade_counts,
        "diff_counts": diff_counts,
        "pcts": pct_values,
        "max_pct": max(pct_values) if pct_values else 0.0,
        "top3_share": top3_share,
    }


# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------
def podium_rects(count: int) -> list[tuple[float, float, float, float]]:
    if count <= 0:
        return []
    if count == 1:
        return [(MARGIN_X, PODIUM_TOP, CANVAS_W - MARGIN_X * 2, 236)]
    if count == 2:
        width = (CANVAS_W - MARGIN_X * 2 - 20) / 2
        return [
            (MARGIN_X, PODIUM_TOP, width, 236),
            (MARGIN_X + width + 20, PODIUM_TOP + 16, width, 220),
        ]
    return [
        (MARGIN_X, PODIUM_TOP, 560, 236),
        (MARGIN_X + 560 + 20, PODIUM_TOP + 16, 472, 220),
        (MARGIN_X + 560 + 20 + 472 + 20, PODIUM_TOP + 16, 472, 220),
    ]


def layout_poster(count: int) -> dict[str, Any]:
    podium_count = min(3, count)
    runlist = count - podium_count
    run_rows = math.ceil(runlist / COLS) if runlist > 0 else 0
    rem = runlist % COLS if runlist > 0 else 0
    slots_left = (COLS - rem) % COLS if runlist > 0 else 0

    summary_mode: str | None = None
    summary_slots = 0
    if runlist >= 10:
        if slots_left >= 2:
            summary_mode = "inline"
            summary_slots = slots_left
        else:
            summary_mode = "row"

    rects = podium_rects(podium_count)
    podium_bottom = max((rect[1] + rect[3] for rect in rects), default=PODIUM_TOP)

    if run_rows == 0:
        grid_bottom = podium_bottom
        footer_y = grid_bottom + 24
    else:
        grid_bottom = RUNLIST_TOP + run_rows * CARD_H + (run_rows - 1) * CARD_GAP_Y
        if summary_mode == "row":
            grid_bottom += CARD_GAP_Y + CARD_H
        footer_y = grid_bottom + 24

    total_h = int(math.ceil(footer_y + 42))
    return {
        "podium_count": podium_count,
        "podium_rects": rects,
        "podium_bottom": podium_bottom,
        "runlist": runlist,
        "run_rows": run_rows,
        "rem": rem,
        "slots_left": slots_left,
        "summary_mode": summary_mode,
        "summary_slots": summary_slots,
        "runlist_label_y": RUNLIST_LABEL_Y if run_rows else None,
        "grid_bottom": grid_bottom,
        "footer_y": footer_y,
        "total_h": total_h,
    }


# ---------------------------------------------------------------------------
# Shared components
# ---------------------------------------------------------------------------
def draw_section_header(
    draw: ImageDraw.ImageDraw,
    y: float,
    title: str,
    caption: str,
    accent: tuple[int, int, int] = CYAN,
) -> None:
    draw.rectangle(
        [(px(MARGIN_X), px(y + 2)), (px(MARGIN_X + 3), px(y + 14))],
        fill=accent,
    )
    draw_tracked(
        draw,
        (MARGIN_X + 12, y),
        title,
        load_font("num-bold", px(13)),
        TEXT,
        tracking=1.5,
    )
    draw_tracked(
        draw,
        (CANVAS_W - MARGIN_X, y + 2),
        caption,
        load_font("num-semi", px(9)),
        TEXT_MUTED,
        tracking=1.1,
        anchor="ra",
    )
    draw.line(
        [(px(MARGIN_X), px(y + 24)), (px(CANVAS_W - MARGIN_X), px(y + 24))],
        fill=HAIRLINE,
        width=max(1, px(1)),
    )


def draw_grade_badge(
    draw: ImageDraw.ImageDraw,
    x: float,
    y: float,
    grade_name: str,
    size: float = 10,
) -> float:
    if not grade_name or grade_name in ("No Grade", "—"):
        grade_name = "—"
    style = GRADE_STYLES.get(
        grade_name,
        {"bg": (24, 31, 44), "fg": TEXT_MUTED, "border": (52, 66, 88)},
    )
    font = load_font("num-bold", px(size))
    w = lw(draw, grade_name, font) + 10
    h = 16
    draw.rounded_rectangle(
        [(px(x), px(y)), (px(x + w), px(y + h))],
        radius=px(3),
        fill=style["bg"],
        outline=style["border"],
        width=max(1, px(0.8)),
    )
    draw_text(draw, (x + 5, y + 2), grade_name, font, style["fg"])
    return w


def draw_diff_tag(
    draw: ImageDraw.ImageDraw,
    x: float,
    y: float,
    label: str,
    level: str,
    mtype: int,
    size: float = 10,
) -> float:
    text = f"{label} {level}"
    font = load_font("num-bold", px(size))
    w = lw(draw, text, font) + 10
    h = 16
    fill = hex_to_rgb(difficulty_color(mtype))
    draw.rounded_rectangle([(px(x), px(y)), (px(x + w), px(y + h))], radius=px(3), fill=fill)
    draw_text(draw, (x + 5, y + 2), text, font, (8, 10, 14))
    return w


def draw_lamp(
    draw: ImageDraw.ImageDraw,
    x: float,
    y: float,
    clear_name: str,
    size: float = 8,
) -> float:
    entry = LAMP_STYLES.get(clear_name)
    if not entry:
        return 0.0
    label = str(entry["text"])
    font = load_font("num-bold", px(size))
    w = lw(draw, label, font) + 8
    h = 14
    draw.rounded_rectangle(
        [(px(x), px(y)), (px(x + w), px(y + h))],
        radius=px(2),
        fill=entry["bg"],
        outline=entry["fg"],
        width=max(1, px(0.8)),
    )
    draw_text(draw, (x + 4, y + 2), label, font, entry["fg"])
    return w
