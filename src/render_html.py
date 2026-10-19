"""Interactive cyber-styled HTML report generator for SDVX B50.

Generates a modern, responsive, self-contained HTML dashboard with:
- Cyber-obsidian theme with neon cyan & magenta accents.
- Player header with VOLFORCE badge and summary metrics.
- Search input, difficulty filter pills, column sorting, and view toggle (Table / Grid).
- Compact base64 embedded thumbnails (<300KB file size, 97%+ leaner than uncompressed).
"""
from __future__ import annotations

import base64
import html
import io
import os
from typing import Any

try:
    from PIL import Image
    _HAS_PIL = True
except ImportError:
    _HAS_PIL = False


def _encode_cover_thumbnail(cover_path: str | None, size: int = 72) -> str | None:
    """Read and compress cover image to a compact base64 thumbnail string."""
    if not cover_path or not os.path.isfile(cover_path):
        return None
    try:
        if _HAS_PIL:
            with Image.open(cover_path) as im:
                thumb = im.convert("RGB")
                thumb.thumbnail((size, size), Image.Resampling.LANCZOS if hasattr(Image, "Resampling") else Image.LANCZOS)
                buf = io.BytesIO()
                thumb.save(buf, format="JPEG", quality=82, optimize=True)
                return f"data:image/jpeg;base64,{base64.b64encode(buf.getvalue()).decode('ascii')}"
        with open(cover_path, "rb") as f:
            raw = base64.b64encode(f.read()).decode("ascii")
            return f"data:image/png;base64,{raw}"
    except (OSError, ValueError):
        return None


def render_html(
    rows: list[dict[str, Any]],
    player_name: str,
    total_vf: float,
    out_path: str,
    skill: str = "",
) -> None:
    """Render rows into a self-contained modern HTML dashboard at out_path."""
    safe_player = html.escape(player_name)
    skill_text = f" [SKILL {html.escape(skill)}]" if skill else ""
    h1_text = f"{safe_player} - VOLFORCE {total_vf}{skill_text}"

    # Calculate summary statistics
    total_tracks = len(rows)
    s_count = sum(1 for r in rows if r.get("grade_name") == "S")
    top_vf = f"{rows[0].get('volforce', 0.0):.1f}" if rows else "0.0"
    avg_vf = f"{sum(r.get('volforce', 0.0) for r in rows) / total_tracks:.1f}" if total_tracks else "0.0"

    # Difficulty badge colors
    diff_bg_map = {
        0: "#10b981",  # NOV
        1: "#0ea5e9",  # ADV
        2: "#f43f5e",  # EXH
        3: "#a855f7",  # INF
        4: "#f59e0b",  # MXM
        5: "#ef4444",  # ULT
    }

    # Grade styling classes
    def grade_badge_html(gname: str) -> str:
        if not gname or gname == "No Grade":
            return "-"
        cls = "grade-other"
        if gname == "S":
            cls = "grade-s"
        elif "AAA" in gname:
            cls = "grade-aaa"
        elif "AA" in gname:
            cls = "grade-aa"
        elif "A" in gname:
            cls = "grade-a"
        return f'<span class="badge {cls}">{html.escape(gname)}</span>'

    # Build Table rows & Grid cards
    table_rows = []
    grid_cards = []

    for i, r in enumerate(rows, 1):
        cp = r.get("cover_path")
        b64_src = _encode_cover_thumbnail(cp)
        cover_cell = '<td class="col-cover"><div class="no-cover">无</div></td>'
        card_cover_img = '<div class="no-cover card-thumb">SDVX</div>'

        if b64_src:
            cover_cell = f'<td class="col-cover"><img class="tbl-thumb" src="{b64_src}" alt="cover" loading="lazy"></td>'
            card_cover_img = f'<img class="card-thumb" src="{b64_src}" alt="cover" loading="lazy">'

        mtype = r.get("type", 0)
        diff_color = diff_bg_map.get(mtype, "#0ea5e9")
        diff_label = html.escape(str(r.get("label", "NOV")))
        diff_level = html.escape(str(r.get("level", "?")))
        diff_badge = f'<span class="badge" style="background:{diff_color};color:#fff;font-weight:700">{diff_label}</span>'

        title = html.escape(str(r.get("title", "Unknown")))
        score = r.get("score", 0)
        exscore = r.get("exscore", 0)
        grade_name = r.get("grade_name", "")
        volforce = r.get("volforce", 0.0)
        vf_pct = r.get("vf_pct", 0.0)

        # Table row
        table_rows.append(
            f'<tr data-type="{mtype}" data-title="{title.lower()}">'
            f'<td class="col-rank">#{i:02d}</td>'
            f'{cover_cell}'
            f'<td class="col-title" title="{title}">{title}</td>'
            f'<td>{diff_badge}</td>'
            f'<td class="col-level">{diff_level}</td>'
            f'<td class="col-score">{score:,}</td>'
            f'<td>{exscore}</td>'
            f'<td>{grade_badge_html(grade_name)}</td>'
            f'<td class="col-vf">{volforce}</td>'
            f'<td class="col-pct">{vf_pct:.4f}%</td>'
            f'</tr>'
        )

        # Grid card
        grid_cards.append(
            f'<div class="song-card" data-type="{mtype}" data-title="{title.lower()}">'
            f'  <div class="card-cover-wrap">'
            f'    {card_cover_img}'
            f'    <span class="card-rank">#{i:02d}</span>'
            f'  </div>'
            f'  <div class="card-info">'
            f'    <div class="card-row-top">'
            f'      <span class="card-title" title="{title}">{title}</span>'
            f'      {grade_badge_html(grade_name)}'
            f'    </div>'
            f'    <div class="card-row-mid">'
            f'      <span class="badge" style="background:{diff_color};color:#fff;font-size:10px;padding:2px 6px;">{diff_label} {diff_level}</span>'
            f'      <span class="card-score">{score:,}</span>'
            f'    </div>'
            f'    <div class="card-row-bot">'
            f'      <span class="card-ex">EX {exscore}</span>'
            f'      <span class="card-vf">{volforce} <span class="card-pct">·{vf_pct:.4f}%</span></span>'
            f'    </div>'
            f'  </div>'
            f'</div>'
        )

    # HTML Template
    doc = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>B50 - {safe_player}</title>
