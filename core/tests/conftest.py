from __future__ import annotations

import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CORE = ROOT / "core"

for path in (ROOT, CORE):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

os.environ.setdefault("MT_MODEL", "test/model")
os.environ.setdefault("SOURCE_LANGUAGE_DEFAULT", "Test Source")
os.environ.setdefault("TARGET_LANGUAGE_DEFAULT", "Test Target")
