import os
from typing import Optional
import requests

BASE = os.environ.get('NIM_TOOLS_URL')

def get_uuid() -> Optional[str]:
    if not BASE:
        return None
    try:
        r = requests.get(BASE.rstrip('/') + '/uuid', timeout=5)
        if r.status_code == 200:
            return r.json().get('uuid')
    except Exception:
        return None
    return None

def get_token(size: int = 32) -> Optional[str]:
    if not BASE:
        return None
    try:
        r = requests.get(BASE.rstrip('/') + '/token', params={'size': size}, timeout=5)
        if r.status_code == 200:
            return r.json().get('token')
    except Exception:
        return None
    return None
