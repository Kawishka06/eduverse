"""
Vercel serverless entry — re-exports the FastAPI ASGI app from main.py.

In the Vercel dashboard, set the project Root Directory to `backend`.
"""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import app  # noqa: E402

__all__ = ["app"]
