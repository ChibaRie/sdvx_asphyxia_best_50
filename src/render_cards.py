"""Podium, runlist and distribution panel for the B50 poster."""
from __future__ import annotations

from typing import Any

from PIL import Image, ImageDraw

from b50_layout import (
    CARD_GAP_X,
    CARD_GAP_Y,
    CARD_H,
    CARD_W,
    COLS,
    DIFF_LABEL_COLORS,
    GRADE_ORDER,
    GRID_X,
    MARGIN_X,
    PODIUM_LABEL_Y,
    PODIUM_TOP,
    RUNLIST_LABEL_Y,
    RUNLIST_TOP,
    TOP3_ACCENTS,
    TOP3_FILLS,
    TOP3_LABELS,
    CANVAS_W,
    draw_diff_tag,
    draw_grade_badge,
    draw_lamp,
    draw_section_header,
    fmt_pct,
    fmt_vf,
    load_or_create_cover,
    lw,
)
from render_theme import (
    BORDER,
    BORDER_STRONG,
    CYAN,
    CYAN_SOFT,
    GRADE_STYLES,
    SURFACE,
    SURFACE_RAISED,
    TEXT,
    TEXT_FAINT,
    TEXT_MUTED,
    TEXT_SECONDARY,
    draw_chamfer,
    draw_text,
    draw_tracked,
    load_font,
    px,
    rounded_mask,
    wrap_text,
)


# ---------------------------------------------------------------------------
# Podium
# ---------------------------------------------------------------------------
def draw_podium(
    canvas: Image.Image,
    draw: ImageDraw.ImageDraw,
    rows: list[dict],
    stats: dict[str, Any],
    layout: dict[str, Any],
) -> None:
    if not rows:
        draw_section_header(draw, PODIUM_LABEL_Y, "TOP 3 / PODIUM", "NO SCORE DATA")
        draw_chamfer(
            draw,
            (MARGIN_X, PODIUM_TOP, CANVAS_W - MARGIN_X * 2, 150),
            fill=SURFACE,
            outline=BORDER,
            width=1,
            cut=12,
        )
        draw_tracked(
            draw,
            (CANVAS_W / 2, PODIUM_TOP + 52),
            "NO SCORE DATA  ·  IMPORT AN ASPHYXIA SAVE OR RUN --DEMO",
            load_font("num-semi", px(11)),
            TEXT_MUTED,
            tracking=0.8,
            anchor="ma",
        )
        return

    total = sum(float(r.get("volforce", 0.0) or 0.0) for r in rows[:3]) or 1.0
    draw_section_header(
        draw,
        PODIUM_LABEL_Y,
        "TOP 3 / PODIUM",
        "HIGHEST VOLFORCE CONTRIBUTORS",
        TOP3_ACCENTS[0],
    )
    for index, rect in enumerate(layout["podium_rects"]):
        row = rows[index]
        share = float(row.get("volforce", 0.0) or 0.0) / total * 100.0
        draw_podium_card(canvas, draw, row, index + 1, rect, share, stats)


