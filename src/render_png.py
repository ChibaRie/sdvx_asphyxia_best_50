"""Card-grid JPEG renderer for SDVX B50.

Renders top 50 songs into an arcade-styled cyber-obsidian card grid JPEG (1200px width).
Features:
- Futuristic cyber HUD header bar with player avatar emblem, VOLFORCE plaque, and summary metrics.
- 5:2 landscape cards with floating square jackets, rank indicators (#01-#50),
  difficulty badges, score, grade badges, clear lamp, EX score, and VOLFORCE contribution.
- Optimized progressive JPEG output.
"""
from __future__ import annotations

import math
import os
from typing import Any
from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# Layout constants
# ---------------------------------------------------------------------------
CANVAS_W = 1200
MARGIN_X = 20
MARGIN_Y = 20
HEADER_H = 92
CARD_W = 220
CARD_H = 88
JACKET_SIZE = 80
CARD_GAP = 15
COLS = 5
JPEG_QUALITY = 88

# ---------------------------------------------------------------------------
# Color Palette (Cyber Obsidian & Neon Accents)
# ---------------------------------------------------------------------------
BG_COLOR = (12, 14, 20)          # #0c0e14 Deep Obsidian
CARD_BG = (18, 22, 32)           # #121620 Sleek Dark Surface
CARD_BORDER = (34, 40, 56)       # #222838 Subtle Hairline Bezel
HEADER_BG_TOP = (20, 24, 36)
HEADER_BG_BOT = (13, 16, 24)

TEXT_PRIMARY = (255, 255, 255)
TEXT_SECONDARY = (241, 245, 249)
TEXT_MUTED = (148, 163, 184)
VF_CYAN = (0, 240, 255)
VF_PCT_COLOR = (125, 211, 252)

# Difficulty colors (SDVX standard & modern cyber accents)
DIFF_COLORS: dict[int, str] = {
    0: "#10b981",  # NOV: Emerald Mint
    1: "#0ea5e9",  # ADV: Cyber Sky Blue
    2: "#f43f5e",  # EXH: Crimson Rose
    3: "#a855f7",  # INF/GRV/HVN/VVD/XCD/NBL: Electric Purple
    4: "#f59e0b",  # MXM: Radiant Gold/Amber
    5: "#ef4444",  # ULT: Ultimate Red
}

GRADE_STYLES: dict[str, dict[str, tuple[int, int, int]]] = {
    "S":    {"bg": (35, 28, 5),   "fg": (255, 215, 0),   "border": (255, 215, 0)},
    "AAA+": {"bg": (38, 12, 18),  "fg": (255, 77, 109),  "border": (255, 77, 109)},
    "AAA":  {"bg": (38, 12, 18),  "fg": (255, 77, 109),  "border": (255, 77, 109)},
    "AA+":  {"bg": (8, 30, 42),   "fg": (0, 240, 255),   "border": (0, 240, 255)},
    "AA":   {"bg": (8, 30, 42),   "fg": (0, 240, 255),   "border": (0, 240, 255)},
    "A+":   {"bg": (8, 32, 22),   "fg": (16, 185, 129),  "border": (16, 185, 129)},
    "A":    {"bg": (8, 32, 22),   "fg": (16, 185, 129),  "border": (16, 185, 129)},
    "B":    {"bg": (24, 30, 42),  "fg": (148, 163, 184), "border": (148, 163, 184)},
    "C":    {"bg": (24, 30, 42),  "fg": (148, 163, 184), "border": (148, 163, 184)},
    "D":    {"bg": (24, 30, 42),  "fg": (148, 163, 184), "border": (148, 163, 184)},
}

LAMP_STYLES: dict[str, dict[str, Any]] = {
    "PUC":             {"text": "PUC", "fg": (255, 215, 0), "bg": (35, 28, 5)},
    "UC":              {"text": "UC",  "fg": (251, 191, 36), "bg": (35, 25, 5)},
    "MAXXIVE CLEAR":   {"text": "MAX", "fg": (244, 63, 94),  "bg": (35, 10, 15)},
    "EXCESSIVE CLEAR": {"text": "EXC", "fg": (244, 63, 94),  "bg": (35, 10, 15)},
    "EFFECTIVE CLEAR": {"text": "CLR", "fg": (6, 182, 212),  "bg": (10, 28, 36)},
    "PLAYED":          {"text": "PLY", "fg": (148, 163, 184), "bg": (20, 24, 32)},
}

