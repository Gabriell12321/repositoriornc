import os
from typing import Optional
import requests

BASE = os.environ.get('HASKELL_TOOLS_URL')

def levenshtein(a: str, b: str) -> Optional[int]:
    if not BASE:
        return None
    try:
        resp = requests.post(BASE.rstrip('/') + '/levenshtein', data=(a + ';' + b).encode('utf-8'), timeout=10)
        if resp.status_code == 200:
            return resp.json().get('distance')
    except Exception:
        return None
    return None