def draw_podium_card(
    canvas: Image.Image,
    draw: ImageDraw.ImageDraw,
    row: dict,
    rank: int,
    rect: tuple[float, float, float, float],
    share: float,
    stats: dict[str, Any],
) -> None:
    x, y, w, h = rect
    accent = TOP3_ACCENTS[rank - 1]
    fill = TOP3_FILLS[rank - 1]
    border = tuple(int(c * 0.55) for c in accent)
    draw_chamfer(draw, (x, y, w, h), fill=fill, outline=border, width=1.2, cut=14)
    draw.rectangle(
        [(px(x + 1), px(y + 22)), (px(x + 3), px(y + h - 22))],
        fill=accent,
    )

    cover_side = 176 if rank == 1 else 148
    cx, cy = x + 16, y + 16
    cover = load_or_create_cover(
        row.get("cover_path"),
        cover_side,
        int(row.get("type", 0) or 0),
        str(row.get("label", "?")),
        load_font("num-bold", px(9)),
    )
    mask = rounded_mask(cover_side, 8)
    canvas.paste(cover, (px(cx), px(cy)), mask)
    draw.rounded_rectangle(
        [(px(cx), px(cy)), (px(cx + cover_side) - 1, px(cy + cover_side) - 1)],
        radius=px(8),
        outline=accent,
        width=max(1, px(0.8)),
    )

    # Rank medallion
    med = 46 if rank == 1 else 40
    draw_chamfer(
        draw,
        (cx, cy, med, med),
        fill=(12, 11, 14),
        outline=accent,
        width=1.1,
        cut=6,
    )
    draw.text(
        (px(cx + med / 2), px(cy + med / 2 - 1)),
        f"#{rank:02d}",
        font=load_font("num-xbold", px(16 if rank == 1 else 14)),
        fill=accent,
        anchor="mm",
    )

    dx = cx + cover_side + 18
    dw = x + w - 16 - dx
    title_font = load_font("cjk", px(22 if rank == 1 else 20))
    title_lines = wrap_text(
        draw,
        str(row.get("title", "Unknown")),
        title_font,
        px(dw),
        2,
    )
    line_h = 26 if rank == 1 else 24

    draw_tracked(
        draw,
        (dx, y + 12),
        TOP3_LABELS[rank - 1],
        load_font("num-bold", px(9)),
        accent,
        tracking=1.4,
    )
    for line_index, line in enumerate(title_lines):
        draw_text(draw, (dx, y + 26 + line_index * line_h), line, title_font, TEXT)

    meta_y = y + 26 + 2 * line_h + 6
    tag_w = draw_diff_tag(
        draw,
        dx,
        meta_y,
        str(row.get("label", "?")),
        str(row.get("level", "?")),
        int(row.get("type", 0) or 0),
        10,
    )
    grade_w = draw_grade_badge(draw, dx + tag_w + 6, meta_y, str(row.get("grade_name", "")), 10)
    draw_lamp(draw, dx + tag_w + grade_w + 12, meta_y + 1, str(row.get("clear_name", "")), 9)

    score_y = meta_y + 22
    score_font = load_font("num-bold", px(17 if rank == 1 else 15))
    score_str = f"{int(row.get('score', 0) or 0):,}"
    draw_text(draw, (dx, score_y), score_str, score_font, TEXT_SECONDARY)
    draw_text(
        draw,
        (dx + dw, score_y + 3),
        f"EX {int(row.get('exscore', 0) or 0)}",
        load_font("num", px(10)),
        TEXT_MUTED,
        anchor="ra",
    )

    vf_y = y + h - 62
    draw_tracked(
        draw,
        (dx, vf_y - 12),
        "VOLFORCE",
        load_font("num-semi", px(8)),
        TEXT_FAINT,
        tracking=1.2,
    )
    vf_font = load_font("num-xbold", px(44 if rank == 1 else 36))
    draw_text(draw, (dx, vf_y), fmt_vf(row.get("volforce", 0.0)), vf_font, CYAN)
    draw_text(
        draw,
        (dx + dw, vf_y + (18 if rank == 1 else 14)),
        f"{share:.2f}% OF TOP 3",
        load_font("num-semi", px(9)),
        CYAN_SOFT,
        anchor="ra",
    )

    bar_x, bar_y = dx, y + h - 16
    draw.rectangle([(px(bar_x), px(bar_y)), (px(bar_x + dw), px(bar_y + 3))], fill=(28, 38, 54))
    vf_ratio = float(row.get("volforce", 0.0) or 0.0) / max(1.0, stats["top_vf"])
    draw.rectangle(
        [(px(bar_x), px(bar_y)), (px(bar_x + dw * vf_ratio), px(bar_y + 3))],
        fill=accent,
    )


