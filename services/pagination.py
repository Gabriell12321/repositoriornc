"""
Utilities for cursor-based pagination across endpoints.

Contract:
- parse_cursor_limit(request, default_limit=20, max_limit=100) -> (cursor_id:int|None, limit:int)
- compute_window(rows:list[tuple], limit:int, id_index:int=0) -> (page_rows, has_more:bool, next_cursor:int|None)

Notes:
- We paginate on a monotonically increasing integer key (usually `id`).
- Ordering is DESC (newest first), and we fetch limit+1 to detect has_more.
"""
from typing import Any, List, Optional, Tuple


def parse_cursor_limit(req, default_limit: int = 20, max_limit: int = 100) -> Tuple[Optional[int], int]:
    raw_cursor = req.args.get('cursor') or req.args.get('after')
    try:
        cursor_id = int(raw_cursor) if raw_cursor is not None and str(raw_cursor).isdigit() else None
    except Exception:
        cursor_id = None
    try:
        limit = int(req.args.get('limit') or default_limit)
    except Exception:
        limit = default_limit
    if limit < 1:
        limit = 1
    if limit > max_limit:
        limit = max_limit
    return cursor_id, limit


def compute_window(rows: List[tuple], limit: int, id_index: int = 0):
    has_more = len(rows) > limit
    if has_more:
        rows = rows[:limit]
    next_cursor = rows[-1][id_index] if rows else None
    return rows, has_more, next_cursor
