"""Optional client for Julia analytics service.
Set JULIA_ANALYTICS_URL to enable.
"""
from __future__ import annotations

import os
from typing import Any, Dict, Optional

try:
    import requests  # type: ignore
except Exception:  # pragma: no cover
    requests = None  # type: ignore


def get_summary(timeout: float = 5.0) -> Optional[Dict[str, Any]]:
    base = os.environ.get("JULIA_ANALYTICS_URL")
    if not base or requests is None:
        return None
    try:
        r = requests.get(base.rstrip('/') + '/summary', timeout=timeout)
        if r.ok:
            return r.json()
    except Exception:
        return None
    return None
