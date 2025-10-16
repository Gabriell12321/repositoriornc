import os
from typing import Optional
import requests

BASE = os.environ.get('SWIFT_TOOLS_URL')

def sha256(text: str) -> Optional[str]:
    if not BASE:
        return None
    try:
        url = BASE.rstrip('/') + '/hash'
        # Our server just reads the raw body and responds JSON
        resp = requests.post(url, data=text.encode('utf-8'), timeout=10)
        if resp.status_code == 200:
            j = resp.json()
            return j.get('sha256')
    except Exception:
        return None
    return None
