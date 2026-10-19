"""Script to generate showcase assets (assets/b50.jpg and assets/preview_sm.jpg)."""
from __future__ import annotations

import os
import sys

# Ensure src is on sys.path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
SRC_DIR = os.path.join(REPO_ROOT, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from PIL import Image  # noqa: E402
from render_html import render_html  # noqa: E402
from render_png import render_png  # noqa: E402
from sample_data import get_sample_rows  # noqa: E402


def generate_assets() -> None:
    rows = get_sample_rows()
    player_name = "RIE"
    total_vf = 11.184
    skill = ""

    assets_dir = os.path.join(REPO_ROOT, "assets")
    os.makedirs(assets_dir, exist_ok=True)
    out_b50 = os.path.join(assets_dir, "b50.jpg")
    out_preview = os.path.join(assets_dir, "preview_sm.jpg")
    out_html = os.path.join(assets_dir, "b50.html")
    font_path = os.path.join(assets_dir, "fonts", "msyh.ttc")

    # Render card-grid JPEG
    render_png(rows, player_name, total_vf, out_b50, skill=skill, font_path=font_path)
    print(f"Generated {out_b50} ({os.path.getsize(out_b50)} bytes)")

    # Render preview thumbnail
    with Image.open(out_b50) as im:
        target_w = 900
        target_h = int(im.height * (target_w / im.width))
        sm = im.resize((target_w, target_h), Image.Resampling.LANCZOS)
        sm.save(out_preview, "JPEG", quality=85, optimize=True, progressive=True)
    print(f"Generated {out_preview} ({os.path.getsize(out_preview)} bytes)")

    # Render HTML dashboard
    render_html(rows, player_name, total_vf, out_html, skill=skill)
    print(f"Generated {out_html} ({os.path.getsize(out_html)} bytes)")


if __name__ == "__main__":
    generate_assets()
