import os

from PIL import Image
from render_png import _build_stats, _layout, format_vf, render_png


def test_render_png_card_grid_no_overlap(tmp_path):
    rows = []
    for i in range(50):
        rows.append({
            "mid": i + 1, "type": (i % 5), "title": "Very Long Song Title That Should Be Clipped",
            "label": "ADV", "level": "14", "score": 9500000 + i * 100,
            "volforce": 250.0 - i, "clear": 6, "grade": 10,
            "clear_name": "PUC", "grade_name": "S", "cover_path": None,
        })
    out = tmp_path / "b50.png"
    render_png(rows, "Tester", 11.184, str(out))
    img = Image.open(out)
    assert img.width == 1600
    # Hero + podium + 10 runlist rows + summary panel + footer
    assert 2000 <= img.height < 2400
    img.close()


def test_render_png_renders_exscore(tmp_path):
    rows = [{
        "mid": 1, "type": 0, "title": "T", "label": "NOV", "level": "5",
        "score": 100, "exscore": 9999, "volforce": 10.0, "clear": 6, "grade": 10,
        "clear_name": "PUC", "grade_name": "S", "cover_path": None,
    }]
    out = tmp_path / "b50.png"
    render_png(rows, "Tester", 1.0, str(out))
    img = Image.open(out)
    # EX SCORE 视觉断言困难，仅验证无报错且尺寸正确
    assert img.width == 1600
    img.close()


def test_render_png_long_title_does_not_crash(tmp_path):
    rows = [{
        "mid": 1, "type": 2, "title": "A" * 200, "label": "EXH", "level": "18",
        "score": 9_900_000, "exscore": 9999, "volforce": 500.0, "clear": 6,
        "grade": 10, "clear_name": "PUC", "grade_name": "S", "cover_path": None,
    }]
    out = tmp_path / "b50.png"
    render_png(rows, "Tester", 5.0, str(out))
    img = Image.open(out)
    assert img.width == 1600
    img.close()


def test_render_png_with_skill_no_crash(tmp_path):
    rows = [{
        "mid": 1, "type": 0, "title": "T", "label": "NOV", "level": "5",
        "score": 100, "exscore": 90, "volforce": 10.0, "clear": 6, "grade": 10,
        "clear_name": "PUC", "grade_name": "S", "cover_path": None,
    }]
    out = tmp_path / "b50.png"
    render_png(rows, "Tester", 1.0, str(out), skill="蒼穹")
    img = Image.open(out)
    assert img.width == 1600
    img.close()


def test_render_png_outputs_jpeg(tmp_path):
    rows = [{
        "mid": i + 1, "type": 0, "title": "T", "label": "NOV", "level": "5",
        "score": 9_000_000, "exscore": 9000, "volforce": 20.0, "clear": 6, "grade": 10,
        "clear_name": "PUC", "grade_name": "S", "cover_path": None,
    } for i in range(50)]
    out = tmp_path / "b50.jpg"
    render_png(rows, "Tester", 11.0, str(out))
    img = Image.open(out)
    assert img.format == "JPEG"
    assert img.width == 1600
    img.close()
    assert os.path.getsize(str(out)) < 2_000_000


def test_format_vf_appends_pct():
    assert format_vf(250.0, 12.3456) == "250.0 ·12.3456%"
    assert format_vf(1.5, 0.1) == "1.5 ·0.1000%"
    assert format_vf(0.0, 0.0) == "0.0 ·0.0000%"


def test_render_png_with_vf_pct_no_crash(tmp_path):
    rows = [{
        "mid": 1, "type": 0, "title": "T", "label": "NOV", "level": "5",
        "score": 100, "exscore": 90, "volforce": 10.0, "vf_pct": 100.0,
        "clear": 6, "grade": 10, "clear_name": "PUC", "grade_name": "S",
        "cover_path": None,
    }]
    out = tmp_path / "b50.jpg"
    render_png(rows, "Tester", 1.0, str(out))
    img = Image.open(out)
    assert img.format == "JPEG"
    assert img.width == 1600
    img.close()


def test_layout_50_tracks_uses_podium_and_inline_summary():
    layout = _layout(50)
    assert layout["podium_count"] == 3
    assert layout["run_rows"] == 10
    assert layout["summary_mode"] == "inline"
    assert layout["summary_slots"] == 3


def test_layout_one_track_skips_runlist():
    layout = _layout(1)
    assert layout["podium_count"] == 1
    assert layout["run_rows"] == 0
    assert layout["summary_mode"] is None


def test_build_stats_derives_missing_vf_share():
    rows = [{"volforce": 300.0}, {"volforce": 100.0}]
    stats = _build_stats(rows)
    assert stats["pcts"] == [75.0, 25.0]
    assert stats["top3_share"] == 100.0
    assert stats["avg_vf"] == 200.0


def test_render_png_empty_rows_does_not_crash(tmp_path):
    out = tmp_path / "b50.jpg"
    render_png([], "Tester", 0.0, str(out))
    img = Image.open(out)
    assert img.width == 1600
    assert img.format == "JPEG"
    img.close()


def test_render_png_missing_background_falls_back(tmp_path):
    rows = [{
        "mid": 1, "type": 0, "title": "T", "label": "NOV", "level": "5",
        "score": 100, "exscore": 90, "volforce": 10.0, "clear": 6, "grade": 10,
        "clear_name": "PUC", "grade_name": "S", "cover_path": None,
    }]
    out = tmp_path / "b50.jpg"
    render_png(
        rows, "Tester", 1.0, str(out),
        background_path=str(tmp_path / "missing.jpg"),
    )
    img = Image.open(out)
    assert img.width == 1600
    img.close()
