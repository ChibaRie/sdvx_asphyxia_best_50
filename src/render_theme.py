"""Shared visual system for the SDVX B50 renderer.

This module owns the palette, local typography, shape primitives and the
procedural environment layers. Layout lives in :mod:`render_png`.

The renderer draws at 2x and downsamples once, so every coordinate helper here
works in *logical* pixels and multiplies by :data:`SS` via :func:`px`.
"""
from __future__ import annotations

import os
import sys
from typing import Sequence

from PIL import (
    Image,
    ImageChops,
    ImageDraw,
    ImageEnhance,
    ImageFilter,
    ImageFont,
    ImageOps,
)

# ---------------------------------------------------------------------------
# Canvas scale
# ---------------------------------------------------------------------------
SS = 2


def px(value: float) -> int:
    """Convert a logical pixel value to a device pixel value."""
    return int(round(value * SS))


# ---------------------------------------------------------------------------
# Palette
# ---------------------------------------------------------------------------
BG_DEEP = (7, 9, 14)
BG_HERO_TOP = (12, 17, 27)
BG_HERO_BOT = (7, 9, 14)
SURFACE = (13, 19, 32)
SURFACE_RAISED = (17, 24, 39)
BORDER = (30, 42, 63)
BORDER_STRONG = (44, 60, 88)
HAIRLINE = (20, 30, 45)

TEXT = (244, 248, 255)
TEXT_SECONDARY = (199, 213, 232)
TEXT_MUTED = (129, 148, 173)
TEXT_FAINT = (111, 130, 153)

CYAN = (56, 232, 255)
CYAN_SOFT = (125, 211, 252)
MAGENTA = (255, 61, 154)
GOLD = (255, 200, 87)
ICE = (207, 232, 255)
COPPER = (255, 154, 107)
GREEN = (74, 222, 128)
RED = (255, 99, 132)

DIFF_COLORS: dict[int, str] = {
    0: "#34d399",  # NOV: emerald
    1: "#38bdf8",  # ADV: sky
    2: "#fb7185",  # EXH: rose
    3: "#a78bfa",  # INF/GRV/HVN/VVD/XCD/NBL: violet
    4: "#fbbf24",  # MXM: amber
    5: "#ef4444",  # ULT: red
}

GRADE_STYLES: dict[str, dict[str, tuple[int, int, int]]] = {
    "S": {"bg": (36, 30, 9), "fg": GOLD, "border": (118, 88, 22)},
    "AAA+": {"bg": (42, 14, 25), "fg": (255, 122, 145), "border": (108, 40, 60)},
    "AAA": {"bg": (38, 13, 23), "fg": (255, 113, 138), "border": (96, 36, 56)},
    "AA+": {"bg": (8, 31, 44), "fg": CYAN, "border": (22, 84, 110)},
    "AA": {"bg": (8, 28, 40), "fg": CYAN_SOFT, "border": (20, 74, 98)},
    "A+": {"bg": (8, 35, 25), "fg": GREEN, "border": (24, 94, 62)},
    "A": {"bg": (8, 32, 23), "fg": GREEN, "border": (22, 84, 56)},
    "B": {"bg": (24, 31, 44), "fg": TEXT_MUTED, "border": (52, 66, 88)},
    "C": {"bg": (23, 29, 42), "fg": TEXT_MUTED, "border": (48, 60, 80)},
    "D": {"bg": (22, 27, 39), "fg": TEXT_FAINT, "border": (44, 56, 74)},
}

LAMP_STYLES: dict[str, dict[str, object]] = {
    "PUC": {"text": "PUC", "fg": GOLD, "bg": (34, 28, 8)},
    "UC": {"text": "UC", "fg": (251, 191, 36), "bg": (33, 24, 6)},
    "MAXXIVE CLEAR": {"text": "MAX", "fg": RED, "bg": (34, 11, 17)},
    "EXCESSIVE CLEAR": {"text": "EXC", "fg": RED, "bg": (32, 11, 16)},
    "EFFECTIVE CLEAR": {"text": "CLR", "fg": CYAN_SOFT, "bg": (9, 27, 37)},
    "PLAYED": {"text": "PLY", "fg": TEXT_MUTED, "bg": (20, 26, 36)},
}


def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    h = hex_color.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]


def difficulty_color(mtype: int) -> str:
    return DIFF_COLORS.get(mtype, "#38bdf8")


