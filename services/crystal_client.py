import os
from typing import Optional
import requests

BASE = os.environ.get('CRYSTAL_TOOLS_URL')

def sha256(text: str) -> Optional[str]:
    if not BASE:
        return None
    try:
        r = requests.post(BASE.rstrip('/') + '/sha256', data=text.encode('utf-8'), timeout=5)
        if r.status_code == 200:
            return r.json().get('sha256')
    except Exception:
        return None
    return None
