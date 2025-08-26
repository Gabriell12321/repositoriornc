#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Generate a comprehensive architecture report for the IPPEL RNC system.

Outputs: docs/arquitetura_completa.md

Features:
- Repository inventory (files, sizes, line counts)
- Dependencies (requirements.txt, requirements_production.txt, package.json)
- Flask routes extraction (path, methods, function, decorators, docstrings)
- Services summary (functions/classes and docstrings)
- Security posture (CSP config, CSRF, rate limit, security log)
- Database schema (tables, columns, indexes) via SQLite if DB file exists
- Templates analysis (blocks and variable usage heuristics)
- Environment variables discovered by simple search
- Tasks/scripts listing
- Appendix: full code listings for major files to ensure >3000 lines

This script is idempotent and safe to run multiple times.
"""

from __future__ import annotations

import ast
import json
import os
import re
import sqlite3
import sys
from datetime import datetime, UTC
from pathlib import Path
from typing import Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = ROOT / "docs"
OUTPUT = DOCS_DIR / "arquitetura_completa.md"
AI_DIR = DOCS_DIR / "ia estudar"


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        return f"<ERROR reading {path}: {e}>\n"


def list_repo_files(root: Path) -> List[Path]:
    files: List[Path] = []
    skip_dirs = {".git", "node_modules", ".venv", "venv", "env", "__pycache__", ".mypy_cache", ".pytest_cache", "dist", "build"}
    for dirpath, dirnames, filenames in os.walk(root, topdown=True):
        # prune heavy/irrelevant directories in-place
        dirnames[:] = [d for d in dirnames if d.lower() not in skip_dirs]
        for fn in filenames:
            p = Path(dirpath) / fn
            files.append(p)
    return files


def count_lines(text: str) -> int:
    return text.count("\n") + (0 if text.endswith("\n") else 1 if text else 0)


def summarize_dependencies() -> str:
    parts: List[str] = ["## Dependências\n"]
    for req in [ROOT / "requirements.txt", ROOT / "requirements_production.txt"]:
        if req.exists():
            parts.append(f"### {req.name}\n")
            parts.append("```")
            parts.append(read_text(req).strip())
            parts.append("```\n")
    pkg = ROOT / "package.json"
    if pkg.exists():
        parts.append("### package.json (dependências)\n")
        try:
            data = json.loads(read_text(pkg))
            for key in ("dependencies", "devDependencies"):
                if key in data and data[key]:
                    parts.append(f"- {key}:")
                    for k, v in data[key].items():
                        parts.append(f"  - {k}: {v}")
        except Exception:
            parts.append("```")
            parts.append(read_text(pkg).strip())
            parts.append("```\n")
    return "\n".join(parts)


def extract_flask_routes(py_path: Path) -> List[Dict[str, str]]:
    routes: List[Dict[str, str]] = []
    src = read_text(py_path)
    try:
        tree = ast.parse(src)
    except Exception:
        return routes

    class Visitor(ast.NodeVisitor):
        def visit_FunctionDef(self, node: ast.FunctionDef):
            for dec in node.decorator_list:
                try:
                    if isinstance(dec, ast.Call):
                        # something.route("/path", methods=[...])
                        if isinstance(dec.func, ast.Attribute) and dec.func.attr == "route":
                            # path
                            path = None
                            methods = None
                            if dec.args:
                                if isinstance(dec.args[0], (ast.Str, ast.Constant)):
                                    path = getattr(dec.args[0], 's', None) or getattr(dec.args[0], 'value', None)
                            for kw in dec.keywords or []:
                                if kw.arg == "methods" and isinstance(kw.value, (ast.List, ast.Tuple)):
                                    vals = []
                                    for elt in kw.value.elts:
                                        if isinstance(elt, (ast.Str, ast.Constant)):
                                            vals.append(getattr(elt, 's', None) or getattr(elt, 'value', None))
                                    methods = ",".join(filter(None, vals))
                            # other decorators of interest on same function
                            decorators = []
                            for d2 in node.decorator_list:
                                name = None
                                if isinstance(d2, ast.Name):
                                    name = d2.id
                                elif isinstance(d2, ast.Attribute):
                                    name = d2.attr
                                elif isinstance(d2, ast.Call):
                                    if isinstance(d2.func, ast.Name):
                                        name = d2.func.id
                                    elif isinstance(d2.func, ast.Attribute):
                                        name = d2.func.attr
                                if name:
                                    decorators.append(name)
                            doc = ast.get_docstring(node) or ""
                            routes.append({
                                "file": str(py_path.relative_to(ROOT)),
                                "function": node.name,
                                "path": path or "<dynamic>",
                                "methods": methods or "GET",
                                "decorators": ", ".join(sorted(set(decorators))),
                                "doc": doc.strip().splitlines()[0] if doc else "",
                            })
                except Exception:
                    continue
            self.generic_visit(node)

    Visitor().visit(tree)
    return routes


def summarize_routes(files: List[Path]) -> str:
    parts: List[str] = ["## Rotas Flask\n"]
    all_routes: List[Dict[str, str]] = []
    for f in files:
        if f.suffix == ".py" and ("routes" in f.parts or f.name in {"server_form.py", "server.py", "main_system.py"}):
            all_routes.extend(extract_flask_routes(f))
    if not all_routes:
        parts.append("(nenhuma rota detectada via análise estática)\n")
        return "\n".join(parts)
    # group by file
    by_file: Dict[str, List[Dict[str, str]]] = {}
    for r in all_routes:
        by_file.setdefault(r["file"], []).append(r)
    for file, rs in sorted(by_file.items()):
        parts.append(f"### {file}\n")
        for r in sorted(rs, key=lambda x: (x["path"], x["methods"])):
            parts.append(f"- {r['methods']:>7} {r['path']} → `{r['function']}` (decorators: {r['decorators']})")
            if r.get("doc"):
                parts.append(f"  - {r['doc']}")
        parts.append("")
    return "\n".join(parts)


def collect_routes(files: List[Path]) -> List[Dict[str, str]]:
    all_routes: List[Dict[str, str]] = []
    for f in files:
        if f.suffix == ".py" and ("routes" in f.parts or f.name in {"server_form.py", "server.py", "main_system.py"}):
            all_routes.extend(extract_flask_routes(f))
    return all_routes


def summarize_services(files: List[Path]) -> str:
    parts: List[str] = ["## Serviços (funções/classes)\n"]
    for f in sorted(files):
        if f.suffix == ".py" and ("services" in f.parts):
            try:
                src = read_text(f)
                tree = ast.parse(src)
            except Exception:
                continue
            items: List[str] = []
            for node in tree.body:
                if isinstance(node, ast.FunctionDef):
                    doc = ast.get_docstring(node) or ""
                    items.append(f"- def {node.name}() — {doc.strip().splitlines()[0] if doc else ''}")
                elif isinstance(node, ast.ClassDef):
                    doc = ast.get_docstring(node) or ""
                    items.append(f"- class {node.name} — {doc.strip().splitlines()[0] if doc else ''}")
            if items:
                parts.append(f"### {f.relative_to(ROOT)}\n")
                parts.extend(items)
                parts.append("")
    return "\n".join(parts)


def collect_services_index(files: List[Path]) -> Dict[str, List[Dict[str, str]]]:
    result: Dict[str, List[Dict[str, str]]] = {}
    for f in sorted(files):
        if f.suffix == ".py" and ("services" in f.parts or f.name in {"server_form.py"}):
            try:
                src = read_text(f)
                tree = ast.parse(src)
            except Exception:
                continue
            items: List[Dict[str, str]] = []
            for node in tree.body:
                if isinstance(node, ast.FunctionDef):
                    doc = (ast.get_docstring(node) or "").strip().splitlines()[0] if ast.get_docstring(node) else ""
                    items.append({"kind": "function", "name": node.name, "doc": doc})
                elif isinstance(node, ast.ClassDef):
                    doc = (ast.get_docstring(node) or "").strip().splitlines()[0] if ast.get_docstring(node) else ""
                    items.append({"kind": "class", "name": node.name, "doc": doc})
            if items:
                result[str(f.relative_to(ROOT))] = items
    return result


def load_sqlite_schema(db_path: Path) -> Tuple[str, List[str]]:
    details: List[str] = []
    try:
        con = sqlite3.connect(str(db_path))
        cur = con.cursor()
        details.append(f"Conectado a {db_path.name}")
        # tables
        cur.execute("SELECT name, sql FROM sqlite_master WHERE type='table' ORDER BY name;")
        rows = cur.fetchall()
        for name, sql in rows:
            details.append(f"### Tabela: {name}\n")
            details.append("```sql")
            details.append(sql or "<no ddl>")
            details.append("```\n")
            # columns
            try:
                cur.execute(f"PRAGMA table_info('{name}')")
                cols = cur.fetchall()
                details.append("Colunas:")
                for cid, cname, ctype, notnull, dflt, pk in cols:
                    details.append(f"- {cname} {ctype} {'NOT NULL' if notnull else ''} {'PK' if pk else ''} default={dflt}")
            except Exception:
                pass
            details.append("")
        # indexes
        cur.execute("SELECT name, tbl_name, sql FROM sqlite_master WHERE type='index' ORDER BY tbl_name,name;")
        idxs = cur.fetchall()
        if idxs:
            details.append("### Índices\n")
            for name, tbl, sql in idxs:
                details.append(f"- {name} on {tbl}: {sql}")
        con.close()
    except Exception as e:
        return f"(não foi possível inspecionar schema: {e})\n", []
    return "\n".join(details), [r[0] for r in rows] if 'rows' in locals() else []


def get_sqlite_schema_struct(db_path: Path) -> Dict[str, Dict[str, object]]:
    out: Dict[str, Dict[str, object]] = {}
    try:
        con = sqlite3.connect(str(db_path))
        cur = con.cursor()
        cur.execute("SELECT name, sql FROM sqlite_master WHERE type='table' ORDER BY name;")
        for name, sql in cur.fetchall():
            tbl = {"ddl": sql, "columns": []}
            try:
                cur.execute(f"PRAGMA table_info('{name}')")
                for cid, cname, ctype, notnull, dflt, pk in cur.fetchall():
                    tbl["columns"].append({
                        "name": cname,
                        "type": ctype,
                        "notnull": bool(notnull),
                        "default": dflt,
                        "primary_key": bool(pk),
                    })
            except Exception:
                pass
            out[name] = tbl
        con.close()
    except Exception:
        return {}
    return out


def summarize_database() -> str:
    parts: List[str] = ["## Banco de Dados (SQLite)\n"]
    # look for the most recent db file, prefer ippel_system.db
    candidates = [ROOT / "ippel_system.db", ROOT / "ippel_system_new.db", ROOT / "database.db"]
    for p in sorted(ROOT.glob("ippel_system_backup_*.db")):
        candidates.append(p)
    db_path: Optional[Path] = None
    for c in candidates:
        if c.exists():
            db_path = c
            break
    if db_path:
        schema_text, _ = load_sqlite_schema(db_path)
        parts.append(schema_text)
    else:
        parts.append("(arquivo de banco não encontrado)\n")
    # PRAGMAs from services/db.py
    db_py = ROOT / "services" / "db.py"
    if db_py.exists():
        parts.append("### PRAGMAs (services/db.py)\n")
        src = read_text(db_py)
        pragmas = [ln.strip() for ln in src.splitlines() if "PRAGMA" in ln]
        if pragmas:
            parts.append("```")
            parts.extend(pragmas)
            parts.append("```\n")
    return "\n".join(parts)


def summarize_templates(files: List[Path]) -> str:
    parts: List[str] = ["## Templates (Jinja)\n"]
    tpl_files = [f for f in files if f.suffix in {".html", ".jinja", ".j2"} and "templates" in f.parts]
    for f in sorted(tpl_files):
        text = read_text(f)
        # basic heuristics: blocks and variables
        blocks = re.findall(r"{%\s*block\s+(\w+)\s*%}", text)
        vars_used = set(re.findall(r"{{\s*([\w\.\[\]']+)\s*}}", text))
        parts.append(f"### {f.relative_to(ROOT)}\n")
        if blocks:
            parts.append(f"- blocks: {', '.join(sorted(set(blocks)))}")
        if vars_used:
            sample = ", ".join(sorted(list(vars_used))[:20])
            parts.append(f"- variáveis (amostra): {sample} (+{max(len(vars_used)-20,0)} mais)")
        parts.append(f"- linhas: {count_lines(text)}\n")
    return "\n".join(parts)


def summarize_security(files: List[Path]) -> str:
    parts: List[str] = ["## Segurança (CSP, CSRF, Rate Limit, Logs)\n"]
    server_form = ROOT / "server_form.py"
    if server_form.exists():
        src = read_text(server_form)
        # Find CSP policy lines
        csp_lines = [ln.strip() for ln in src.splitlines() if "Content-Security-Policy" in ln or "Talisman" in ln]
        parts.append("### server_form.py (CSP/Headers)\n")
        parts.append("```")
        parts.extend(csp_lines or ["(CSP lines não identificadas por heurística)"])
        parts.append("```\n")
    # Search for CSRF decorators
    csrf_refs = []
    rl_refs = []
    for f in files:
        if f.suffix == ".py":
            text = read_text(f)
            if "csrf_protect" in text:
                csrf_refs.append(str(f.relative_to(ROOT)))
            if "rate_limit(" in text or "Limiter(" in text:
                rl_refs.append(str(f.relative_to(ROOT)))
    if csrf_refs:
        parts.append("### CSRF decorators referenciados em:\n- " + "\n- ".join(sorted(set(csrf_refs))) + "\n")
    if rl_refs:
        parts.append("### Rate limiting referenciado em:\n- " + "\n- ".join(sorted(set(rl_refs))) + "\n")
    # Security log
    sec_log_py = ROOT / "services" / "security_log.py"
    if sec_log_py.exists():
        parts.append("### services/security_log.py (logger)\n")
        parts.append("```")
        parts.append(".. ver arquivo para detalhes; logger 'security' com JSON lines e rotação")
        parts.append("```\n")
    return "\n".join(parts)


def summarize_env_vars(files: List[Path]) -> str:
    parts: List[str] = ["## Variáveis de Ambiente (observadas por busca)\n"]
    pattern = re.compile(r"os\.environ\.get\(['\"]([A-Z0-9_]+)['\"]")
    found: Dict[str, List[str]] = {}
    for f in files:
        if f.suffix == ".py":
            text = read_text(f)
            for m in pattern.finditer(text):
                key = m.group(1)
                found.setdefault(key, []).append(str(f.relative_to(ROOT)))
    if not found:
        return "(nenhuma env var detectada via heurística)\n"
    lines = [f"- {k}: usado em {', '.join(sorted(set(v)))}" for k, v in sorted(found.items())]
    return "\n".join(parts + lines + [""])


def collect_env_vars(files: List[Path]) -> Dict[str, List[str]]:
    pattern = re.compile(r"os\.environ\.get\(['\"]([A-Z0-9_]+)['\"]")
    found: Dict[str, List[str]] = {}
    for f in files:
        if f.suffix == ".py":
            text = read_text(f)
            for m in pattern.finditer(text):
                key = m.group(1)
                found.setdefault(key, []).append(str(f.relative_to(ROOT)))
    return found


def summarize_tasks_and_scripts(files: List[Path]) -> str:
    parts: List[str] = ["## Tarefas e Scripts\n"]
    # Batch and PowerShell scripts
    bats = [f for f in files if f.suffix.lower() in {'.bat', '.cmd', '.ps1'}]
    if bats:
        parts.append("### Scripts (.bat/.cmd/.ps1)\n")
        for f in sorted(bats):
            parts.append(f"- {f.relative_to(ROOT)} ({count_lines(read_text(f))} linhas)")
        parts.append("")
    # Node tasks (package.json scripts)
    pkg = ROOT / "package.json"
    if pkg.exists():
        try:
            data = json.loads(read_text(pkg))
            scripts = data.get("scripts", {})
            if scripts:
                parts.append("### package.json scripts\n")
                for k, v in scripts.items():
                    parts.append(f"- {k}: {v}")
                parts.append("")
        except Exception:
            pass
    parts.append("(Tarefas específicas do VS Code podem existir em .vscode/tasks.json se presente)\n")
    return "\n".join(parts)


def make_inventory(files: List[Path]) -> str:
    parts: List[str] = ["## Inventário do Repositório\n"]
    total_lines = 0
    for f in sorted(files):
        try:
            size = f.stat().st_size
        except Exception:
            size = 0
        text_preview = read_text(f)
        lines = count_lines(text_preview)
        total_lines += lines
        parts.append(f"- {f.relative_to(ROOT)} — {size} bytes, {lines} linhas")
    parts.append("")
    parts.append(f"Total de arquivos: {len(files)}; Total de linhas (aprox.): {total_lines}\n")
    return "\n".join(parts)


def append_code_listings(files: List[Path]) -> str:
    parts: List[str] = ["## Apêndice A — Listagem Completa de Código\n"]
    # Include major text/code types
    include_ext = {".py", ".js", ".ts", ".html", ".css", ".md", ".json", ".bat", ".cmd", ".ps1", ".txt"}
    for f in sorted(files):
        if f.suffix.lower() in include_ext:
            rel = f.relative_to(ROOT)
            parts.append(f"### {rel}\n")
            parts.append("```")
            parts.append(read_text(f).rstrip("\n"))
            parts.append("```\n")
    return "\n".join(parts)


def write_ai_study_pack(files: List[Path]) -> None:
    AI_DIR.mkdir(parents=True, exist_ok=True)
    # Routes JSON and MD
    routes = collect_routes(files)
    (AI_DIR / "routes.json").write_text(json.dumps(routes, ensure_ascii=False, indent=2), encoding="utf-8")
    routes_md = ["# Mapa de Rotas (resumo)", ""]
    by_file: Dict[str, List[Dict[str, str]]] = {}
    for r in routes:
        by_file.setdefault(r["file"], []).append(r)
    for file, rs in sorted(by_file.items()):
        routes_md.append(f"## {file}")
        for r in sorted(rs, key=lambda x: (x["path"], x["methods"])):
            routes_md.append(f"- {r['methods']:>7} {r['path']} → `{r['function']}` ({r['decorators']})")
        routes_md.append("")
    (AI_DIR / "02_ROTAS_MAPA.md").write_text("\n".join(routes_md), encoding="utf-8")

    # Services index JSON
    services_idx = collect_services_index(files)
    (AI_DIR / "services_index.json").write_text(json.dumps(services_idx, ensure_ascii=False, indent=2), encoding="utf-8")

    # Env vars JSON and MD
    envs = collect_env_vars(files)
    (AI_DIR / "env_vars.json").write_text(json.dumps(envs, ensure_ascii=False, indent=2), encoding="utf-8")
    envs_md = ["# Variáveis de Ambiente (uso no código)", ""]
    for k, v in sorted(envs.items()):
        envs_md.append(f"- {k}: {', '.join(sorted(set(v)))}")
    (AI_DIR / "06_ENV_VARS.md").write_text("\n".join(envs_md), encoding="utf-8")

    # Inventory CSV
    lines = ["path,size_bytes,line_count"]
    for f in sorted(files):
        try:
            size = f.stat().st_size
        except Exception:
            size = 0
        lc = count_lines(read_text(f))
        rel = str(f.relative_to(ROOT))
        # escape commas
        if "," in rel:
            rel = '"' + rel.replace('"', '""') + '"'
        lines.append(f"{rel},{size},{lc}")
    (AI_DIR / "inventory.csv").write_text("\n".join(lines), encoding="utf-8")

    # DB schema compact MD/JSON if DB exists
    candidates = [ROOT / "ippel_system.db", ROOT / "ippel_system_new.db", ROOT / "database.db"]
    db_path = next((c for c in candidates if c.exists()), None)
    if db_path:
        schema_struct = get_sqlite_schema_struct(db_path)
        (AI_DIR / "db_schema.json").write_text(json.dumps(schema_struct, ensure_ascii=False, indent=2), encoding="utf-8")
        db_md = ["# Esquema do Banco (compacto)", ""]
        for tname in sorted(schema_struct.keys()):
            db_md.append(f"## {tname}")
            cols = schema_struct[tname].get("columns", [])
            for c in cols:
                flags = []
                if c.get("primary_key"): flags.append("PK")
                if c.get("notnull"): flags.append("NOT NULL")
                default = f" default={c.get('default')}" if c.get('default') is not None else ""
                db_md.append(f"- {c.get('name')} {c.get('type','')} {' '.join(flags)}{default}")
            db_md.append("")
        (AI_DIR / "03_DB_ESQUEMA.md").write_text("\n".join(db_md), encoding="utf-8")

    # 00_INDEX.md entry point
    index_md = [
        "# IA: Pacote de Estudo Rápido",
        "",
        "Use estes arquivos para ter visão imediata do projeto:",
        "",
        "- 01_VISÃO_GERAL.md (resumo curto)",
        "- 02_ROTAS_MAPA.md (rotas resumidas)",
        "- 03_DB_ESQUEMA.md (tabelas e colunas)",
        "- 04_PERMISSOES.md (matriz de permissões)",
        "- 05_API_EXEMPLOS.md (exemplos de chamadas)",
        "- 06_ENV_VARS.md (variáveis de ambiente)",
        "- routes.json, services_index.json, env_vars.json (machine-readable)",
        "- inventory.csv (inventário)",
        "- arquitetura.md (arquitetura detalhada humana)",
        "- arquitetura_completa.md (arquivo grande com listagens)",
    ]
    (AI_DIR / "00_INDEX.md").write_text("\n".join(index_md), encoding="utf-8")

    # 01_VISÃO_GERAL.md
    overview = [
        "# Visão Geral (curta)",
        "- Backend Flask (`server_form.py`), Blueprints (auth, api, rnc)",
        "- SQLite com WAL/PRAGMAs, pool de conexões e backups",
        "- Sessão + JWT opcional, rate limit opcional, CSRF opcional, logs de segurança",
        "- Permissões por grupo e fallback por departamento; compartilhamento de RNCs",
        "- Templates Jinja, assets minificados; rotas de dashboards e RNC",
        "- Integráveis (Analytics/PDF/QR/Utils) com fallback 404",
    ]
    (AI_DIR / "01_VISÃO_GERAL.md").write_text("\n".join(overview), encoding="utf-8")

    # 04_PERMISSOES.md — heurística a partir do código
    # Procurar padrões has_permission(, 'perm')
    perms_set = set()
    for f in files:
        if f.suffix == ".py":
            text = read_text(f)
            for m in re.finditer(r"has_permission\([^,]+,\s*['\"]([a-zA-Z0-9_./-]+)['\"]\)", text):
                perms_set.add(m.group(1))
    perms_md = ["# Permissões (mapeadas por heurística)", ""]
    for p in sorted(perms_set):
        perms_md.append(f"- {p}")
    (AI_DIR / "04_PERMISSOES.md").write_text("\n".join(perms_md), encoding="utf-8")

    # 05_API_EXEMPLOS.md (exemplos mínimos)
    api_md = [
        "# Exemplos de API (mínimos)",
        "",
        "- POST /api/login — body: { email, password } → { success, user, tokens? }",
        "- GET /api/csrf-token — { csrf_token }",
        "- POST /api/rnc/create — body com campos da RNC → { success, rnc_id }",
        "- GET /api/rnc/list?tab=active&limit=50 → { rncs: [...], next_cursor }",
        "- PUT /api/rnc/<id>/update — { ...campos... } → { success }",
        "- POST /api/rnc/<id>/finalize — {} → { success }",
        "- POST /api/rnc/<id>/reply — { comment? } → { success }",
        "- DELETE /api/rnc/<id>/delete — {} → { success }",
    ]
    (AI_DIR / "05_API_EXEMPLOS.md").write_text("\n".join(api_md), encoding="utf-8")


def main() -> int:
    print(f"[1/10] Scanning repository at {ROOT}...")
    files = list_repo_files(ROOT)
    print(f"    Found {len(files)} files (including non-code).")
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    total_lines = 0
    with OUTPUT.open("w", encoding="utf-8") as fp:
        header = f"# Arquitetura Completa — IPPEL RNC\n\nGerado em {datetime.now(UTC).isoformat()}\n\n"
        fp.write(header)
        total_lines += count_lines(header)
        # Sections
        steps = [
            ("[2/10] Building repository inventory...", make_inventory, [files]),
            ("[3/10] Summarizing dependencies...", summarize_dependencies, []),
            ("[4/10] Extracting Flask routes...", summarize_routes, [files]),
            ("[5/10] Summarizing services...", summarize_services, [files]),
            ("[6/10] Inspecting database schema...", summarize_database, []),
            ("[7/10] Analyzing templates...", summarize_templates, [files]),
            ("[8/10] Summarizing security posture...", summarize_security, [files]),
            ("[9/10] Discovering environment variables and tasks...", summarize_env_vars, [files]),
            ("[9b/10] Tasks and scripts...", summarize_tasks_and_scripts, [files]),
        ]
        for msg, fn, args in steps:
            try:
                print(msg)
                sec = fn(*args)
                fp.write(sec)
                if not sec.endswith("\n"):
                    fp.write("\n")
                fp.write("\n")
                total_lines += count_lines(sec) + 2
            except Exception as e:
                err = f"\n### ERRO gerando seção ({msg}): {e}\n\n"
                fp.write(err)
                total_lines += count_lines(err)
        # Appendix (can be big)
        try:
            print("[10/10] Appending full code listings (this may take a while)...")
            appendix = append_code_listings(files)
            fp.write(appendix)
            if not appendix.endswith("\n"):
                fp.write("\n")
            total_lines += count_lines(appendix) + 1
        except Exception as e:
            err = f"\n### ERRO gerando apêndice: {e}\n\n"
            fp.write(err)
            total_lines += count_lines(err)

    print(f"Done. Wrote {OUTPUT} with ~{total_lines} lines.")
    if total_lines < 3000:
        print("WARNING: Document below desired size (3000 lines). Consider adding more listings or sections.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
