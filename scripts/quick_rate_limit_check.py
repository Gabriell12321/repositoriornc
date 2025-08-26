#!/usr/bin/env python3
"""
Quick smoke test for rate limiting on /api/login.
Sends 6 bad login attempts and prints status codes; expect 401 then 429.
"""
import json
import os
import sys

# Add project root to sys.path
ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from server_form import app


def main() -> int:
    client = app.test_client()
    statuses = []
    payload = {"email": "naoexiste@example.com", "password": "errada"}
    headers = {"Content-Type": "application/json"}
    for i in range(6):
        resp = client.post('/api/login', data=json.dumps(payload), headers=headers)
        statuses.append(resp.status_code)
    print("Statuses:", statuses)
    # Basic expectation: first <=5 requests 401, then 429
    ok = any(s == 429 for s in statuses)
    print("Has 429:", ok)
    return 0 if ok else 1


if __name__ == '__main__':
    raise SystemExit(main())