try:
    _RESAMPLE = Image.Resampling.LANCZOS
except AttributeError:  # pragma: no cover
    _RESAMPLE = Image.LANCZOS


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------
def _font(font_path: str, size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Load font with resilient fallbacks across platforms."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        font_path,
        os.path.join(base_dir, "..", "assets", "fonts", "msyh.ttc"),
        os.path.join(base_dir, "assets", "fonts", "msyh.ttc"),
        os.path.join(base_dir, "msyh.ttc"),
        "assets/fonts/msyh.ttc",
        "msyh.ttc",
        "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/simhei.ttf",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/System/Library/Fonts/PingFang.ttc",
    ]
    for p in candidates:
        if p and os.path.isfile(p):
            try:
                return ImageFont.truetype(p, size)
            except OSError:
                continue
    try:
        return ImageFont.truetype("arial.ttf", size)
    except OSError:
        return ImageFont.load_default()


def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    h = hex_color.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]


def format_vf(vf: float, pct: float) -> str:
    """Format the VF value plus its share of total VOLFORCE, e.g. '250.0 ·12.3456%'."""
    return f"{vf} ·{pct:.4f}%"


def _difficulty_color(mtype: int) -> str:
    """Return the hex color for a given difficulty type."""
    return DIFF_COLORS.get(mtype, "#0ea5e9")


def _draw_text_within(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.FreeTypeFont | ImageFont.ImageFont,
    x: int,
    y: int,
    max_w: int,
    fill: tuple[int, int, int],
) -> None:
    """Draw text at (x, y), truncating with '...' if it exceeds max_w."""
    if max_w <= 0 or not text:
        return
    if draw.textlength(text, font=font) <= max_w:
        draw.text((x, y), text, font=font, fill=fill)
        return
    ellipsis = "..."
    low, high = 0, len(text)
    while low < high:
        mid = (low + high + 1) // 2
        if draw.textlength(text[:mid] + ellipsis, font=font) <= max_w:
            low = mid
        else:
            high = mid - 1
    draw.text((x, y), text[:low] + ellipsis, font=font, fill=fill)


