"""Optional client for Go reports service.
Set GO_REPORTS_URL to enable.
"""
from __future__ import annotations

import os
from typing import Optional

try:
    import requests  # type: ignore
except Exception:
    requests = None  # type: ignore


def get_rnc_pdf(rnc_id: int | str, timeout: float = 15.0) -> Optional[bytes]:
    base = os.environ.get("GO_REPORTS_URL")
    if not base or requests is None:
        return None
    try:
        r = requests.get(f"{base.rstrip('/')}/reports/rnc/{rnc_id}.pdf", timeout=timeout)
        if r.ok and r.headers.get('Content-Type','').lower().startswith('application/pdf'):
            return r.content
    except Exception:
        return None
    return None
