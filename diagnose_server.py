#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Diagnóstico dos servidores IPPEL
"""

import os
import sys
import socket
import subprocess

def check_port(port):
    """Verificar se uma porta está livre ou ocupada"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = s.connect_ex(('localhost', port))
        s.close()
        return result == 0  # True se ocupada, False se livre
    except:
        return False

def check_python_modules():
    """Verificar módulos Python necessários"""
    modules = ['flask', 'flask_login', 'werkzeug', 'sqlite3']
    missing = []
    
    for module in modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError:
            print(f"❌ {module} - FALTANDO")
            missing.append(module)
    
    return missing

def check_database():
    """Verificar banco de dados"""
    try:
        import sqlite3
        conn = sqlite3.connect('ippel_system.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        conn.close()
        
        print(f"✅ Banco de dados OK - {len(tables)} tabelas encontradas")
        return True
    except Exception as e:
        print(f"❌ Erro no banco de dados: {e}")
        return False

def test_simple_flask():
    """Testar Flask básico"""
    try:
        from flask import Flask
        app = Flask(__name__)
        print("✅ Flask básico funcionando")
        return True
    except Exception as e:
        print(f"❌ Erro no Flask: {e}")
        return False

def main():
    print("🔍 DIAGNÓSTICO DOS SERVIDORES IPPEL")
    print("=" * 50)
    
    # Verificar portas
    print("\n📡 VERIFICAÇÃO DE PORTAS:")
    ports = [5000, 5001, 3000]
    for port in ports:
        status = "OCUPADA" if check_port(port) else "LIVRE"
        print(f"Porta {port}: {status}")
    
    # Verificar módulos Python
    print("\n🐍 MÓDULOS PYTHON:")
    missing_modules = check_python_modules()
    
    # Verificar banco de dados
    print("\n🗄️ BANCO DE DADOS:")
    db_ok = check_database()
    
    # Testar Flask
    print("\n🌐 TESTE FLASK:")
    flask_ok = test_simple_flask()
    
    # Resumo
    print("\n📊 RESUMO:")
    print("=" * 50)
    
    if not missing_modules and db_ok and flask_ok:
        print("✅ Todos os componentes estão funcionando!")
        print("💡 Tente executar: python main_system.py")
    else:
        print("❌ Há problemas que precisam ser resolvidos:")
        if missing_modules:
            print(f"   - Instale os módulos faltantes: pip install {' '.join(missing_modules)}")
        if not db_ok:
            print("   - Verifique o banco de dados")
        if not flask_ok:
            print("   - Verifique a instalação do Flask")

if __name__ == '__main__':
    main()
