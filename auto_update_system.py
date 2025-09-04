#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de atualização automática
Executa atualizações periódicas dos dados e relatórios
"""

import time
import schedule
import threading
from datetime import datetime
import os
import sys

def run_update_scripts():
    """Executar scripts de atualização"""
    
    print(f"\n🔄 [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Executando atualizações...")
    
    try:
        # Executar script de atualização de gráficos e relatórios
        os.system('python update_charts_and_reports.py')
        print("✅ Atualizações executadas com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro durante atualização: {e}")

def start_scheduler():
    """Iniciar agendador de tarefas"""
    
    print("🚀 Iniciando sistema de atualização automática...")
    print("📅 Agendamentos configurados:")
    print("   - A cada 30 minutos: Atualização de dados")
    print("   - A cada 2 horas: Atualização completa")
    print("   - Diariamente às 06:00: Atualização completa")
    print("   - Diariamente às 18:00: Atualização completa")
    print("\n⏰ Sistema rodando... (Ctrl+C para parar)")
    
    # Agendar tarefas
    schedule.every(30).minutes.do(run_update_scripts)
    schedule.every(2).hours.do(run_update_scripts)
    schedule.every().day.at("06:00").do(run_update_scripts)
    schedule.every().day.at("18:00").do(run_update_scripts)
    
    # Executar uma vez imediatamente
    run_update_scripts()
    
    # Loop principal
    while True:
        schedule.run_pending()
        time.sleep(60)  # Verificar a cada minuto

def manual_update():
    """Executar atualização manual"""
    
    print("🔄 Executando atualização manual...")
    run_update_scripts()
    print("✅ Atualização manual concluída!")

def show_status():
    """Mostrar status do sistema"""
    
    print("📊 STATUS DO SISTEMA")
    print("="*40)
    
    # Verificar se os arquivos de dados existem
    files_to_check = [
        'ippel_system.db',
        'static/dashboard_data.json',
        'static/last_update.txt'
    ]
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            modified = datetime.fromtimestamp(os.path.getmtime(file_path))
            print(f"✅ {file_path}")
            print(f"   📏 Tamanho: {size:,} bytes")
            print(f"   🕒 Modificado: {modified.strftime('%Y-%m-%d %H:%M:%S')}")
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
            start_scheduler()
        else:
            print("❌ Comando inválido!")
            print("Comandos disponíveis:")
            print("  python auto_update_system.py manual  - Executar atualização manual")
            print("  python auto_update_system.py status  - Mostrar status do sistema")
            print("  python auto_update_system.py start   - Iniciar agendador automático")
    else:
        print("🔄 Sistema de Atualização Automática IPPEL")
        print("="*50)
        print("Comandos disponíveis:")
        print("  python auto_update_system.py manual  - Executar atualização manual")
        print("  python auto_update_system.py status  - Mostrar status do sistema")
        print("  python auto_update_system.py start   - Iniciar agendador automático")
        print()
        print("💡 Dica: Use 'python auto_update_system.py start' para iniciar o sistema automático")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Sistema interrompido pelo usuário")
        print("✅ Atualizações automáticas paradas")
