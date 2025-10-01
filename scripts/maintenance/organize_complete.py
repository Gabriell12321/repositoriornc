#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para organizar completamente todos os arquivos do projeto
"""

import os
import shutil
from pathlib import Path

def organize_all_files():
    """Organiza completamente todos os arquivos do projeto."""
    
    print("=" * 80)
    print("ORGANIZAÇÃO COMPLETA DE ARQUIVOS - SISTEMA RNC IPPEL")
    print("=" * 80)
    
    base_dir = Path(".")
    moved_count = 0
    
    # Definir estrutura de organização
    organization_rules = {
        # Documentação e imagens
        'assets/': [
            '*.png', '*.jpg', '*.jpeg', '*.gif', '*.ico', '*.svg',
            '*.pdf', 'modelo.html'
        ],
        
        # Scripts Python auxiliares
        'scripts/maintenance/': [
            'security_enhancements.py', 'security_routes.py', 
            'security_integration.py', 'main_system_fixed.py',
            'remove_company_prefixes.py', 'restart_server.py',
            'reset_database.py', 'disable_rnc_triggers.py',
            'apply_optimizations.py'
        ],
        
        # Scripts Python de teste/diagnóstico
        'scripts/diagnostics/': [
            'rnc_tester.py'
        ],
        
        # Bancos de dados e backups
        'db/': [
            '*.db', '*.accdb', '*.laccdb', 'database.db'
        ],
        
        # Arquivos SQL
        'db/sql/': [
            '*.sql'
        ],
        
        # Logs e arquivos temporários
        'logs/': [
            '*.log', 'hs_err_pid*.log', 'replay_pid*.log', 
            'commits_numerados.txt', 'hashes.txt', 'temp_commits.txt',
            'rnc_test_results.log', 'fix_db_locks.log', 'fix_rnc_creation.log'
        ],
        
        # Arquivos de dados
        'data/': [
            'DADOS RNC ATUALIZADO.txt', 'teste.pdf'
        ],
        
        # Configuração Docker
        'docker/': [
            'docker-compose.yml', 'docker-compose.override.yml',
            'Dockerfile', 'Makefile'
        ],
        
        # Configurações de ambiente virtual antigas
        'archive/old_venvs/': [
            '.venv_bad_20250825135353', '.venv_fix', '.venv_final', '.venv_new'
        ],
        
        # Configurações e chaves
        'config/': [
            'ippel_secret.key', '.env.example'
        ],
        
        # Templates HTML adicionais
        'templates/misc/': [
            'print_test.html'
        ]
    }
    
    # Arquivos que devem permanecer na raiz
    keep_in_root = {
        'server_form.py', 'server.py', 'main_system.py', 'index.html',
        'package.json', 'requirements.txt', 'requirements_production.txt',
        'ippel_system.db', 'organize_root.py', 'README.md', 'server.js',
        '.gitignore'
    }
    
    # Pastas que devem permanecer na raiz
    keep_folders_in_root = {
        'routes', 'services', 'templates', 'static', 'node_modules',
        '__pycache__', '.git', '.vscode', 'backups', 'logs', 'scripts',
        'data', 'app', 'utils', 'Lib', 'share', '.github', 'monitoring',
        'nginx', 'tests', 'docs', '.venv', 'db'
    }
    
    print(f"\n📁 Criando estrutura de diretórios...")
    
    # Criar diretórios de destino
    for target_dir in organization_rules.keys():
        target_path = base_dir / target_dir
        target_path.mkdir(parents=True, exist_ok=True)
        print(f"  ✅ {target_dir}")
    
    print(f"\n📦 Organizando arquivos...")
    
    # Processar cada regra de organização
    for target_dir, patterns in organization_rules.items():
        target_path = base_dir / target_dir
        
        for pattern in patterns:
            if '*' in pattern:
                # Padrão com wildcard
                import glob
                matches = glob.glob(pattern)
                for match in matches:
                    source_path = Path(match)
                    if source_path.exists() and source_path.is_file():
                        dest_path = target_path / source_path.name
                        try:
                            shutil.move(str(source_path), str(dest_path))
                            print(f"  📄 {match} → {target_dir}{source_path.name}")
                            moved_count += 1
                        except Exception as e:
                            print(f"  ❌ Erro ao mover {match}: {e}")
            else:
                # Nome específico de arquivo ou pasta
                source_path = base_dir / pattern
                if source_path.exists():
                    dest_path = target_path / source_path.name
                    try:
                        if source_path.is_file():
                            shutil.move(str(source_path), str(dest_path))
                            print(f"  📄 {pattern} → {target_dir}{source_path.name}")
                        else:
                            shutil.move(str(source_path), str(dest_path))
                            print(f"  📁 {pattern}/ → {target_dir}{source_path.name}/")
                        moved_count += 1
                    except Exception as e:
                        print(f"  ❌ Erro ao mover {pattern}: {e}")
    
    print(f"\n📊 RESUMO DA ORGANIZAÇÃO:")
    print(f"  ✅ Arquivos movidos: {moved_count}")
    
    # Listar arquivos restantes na raiz
    remaining_files = []
    remaining_folders = []
    
    for item in base_dir.iterdir():
        if item.name.startswith('.'):
            continue
        if item.is_file() and item.name not in keep_in_root:
            remaining_files.append(item.name)
        elif item.is_dir() and item.name not in keep_folders_in_root:
            remaining_folders.append(item.name)
    
    if remaining_files:
        print(f"\n📋 ARQUIVOS RESTANTES NA RAIZ:")
        for file in remaining_files:
            print(f"  📄 {file}")
    
    if remaining_folders:
        print(f"\n📋 PASTAS RESTANTES NA RAIZ:")
        for folder in remaining_folders:
            print(f"  📁 {folder}/")
    
    print(f"\n" + "=" * 80)
    print("✅ ORGANIZAÇÃO COMPLETA FINALIZADA!")
    print("=" * 80)
    
    # Mostrar estrutura final
    print(f"\n📂 ESTRUTURA FINAL DO PROJETO:")
    show_directory_structure(base_dir, max_depth=2)

def show_directory_structure(path, prefix="", max_depth=3, current_depth=0):
    """Mostra a estrutura de diretórios."""
    if current_depth >= max_depth:
        return
        
    items = sorted(path.iterdir(), key=lambda x: (x.is_file(), x.name.lower()))
    for i, item in enumerate(items):
        if item.name.startswith('.'):
            continue
            
        is_last = i == len(items) - 1
        current_prefix = "└── " if is_last else "├── "
        print(f"{prefix}{current_prefix}{item.name}")
        
        if item.is_dir() and current_depth < max_depth - 1:
            extension = "    " if is_last else "│   "
            show_directory_structure(item, prefix + extension, max_depth, current_depth + 1)

if __name__ == "__main__":
    organize_all_files()
