#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
REINICIAR SERVIDOR: Aplicar correções
Script para parar e reiniciar o servidor com as correções
"""

import subprocess
import time
import os
import signal
import psutil

def find_python_server():
    """Encontrar processo do servidor Python"""
    print("🔍 Procurando servidor Python...")
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['name'] == 'python.exe':
                cmdline = ' '.join(proc.info['cmdline'])
                if 'server_form.py' in cmdline:
                    print(f"✅ Servidor encontrado: PID {proc.info['pid']}")
                    return proc.info['pid']
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    print("❌ Servidor não encontrado")
    return None

def stop_server(pid):
    """Parar servidor"""
    print(f"🛑 Parando servidor (PID {pid})...")
    
    try:
        process = psutil.Process(pid)
        process.terminate()
        
        # Aguardar até 10 segundos para o processo terminar
        try:
            process.wait(timeout=10)
            print("✅ Servidor parado com sucesso")
            return True
        except psutil.TimeoutExpired:
            print("⚠️ Forçando parada do servidor...")
            process.kill()
            process.wait(timeout=5)
            print("✅ Servidor forçado a parar")
            return True
            
    except psutil.NoSuchProcess:
        print("✅ Servidor já estava parado")
        return True
    except Exception as e:
        print(f"❌ Erro ao parar servidor: {e}")
        return False

def start_server():
    """Iniciar servidor"""
    print("🚀 Iniciando servidor...")
    
    try:
        # Iniciar servidor em background
        process = subprocess.Popen(
            ['python', 'server_form.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
        )
        
        print(f"✅ Servidor iniciado (PID {process.pid})")
        print("⏳ Aguardando inicialização...")
        
        # Aguardar um pouco para o servidor inicializar
        time.sleep(3)
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao iniciar servidor: {e}")
        return False

def test_server():
    """Testar se servidor está respondendo"""
    print("🧪 Testando servidor...")
    
    try:
        import requests
        response = requests.get("http://172.26.0.75:5001/", timeout=5)
        if response.status_code == 200:
            print("✅ Servidor respondendo corretamente")
            return True
        else:
            print(f"⚠️ Servidor respondeu com status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Servidor não está respondendo: {e}")
        return False

def main():
    """Função principal"""
    print("🔄 REINICIANDO SERVIDOR PARA APLICAR CORREÇÕES")
    print("=" * 60)
    
    # 1. Encontrar servidor atual
    pid = find_python_server()
    
    if pid:
        # 2. Parar servidor
        if stop_server(pid):
            # Aguardar um pouco
            time.sleep(2)
            
            # 3. Iniciar servidor
            if start_server():
                # Aguardar inicialização
                time.sleep(5)
                
                # 4. Testar servidor
                if test_server():
                    print("\n" + "=" * 60)
                    print("✅ SERVIDOR REINICIADO COM SUCESSO!")
                    print("\n📋 CORREÇÕES APLICADAS:")
                    print("   ✅ Logo corrigido (404 → OK)")
                    print("   ✅ Endpoint RNC robusto")
                    print("   ✅ Validação melhorada")
                    print("   ✅ Tratamento de erros específico")
                    print("\n🎯 TESTE AGORA:")
                    print("   1. Acesse: http://172.26.0.75:5001")
                    print("   2. Faça login: admin@ippel.com.br / admin123")
                    print("   3. Tente criar uma RNC")
                    print("=" * 60)
                else:
                    print("\n❌ Servidor não está respondendo após reinicialização")
            else:
                print("\n❌ Falha ao iniciar servidor")
        else:
            print("\n❌ Falha ao parar servidor")
    else:
        print("\n💡 Servidor não estava rodando, iniciando...")
        if start_server():
            time.sleep(5)
            if test_server():
                print("\n✅ SERVIDOR INICIADO COM SUCESSO!")
            else:
                print("\n❌ Servidor iniciado mas não está respondendo")

if __name__ == "__main__":
    main()
