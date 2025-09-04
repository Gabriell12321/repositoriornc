#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de atualização automática simples
Sem dependências externas
"""

import time
import os
import sys
from datetime import datetime, timedelta

def run_update():
    """Executar atualização"""
    
    print(f"\n🔄 [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Executando atualização...")
    
    try:
        # Executar script de atualização
        os.system('python update_charts_and_reports.py')
        print("✅ Atualização concluída!")
        
    except Exception as e:
        print(f"❌ Erro: {e}")

def auto_update_loop(interval_minutes=30):
    """Loop de atualização automática"""
    
    print("🚀 Sistema de Atualização Automática IPPEL")
    print(f"⏰ Intervalo: {interval_minutes} minutos")
    print("🛑 Pressione Ctrl+C para parar")
    print("="*50)
    
    # Executar primeira atualização
    run_update()
    
    # Calcular próximo horário
    next_update = datetime.now() + timedelta(minutes=interval_minutes)
    
    while True:
        try:
            now = datetime.now()
            
            # Verificar se é hora de atualizar
            if now >= next_update:
                run_update()
                next_update = now + timedelta(minutes=interval_minutes)
            
            # Mostrar próximo horário a cada 5 minutos
            if now.minute % 5 == 0 and now.second < 10:
                print(f"⏰ Próxima atualização: {next_update.strftime('%H:%M:%S')}")
            
            time.sleep(60)  # Aguardar 1 minuto
            
        except KeyboardInterrupt:
            print("\n🛑 Sistema interrompido pelo usuário")
            break

def manual_update():
    """Atualização manual"""
    
    print("🔄 Executando atualização manual...")
    run_update()
    print("✅ Concluído!")

def show_status():
    """Mostrar status"""
    
    print("📊 STATUS DO SISTEMA")
    print("="*40)
    
    files = [
        'ippel_system.db',
        'static/dashboard_data.json',
        'static/last_update.txt'
    ]
    
    for file_path in files:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            modified = datetime.fromtimestamp(os.path.getmtime(file_path))
            print(f"✅ {file_path}")
            print(f"   📏 {size:,} bytes")
            print(f"   🕒 {modified.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            print(f"❌ {file_path} - Não encontrado")
        print()

def main():
    """Função principal"""
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'manual':
            manual_update()
        elif command == 'status':
            show_status()
        elif command == 'start':
            interval = 30  # Padrão 30 minutos
            if len(sys.argv) > 2:
                try:
                    interval = int(sys.argv[2])
                except ValueError:
                    print("❌ Intervalo inválido!")
                    return
            auto_update_loop(interval)
        else:
            print("❌ Comando inválido!")
            print("Comandos:")
            print("  python simple_auto_update.py manual     - Atualização manual")
            print("  python simple_auto_update.py status     - Mostrar status")
            print("  python simple_auto_update.py start [30] - Iniciar automático (30min padrão)")
    else:
        print("🔄 Sistema de Atualização Automática IPPEL")
        print("="*50)
        print("Comandos disponíveis:")
        print("  python simple_auto_update.py manual     - Executar atualização manual")
        print("  python simple_auto_update.py status     - Mostrar status do sistema")
        print("  python simple_auto_update.py start [30] - Iniciar automático (30min padrão)")
        print()
        print("💡 Exemplo: python simple_auto_update.py start 60 (atualizar a cada 60 minutos)")

if __name__ == "__main__":
    main()