# ---------------------------------------------------------------------------
# Local fonts
# ---------------------------------------------------------------------------
_NUM_FONT_FILES = {
    "num": "BarlowCondensed-Regular.ttf",
    "num-semi": "BarlowCondensed-SemiBold.ttf",
    "num-bold": "BarlowCondensed-Bold.ttf",
    "num-xbold": "BarlowCondensed-ExtraBold.ttf",
}

_CJK_OVERRIDE: str | None = None
_CJK_BOLD_OVERRIDE: str | None = None
_FONT_CACHE: dict[tuple[str, int], ImageFont.FreeTypeFont | ImageFont.ImageFont] = {}


def resource_root() -> str:
    """Return the asset root for source runs and PyInstaller one-file runs."""
    bundled = getattr(sys, "_MEIPASS", None)
    if bundled:
        return bundled
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def asset_path(*parts: str) -> str:
    return os.path.join(resource_root(), "assets", *parts)


def set_cjk_font(path: str | None, bold_path: str | None = None) -> None:
    """Tell the font loader which CJK face the caller resolved."""
    global _CJK_OVERRIDE, _CJK_BOLD_OVERRIDE
    if path != _CJK_OVERRIDE or bold_path != _CJK_BOLD_OVERRIDE:
        _FONT_CACHE.clear()
    _CJK_OVERRIDE = path
    _CJK_BOLD_OVERRIDE = bold_path


def _cjk_candidates() -> list[str]:
    here = os.path.dirname(os.path.abspath(__file__))
    return [
        p for p in (
            _CJK_OVERRIDE or "",
            asset_path("fonts", "msyh.ttc"),
            os.path.join(here, "..", "assets", "fonts", "msyh.ttc"),
            os.path.join(here, "assets", "fonts", "msyh.ttc"),
            "C:/Windows/Fonts/msyh.ttc",
            "C:/Windows/Fonts/simhei.ttf",
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
            "/System/Library/Fonts/PingFang.ttc",
        ) if p
    ]


def _cjk_bold_candidates() -> list[str]:
    here = os.path.dirname(os.path.abspath(__file__))
    return [
        p for p in (
            _CJK_BOLD_OVERRIDE or "",
            asset_path("fonts", "msyhbd.ttc"),
            os.path.join(here, "..", "assets", "fonts", "msyhbd.ttc"),
            "C:/Windows/Fonts/msyhbd.ttc",
        ) if p
    ] + _cjk_candidates()


