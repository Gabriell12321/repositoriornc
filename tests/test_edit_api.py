#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste da API de edição de RNC
"""
import requests
import json

def test_edit_api():
    """Testar API de edição diretamente"""
    base_url = "http://192.168.3.11:5001"
    
    print("🔧 TESTE DA API DE EDIÇÃO DE RNC")
    print("=" * 50)
    
    try:
        # 1. Login como admin
        session = requests.Session()
        login_response = session.post(f"{base_url}/api/login", json={
            'email': 'admin@ippel.com.br',
            'password': 'admin123'
        })
        
        if login_response.status_code != 200:
            print(f"❌ Falha no login: {login_response.status_code}")
            return
        
        print("✅ Login realizado com sucesso")
        
        # 2. Listar RNCs para pegar um ID
        rncs_response = session.get(f"{base_url}/api/rnc/list?tab=active")
        
        if rncs_response.status_code != 200:
            print(f"❌ Falha ao listar RNCs: {rncs_response.status_code}")
            return
        
        rncs_data = rncs_response.json()
        if not rncs_data['success'] or not rncs_data['rncs']:
            print("⚠️ Nenhum RNC encontrado para teste")
            return
        
        # Pegar o primeiro RNC
        test_rnc = rncs_data['rncs'][0]
        rnc_id = test_rnc['id']
        original_title = test_rnc['title']
        
        print(f"📄 Testando edição do RNC {rnc_id}")
        print(f"   Título original: {original_title}")
        print(f"   Criador: {test_rnc['user_name']} (ID: {test_rnc['user_id']})")
        print(f"   Status: {test_rnc['status']}")
        
        # 3. Preparar dados de edição
        edit_data = {
            'title': f"TESTE EDITADO - {original_title}",
            'description': 'Esta é uma descrição editada pelo teste automatizado',
            'equipment': 'Equipamento de Teste',
            'client': 'Cliente de Teste',
            'priority': 'Alta',
            'status': 'Em Andamento',
            'assinatura1': 'Teste Assinatura 1',
            'assinatura2': 'Teste Assinatura 2',
            'assinatura3': 'Teste Assinatura 3'
        }
        
        print("\n📝 Dados que serão enviados:")
        for key, value in edit_data.items():
            print(f"   {key}: {value}")
        
        # 4. Tentar editar via API
        print(f"\n🔧 Enviando PUT para /api/rnc/{rnc_id}/update")
        
        edit_response = session.put(f"{base_url}/api/rnc/{rnc_id}/update", json=edit_data)
        
        print(f"📊 Status da resposta: {edit_response.status_code}")
        
        try:
            response_data = edit_response.json()
            print(f"📋 Resposta JSON: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
        except:
            print(f"📋 Resposta não-JSON: {edit_response.text}")
        
        if edit_response.status_code == 200:
            print("✅ API retornou sucesso!")
            
            # 5. Verificar se realmente foi editado
            print("\n🔍 Verificando se foi realmente editado...")
            
            # Aguardar um pouco para evitar cache
            import time
            time.sleep(1)
            
            # Listar novamente
            rncs_check = session.get(f"{base_url}/api/rnc/list?tab=active")
            if rncs_check.status_code == 200:
                rncs_check_data = rncs_check.json()
                
                # Procurar o RNC editado
                edited_rnc = None
                for rnc in rncs_check_data['rncs']:
                    if rnc['id'] == rnc_id:
                        edited_rnc = rnc
                        break
                
                if edited_rnc:
                    print(f"📄 RNC após edição:")
                    print(f"   Título: {edited_rnc['title']}")
                    print(f"   Descrição: {edited_rnc['description']}")
                    print(f"   Equipment: {edited_rnc['equipment']}")
                    print(f"   Cliente: {edited_rnc['client']}")
                    print(f"   Prioridade: {edited_rnc['priority']}")
                    print(f"   Status: {edited_rnc['status']}")
                    
                    # Verificar se realmente mudou
                    title_changed = edited_rnc['title'] != original_title
                    print(f"\n🎯 RESULTADO: Título foi alterado? {title_changed}")
                    
                    if title_changed:
                        print("🎉 SUCESSO: A edição funcionou!")
                    else:
                        print("❌ PROBLEMA: A edição não foi aplicada!")
                else:
                    print("❌ RNC não encontrado após edição")
            else:
                print("❌ Falha ao verificar RNC após edição")
        else:
            print("❌ API retornou erro")
    
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_edit_api()
