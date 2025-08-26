import shutil
from pathlib import Path
import datetime
import argparse

ROOT = Path(__file__).resolve().parent

# Target folders
DIRS = {
    'docs': ROOT / 'docs',
    'docs_ia': ROOT / 'docs' / 'ia estudar',
    'logs': ROOT / 'logs',
    'backups': ROOT / 'backups',
    'tests': ROOT / 'tests',
    'tests_html': ROOT / 'tests' / 'html',
    'scripts': ROOT / 'scripts',
    'scripts_diag': ROOT / 'scripts' / 'diagnostics',
    'scripts_extract': ROOT / 'scripts' / 'extract',
    'scripts_import': ROOT / 'scripts' / 'import',
    'scripts_gen': ROOT / 'scripts' / 'generation',
    'scripts_maint': ROOT / 'scripts' / 'maintenance',
    'scripts_run': ROOT / 'scripts' / 'runners',
    'db': ROOT / 'db',
}

for d in DIRS.values():
    d.mkdir(parents=True, exist_ok=True)

moved = []
skipped = []
now_tag = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')

parser = argparse.ArgumentParser(description='Organize root files into folders.')
parser.add_argument('--dry-run', action='store_true', help='Show what will be moved without applying changes')
parser.add_argument('--move-json', action='store_true', help='Also move loose JSON files into data/ (may require code updates)')
args = parser.parse_args()

def safe_move(src: Path, dst_dir: Path):
    dst = dst_dir / src.name
    if dst.exists():
        # keep existing, rename source into a timestamped name
        dst = dst_dir / f"{src.stem}_{now_tag}{src.suffix}"
    dst.parent.mkdir(parents=True, exist_ok=True)
    if args.dry_run:
        moved.append((src.relative_to(ROOT), dst.relative_to(ROOT)))
    else:
        try:
            shutil.move(str(src), str(dst))
            moved.append((src.relative_to(ROOT), dst.relative_to(ROOT)))
        except Exception as e:
            # Fallback: if file is locked by another process on Windows, try copy
            msg = str(e).lower()
            if "used by another process" in msg or isinstance(e, PermissionError):
                try:
                    shutil.copy2(str(src), str(dst))
                    moved.append((src.relative_to(ROOT), dst.relative_to(ROOT)))
                except Exception as e2:
                    raise e2
            else:
                raise e

# 1) Docs (Markdown) except root README.md
for p in ROOT.glob('*.md'):
    if p.name.lower() == 'readme.md':
        continue
    try:
        safe_move(p, DIRS['docs'])
    except Exception as e:
        skipped.append((p.name, str(e)))

# 1.1) Docs de arquitetura/estudo → docs/ia estudar
arch_patterns = (
    'arquitetura*.md',  # arquitetura.md, arquitetura_completa.md, etc.
)
# Mover dentro de docs/
for pattern in arch_patterns:
    for p in DIRS['docs'].glob(pattern):
        try:
            safe_move(p, DIRS['docs_ia'])
        except Exception as e:
            skipped.append((p.name, str(e)))
# Caso estejam no root por algum motivo
for pattern in arch_patterns:
    for p in ROOT.glob(pattern):
        try:
            safe_move(p, DIRS['docs_ia'])
        except Exception as e:
            skipped.append((p.name, str(e)))

# 2) Logs (known log files only)
for name in ('ippel_system.log', 'email_system.log', 'ippel_security.log'):
    p = ROOT / name
    if p.exists():
        try:
            safe_move(p, DIRS['logs'])
        except Exception as e:
            skipped.append((p.name, str(e)))

# 3) Backups (patterned)
for p in ROOT.glob('ippel_system_backup_*.db'):
    try:
        safe_move(p, DIRS['backups'])
    except Exception as e:
        skipped.append((p.name, str(e)))

# 4) Tests (html)
for pattern in ('test*.html', 'debug*.html'):
    for p in ROOT.glob(pattern):
        try:
            safe_move(p, DIRS['tests_html'])
        except Exception as e:
            skipped.append((p.name, str(e)))