def _make_procedural_cover(
    side: int,
    mtype: int,
    label: str,
    font: ImageFont.FreeTypeFont | ImageFont.ImageFont,
) -> Image.Image:
    """Generate a sleek cyber-themed placeholder cover when the cover file is missing."""
    img = Image.new("RGB", (side, side), (15, 18, 26))
    draw = ImageDraw.Draw(img)
    diff_rgb = _hex_to_rgb(_difficulty_color(mtype))

    # Diagonal cyber scanlines
    for i in range(0, side * 2, 8):
        draw.line([(i, 0), (0, i)], fill=(22, 26, 38))

    cx, cy = side // 2, side // 2
    r = 22
    diamond = [(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)]
    draw.polygon(diamond, fill=(24, 29, 44), outline=diff_rgb)

    r2 = 11
    diamond2 = [(cx, cy - r2), (cx + r2, cy), (cx, cy + r2), (cx - r2, cy)]
    draw.polygon(diamond2, fill=diff_rgb)

    txt = label or "SDVX"
    tw = int(draw.textlength(txt, font=font))
    draw.text((cx - tw // 2, side - 18), txt, font=font, fill=diff_rgb)
    return img


def _load_or_create_cover(
    cover_path: str | None,
    side: int,
    mtype: int,
    label: str,
    font: ImageFont.FreeTypeFont | ImageFont.ImageFont,
) -> Image.Image:
    """Load cover image or generate procedural cyber cover."""
    if cover_path and os.path.isfile(cover_path):
        try:
            with Image.open(cover_path) as src:
                return src.convert("RGB").resize((side, side), _RESAMPLE)
        except (OSError, ValueError):
            pass
    return _make_procedural_cover(side, mtype, label, font)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def render_png(
    rows: list[dict],
    player_name: str,
    total_vf: float,
    out_path: str,
    skill: str = "",
    font_path: str = "C:/Windows/Fonts/msyh.ttc",
) -> None:
    """Render rows into a high-end card-grid JPEG at out_path."""
    n = max(1, len(rows))
    grid_rows = math.ceil(n / COLS)
    total_h = HEADER_H + MARGIN_Y + grid_rows * (CARD_H + CARD_GAP) - CARD_GAP + MARGIN_Y

    canvas = Image.new("RGB", (CANVAS_W, total_h), BG_COLOR)
    draw = ImageDraw.Draw(canvas)

    # Typography
    header_name_font = _font(font_path, 25)
    header_title_font = _font(font_path, 10)
    header_vf_font = _font(font_path, 26)
    header_chip_font = _font(font_path, 10)
    stat_val_font = _font(font_path, 16)
    title_font = _font(font_path, 11)
    tag_font = _font(font_path, 9)
    score_font = _font(font_path, 9)
    ex_font = _font(font_path, 8)
    vf_val_font = _font(font_path, 10)
    vf_pct_font = _font(font_path, 8)
    rank_font = _font(font_path, 8)
    grade_font = _font(font_path, 8)

    # ---- 1. Header Bar -----------------------------------------------------
    for y in range(HEADER_H):
        ratio = y / HEADER_H
        r = int(HEADER_BG_TOP[0] * (1 - ratio) + HEADER_BG_BOT[0] * ratio)
        g = int(HEADER_BG_TOP[1] * (1 - ratio) + HEADER_BG_BOT[1] * ratio)
        b = int(HEADER_BG_TOP[2] * (1 - ratio) + HEADER_BG_BOT[2] * ratio)
        draw.line([(0, y), (CANVAS_W, y)], fill=(r, g, b))

    # Cyber accent gradient line (Cyan -> Magenta -> Violet)
    for x in range(CANVAS_W):
        t = x / CANVAS_W
        if t < 0.4:
            p = t / 0.4
            r = int(0 * (1 - p) + 255 * p)
            g = int(240 * (1 - p) + 45 * p)
            b = int(255 * (1 - p) + 135 * p)
        elif t < 0.7:
            p = (t - 0.4) / 0.3
            r = int(255 * (1 - p) + 121 * p)
            g = int(45 * (1 - p) + 40 * p)
            b = int(135 * (1 - p) + 202 * p)
        else:
            p = (t - 0.7) / 0.3
            r = int(121 * (1 - p) + 18 * p)
            g = int(40 * (1 - p) + 22 * p)
            b = int(202 * (1 - p) + 34 * p)
        draw.point((x, HEADER_H - 2), fill=(r, g, b))
        draw.point((x, HEADER_H - 1), fill=(r, g, b))

    # Avatar ring & soundwave emblem
    ax, ay, asize = 24, 14, 64
    draw.ellipse(
        [(ax, ay), (ax + asize, ay + asize)],
        fill=(14, 18, 28), outline=VF_CYAN, width=2,
    )
    cx_a = ax + asize // 2
    cy_a = ay + asize // 2
    for bar_i, bar_h in enumerate([8, 15, 23, 15, 8]):
        bx = cx_a - 14 + bar_i * 7
        draw.rounded_rectangle(
            [(bx, cy_a - bar_h), (bx + 3, cy_a + bar_h)],
            radius=2, fill=VF_CYAN,
        )

    # Player Name
    _draw_text_within(
        draw, player_name, header_name_font,
        104, 16, 340, TEXT_PRIMARY,
    )

    # Dan Skill / Subtitle Badge
    if skill:
        skill_text = f"◆ SKILL: {skill} ◆"
        sk_w = int(draw.textlength(skill_text, font=header_chip_font)) + 16
        draw.rounded_rectangle(
            [(104, 52), (104 + sk_w, 74)],
            radius=4, fill=(26, 22, 42), outline=(168, 85, 247), width=1,
        )
        draw.text((112, 56), skill_text, font=header_chip_font, fill=(216, 180, 254))
    else:
        sub_text = "◆ SOUND VOLTEX EXCEED GEAR ∇ ◆"
        sub_w = int(draw.textlength(sub_text, font=header_chip_font)) + 16
        draw.rounded_rectangle(
            [(104, 52), (104 + sub_w, 74)],
            radius=4, fill=(20, 25, 38), outline=(56, 189, 248), width=1,
        )
        draw.text((112, 56), sub_text, font=header_chip_font, fill=(125, 211, 252))

    # VOLFORCE Center Plaque
    vf_box_x = 460
    draw.rounded_rectangle(
        [(vf_box_x, 14), (vf_box_x + 230, 76)],
        radius=6, fill=(18, 22, 34), outline=(38, 46, 66), width=1,
    )
    draw.rounded_rectangle(
        [(vf_box_x + 2, 16), (vf_box_x + 5, 74)],
        radius=2, fill=VF_CYAN,
    )
    draw.text((vf_box_x + 16, 20), "VOLFORCE", font=header_title_font, fill=(56, 189, 248))
    draw.text((vf_box_x + 16, 36), f"{total_vf:.3f}" if isinstance(total_vf, float) else str(total_vf), font=header_vf_font, fill=VF_CYAN)

    # Right Statistics Panel
    sx = 730
    draw.rounded_rectangle(
        [(sx, 14), (CANVAS_W - 24, 76)],
        radius=6, fill=(18, 22, 34), outline=(38, 46, 66), width=1,
    )
    top_vf_val = f"{rows[0].get('volforce', 0.0):.1f}" if rows else "0.0"
    avg_vf_val = f"{sum(r.get('volforce', 0.0) for r in rows) / len(rows):.1f}" if rows else "0.0"
    stats = [
        ("TRACKS", f"{len(rows)} / 50"),
        ("TOP VF", top_vf_val),
        ("AVG VF", avg_vf_val),
    ]
    col_w = (CANVAS_W - 24 - sx) // 3
    for i, (label, val) in enumerate(stats):
        col_x = sx + i * col_w
        if i > 0:
            draw.line([(col_x, 22), (col_x, 68)], fill=(34, 42, 60))
        draw.text((col_x + 16, 22), label, font=header_title_font, fill=TEXT_MUTED)
        draw.text((col_x + 16, 42), val, font=stat_val_font, fill=TEXT_SECONDARY)

    # ---- 2. Card Grid ------------------------------------------------------
    mask = Image.new("L", (JACKET_SIZE, JACKET_SIZE), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle([(0, 0), (JACKET_SIZE, JACKET_SIZE)], radius=6, fill=255)

    for idx, r in enumerate(rows):
        col = idx % COLS
        row = idx // COLS
        cx = MARGIN_X + col * (CARD_W + CARD_GAP)
        cy = HEADER_H + MARGIN_Y + row * (CARD_H + CARD_GAP)

        # Podium Card Border Highlights
        if idx == 0:
            card_border = (180, 140, 30)
            card_bg = (24, 23, 20)
        elif idx == 1:
            card_border = (120, 135, 155)
            card_bg = (20, 23, 30)
        elif idx == 2:
            card_border = (170, 95, 45)
            card_bg = (25, 21, 20)
        else:
            card_border = CARD_BORDER
            card_bg = CARD_BG

        # Outer card container
        draw.rounded_rectangle(
            [(cx, cy), (cx + CARD_W, cy + CARD_H)],
            radius=8, fill=card_bg, outline=card_border, width=1,
        )

        # Floating Jacket Cover
        jx = cx + 4
        jy = cy + 4
        mtype = r.get("type", 0)
        label_text = r.get("label", "NOV")
        level_text = str(r.get("level", "?"))
        cover_img = _load_or_create_cover(
            r.get("cover_path"), JACKET_SIZE, mtype, label_text, tag_font,
        )
        canvas.paste(cover_img, (jx, jy), mask)

        # Rank Badge on cover
        rank_no = f"#{idx + 1:02d}"
        rw = int(draw.textlength(rank_no, font=rank_font)) + 6
        if idx == 0:
            rb_bg, rb_fg = (25, 20, 5), (255, 215, 0)
        elif idx == 1:
            rb_bg, rb_fg = (20, 24, 35), (226, 232, 240)
        elif idx == 2:
            rb_bg, rb_fg = (30, 18, 10), (251, 146, 60)
        elif idx < 10:
            rb_bg, rb_fg = (10, 25, 38), VF_CYAN
        else:
            rb_bg, rb_fg = (14, 17, 24), TEXT_MUTED

        draw.rounded_rectangle(
            [(jx + 3, jy + 3), (jx + 3 + rw, jy + 16)],
            radius=3, fill=rb_bg, outline=rb_fg, width=1,
        )
        draw.text((jx + 6, jy + 4), rank_no, font=rank_font, fill=rb_fg)

        # Right Data Area (128px width)
        dx = cx + JACKET_SIZE + 10
        dw = CARD_W - JACKET_SIZE - 16

        # Row 1: Title (left) & Grade Badge (right)
        grade_name = r.get("grade_name", "")
        gw = int(draw.textlength(grade_name, font=grade_font)) + 6 if grade_name else 0
        gx = dx + dw - gw
        gy = cy + 5

        if grade_name:
            gstyle = GRADE_STYLES.get(grade_name, {"bg": (24, 30, 42), "fg": TEXT_MUTED, "border": TEXT_MUTED})
            draw.rounded_rectangle(
                [(gx, gy), (gx + gw, gy + 14)],
                radius=3, fill=gstyle["bg"], outline=gstyle["border"], width=1,
            )
            draw.text((gx + 3, gy + 1), grade_name, font=grade_font, fill=gstyle["fg"])

        avail_tw = dw - gw - 4 if grade_name else dw
        _draw_text_within(
            draw, r.get("title", "Unknown"), title_font,
            dx, cy + 5, avail_tw, TEXT_PRIMARY,
        )

        # Row 2: Difficulty Tag (left) & Score (right)
        tag_y = cy + 26
        tag_color = _hex_to_rgb(_difficulty_color(mtype))
        tag_str = f"{label_text} {level_text}"
        tag_w = int(draw.textlength(tag_str, font=tag_font)) + 8
        draw.rounded_rectangle(
            [(dx, tag_y), (dx + tag_w, tag_y + 15)],
            radius=3, fill=tag_color,
        )
        tag_text_color = (0, 0, 0) if mtype in (0, 1, 4) else (255, 255, 255)
        draw.text((dx + 4, tag_y + 2), tag_str, font=tag_font, fill=tag_text_color)

        score_val = r.get("score", 0)
        score_str = f"{score_val:,}"
        sw = int(draw.textlength(score_str, font=score_font))
        draw.text((dx + dw - sw, tag_y + 2), score_str, font=score_font, fill=TEXT_SECONDARY)

        # Row 3: Clear Lamp (left) & EX Score (right)
        r3_y = cy + 47
        clear_name = r.get("clear_name", "")
        lamp_entry = LAMP_STYLES.get(clear_name)
        if lamp_entry:
            l_text = lamp_entry["text"]
            l_fg = lamp_entry["fg"]
            l_bg = lamp_entry["bg"]
            lw = int(draw.textlength(l_text, font=ex_font)) + 6
            draw.rounded_rectangle(
                [(dx, r3_y), (dx + lw, r3_y + 13)],
                radius=2, fill=l_bg, outline=l_fg, width=1,
            )
            draw.text((dx + 3, r3_y + 1), l_text, font=ex_font, fill=l_fg)

        ex_str = f"EX {r.get('exscore', 0)}"
        ew = int(draw.textlength(ex_str, font=ex_font))
        draw.text((dx + dw - ew, r3_y + 1), ex_str, font=ex_font, fill=TEXT_MUTED)

        # Row 4: VOLFORCE (left) & Percentage Share (right)
        r4_y = cy + 67
        vf_val = r.get("volforce", 0.0)
        vf_str = f"{vf_val}"
        pct_val = r.get("vf_pct", 0.0)
        pct_str = f"{pct_val:.4f}%"
        draw.text((dx, r4_y), vf_str, font=vf_val_font, fill=VF_CYAN)
        pw = int(draw.textlength(pct_str, font=vf_pct_font))
        draw.text((dx + dw - pw, r4_y + 2), pct_str, font=vf_pct_font, fill=VF_PCT_COLOR)

    # ---- Save --------------------------------------------------------------
    parent = os.path.dirname(out_path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    canvas.save(out_path, "JPEG", quality=JPEG_QUALITY, optimize=True, progressive=True)
