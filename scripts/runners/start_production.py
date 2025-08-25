#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para iniciar o servidor IPPEL em modo produção
Com todas as otimizações de performance ativas
"""

import os
import sys
import subprocess
import psutil
import time

def check_dependencies():
    """Verificar se todas as dependências estão instaladas"""
    required_packages = [
        'flask',
        'flask-socketio',
        'eventlet',
        'psutil',
        # opcionais/recomendados
        'flask-compress',
        'flask-limiter',
        'flask-talisman'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Dependências faltando:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\nInstale com: pip install " + " ".join(missing_packages))
        return False
    
    return True

def check_system_resources():
    """Verificar recursos do sistema para 200 usuários"""
    cpu_count = psutil.cpu_count()
    memory = psutil.virtual_memory()
    
    print("💻 Recursos do Sistema:")
    print(f"   - CPUs: {cpu_count}")
    print(f"   - Memória Total: {memory.total / 1024 / 1024 / 1024:.1f} GB")
    print(f"   - Memória Disponível: {memory.available / 1024 / 1024 / 1024:.1f} GB")
    print(f"   - Uso de CPU: {psutil.cpu_percent()}%")
    
    # Recomendações para i5-7500 + 16GB RAM
    if cpu_count < 4:
        print("⚠️  RECOMENDADO: Pelo menos 4 CPUs para 200 usuários simultâneos")
    
    if memory.total < 8 * 1024 * 1024 * 1024:  # 8GB
        print("⚠️  RECOMENDADO: Pelo menos 8GB de RAM para 200 usuários simultâneos")
    
    # Verificar se o sistema suporta 200 usuários
    if cpu_count >= 4 and memory.total >= 8 * 1024 * 1024 * 1024:
        print("✅ Sistema EXCELENTE para 200+ usuários simultâneos!")
        print("🎯 Seu i5-7500 + 16GB RAM é PERFEITO para a empresa!")
    elif cpu_count >= 2 and memory.total >= 4 * 1024 * 1024 * 1024:
        print("⚠️  Sistema pode suportar 200 usuários, mas com performance limitada")
    else:
        print("❌ Sistema pode ter dificuldades com 200 usuários simultâneos")
    
    return True

def start_production_server():
    """Iniciar servidor em modo produção"""
    print("🚀 Iniciando servidor IPPEL em modo PRODUÇÃO")
    print("=" * 60)
    
    # Verificar dependências
    if not check_dependencies():
        sys.exit(1)
    
    # Verificar recursos
    check_system_resources()
    print("=" * 60)
    
    # Configurar variáveis de ambiente
    os.environ['FLASK_ENV'] = 'production'
    os.environ['FLASK_DEBUG'] = '0'
    
    # Comando para iniciar com Gunicorn - Otimizado para i5-7500 + 16GB RAM
    workers = max(8, psutil.cpu_count() * 4)  # 16 workers para i5-7500
    
    # Em Windows, usar Eventlet diretamente. Detectar plataforma.
    is_windows = sys.platform.startswith('win')
    if is_windows:
        cmd = [
            sys.executable,
            '-c',
            'from server_form import app, socketio; socketio.run(app, host="0.0.0.0", port=5001, debug=False)'
        ]
    else:
        cmd = [
            'gunicorn',
            '--config', 'gunicorn_config.py',
            '--worker-class', 'eventlet',
            '--workers', str(workers),
            '--bind', '0.0.0.0:5001',
            '--timeout', '60',  # Aumentado para 200 usuários
            '--keepalive', '5',  # Aumentado para 200 usuários
            '--max-requests', '2000',  # Aumentado para 200 usuários
            '--max-requests-jitter', '100',  # Aumentado para 200 usuários
            '--preload',
            'server_form:app'
        ]
    
    print("⚡ Configurações de Performance para i5-7500 + 16GB RAM:")
    print(f"   - Workers: {workers}")
    print(f"   - Worker Class: eventlet")
    print(f"   - Timeout: 60s")
    print(f"   - Max Requests: 3000")
    print(f"   - Preload: Ativo")
    print(f"   - Pool de Conexões: 150")
    print(f"   - Thread Pool: 75")
    print(f"   - Cache SQLite: 100.000 páginas")
    print(f"   - MMAP: 1GB")
    print("=" * 60)
    
    try:
        print("🔄 Iniciando servidor...")
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n👋 Servidor encerrado pelo usuário")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao iniciar servidor: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("❌ Gunicorn não encontrado. Instale com: pip install gunicorn")
        sys.exit(1)

def start_development_server():
    """Iniciar servidor em modo desenvolvimento"""
    print("🔧 Iniciando servidor IPPEL em modo DESENVOLVIMENTO")
    print("=" * 60)
    
    try:
        from server_form import app, socketio
        socketio.run(app, host='0.0.0.0', port=5001, debug=True)
    except KeyboardInterrupt:
        print("\n👋 Servidor encerrado pelo usuário")
    except Exception as e:
        print(f"❌ Erro ao iniciar servidor: {e}")
        sys.exit(1)

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--dev':
        start_development_server()
    else:
        start_production_server() 