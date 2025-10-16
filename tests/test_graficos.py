#!/usr/bin/env python3
"""
Script para testar a funcionalidade dos gráficos do sistema RNC
"""

import requests
import json
import time
from datetime import datetime

def test_charts_api():
    """Testa a API de gráficos"""
    print("🧪 Testando API de Gráficos...")
    
    # URL base do servidor
    base_url = "http://localhost:5000"
    
    # 1. Testar login
    print("\n1️⃣ Testando login...")
    login_data = {
        "email": "admin@ippel.com",
        "password": "admin123"
    }
    
    try:
        session = requests.Session()
        response = session.post(f"{base_url}/api/login", json=login_data)
        
        if response.status_code == 200:
            print("✅ Login realizado com sucesso")
        else:
            print(f"❌ Erro no login: {response.status_code}")
            print(f"Resposta: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Erro ao conectar com o servidor: {e}")
        return False
    
    # 2. Testar API de gráficos com diferentes períodos
    periods = [30, 90, 180, 365]
    
    for period in periods:
        print(f"\n2️⃣ Testando gráficos para {period} dias...")
        
        try:
            response = session.get(f"{base_url}/api/charts/data?period={period}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Dados carregados para {period} dias")
                
                # Verificar se todos os tipos de gráficos estão presentes
                chart_types = ['status', 'trend', 'clients', 'equipment', 'departments', 'priorities', 'dispositions', 'users']
                
                for chart_type in chart_types:
                    if chart_type in data and data[chart_type]:
                        print(f"   📊 {chart_type}: {len(data[chart_type])} itens")
                    else:
                        print(f"   ⚠️ {chart_type}: sem dados")
                
                # Mostrar alguns dados de exemplo
                if data.get('status'):
                    print(f"   📈 Status encontrados: {[item['label'] for item in data['status']]}")
                
                if data.get('trend'):
                    print(f"   📅 Período de tendência: {len(data['trend'])} dias")
                
            else:
                print(f"❌ Erro na API: {response.status_code}")
                print(f"Resposta: {response.text}")
                
        except Exception as e:
            print(f"❌ Erro ao testar gráficos: {e}")
    
    # 3. Testar dashboard
    print("\n3️⃣ Testando acesso ao dashboard...")
    
    try:
        response = session.get(f"{base_url}/dashboard")
        
        if response.status_code == 200:
            print("✅ Dashboard acessível")
            
            # Verificar se a aba de gráficos está presente
            if "📊 Gráficos" in response.text:
                print("✅ Aba de gráficos encontrada no HTML")
            else:
                print("❌ Aba de gráficos não encontrada no HTML")
                
        else:
            print(f"❌ Erro ao acessar dashboard: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro ao testar dashboard: {e}")
    
    print("\n🎯 Teste de gráficos concluído!")
    return True

def test_chart_data_quality():
    """Testa a qualidade dos dados dos gráficos"""
    print("\n🔍 Testando qualidade dos dados...")
    
    base_url = "http://localhost:5000"
    
    try:
        session = requests.Session()
        
        # Login
        login_data = {"email": "admin@ippel.com", "password": "admin123"}
        response = session.post(f"{base_url}/api/login", json=login_data)
        
        if response.status_code != 200:
            print("❌ Falha no login para teste de qualidade")
            return
        
        # Buscar dados
        response = session.get(f"{base_url}/api/charts/data?period=30")
        
        if response.status_code == 200:
            data = response.json()
            
            print("📊 Análise de qualidade dos dados:")
            
            # Verificar dados de status
            if data.get('status'):
                total_status = sum(item['count'] for item in data['status'])
                print(f"   📈 Total de RNCs por status: {total_status}")
                
                for item in data['status']:
                    percentage = (item['count'] / total_status * 100) if total_status > 0 else 0
                    print(f"      {item['label']}: {item['count']} ({percentage:.1f}%)")
            
            # Verificar dados de tendência
            if data.get('trend'):
                total_trend = sum(item['count'] for item in data['trend'])
                print(f"   📅 Total de RNCs no período: {total_trend}")
                print(f"   📅 Média por dia: {total_trend / len(data['trend']):.1f}")
            
            # Verificar dados de clientes
            if data.get('clients'):
                print(f"   🏢 Top 3 clientes:")
                for i, item in enumerate(data['clients'][:3], 1):
                    print(f"      {i}. {item['label']}: {item['count']}")
            
            # Verificar dados de equipamentos
            if data.get('equipment'):
                print(f"   ⚙️ Top 3 equipamentos:")
                for i, item in enumerate(data['equipment'][:3], 1):
                    print(f"      {i}. {item['label']}: {item['count']}")
            
            # Verificar dados de departamentos
            if data.get('departments'):
                print(f"   🏭 Departamentos com RNCs:")
                for item in data['departments']:
                    print(f"      {item['label']}: {item['count']}")
            
            # Verificar dados de prioridades
            if data.get('priorities'):
                print(f"   🎯 Prioridades:")
                for item in data['priorities']:
                    print(f"      {item['label']}: {item['count']}")
            
            # Verificar dados de disposição
            if data.get('dispositions'):
                print(f"   ✅ Disposições:")
                for item in data['dispositions']:
                    print(f"      {item['label']}: {item['count']}")
            
            # Verificar dados de usuários
            if data.get('users'):
                print(f"   👥 Top 5 usuários:")
                for i, item in enumerate(data['users'][:5], 1):
                    print(f"      {i}. {item['label']}: {item['count']}")
                    
        else:
            print(f"❌ Erro ao buscar dados: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro no teste de qualidade: {e}")

if __name__ == "__main__":
    print("🚀 Iniciando testes dos gráficos do sistema RNC")
    print("=" * 50)
    
    # Verificar se o servidor está rodando
    try:
        response = requests.get("http://localhost:5000", timeout=5)
        print("✅ Servidor está rodando")
    except:
        print("❌ Servidor não está rodando. Inicie o servidor primeiro!")
        exit(1)
    
    # Executar testes
    test_charts_api()
    test_chart_data_quality()
    
    print("\n🎉 Testes concluídos!")
    print("\n💡 Para testar os gráficos no navegador:")
    print("   1. Acesse: http://localhost:5000/dashboard")
    print("   2. Faça login")
    print("   3. Clique na aba '📊 Gráficos'")
    print("   4. Teste diferentes períodos no seletor") 