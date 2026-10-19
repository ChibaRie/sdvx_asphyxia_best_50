"""Command-line entrypoint for SDVX Best 50 generator.

Orchestrates save extraction, MDB lookup, cover resolution, and output generation.
Usage:
    SDVX_B50.exe [--demo] [save_db] [music_db] [music_dir] [out_dir]
"""
from __future__ import annotations

import os
import sys

from b50data import (
    build_rows,
    detect_refid,
    extract_music,
    load_mdb,
    load_profile_name,
    load_skill,
    parse_db,
    resolve_cover,
    select_best50,
)
from render_html import render_html
from render_png import render_png
from sample_data import get_sample_rows
# Configure safe terminal encoding on Windows
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def print_help() -> None:
    help_text = """
========================================================================
  Sound Voltex asphyxia Best 50 Generator (EXCEED GEAR)
========================================================================
Usage:
  SDVX_B50.exe [save_db] [music_db] [music_dir] [out_dir]
  SDVX_B50.exe --demo [out_dir]
  SDVX_B50.exe --help

Options:
  --demo, -d       Generate a sample B50 card and HTML report using built-in data
  --help, -h       Display this help documentation

Default Paths:
  save_db:         ./asphyxia/savedata/sdvx@asphyxia.db
  music_db:        ./asphyxia/plugins/sdvx@asphyxia/webui/asset/json/music_db.json
  music_dir:       ./contents/data/music
  out_dir:         ./b50_output/

Outputs:
  ./b50_output/b50.jpg   -> 1200px Cyber-styled Best 50 Card Grid JPEG (~400KB)
  ./b50_output/b50.html  -> Responsive interactive HTML dashboard with search & filter
"""
    print(help_text.strip())


def run_demo(out_dir: str, font_path: str) -> None:
    print(">> Running in DEMO mode with built-in showcase data...")
    rows = get_sample_rows()
    player = "RIE"
    total_vf = 11.184
    skill = ""

    os.makedirs(out_dir, exist_ok=True)
    jpg_path = os.path.join(out_dir, "b50.jpg")
    htm_path = os.path.join(out_dir, "b50.html")

    render_png(rows, player, total_vf, jpg_path, skill=skill, font_path=font_path)
    render_html(rows, player, total_vf, htm_path, skill=skill)

    print(f"[OK] Player: {player} | Tracks: {len(rows)} | Total VF: {total_vf}")
    print(f"[OK] Generated JPEG: {jpg_path}")
    print(f"[OK] Generated HTML: {htm_path}")
    print(">> Demo generation finished successfully!")


def main() -> None:
    args = sys.argv[1:]

    # Handle help
    if any(arg in ("--help", "-h", "/?") for arg in args):
        print_help()
        sys.exit(0)

    cwd = os.getcwd()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    font_candidates = [
        os.path.join(script_dir, "..", "assets", "fonts", "msyh.ttc"),
        os.path.join(script_dir, "assets", "fonts", "msyh.ttc"),
        os.path.join(cwd, "assets", "fonts", "msyh.ttc"),
        os.path.join(script_dir, "msyh.ttc"),
        os.path.join(cwd, "msyh.ttc"),
        "C:/Windows/Fonts/msyh.ttc",
    ]
    font_path = next((p for p in font_candidates if os.path.isfile(p)), "C:/Windows/Fonts/msyh.ttc")

    # Handle demo mode
    if any(arg in ("--demo", "-d", "--sample") for arg in args):
        out_dir = next((a for a in args if not a.startswith("-")), os.path.join(cwd, "b50_output"))
        run_demo(out_dir, font_path)
        sys.exit(0)

    # Standard mode paths
    db_path = args[0] if len(args) > 0 else os.path.join(cwd, "asphyxia", "savedata", "sdvx@asphyxia.db")
    mdb_path = args[1] if len(args) > 1 else os.path.join(cwd, "asphyxia", "plugins", "sdvx@asphyxia", "webui", "asset", "json", "music_db.json")
    music_root = args[2] if len(args) > 2 else os.path.join(cwd, "contents", "data", "music")
    out_dir = args[3] if len(args) > 3 else os.path.join(cwd, "b50_output")

    if not os.path.isfile(db_path):
        print(f"[ERROR] Save database not found at: {db_path}")
        print("\nNotice: Place SDVX_B50.exe in the game root folder (beside asphyxia/ and contents/).")
        print("Tip: Run 'SDVX_B50.exe --demo' to preview generation using built-in showcase data.")
        sys.exit(1)

    print(">> Loading asphyxia save database...")
    try:
        records = parse_db(db_path)
    except OSError as e:
        print(f"[ERROR] Cannot read save database: {e}")
        sys.exit(1)

    try:
        refid = detect_refid(records)
    except ValueError as e:
        print(f"[ERROR] {e}")
        sys.exit(1)

    player = load_profile_name(records, refid)
    skill = load_skill(records, refid)
    print(f">> Player detected: {player}" + (f" (Skill: {skill})" if skill else ""))

    music_records = extract_music(records, refid)
    if not music_records:
        print("[WARNING] No music records found for current version.")
    top, total_vf = select_best50(music_records)
    print(f">> Top records selected: {len(top)} tracks | Total VOLFORCE: {total_vf}")

    print(">> Loading music database (music_db.json)...")
    try:
        mdb = load_mdb(mdb_path)
    except OSError as e:
        print(f"[ERROR] Cannot read music database: {e}")
        sys.exit(1)

    rows = build_rows(top, mdb)
    print(">> Resolving track jacket covers...")
    rows = [
        {**r, "cover_path": resolve_cover(music_root, r["mid"], r["type"])}
        for r in rows
    ]

    os.makedirs(out_dir, exist_ok=True)
    jpg = os.path.join(out_dir, "b50.jpg")
    htm = os.path.join(out_dir, "b50.html")

    print(f">> Rendering cyber card-grid JPEG -> {jpg}...")
    render_png(rows, player, total_vf, jpg, skill=skill, font_path=font_path)

    print(f">> Rendering interactive HTML dashboard -> {htm}...")
    render_html(rows, player, total_vf, htm, skill=skill)

    print(f"\n[DONE] Player={player} | Tracks={len(rows)} | Total VF={total_vf}")
    print(f"[SUCCESS] Written JPEG: {jpg}")
    print(f"[SUCCESS] Written HTML: {htm}")


if __name__ == "__main__":
    main()