# ---------------------------------------------------------------------------
# Runlist
# ---------------------------------------------------------------------------
def draw_runlist(
    canvas: Image.Image,
    draw: ImageDraw.ImageDraw,
    rows: list[dict],
    stats: dict[str, Any],
    layout: dict[str, Any],
) -> None:
    runlist = rows[layout["podium_count"]:]
    if not runlist:
        return
    start_rank = layout["podium_count"] + 1
    end_rank = layout["podium_count"] + len(runlist)
    draw_section_header(
        draw,
        RUNLIST_LABEL_Y,
        f"RANKS {start_rank:02d}-{end_rank:02d}",
        f"{len(runlist)} TRACKS  ·  SORTED BY VOLFORCE",
        CYAN,
    )

    for index, row in enumerate(runlist):
        col = index % COLS
        line = index // COLS
        x = GRID_X + col * (CARD_W + CARD_GAP_X)
        y = RUNLIST_TOP + line * (CARD_H + CARD_GAP_Y)
        draw_song_card(canvas, draw, row, start_rank + index, x, y, stats)

    if layout["summary_mode"] == "inline":
        line = (len(runlist) - 1) // COLS
        x = GRID_X + layout["rem"] * (CARD_W + CARD_GAP_X)
        y = RUNLIST_TOP + line * (CARD_H + CARD_GAP_Y)
        w = layout["summary_slots"] * CARD_W + (layout["summary_slots"] - 1) * CARD_GAP_X
        draw_summary_panel(draw, rows, stats, x, y, w, CARD_H)
    elif layout["summary_mode"] == "row":
        y = RUNLIST_TOP + layout["run_rows"] * (CARD_H + CARD_GAP_Y)
        draw_summary_panel(
            draw,
            rows,
            stats,
            GRID_X,
            y,
            COLS * CARD_W + (COLS - 1) * CARD_GAP_X,
            CARD_H,
        )


def draw_song_card(
    canvas: Image.Image,
    draw: ImageDraw.ImageDraw,
    row: dict,
    rank: int,
    x: float,
    y: float,
    stats: dict[str, Any],
) -> None:
    draw_chamfer(draw, (x, y, CARD_W, CARD_H), fill=SURFACE, outline=BORDER, width=1, cut=8)
    draw.line(
        [(px(x + 12), px(y + 1)), (px(x + CARD_W - 12), px(y + 1))],
        fill=(33, 46, 66),
        width=max(1, px(0.8)),
    )
    if rank <= 10:
        draw.rectangle([(px(x + 1), px(y + 14)), (px(x + 3), px(y + CARD_H - 14))], fill=CYAN)

    jacket = 100
    jx, jy = x + 10, y + 14
    cover = load_or_create_cover(
        row.get("cover_path"),
        jacket,
        int(row.get("type", 0) or 0),
        str(row.get("label", "?")),
        load_font("num-bold", px(8)),
    )
    mask = rounded_mask(jacket, 6)
    canvas.paste(cover, (px(jx), px(jy)), mask)
    draw.rounded_rectangle(
        [(px(jx), px(jy)), (px(jx + jacket) - 1, px(jy + jacket) - 1)],
        radius=px(6),
        outline=(44, 60, 84),
        width=max(1, px(0.7)),
    )

    rank_text = f"#{rank:02d}"
    rank_font = load_font("num-bold", px(10))
    rank_w = lw(draw, rank_text, rank_font) + 8
    draw.rounded_rectangle(
        [(px(jx + 3), px(jy + 3)), (px(jx + 3 + rank_w), px(jy + 18))],
        radius=px(2),
        fill=(10, 14, 22) if rank > 10 else (7, 20, 30),
        outline=CYAN if rank <= 10 else (58, 74, 96),
        width=max(1, px(0.7)),
    )
    draw_text(
        draw,
        (jx + 7, jy + 5),
        rank_text,
        rank_font,
        CYAN if rank <= 10 else TEXT_SECONDARY,
    )

    dx = jx + jacket + 10
    dw = x + CARD_W - 10 - dx
    title_font = load_font("cjk", px(14))
    title_lines = wrap_text(draw, str(row.get("title", "Unknown")), title_font, px(dw), 2)
    for line_index, line in enumerate(title_lines):
        draw_text(draw, (dx, y + 10 + line_index * 17), line, title_font, TEXT)

    meta_y = y + 48
    tag_w = draw_diff_tag(
        draw,
        dx,
        meta_y,
        str(row.get("label", "?")),
        str(row.get("level", "?")),
        int(row.get("type", 0) or 0),
        10,
    )
    grade_w = draw_grade_badge(draw, dx + tag_w + 6, meta_y, str(row.get("grade_name", "")), 10)
    draw_lamp(draw, dx + tag_w + grade_w + 12, meta_y + 1, str(row.get("clear_name", "")), 9)

    draw_text(
        draw,
        (dx + dw, y + 70),
        f"{int(row.get('score', 0) or 0):,}",
        load_font("num-semi", px(14)),
        TEXT_SECONDARY,
        anchor="ra",
    )
    draw_text(
        draw,
        (dx, y + 72),
        f"EX {int(row.get('exscore', 0) or 0)}",
        load_font("num", px(9)),
        TEXT_MUTED,
    )

    draw_text(draw, (dx, y + 92), fmt_vf(row.get("volforce", 0.0)), load_font("num-xbold", px(24)), CYAN)
    pct = float(row.get("vf_pct", 0.0) or 0.0)
    draw_text(
        draw,
        (dx + dw, y + 100),
        fmt_pct(pct),
        load_font("num-semi", px(9)),
        CYAN_SOFT,
        anchor="ra",
    )

    bar_y = y + CARD_H - 10
    draw.rectangle([(px(dx), px(bar_y)), (px(dx + dw), px(bar_y + 2))], fill=(24, 34, 50))
    if stats["max_pct"] > 0:
        ratio = min(1.0, pct / stats["max_pct"])
        draw.rectangle(
            [(px(dx), px(bar_y)), (px(dx + dw * ratio), px(bar_y + 2))],
            fill=CYAN if rank <= 10 else (52, 144, 172),
        )


