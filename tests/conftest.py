import os
import sys

# Ensure src/ and repo root are on sys.path for test discovery
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(REPO_ROOT, "src")

for p in (SRC_DIR, REPO_ROOT):
    if p not in sys.path:
        sys.path.insert(0, p)
