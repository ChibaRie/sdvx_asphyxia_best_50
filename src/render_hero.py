"""Hero, VOLFORCE spectrum and summary stats for the B50 poster."""
from __future__ import annotations

from typing import Any

from PIL import Image, ImageDraw, ImageFilter

from b50_layout import CANVAS_W, MARGIN_X, TOP3_ACCENTS, lw
from render_theme import (
    BORDER,
    CYAN,
    GOLD,
    MAGENTA,
    SS,
    TEXT,
    TEXT_FAINT,
    TEXT_MUTED,
    draw_chamfer,
    draw_text,
    draw_tracked,
    ellipsize,
    has_cjk,
    load_font,
    load_hero_art,
    paint_key_art_fallback,
    px,
    text_width,
    tracked_width,
)


def paint_hero_art(canvas: Image.Image, background_path: str | None) -> None:
    box = (CANVAS_W - MARGIN_X - 360, 0, 360, 360)
    loaded = load_hero_art(360, background_path)
    if loaded is None:
        paint_key_art_fallback(canvas, box)
        return
    art, mask = loaded
    canvas.paste(art, (px(box[0]), px(box[1])), mask)


def draw_hero(
    canvas: Image.Image,
    draw: ImageDraw.ImageDraw,
    rows: list[dict],
    player_name: str,
    total_vf: float,
    skill: str,
    stats: dict[str, Any],
    source_label: str,
    background_path: str | None,
) -> None:
    paint_hero_art(canvas, background_path)

    # Eyebrow
    draw.polygon(
        [(px(40), px(38)), (px(44), px(34)), (px(48), px(38)), (px(44), px(42))],
        fill=CYAN,
    )
    eyebrow_font = load_font("num-semi", px(11))
    eyebrow_text = "SOUND VOLTEX EXCEED GEAR"
    draw_tracked(draw, (56, 30), eyebrow_text, eyebrow_font, (126, 176, 198), tracking=1.8)
    eyebrow_w = tracked_width(draw, eyebrow_text, eyebrow_font, 1.8) / SS
    mark_x = 56 + eyebrow_w + 9
    draw.polygon(
        [(px(mark_x), px(33)), (px(mark_x + 9), px(33)), (px(mark_x + 4.5), px(40))],
        fill=CYAN,
    )
    draw.line([(px(300), px(34)), (px(316), px(34))], fill=(52, 86, 104), width=max(1, px(1)))
    draw_tracked(
        draw,
        (324, 30),
        "BEST 50 / VOLFORCE ARCHIVE",
        load_font("num-semi", px(9)),
        MAGENTA,
        tracking=1.5,
    )

    # Player identity
    name_size = 52 if has_cjk(player_name) else 64
    name_font = load_font("cjk-bold" if has_cjk(player_name) else "num-xbold", px(name_size))
    name = ellipsize(draw, player_name or "PLAYER", name_font, px(520))
    draw_text(draw, (40, 54), name, name_font, TEXT)
    name_w = text_width(draw, name, name_font) / SS

    badge_text = f"SKILL · {skill}" if skill else "EXCEED GEAR"
    badge_font = load_font("num-bold", px(10))
    badge_w = lw(draw, badge_text, badge_font) + 18
    badge_x = min(40 + name_w + 18, 620)
    draw_chamfer(
        draw,
        (badge_x, 82, badge_w, 22),
        fill=(30, 14, 28),
        outline=(112, 38, 88),
        width=0.8,
        cut=4,
    )
    draw_tracked(draw, (badge_x + 9, 87), badge_text, badge_font, (255, 178, 214), tracking=1.0)

    draw_tracked(
        draw,
        (40, 122),
        "PERSONAL VOLFORCE ARCHIVE · TOP 50",
        load_font("num-semi", px(9)),
        TEXT_FAINT,
        tracking=1.4,
    )

    # Total VOLFORCE
    draw_tracked(
        draw,
        (40, 144),
        "TOTAL VOLFORCE",
        load_font("num-bold", px(11)),
        (112, 178, 198),
        tracking=2.0,
    )
    vf_font = load_font("num-xbold", px(108))
    vf_text = f"{float(total_vf):.3f}" if isinstance(total_vf, (int, float)) else str(total_vf)
    vf_text = ellipsize(draw, vf_text, vf_font, px(420))
    vf_w = text_width(draw, vf_text, vf_font) / SS

    glow = Image.new("RGBA", (px(vf_w + 60), px(150)), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    glow_draw.text((px(30), px(8)), vf_text, font=vf_font, fill=(*CYAN, 170), anchor="la")
    glow = glow.filter(ImageFilter.GaussianBlur(px(13)))
    canvas.paste(glow, (px(40 - 30), px(148 - 8)), glow)
    draw_text(draw, (40, 148), vf_text, vf_font, CYAN)
    draw_tracked(
        draw,
        (40 + vf_w + 12, 206),
        "VF",
        load_font("num-bold", px(14)),
        (54, 132, 158),
        tracking=1.2,
    )
    draw_tracked(
        draw,
        (40, 270),
        f"{stats['count']} TRACKS  ·  TOP {min(50, stats['count'])}  ·  {source_label}",
        load_font("num-semi", px(9)),
        TEXT_MUTED,
        tracking=1.0,
    )

    draw_spectrum(canvas, draw, rows, stats, 600, 150, 570, 126)
    draw_hero_stats(draw, stats, 40, 306, 1140)


def draw_spectrum(
    canvas: Image.Image,
    draw: ImageDraw.ImageDraw,
    rows: list[dict],
    stats: dict[str, Any],
    x: float,
    y: float,
    w: float,
    h: float,
) -> None:
    draw_tracked(
        draw,
        (x, y - 24),
        "VOLFORCE SPECTRUM",
        load_font("num-bold", px(10)),
        (126, 176, 198),
        tracking=1.5,
    )
    draw_tracked(
        draw,
        (x + w, y - 23),
        f"DEVIATION FROM AVG {stats['avg_vf']:.1f}",
        load_font("num-semi", px(8)),
        TEXT_FAINT,
        tracking=0.8,
        anchor="ra",
    )

    if not rows:
        draw.line([(px(x), px(y + h / 2)), (px(x + w), px(y + h / 2))], fill=BORDER, width=px(1))
        return

    devs = [float(r.get("volforce", 0.0) or 0.0) - stats["avg_vf"] for r in rows]
    max_dev = max((abs(d) for d in devs), default=0.0) or 1.0
    mid = h * 0.52
    slot = w / len(rows)
    bar_w = max(2.4, slot * 0.58)

    # Dashed average baseline
    dash = 5.0
    cursor = 0.0
    while cursor < w:
        draw.line(
            [(px(x + cursor), px(y + mid)), (px(x + min(cursor + dash, w)), px(y + mid))],
            fill=(38, 58, 80),
            width=max(1, px(1)),
        )
        cursor += dash * 2

    layer = Image.new("RGBA", (px(w) + px(8), px(h) + px(8)), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    glow_layer = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow_layer)

    for index, dev in enumerate(devs):
        bar_h = dev / max_dev * (h * 0.40)
        bx = index * slot + (slot - bar_w) / 2
        if index < 3:
            color = TOP3_ACCENTS[index]
        elif dev >= 0:
            color = CYAN
        else:
            color = (44, 78, 108)
        alpha = 235 if index < 3 else (185 if dev >= 0 else 150)
        if bar_h >= 0:
            top, bottom = mid - bar_h, mid
        else:
            top, bottom = mid, mid + abs(bar_h)
        ld.rectangle(
            [(px(bx), px(top)), (px(bx + bar_w), px(bottom))],
            fill=(*color, alpha),
        )
        cap_y = top if bar_h >= 0 else bottom
        ld.line(
            [(px(bx), px(cap_y)), (px(bx + bar_w), px(cap_y))],
            fill=(*color, 255),
            width=max(1, px(1)),
        )
        if index < 3:
            gd.rectangle(
                [(px(bx), px(top)), (px(bx + bar_w), px(bottom))],
                fill=(*color, 150),
            )

    glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(px(6)))
    canvas.paste(glow_layer, (px(x) - px(4), px(y) - px(4)), glow_layer)
    canvas.paste(layer, (px(x) - px(4), px(y) - px(4)), layer)

    tick_font = load_font("num-semi", px(8))
    for rank_no in (1, 10, 20, 30, 40, 50):
        if rank_no > len(rows):
            continue
        tx = x + (rank_no - 1) * slot + slot / 2
        draw.text(
            (px(tx), px(y + h + 8)),
            f"#{rank_no:02d}",
            font=tick_font,
            fill=TEXT_FAINT,
            anchor="ma",
        )


def draw_hero_stats(
    draw: ImageDraw.ImageDraw,
    stats: dict[str, Any],
    x: float,
    y: float,
    width: float,
) -> None:
    values = [
        ("TRACKS", f"{stats['count']} / 50"),
        ("TOP VF", f"{stats['top_vf']:.1f}"),
        ("AVG VF", f"{stats['avg_vf']:.1f}"),
        ("S RANK", f"{stats['s_count']}"),
    ]
    col_w = width / len(values)
    label_font = load_font("num-semi", px(9))
    value_font = load_font("num-bold", px(24))
    for index, (label, value) in enumerate(values):
        cx = x + index * col_w
        if index > 0:
            draw.line(
                [(px(cx - 12), px(y + 2)), (px(cx - 12), px(y + 38))],
                fill=(28, 40, 58),
                width=max(1, px(1)),
            )
        draw_tracked(draw, (cx, y), label, label_font, TEXT_MUTED, tracking=1.3)
        if index == 1:
            value_color = CYAN
        elif index == 3:
            value_color = GOLD if stats["s_count"] > 0 else TEXT_MUTED
        else:
            value_color = TEXT
        draw_text(draw, (cx, y + 14), value, value_font, value_color)