# ---------------------------------------------------------------------------
# Distribution panel
# ---------------------------------------------------------------------------
def draw_summary_panel(
    draw: ImageDraw.ImageDraw,
    rows: list[dict],
    stats: dict[str, Any],
    x: float,
    y: float,
    w: float,
    h: float,
) -> None:
    draw_chamfer(draw, (x, y, w, h), fill=SURFACE_RAISED, outline=BORDER_STRONG, width=1, cut=8)
    draw.rectangle([(px(x + 1), px(y + 14)), (px(x + 3), px(y + h - 14))], fill=CYAN)
    draw_tracked(
        draw,
        (x + 16, y + 10),
        "B50 DISTRIBUTION",
        load_font("num-bold", px(10)),
        TEXT_SECONDARY,
        tracking=1.4,
    )
    draw_tracked(
        draw,
        (x + w - 14, y + 11),
        f"{stats['count']} TRACKS",
        load_font("num-semi", px(8)),
        TEXT_FAINT,
        tracking=1.0,
        anchor="ra",
    )

    col_w = (w - 48) / 3
    col1 = x + 16
    col2 = x + 16 + col_w + 12
    col3 = x + 16 + (col_w + 12) * 2
    label_font = load_font("num-semi", px(8))
    legend_font = load_font("num-semi", px(9))
    top = y + 36

    for sep_x in (col1 + col_w + 6, col2 + col_w + 6):
        draw.line(
            [(px(sep_x), px(y + 34)), (px(sep_x), px(y + h - 26))],
            fill=(28, 40, 58),
            width=max(1, px(1)),
        )

    known_grade_total = sum(stats["grade_counts"].get(grade, 0) for grade in GRADE_ORDER)
    other_grades = max(0, stats["count"] - known_grade_total)
    grade_bar_items = [
        (grade, stats["grade_counts"].get(grade, 0), GRADE_STYLES.get(grade, {}).get("fg", TEXT_MUTED))
        for grade in GRADE_ORDER
    ]
    if other_grades:
        grade_bar_items.append(("—", other_grades, (70, 84, 104)))

    draw_tracked(draw, (col1, top), "GRADE", label_font, TEXT_MUTED, tracking=1.2)
    draw_stacked_bar(
        draw,
        (col1, top + 14, col_w - 8, 8),
        grade_bar_items,
        stats["count"],
    )
    grade_legend = [
        (grade, stats["grade_counts"].get(grade, 0))
        for grade in GRADE_ORDER
        if stats["grade_counts"].get(grade, 0) > 0
    ][:4]
    if other_grades and len(grade_legend) < 4:
        grade_legend.append(("—", other_grades))
    draw_legend(draw, col1, top + 30, col_w - 8, grade_legend, legend_font)

    draw_tracked(draw, (col2, top), "DIFFICULTY", label_font, TEXT_MUTED, tracking=1.2)
    diff_items = sorted(stats["diff_counts"].items(), key=lambda item: (-item[1], item[0]))
    draw_stacked_bar(
        draw,
        (col2, top + 14, col_w - 8, 8),
        [(label, count, DIFF_LABEL_COLORS.get(label, CYAN)) for label, count in diff_items],
        stats["count"],
    )
    draw_legend(draw, col2, top + 30, col_w - 8, diff_items[:4], legend_font)

    draw_tracked(draw, (col3, top), "TOP 3 SHARE", label_font, TEXT_MUTED, tracking=1.2)
    draw_text(
        draw,
        (col3, top + 12),
        f"{stats['top3_share']:.2f}%",
        load_font("num-xbold", px(28)),
        CYAN,
    )
    draw_tracked(
        draw,
        (col3, top + 44),
        "OF TOTAL VOLFORCE",
        load_font("num-semi", px(8)),
        TEXT_FAINT,
        tracking=1.0,
    )
    split_y = top + 60
    split_w = col_w - 12
    draw.rectangle([(px(col3), px(split_y)), (px(col3 + split_w), px(split_y + 5))], fill=(26, 37, 54))
    share_ratio = min(1.0, max(0.0, stats["top3_share"] / 100.0))
    draw.rectangle(
        [(px(col3), px(split_y)), (px(col3 + split_w * share_ratio), px(split_y + 5))],
        fill=TOP3_ACCENTS[0],
    )
    draw_text(
        draw,
        (col3, split_y + 10),
        f"REST {100.0 - stats['top3_share']:.2f}%",
        load_font("num-semi", px(8)),
        TEXT_MUTED,
    )

    draw_tracked(
        draw,
        (x + 16, y + h - 15),
        "GRADE / DIFFICULTY / VF SHARE COMPUTED FROM THE TRACKS ABOVE",
        load_font("num-semi", px(7)),
        TEXT_FAINT,
        tracking=0.8,
    )


