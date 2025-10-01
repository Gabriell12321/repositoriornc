#!/usr/bin/env python3
"""
Minify static CSS/JS into .min files and append a short report.
Uses rjsmin and cssmin if available; falls back to simple whitespace minification.
"""
import os
import sys
import re
from typing import Tuple

ROOT = os.path.dirname(os.path.dirname(__file__))
STATIC_DIR = os.path.join(ROOT, 'static')

def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)

def read(path: str) -> str:
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def write(path: str, data: str) -> None:
    ensure_dir(os.path.dirname(path))
    with open(path, 'w', encoding='utf-8') as f:
        f.write(data)

def try_js_min(src: str) -> str:
    try:
        import rjsmin  # type: ignore
        return rjsmin.jsmin(src)
    except Exception:
        # naive fallback: strip comments and collapse whitespace
        src = re.sub(r"/\*.*?\*/", "", src, flags=re.S)
        src = re.sub(r"(^|\n)\s*//.*?$", "", src, flags=re.M)
        src = re.sub(r"\s+", " ", src)
        return src.strip()

def try_css_min(src: str) -> str:
    try:
        import cssmin  # type: ignore
        return cssmin.cssmin(src)
    except Exception:
        src = re.sub(r"/\*.*?\*/", "", src, flags=re.S)
        src = re.sub(r"\s+", " ", src)
        return src.strip()

def process_file(path: str) -> Tuple[str, int, int]:
    raw = read(path)
    if path.endswith('.js'):
        out = try_js_min(raw)
    else:
        out = try_css_min(raw)
    before = len(raw.encode('utf-8'))
    after = len(out.encode('utf-8'))
    parts = path.rsplit('.', 1)
    out_path = parts[0] + '.min.' + parts[1]
    write(out_path, out)
    return out_path, before, after

def main() -> int:
    if not os.path.isdir(STATIC_DIR):
        print(f"Static dir not found: {STATIC_DIR}")
        return 1
    total_before = total_after = 0
    written = []
    for root, _dirs, files in os.walk(STATIC_DIR):
        for fn in files:
            if fn.endswith(('.min.js', '.min.css')):
                continue
            if fn.endswith('.js') or fn.endswith('.css'):
                path = os.path.join(root, fn)
                try:
                    out_path, before, after = process_file(path)
                    written.append((path, out_path, before, after))
                    total_before += before
                    total_after += after
                    print(f"Minified: {os.path.relpath(path, STATIC_DIR)} -> {os.path.relpath(out_path, STATIC_DIR)} ({before} -> {after} bytes)")
                except Exception as e:
                    print(f"Failed to minify {path}: {e}")
    print(f"Summary: {len(written)} files, total {total_before} -> {total_after} bytes ({(1 - (total_after/total_before)) * 100:.1f}% saved)" if total_before else "No assets processed")
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