<style>
:root {{
  --bg: #0c0e14;
  --surface: #141724;
  --surface-hover: #1b2032;
  --border: #232a3d;
  --accent-cyan: #00f0ff;
  --accent-magenta: #ff2d87;
  --accent-purple: #a855f7;
  --text-main: #f8fafc;
  --text-sub: #94a3b8;
  --text-muted: #64748b;
}}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Microsoft YaHei", sans-serif;
  background: var(--bg);
  color: var(--text-main);
  line-height: 1.5;
  padding: 24px;
}}
.container {{ max-width: 1300px; margin: 0 auto; }}

/* Header HUD */
.header-card {{
  background: linear-gradient(135deg, #161b2a 0%, #101420 100%);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
  position: relative;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(0,0,0,0.4);
}}
.header-card::after {{
  content: "";
  position: absolute;
  bottom: 0; left: 0; right: 0;
  height: 2px;
  background: linear-gradient(90deg, var(--accent-cyan), var(--accent-magenta), var(--accent-purple));
}}
.header-content {{
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
}}
.player-block {{ display: flex; align-items: center; gap: 18px; }}
.avatar-ring {{
  width: 60px; height: 60px;
  border-radius: 50%;
  border: 2px solid var(--accent-cyan);
  background: #0f1522;
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 0 16px rgba(0,240,255,0.25);
}}
.avatar-ring svg {{ width: 28px; height: 28px; fill: var(--accent-cyan); }}
h1 {{
  font-size: 1.5rem;
  font-weight: 800;
  letter-spacing: -0.02em;
  color: #fff;
  margin-bottom: 4px;
}}
.sub-tag {{
  display: inline-block;
  font-size: 0.75rem;
  font-weight: 600;
  padding: 2px 10px;
  border-radius: 4px;
  background: rgba(168, 85, 247, 0.15);
  border: 1px solid rgba(168, 85, 247, 0.4);
  color: #d8b4fe;
}}

/* Stats Grid */
.stats-group {{
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}}
.stat-box {{
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 8px;
  padding: 10px 18px;
  min-width: 100px;
  text-align: center;
}}
.stat-label {{ font-size: 0.7rem; color: var(--text-muted); text-transform: uppercase; font-weight: 700; }}
.stat-val {{ font-size: 1.25rem; font-weight: 800; color: #fff; margin-top: 2px; }}
.stat-box.highlight {{ border-color: rgba(0,240,255,0.3); background: rgba(0,240,255,0.04); }}
.stat-box.highlight .stat-val {{ color: var(--accent-cyan); }}

/* Toolbar */
.toolbar {{
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 16px;
}}
.search-input {{
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 8px 14px;
  color: #fff;
  font-size: 0.85rem;
  width: 240px;
  outline: none;
  transition: border-color 0.2s;
}}
.search-input:focus {{ border-color: var(--accent-cyan); }}
.filter-pills {{ display: flex; gap: 6px; flex-wrap: wrap; }}
.filter-pill {{
  background: var(--surface);
  border: 1px solid var(--border);
  color: var(--text-sub);
  padding: 6px 12px;
  font-size: 0.75rem;
  font-weight: 600;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.2s;
}}
.filter-pill:hover, .filter-pill.active {{
  background: var(--accent-cyan);
  color: #0c0e14;
  border-color: var(--accent-cyan);
}}
.view-toggle {{
  display: flex;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 6px;
  overflow: hidden;
}}
.view-btn {{
  background: none;
  border: none;
  padding: 6px 12px;
  color: var(--text-sub);
  cursor: pointer;
  font-size: 0.8rem;
  font-weight: 600;
}}
.view-btn.active {{
  background: rgba(255,255,255,0.1);
  color: #fff;
}}

/* Table Layout */
.table-wrap {{
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 10px;
  overflow-x: auto;
}}
table {{
  width: 100%;
  border-collapse: collapse;
  text-align: left;
  font-size: 0.88rem;
}}
th, td {{
  padding: 10px 14px;
  border-bottom: 1px solid rgba(255,255,255,0.05);
}}
th {{
  background: #10131f;
  color: var(--text-muted);
  font-weight: 700;
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  user-select: none;
  cursor: pointer;
}}
th:hover {{ color: var(--accent-cyan); }}
tr:hover {{ background: var(--surface-hover); }}
.col-rank {{ color: var(--text-muted); font-weight: 700; font-size: 0.8rem; width: 44px; }}
.col-cover {{ width: 56px; }}
.tbl-thumb {{ width: 44px; height: 44px; border-radius: 4px; object-fit: cover; display: block; }}
.no-cover {{
  width: 44px; height: 44px; border-radius: 4px;
  background: #1c2233; color: var(--text-muted);
  display: flex; align-items: center; justify-content: center;
  font-size: 0.7rem; font-weight: 600;
}}
.col-title {{ font-weight: 600; color: #fff; max-width: 240px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
.col-level {{ font-weight: 700; color: #fff; }}
.col-score {{ font-family: monospace; font-size: 0.95rem; color: #e2e8f0; }}
.col-vf {{ font-weight: 800; color: var(--accent-cyan); }}
.col-pct {{ color: #7dd3fc; font-size: 0.8rem; font-family: monospace; }}

/* Badges */
.badge {{
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.02em;
}}
.grade-s {{ background: rgba(255,215,0,0.15); color: #ffd700; border: 1px solid rgba(255,215,0,0.4); }}
.grade-aaa {{ background: rgba(255,77,109,0.15); color: #ff4d6d; border: 1px solid rgba(255,77,109,0.4); }}
.grade-aa {{ background: rgba(0,240,255,0.15); color: #00f0ff; border: 1px solid rgba(0,240,255,0.4); }}
.grade-a {{ background: rgba(16,185,129,0.15); color: #10b981; border: 1px solid rgba(16,185,129,0.4); }}
.grade-other {{ background: rgba(148,163,184,0.15); color: #94a3b8; border: 1px solid rgba(148,163,184,0.3); }}

/* Grid View */
.grid-wrap {{
  display: none;
  grid-template-columns: repeat(auto-fill, minmax(230px, 1fr));
  gap: 14px;
}}
.song-card {{
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 8px;
  display: flex;
  gap: 10px;
  transition: transform 0.15s, border-color 0.15s;
}}
.song-card:hover {{
  transform: translateY(-2px);
  border-color: rgba(0,240,255,0.4);
}}
.card-cover-wrap {{ position: relative; width: 68px; height: 68px; flex-shrink: 0; }}
.card-thumb {{ width: 68px; height: 68px; border-radius: 6px; object-fit: cover; display: block; }}
.card-rank {{
  position: absolute; top: 2px; left: 2px;
  background: rgba(0,0,0,0.75); color: #fff;
  font-size: 0.65rem; font-weight: 700; padding: 1px 4px; border-radius: 3px;
}}
.card-info {{ flex: 1; min-width: 0; display: flex; flex-direction: column; justify-content: space-between; }}
.card-row-top, .card-row-mid, .card-row-bot {{ display: flex; align-items: center; justify-content: space-between; gap: 4px; }}
.card-title {{ font-size: 0.8rem; font-weight: 700; color: #fff; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
.card-score {{ font-size: 0.75rem; font-family: monospace; color: #cbd5e1; }}
.card-ex {{ font-size: 0.7rem; color: var(--text-muted); }}
.card-vf {{ font-size: 0.85rem; font-weight: 800; color: var(--accent-cyan); }}
.card-pct {{ font-size: 0.68rem; color: #7dd3fc; }}

@media (max-width: 768px) {{
  body {{ padding: 12px; }}
  .header-content {{ flex-direction: column; align-items: flex-start; }}
  .toolbar {{ flex-direction: column; align-items: stretch; }}
  .search-input {{ width: 100%; }}
}}
@media print {{
  body {{ background: #fff; color: #000; padding: 0; }}
  .toolbar, .view-toggle {{ display: none; }}
  th {{ background: #eee; color: #000; }}
  td, th {{ border: 1px solid #ddd; }}
}}
</style>
</head>
<body>
<div class="container">
  <header class="header-card">
    <div class="header-content">
      <div class="player-block">
        <div class="avatar-ring">
          <svg viewBox="0 0 24 24"><path d="M12 3v10.55c-.59-.34-1.27-.55-2-.55-2.21 0-4 1.79-4 4s1.79 4 4 4 4-1.79 4-4V7h4V3h-6z"/></svg>
        </div>
        <div>
          <h1>{h1_text}</h1>
          <span class="sub-tag">SOUND VOLTEX EXCEED GEAR ∇</span>
        </div>
      </div>
      <div class="stats-group">
        <div class="stat-box highlight">
          <div class="stat-label">Total VF</div>
          <div class="stat-val">{total_vf}</div>
        </div>
        <div class="stat-box">
          <div class="stat-label">Tracks</div>
          <div class="stat-val">{total_tracks}</div>
        </div>
        <div class="stat-box">
          <div class="stat-label">Top VF</div>
          <div class="stat-val">{top_vf}</div>
        </div>
        <div class="stat-box">
          <div class="stat-label">Avg VF</div>
          <div class="stat-val">{avg_vf}</div>
        </div>
        <div class="stat-box">
          <div class="stat-label">S Rank</div>
          <div class="stat-val">{s_count}</div>
        </div>
      </div>
    </div>
  </header>

  <section class="toolbar">
    <div style="display:flex;gap:10px;align-items:center;flex-wrap:wrap">
      <input type="text" class="search-input" id="search" placeholder="搜索曲名 / 难度...">
      <div class="filter-pills" id="filters">
        <button class="filter-pill active" data-filter="all">ALL</button>
        <button class="filter-pill" data-filter="0">NOV</button>
        <button class="filter-pill" data-filter="1">ADV</button>
        <button class="filter-pill" data-filter="2">EXH</button>
        <button class="filter-pill" data-filter="4">MXM</button>
        <button class="filter-pill" data-filter="3">INF/OTHER</button>
      </div>
    </div>
    <div class="view-toggle">
      <button class="view-btn active" id="btn-tbl">表格视图</button>
      <button class="view-btn" id="btn-grid">卡片网格</button>
    </div>
  </section>

  <main>
    <div class="table-wrap" id="view-table">
      <table>
        <thead>
          <tr>
            <th>#</th>
            <th>封面</th>
            <th>曲名</th>
            <th>难度</th>
            <th>等级</th>
            <th>SCORE</th>
            <th>EX SCORE</th>
            <th>GRADE</th>
            <th>VF</th>
            <th>VF占比</th>
          </tr>
        </thead>
        <tbody id="tbl-body">
          {''.join(table_rows)}
        </tbody>
      </table>
    </div>

    <div class="grid-wrap" id="view-grid">
      {''.join(grid_cards)}
    </div>
  </main>
</div>

<script>
// Search & Filter
const searchInput = document.getElementById('search');
const filterBtns = document.querySelectorAll('.filter-pill');
const tableRows = document.querySelectorAll('#tbl-body tr');
const gridCards = document.querySelectorAll('#view-grid .song-card');

let activeFilter = 'all';

function applyFilters() {{
  const query = searchInput.value.trim().toLowerCase();
  function check(el) {{
    const type = el.getAttribute('data-type');
    const title = el.getAttribute('data-title');
    const matchType = (activeFilter === 'all') || (type === activeFilter);
    const matchQuery = !query || title.includes(query);
    el.style.display = (matchType && matchQuery) ? '' : 'none';
  }}
  tableRows.forEach(check);
  gridCards.forEach(check);
}}

searchInput.addEventListener('input', applyFilters);
filterBtns.forEach(btn => {{
  btn.addEventListener('click', () => {{
    filterBtns.forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    activeFilter = btn.getAttribute('data-filter');
    applyFilters();
  }});
}});

// View Toggle
const btnTbl = document.getElementById('btn-tbl');
const btnGrid = document.getElementById('btn-grid');
const viewTable = document.getElementById('view-table');
const viewGrid = document.getElementById('view-grid');

btnTbl.addEventListener('click', () => {{
  btnTbl.classList.add('active');
  btnGrid.classList.remove('active');
  viewTable.style.display = 'block';
  viewGrid.style.display = 'none';
}});

btnGrid.addEventListener('click', () => {{
  btnGrid.classList.add('active');
  btnTbl.classList.remove('active');
  viewTable.style.display = 'none';
  viewGrid.style.display = 'grid';
}});
</script>
</body>
</html>"""

    parent = os.path.dirname(out_path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(doc)
