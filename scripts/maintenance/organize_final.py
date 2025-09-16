#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script final para organizar os últimos arquivos restantes
"""

import os
import shutil
from pathlib import Path

def organize_remaining_files():
    """Move os arquivos restantes para suas pastas apropriadas."""
    
    print("=" * 60)
    print("ORGANIZANDO ARQUIVOS RESTANTES")
    print("=" * 60)
    
    base_dir = Path(".")
    moved_count = 0
    
    # Arquivos para mover
    files_to_move = {
        'scripts/maintenance/': [
            'organize_root.py',
            'organize_complete.py'
        ]
    }
    
    print(f"\n📦 Movendo arquivos restantes...")
    
    for target_dir, files in files_to_move.items():
        target_path = base_dir / target_dir
        target_path.mkdir(parents=True, exist_ok=True)
        
        for file_name in files:
            source_path = base_dir / file_name
            if source_path.exists() and source_path.is_file():
                dest_path = target_path / file_name
                try:
                    shutil.move(str(source_path), str(dest_path))
                    print(f"  📄 {file_name} → {target_dir}")
                    moved_count += 1
                except Exception as e:
                    print(f"  ❌ Erro ao mover {file_name}: {e}")
    
    print(f"\n📊 RESUMO:")
    print(f"  ✅ Arquivos movidos: {moved_count}")
    
    # Listar arquivos finais na raiz
    print(f"\n📋 ARQUIVOS FINAIS NA RAIZ:")
    root_files = []
    for item in base_dir.iterdir():
        if item.is_file() and not item.name.startswith('.'):
            root_files.append(item.name)
    
    # Arquivos essenciais que devem ficar na raiz
    essential_files = {
        'server_form.py', 'server.py', 'main_system.py', 
        'index.html', 'package.json', 'requirements.txt', 
        'requirements_production.txt', 'README.md', 
        'server.js'
    }
    
    print("  🔹 ESSENCIAIS (devem ficar):")
    for file in sorted(root_files):
        if file in essential_files:
            print(f"    ✅ {file}")
    
    print("  🔹 OUTROS:")
    for file in sorted(root_files):
        if file not in essential_files:
            print(f"    📄 {file}")
    
    print(f"\n" + "=" * 60)
    print("✅ ORGANIZAÇÃO FINAL CONCLUÍDA!")
    print("=" * 60)

if __name__ == "__main__":
    organize_remaining_files()