def load_font(role: str, size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Load a cached font by role at a device-pixel size."""
    key = (role, size)
    cached = _FONT_CACHE.get(key)
    if cached is not None:
        return cached

    if role in _NUM_FONT_FILES:
        candidates = [
            asset_path("fonts", _NUM_FONT_FILES[role]),
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "fonts", _NUM_FONT_FILES[role]),
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "fonts", _NUM_FONT_FILES[role]),
        ] + _cjk_candidates()
    elif role == "cjk-bold":
        candidates = _cjk_bold_candidates()
    else:
        candidates = _cjk_candidates()

    font: ImageFont.FreeTypeFont | ImageFont.ImageFont
    for path in candidates:
        if path and os.path.isfile(path):
            try:
                font = ImageFont.truetype(path, size)
                _FONT_CACHE[key] = font
                return font
            except OSError:
                continue
    try:
        font = ImageFont.load_default(size)
    except TypeError:  # pragma: no cover - very old Pillow
        font = ImageFont.load_default()
    _FONT_CACHE[key] = font
    return font


def has_cjk(text: str) -> bool:
    for ch in text:
        code = ord(ch)
        if (0x2E80 <= code <= 0x9FFF
                or 0x3040 <= code <= 0x30FF
                or 0xAC00 <= code <= 0xD7AF
                or 0xF900 <= code <= 0xFAFF):
            return True
    return False




# ---------------------------------------------------------------------------
# Text primitives
# ---------------------------------------------------------------------------
def text_width(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont | ImageFont.ImageFont) -> float:
    return draw.textlength(text, font=font)


def ellipsize(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.FreeTypeFont | ImageFont.ImageFont,
    max_width: float,
    ellipsis: str = "…",
) -> str:
    """Trim a string until it fits max_width."""
    if max_width <= 0 or not text:
        return ""
    if text_width(draw, text, font) <= max_width:
        return text
    low, high = 0, len(text)
    while low < high:
        mid = (low + high + 1) // 2
        if text_width(draw, text[:mid] + ellipsis, font) <= max_width:
            low = mid
        else:
            high = mid - 1
    return text[:low] + ellipsis


def wrap_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.FreeTypeFont | ImageFont.ImageFont,
    max_width: float,
    max_lines: int = 2,
) -> list[str]:
    """Greedy wrap that respects spaces for Latin and breaks anywhere for CJK."""
    text = text.strip()
    if not text or max_lines <= 0:
        return []

    lines: list[str] = []
    current = ""
    consumed = 0
    broke = False

    for index, ch in enumerate(text):
        trial = current + ch
        if text_width(draw, trial, font) <= max_width:
            current = trial
            consumed = index + 1
            continue

        if current and not has_cjk(current) and " " in current:
            split_at = current.rfind(" ")
            lines.append(current[:split_at].rstrip())
            current = current[split_at + 1:] + ch
        else:
            if current:
                lines.append(current.rstrip())
            current = ch
        consumed = index + 1

        if len(lines) >= max_lines:
            broke = True
            break

    if not broke and current and len(lines) < max_lines:
        lines.append(current.rstrip())
    elif broke:
        remainder = text[consumed - len(current):]
        last = (lines[-1] if lines else "") + (current if current else "")
        lines = lines[:max_lines - 1]
        lines.append(ellipsize(draw, last + remainder, font, max_width))
    return lines[:max_lines]


def draw_text(
    draw: ImageDraw.ImageDraw,
    xy: tuple[float, float],
    text: str,
    font: ImageFont.FreeTypeFont | ImageFont.ImageFont,
    fill: tuple[int, int, int] | tuple[int, int, int, int],
    anchor: str = "la",
) -> None:
    draw.text((px(xy[0]), px(xy[1])), text, font=font, fill=fill, anchor=anchor)


def tracked_width(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.FreeTypeFont | ImageFont.ImageFont,
    tracking: float,
) -> float:
    if not text:
        return 0.0
    total = sum(text_width(draw, ch, font) for ch in text)
    return total + tracking * (len(text) - 1)


def draw_tracked(
    draw: ImageDraw.ImageDraw,
    xy: tuple[float, float],
    text: str,
    font: ImageFont.FreeTypeFont | ImageFont.ImageFont,
    fill: tuple[int, int, int] | tuple[int, int, int, int],
    tracking: float = 1.0,
    anchor: str = "la",
) -> None:
    """Draw letter-spaced text (used only for short Latin labels)."""
    if not text:
        return
    total = tracked_width(draw, text, font, tracking)
    x, y = xy
    if anchor.startswith("r"):
        x -= total
    elif anchor.startswith("m"):
        x -= total / 2.0
    cursor = px(x)
    for ch in text:
        draw.text((cursor, px(y)), ch, font=font, fill=fill, anchor="la")
        cursor += text_width(draw, ch, font) + px(tracking)


# ---------------------------------------------------------------------------
# Shape primitives
# ---------------------------------------------------------------------------
def chamfer_points(x: float, y: float, w: float, h: float, cut: float) -> list[tuple[int, int]]:
    """A rectangle with the top-left and bottom-right corners cut."""
    return [
        (px(x + cut), px(y)),
        (px(x + w), px(y)),
        (px(x + w), px(y + h - cut)),
        (px(x + w - cut), px(y + h)),
        (px(x), px(y + h)),
        (px(x), px(y + cut)),
    ]


def draw_chamfer(
    draw: ImageDraw.ImageDraw,
    box: tuple[float, float, float, float],
    fill: tuple[int, int, int] | tuple[int, int, int, int] | None,
    outline: tuple[int, int, int] | tuple[int, int, int, int] | None = None,
    width: float = 1.0,
    cut: float = 8.0,
) -> None:
    x, y, w, h = box
    points = chamfer_points(x, y, w, h, cut)
    draw.polygon(points, fill=fill)
    if outline is not None and width > 0:
        draw.line(points + [points[0]], fill=outline, width=max(1, px(width)), joint="curve")


def rounded_mask(size: int, radius: float) -> Image.Image:
    mask = Image.new("L", (px(size), px(size)), 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        [(0, 0), (px(size) - 1, px(size) - 1)],
        radius=px(radius),
        fill=255,
    )
    return mask


# ---------------------------------------------------------------------------
# Background primitives
# ---------------------------------------------------------------------------
def vertical_gradient(
    size: tuple[int, int],
    top: tuple[int, int, int],
    bottom: tuple[int, int, int],
) -> Image.Image:
    width, height = size
    strip = Image.new("RGB", (1, height))
    pixels = strip.load()
    for y in range(height):
        t = y / max(1, height - 1)
        pixels[0, y] = (
            int(top[0] + (bottom[0] - top[0]) * t),
            int(top[1] + (bottom[1] - top[1]) * t),
            int(top[2] + (bottom[2] - top[2]) * t),
        )
    return strip.resize((width, height), Image.Resampling.BILINEAR)


def add_radial_glow(
    canvas: Image.Image,
    center: tuple[float, float],
    radius: float,
    color: tuple[int, int, int],
    alpha: int,
) -> None:
    r = px(radius)
    if r <= 0:
        return
    mask = ImageOps.invert(Image.radial_gradient("L")).resize((r * 2, r * 2), Image.Resampling.BILINEAR)
    mask = mask.point(lambda v: int((v / 255) ** 2.1 * alpha))
    glow = Image.new("RGB", (r * 2, r * 2), color)
    canvas.paste(glow, (px(center[0]) - r, px(center[1]) - r), mask)


def add_grid(
    canvas: Image.Image,
    box: tuple[float, float, float, float],
    step: float,
    color: tuple[int, int, int],
    alpha: int,
    fade: float = 1.0,
) -> None:
    x, y, w, h = box
    width, height = px(w), px(h)
    if width <= 0 or height <= 0:
        return
    layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    step_px = max(1, px(step))
    for gx in range(0, width, step_px):
        draw.line([(gx, 0), (gx, height)], fill=(*color, alpha), width=1)
    for gy in range(0, height, step_px):
        draw.line([(0, gy), (width, gy)], fill=(*color, alpha), width=1)
    if fade < 1.0:
        vertical = Image.new("L", (1, height))
        vp = vertical.load()
        for gy in range(height):
            t = gy / max(1, height - 1)
            vp[0, gy] = int(255 * max(0.0, 1.0 - t / max(0.001, fade)))
        vertical = vertical.resize((width, height), Image.Resampling.BILINEAR)
        layer.putalpha(ImageChops.multiply(layer.getchannel("A"), vertical))
    canvas.paste(layer, (px(x), px(y)), layer)


def add_lasers(
    canvas: Image.Image,
    box: tuple[float, float, float, float],
    lines: Sequence[tuple[float, float, float, float, tuple[int, int, int], float, int]],
) -> None:
    """Draw a set of soft laser beams inside *box*.

    Each line is ``(x1, y1, x2, y2, color, width, alpha)`` in logical
    coordinates relative to *box*.
    """
    x, y, w, h = box
    width, height = px(w), px(h)
    if width <= 0 or height <= 0:
        return

    glow = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    core = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    cd = ImageDraw.Draw(core)
    for x1, y1, x2, y2, color, line_w, alpha in lines:
        gd.line(
            [(px(x1), px(y1)), (px(x2), px(y2))],
            fill=(*color, alpha),
            width=max(2, px(line_w * 5)),
        )
        cd.line(
            [(px(x1), px(y1)), (px(x2), px(y2))],
            fill=(*color, min(255, int(alpha * 3))),
            width=max(1, px(line_w)),
        )
    glow = glow.filter(ImageFilter.GaussianBlur(px(9)))
    canvas.paste(glow, (px(x), px(y)), glow)
    canvas.paste(core, (px(x), px(y)), core)


def load_hero_art(size: float, path: str | None = None) -> tuple[Image.Image, Image.Image] | None:
    """Load and treat the official key visual, returning (art, alpha mask)."""
    art_path = path or asset_path("backgrounds", "sdvx_exceed_gear_key.jpg")
    if not os.path.isfile(art_path):
        return None
    try:
        with Image.open(art_path) as source:
            art = source.convert("RGB")
    except (OSError, ValueError):
        return None

    side = px(size)
    art = art.resize((side, side), Image.Resampling.LANCZOS)
    art = ImageEnhance.Color(art).enhance(0.82)
    art = ImageEnhance.Brightness(art).enhance(0.58)
    art = ImageEnhance.Contrast(art).enhance(1.08)
    art = Image.blend(art, Image.new("RGB", art.size, (10, 13, 22)), 0.24)

    left_fade = px(size * 0.34)
    bottom_fade = px(size * 0.16)
    left_mask = Image.new("L", (side, side), 255)
    lm = ImageDraw.Draw(left_mask)
    for index in range(left_fade):
        lm.line([(index, 0), (index, side - 1)], fill=int(255 * index / max(1, left_fade - 1)))
    bottom_mask = Image.new("L", (side, side), 255)
    bm = ImageDraw.Draw(bottom_mask)
    for index in range(bottom_fade):
        y = side - bottom_fade + index
        bm.line([(0, y), (side - 1, y)], fill=int(255 * (1.0 - index / max(1, bottom_fade - 1))))
    return art, ImageChops.multiply(left_mask, bottom_mask)


def paint_key_art_fallback(
    canvas: Image.Image,
    box: tuple[float, float, float, float],
) -> None:
    """Original SDVX-flavoured stand-in used when the key visual is absent."""
    x, y, w, h = box
    draw = ImageDraw.Draw(canvas)
    draw_chamfer(draw, (x, y, w, h), fill=(12, 17, 28), outline=BORDER, width=1, cut=18)
    add_radial_glow(canvas, (x + w * 0.68, y + h * 0.42), w * 0.48, (70, 20, 48), 58)
    add_radial_glow(canvas, (x + w * 0.55, y + h * 0.38), w * 0.32, (10, 68, 82), 40)

    # A drawn "del" mark rather than a font glyph, so it survives every face.
    cx = x + w / 2
    cy = y + h * 0.40
    size = min(w, h) * 0.34
    outer = [
        (px(cx), px(cy - size * 0.52)),
        (px(cx + size * 0.62), px(cy + size * 0.46)),
        (px(cx - size * 0.62), px(cy + size * 0.46)),
    ]
    inner = [
        (px(cx), px(cy - size * 0.18)),
        (px(cx + size * 0.36), px(cy + size * 0.40)),
        (px(cx - size * 0.36), px(cy + size * 0.40)),
    ]
    draw.polygon(outer, fill=(30, 92, 112))
    draw.polygon(inner, fill=(12, 17, 28))
    draw.line(outer + [outer[0]], fill=(56, 232, 255), width=max(1, px(1)))

    label_font = load_font("num-bold", px(10))
    draw_tracked(
        draw,
        (x + w - 14, y + h - 24),
        "SOUND VOLTEX  /  EXCEED GEAR",
        label_font,
        TEXT_MUTED,
        tracking=1.4,
        anchor="ra",
    )


# ---------------------------------------------------------------------------
# Page environment
# ---------------------------------------------------------------------------
def paint_page_background(
    canvas: Image.Image,
    hero_h: float,
    canvas_w: float,
    canvas_h: float,
) -> None:
    """Paint the obsidian gradient, neon atmosphere and hero grid."""
    base = vertical_gradient((px(canvas_w), px(canvas_h)), BG_HERO_TOP, BG_DEEP)
    canvas.paste(base, (0, 0))

    add_radial_glow(canvas, (canvas_w * 0.88, hero_h * 0.34), 520, (86, 18, 62), 44)
    add_radial_glow(canvas, (canvas_w * 0.18, hero_h * 0.72), 430, (12, 72, 92), 34)
    add_radial_glow(canvas, (canvas_w * 0.52, hero_h * 0.10), 300, (18, 52, 86), 26)

    add_grid(
        canvas,
        (0, 0, canvas_w, hero_h + 90),
        step=64,
        color=(70, 118, 148),
        alpha=9,
        fade=1.0,
    )
    add_lasers(
        canvas,
        (0, 0, canvas_w, hero_h),
        [
            (-40, hero_h + 20, 720, -40, (56, 232, 255), 1.6, 22),
            (160, hero_h + 60, 1180, -60, (255, 61, 154), 1.2, 18),
            (860, hero_h + 40, 1520, 20, (56, 232, 255), 1.1, 14),
            (1120, hero_h + 80, 1680, 90, (255, 61, 154), 0.9, 12),
        ],
    )

    # A soft fade so the dense atmosphere stops before the card grid.
    fade_top = px(hero_h - 40)
    fade_h = px(120)
    if fade_h > 0:
        fade = Image.new("L", (px(canvas_w), fade_h), 0)
        fd = ImageDraw.Draw(fade)
        for index in range(fade_h):
            fd.line([(0, index), (px(canvas_w) - 1, index)], fill=int(255 * index / max(1, fade_h - 1)))
        veil = Image.new("RGB", (px(canvas_w), fade_h), BG_DEEP)
        canvas.paste(veil, (0, fade_top), fade)


def draw_hero_rule(canvas: Image.Image, y: float, width: float) -> None:
    """A hairline with a cyan signal segment under the hero."""
    draw = ImageDraw.Draw(canvas)
    draw.line([(0, px(y)), (px(width), px(y))], fill=HAIRLINE, width=max(1, px(1)))
    draw.line([(0, px(y)), (px(width * 0.28), px(y))], fill=(28, 92, 116), width=max(1, px(1)))
    draw.line([(px(width * 0.28), px(y)), (px(width * 0.44), px(y))], fill=(70, 36, 70), width=max(1, px(1)))
