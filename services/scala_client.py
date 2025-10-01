import os
from typing import Optional
import requests

BASE = os.environ.get('SCALA_TOOLS_URL')

def b64_encode(data: str) -> Optional[str]:
    if not BASE:
        return None
    try:
        resp = requests.post(BASE.rstrip('/') + '/b64/encode', data=data.encode('utf-8'), timeout=10)
        if resp.status_code == 200:
            return resp.json().get('data')
    except Exception:
        return None
    return None

def b64_decode(b64: str) -> Optional[str]:
    if not BASE:
        return None
    try:
        resp = requests.post(BASE.rstrip('/') + '/b64/decode', data=b64.encode('utf-8'), timeout=10)
        if resp.status_code == 200:
            return resp.json().get('data')
    except Exception:
        return None
    return None
