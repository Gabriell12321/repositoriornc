import os
from typing import Optional
import requests

BASE = os.environ.get('V_TOOLS_URL')

def slugify(text: str) -> Optional[str]:
    if not BASE:
        return None
    try:
        r = requests.get(BASE.rstrip('/') + '/slug', params={'text': text}, timeout=5)
        if r.status_code == 200:
            return r.json().get('slug')
    except Exception:
        return None
    return None
