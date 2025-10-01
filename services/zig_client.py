import os
from typing import Optional
import requests

BASE = os.environ.get('ZIG_TOOLS_URL')

def xxh3(text: str) -> Optional[str]:
    if not BASE:
        return None
    try:
        r = requests.post(BASE.rstrip('/') + '/xxh3', data=text.encode('utf-8'), timeout=5)
        if r.status_code == 200:
            return r.json().get('xxh3')
    except Exception:
        return None
    return None
