"""Built-in demo dataset for SDVX Best 50 generator."""
from __future__ import annotations

import os

SAMPLE_SONGS = [
    ("Daydream café", 1, "ADV", "14", 9551692, 0, 259.0, 2.3158, 2, "EFFECTIVE CLEAR", 8, "AAA"),
    ("What's up? Pop!", 1, "ADV", "14", 9542184, 0, 259.0, 2.3158, 2, "EFFECTIVE CLEAR", 8, "AAA"),
    ("Innocent Azure", 1, "ADV", "13", 9768713, 0, 253.0, 2.2622, 2, "EFFECTIVE CLEAR", 8, "AAA"),
    ("voltississimo", 1, "ADV", "14", 9328859, 0, 245.0, 2.1906, 2, "EFFECTIVE CLEAR", 6, "AA"),
    ("Voice 7 Voice...", 1, "ADV", "13", 9621896, 0, 242.0, 2.1638, 2, "EFFECTIVE CLEAR", 8, "AAA"),
    ("TWO-TORIAL", 1, "ADV", "14", 9213793, 0, 234.0, 2.0923, 2, "EFFECTIVE CLEAR", 6, "AA"),
    ("LaurelS -the...", 1, "ADV", "14", 9206868, 0, 234.0, 2.0923, 2, "EFFECTIVE CLEAR", 6, "AA"),
    ("ドッサンコオ...", 1, "ADV", "14", 9190518, 0, 234.0, 2.0923, 2, "EFFECTIVE CLEAR", 6, "AA"),
    ("ピアノ協奏曲...", 1, "ADV", "14", 9211491, 0, 234.0, 2.0923, 2, "EFFECTIVE CLEAR", 6, "AA"),
    ("Pure Ruby", 1, "ADV", "12", 9715525, 0, 233.0, 2.0833, 2, "EFFECTIVE CLEAR", 8, "AAA"),
    ("淡天滅孤", 1, "ADV", "14", 9144178, 0, 232.0, 2.0744, 2, "EFFECTIVE CLEAR", 5, "A+"),
    ("Absolute Do...", 1, "ADV", "14", 9086901, 0, 231.0, 2.0655, 2, "EFFECTIVE CLEAR", 5, "A+"),
    ("いーあるふぁ...", 2, "EXH", "13", 9458450, 0, 231.0, 2.0655, 2, "EFFECTIVE CLEAR", 6, "AA"),
    ("trea→journey", 1, "ADV", "14", 9084183, 0, 231.0, 2.0655, 2, "EFFECTIVE CLEAR", 5, "A+"),
    ("竹", 1, "ADV", "14", 9081035, 0, 231.0, 2.0655, 2, "EFFECTIVE CLEAR", 5, "A+"),
    ("Meteor☆Shower", 1, "ADV", "13", 9491379, 0, 231.0, 2.0655, 2, "EFFECTIVE CLEAR", 6, "AA"),
    ("まみむめ♪ま...", 1, "ADV", "13", 9371257, 0, 229.0, 2.0476, 2, "EFFECTIVE CLEAR", 6, "AA"),
    ("劇場版ムーニ...", 1, "ADV", "13", 9329629, 0, 228.0, 2.0386, 2, "EFFECTIVE CLEAR", 6, "AA"),
    ("Lièvre -blan...", 1, "ADV", "12", 9665763, 0, 225.0, 2.0118, 2, "EFFECTIVE CLEAR", 6, "AA+"),
    ("雪女", 1, "ADV", "12", 9636591, 0, 224.0, 2.0029, 2, "EFFECTIVE CLEAR", 6, "AA+"),
    ("werewolf ho...", 1, "ADV", "12", 9655000, 0, 224.0, 2.0029, 2, "EFFECTIVE CLEAR", 6, "AA+"),
    ("りむむむむむ", 1, "ADV", "12", 9618055, 0, 223.0, 1.9939, 2, "EFFECTIVE CLEAR", 6, "AA"),
    ("黎明の情", 1, "ADV", "12", 9572892, 0, 222.0, 1.9850, 2, "EFFECTIVE CLEAR", 6, "AA"),
    ("逆月", 1, "ADV", "14", 8983843, 0, 221.0, 1.9760, 2, "EFFECTIVE CLEAR", 4, "A"),
    ("紅の剣舞", 1, "ADV", "12", 9534368, 0, 221.0, 1.9760, 2, "EFFECTIVE CLEAR", 6, "AA"),
    ("ぎょるみっく...", 1, "ADV", "13", 9259776, 0, 219.0, 1.9582, 2, "EFFECTIVE CLEAR", 5, "A+"),
    ("天報譚", 1, "ADV", "13", 9288590, 0, 219.0, 1.9582, 2, "EFFECTIVE CLEAR", 5, "A+"),
    ("Faith of Frenzy", 1, "ADV", "13", 9257871, 0, 219.0, 1.9582, 2, "EFFECTIVE CLEAR", 5, "A+"),
    ("†:OLPHEUX:†", 1, "ADV", "14", 8861788, 0, 218.0, 1.9492, 2, "EFFECTIVE CLEAR", 4, "A"),
    ("Star☆Beat", 1, "ADV", "13", 9252003, 0, 218.0, 1.9492, 2, "EFFECTIVE CLEAR", 5, "A+"),
    ("777 (Vocal ver.)", 1, "ADV", "14", 8877943, 0, 218.0, 1.9492, 2, "EFFECTIVE CLEAR", 4, "A"),
    ("Knew Order", 1, "ADV", "13", 9220279, 0, 218.0, 1.9492, 2, "EFFECTIVE CLEAR", 5, "A+"),
    ("On take SUN", 1, "ADV", "13", 9191443, 0, 217.0, 1.9403, 2, "EFFECTIVE CLEAR", 5, "A+"),
    ("Aurolla", 1, "ADV", "13", 9194560, 0, 217.0, 1.9403, 2, "EFFECTIVE CLEAR", 5, "A+"),
    ("Akzeriyyuth", 1, "ADV", "13", 9181746, 0, 217.0, 1.9403, 2, "EFFECTIVE CLEAR", 5, "A+"),
    ("UNLIMITED F...", 2, "EXH", "11", 9154607, 0, 216.0, 1.9313, 2, "EFFECTIVE CLEAR", 5, "A+"),
    ("ULTIMATE IN...", 1, "ADV", "13", 9168048, 0, 216.0, 1.9313, 2, "EFFECTIVE CLEAR", 5, "A+"),
    ("きより紅い夢...", 2, "EXH", "11", 9130111, 0, 216.0, 1.9313, 2, "EFFECTIVE CLEAR", 5, "A+"),
    ("ピアノ独奏無言...", 1, "ADV", "14", 8779761, 0, 216.0, 1.9313, 2, "EFFECTIVE CLEAR", 4, "A"),
    ("Bangin' Burst", 1, "ADV", "13", 9126063, 0, 215.0, 1.9224, 2, "EFFECTIVE CLEAR", 5, "A+"),
    ("Kontrol Line", 1, "ADV", "13", 9068810, 0, 214.0, 1.9134, 2, "EFFECTIVE CLEAR", 5, "A+"),
    ("Fairy in Stras...", 2, "EXH", "13", 9022988, 0, 213.0, 1.9045, 2, "EFFECTIVE CLEAR", 5, "A+"),
    ("COSMIC R4I...", 1, "ADV", "12", 9399057, 0, 212.0, 1.8956, 2, "EFFECTIVE CLEAR", 6, "AA"),
    ("Lord=Crossight", 1, "ADV", "12", 9393203, 0, 211.0, 1.8866, 2, "EFFECTIVE CLEAR", 6, "AA"),
    ("Invisible Bullets", 1, "ADV", "12", 9372605, 0, 211.0, 1.8866, 2, "EFFECTIVE CLEAR", 6, "AA"),
    ("Roar of Chronos", 1, "ADV", "12", 9319664, 0, 210.0, 1.8777, 2, "EFFECTIVE CLEAR", 6, "AA"),
    ("Garakuta Doll...", 1, "ADV", "12", 9339815, 0, 210.0, 1.8777, 2, "EFFECTIVE CLEAR", 6, "AA"),
    ("Tomorrow Perf...", 2, "EXH", "11", 8979591, 0, 205.0, 1.8330, 2, "EFFECTIVE CLEAR", 4, "A"),
    ("Reb∞t", 1, "ADV", "13", 8993099, 0, 205.0, 1.8330, 2, "EFFECTIVE CLEAR", 4, "A"),
    ("Archangelio", 1, "ADV", "13", 8898385, 0, 203.0, 1.8151, 2, "EFFECTIVE CLEAR", 4, "A"),
]


def get_sample_rows() -> list[dict]:
    """Return a list of 50 sample song records with covers if available."""
    rows = []
    base_dir = os.path.dirname(os.path.abspath(__file__))
    for idx, item in enumerate(SAMPLE_SONGS):
        (title, mtype, label, level, score, exscore, vf, vf_pct, clear, clear_name, grade, grade_name) = item
        candidates = [
            os.path.join(base_dir, "..", "assets", "covers", f"cover_{idx+1:02d}.jpg"),
            os.path.join(base_dir, "assets", "covers", f"cover_{idx+1:02d}.jpg"),
            os.path.join(os.getcwd(), "assets", "covers", f"cover_{idx+1:02d}.jpg"),
        ]
        cover_path = next((p for p in candidates if os.path.isfile(p)), None)
        rows.append({
            "mid": idx + 1,
            "type": mtype,
            "title": title,
            "label": label,
            "level": level,
            "score": score,
            "exscore": exscore,
            "volforce": vf,
            "vf_pct": vf_pct,
            "clear": clear,
            "clear_name": clear_name,
            "grade": grade,
            "grade_name": grade_name,
            "cover_path": cover_path,
        })
    return rows