# 5) Tests (python)
for pattern in ('test*.py', 'debug*.py'):
    for p in ROOT.glob(pattern):
        # Don't move this organizer script
        if p.name == Path(__file__).name:
            continue
        try:
            safe_move(p, DIRS['tests'])
        except Exception as e:
            skipped.append((p.name, str(e)))

# 5.1) Additional test-like scripts (print_*.py)
for p in ROOT.glob('print_*.py'):
    if p.name == Path(__file__).name:
        continue
    try:
        safe_move(p, DIRS['tests'])
    except Exception as e:
        skipped.append((p.name, str(e)))

# 6) Scripts (.bat, .sh)
for pattern in ('*.bat', '*.sh'):
    for p in ROOT.glob(pattern):
        try:
            safe_move(p, DIRS['scripts'])
        except Exception as e:
            skipped.append((p.name, str(e)))

# 6.1) Python maintenance/diagnostic/import/export scripts into structured subfolders
# Keep core runtime entrypoints in root to avoid breaking start processes
RUNTIME_KEEP = {
    'server_form.py', 'main_system.py', 'server.py', 'server.js',
}

pattern_dest_pairs = [
    ('check_*.py', DIRS['scripts_diag']),
    ('analyze_*.py', DIRS['scripts_diag']),
    ('inspect_*.py', DIRS['scripts_diag']),
    ('diagnose_*.py', DIRS['scripts_diag']),
    ('simulate_*.py', DIRS['scripts_diag']),
    ('quick_*.py', DIRS['scripts_diag']),
    ('extract_*.py', DIRS['scripts_extract']),
    ('import_*.py', DIRS['scripts_import']),
    ('create_*.py', DIRS['scripts_gen']),
    ('fix_*.py', DIRS['scripts_maint']),
    ('update_*.py', DIRS['scripts_maint']),
    ('migrate_*.py', DIRS['scripts_maint']),
    ('sync_*.py', DIRS['scripts_maint']),
    ('setup_*.py', DIRS['scripts_maint']),
    ('start_*.py', DIRS['scripts_run']),
    # Legacy/alt servers and backups of server code (but keep primary entrypoints)
    ('server_*.py', DIRS['scripts_run']),
]

for pattern, dest in pattern_dest_pairs:
    for p in ROOT.glob(pattern):
        if p.name == Path(__file__).name or p.name in RUNTIME_KEEP:
            continue
        try:
            safe_move(p, dest)
        except Exception as e:
            skipped.append((p.name, str(e)))

# 7) Optional: JSON data files (guarded by flag)
if args.move_json:
    data_dir = ROOT / 'data'
    data_dir.mkdir(parents=True, exist_ok=True)
    for p in ROOT.glob('*.json'):
        if p.name.lower() == 'package.json':
            continue
        try:
            safe_move(p, data_dir)
        except Exception as e:
            skipped.append((p.name, str(e)))

# 8) Database schema (do NOT move live DB files)
schema = ROOT / 'database_schema.sql'
if schema.exists():
    try:
        safe_move(schema, DIRS['db'])
    except Exception as e:
        skipped.append((schema.name, str(e)))

# 9) Consolidate legacy 'backup/' directory into 'backups/'
legacy_backup_dir = ROOT / 'backup'
if legacy_backup_dir.exists() and legacy_backup_dir.is_dir():
    for p in legacy_backup_dir.iterdir():
        if p.is_file():
            try:
                safe_move(p, DIRS['backups'])
            except Exception as e:
                skipped.append((p.name, str(e)))
    # Try removing the empty directory (ignore errors)
    try:
        legacy_backup_dir.rmdir()
    except Exception:
        pass

print('ORGANIZE SUMMARY:\n')
print(f'Moved: {len(moved)} files')
for src, dst in moved:
    print(f' - {src} -> {dst}')

if skipped:
    print(f'\nSkipped: {len(skipped)} files (errors)')
    for name, err in skipped:
        print(f' - {name}: {err}')

note = ('DRY-RUN: no files moved.' if args.dry_run else 'Applied: files moved.')
print(f"\n{note}")
print('\nNote: intentionally left runtime files (e.g., ippel_system.db, static/, templates/, routes/, services/, server_form.py) in place to avoid breaking the app.')