def draw_stacked_bar(
    draw: ImageDraw.ImageDraw,
    box: tuple[float, float, float, float],
    items: list[tuple[str, int, tuple[int, int, int]]],
    total: int,
) -> None:
    x, y, w, h = box
    draw.rounded_rectangle(
        [(px(x), px(y)), (px(x + w), px(y + h))],
        radius=px(2),
        fill=(26, 37, 54),
    )
    if total <= 0:
        return
    cursor = x
    for index, (_label, count, color) in enumerate(items):
        if count <= 0:
            continue
        segment = w * count / total
        draw.rectangle(
            [(px(cursor), px(y)), (px(min(x + w, cursor + segment)), px(y + h))],
            fill=color,
        )
        cursor += segment
        if index < len(items) - 1:
            draw.line(
                [(px(cursor), px(y)), (px(cursor), px(y + h))],
                fill=(13, 19, 32),
                width=max(1, px(1)),
            )


def draw_legend(
    draw: ImageDraw.ImageDraw,
    x: float,
    y: float,
    width: float,
    items: list[tuple[str, int]],
    font,
) -> None:
    cursor = x
    for label, count in items:
        color = DIFF_LABEL_COLORS.get(label, GRADE_STYLES.get(label, {}).get("fg", TEXT_MUTED))
        draw.ellipse([(px(cursor), px(y + 3)), (px(cursor + 4), px(y + 7))], fill=color)
        text = f"{label} {count}"
        draw_text(draw, (cursor + 7, y), text, font, TEXT_SECONDARY)
        cursor += lw(draw, text, font) + 18
        if cursor > x + width:
            break
