#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de teste abrangente para criação de RNCs no sistema IPPEL

Este script testa:
1. Criação de RNC via API (POST /api/rnc/create)
2. Criação de RNC via API simplificada (POST /api/rnc/create-simple)
3. Criação de RNC via formulário HTML
4. Verificação de endpoint de debug (POST /api/rnc/debug-create)

Executa testes com diferentes parâmetros e relata erros detalhados
"""

import requests
import json
import sys
import time
import argparse
import logging
from datetime import datetime
from urllib.parse import urljoin
from pprint import pprint
import traceback

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('rnc_test_results.log')
    ]
)
logger = logging.getLogger('rnc_tester')

class RNCTester:
    """Classe principal para testar RNCs"""
    
    def __init__(self, base_url="http://localhost:5001", login_credentials=None):
        """Inicializar tester com URL base e credenciais"""
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        
        # Credenciais padrão
        self.credentials = login_credentials or {
            'email': 'admin@ippel.com.br',
            'password': 'admin123'
        }
        
        # Headers JSON padrão
        self.json_headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        # Estado da autenticação
        self.is_authenticated = False
        self.user_info = None
    
    def run_all_tests(self):
        """Executar todos os testes disponíveis"""
        logger.info("Iniciando bateria de testes de RNC")
        
        try:
            # 1. Autenticação
            if not self.authenticate():
                logger.error("❌ Falha na autenticação - Abortando testes")
                return False
            
            # 2. Testes de API
            self.test_api_create_rnc()
            self.test_api_create_simple_rnc()
            self.test_debug_create_rnc()
            
            # 3. Teste de formulário
            self.test_form_create_rnc()
            
            # 4. Relatório
            self.generate_report()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro crítico durante testes: {e}")
            traceback.print_exc()
            return False
    
    def authenticate(self):
        """Autenticar no sistema"""
        logger.info("🔑 Autenticando no sistema...")
        
        try:
            # Tenta fazer login
            login_url = urljoin(self.base_url, "/api/login")
            response = self.session.post(
                login_url, 
                json=self.credentials,
                headers=self.json_headers
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.is_authenticated = True
                    self.user_info = data.get('user', {})
                    logger.info(f"✅ Login bem-sucedido: {self.user_info.get('name')}")
                    return True
                else:
                    logger.error(f"❌ Falha no login: {data.get('message')}")
            else:
                logger.error(f"❌ Erro HTTP {response.status_code} ao tentar login")
                logger.debug(f"Resposta: {response.text[:200]}")
            
            return False
            
        except requests.RequestException as e:
            logger.error(f"❌ Erro de conexão: {e}")
            return False
    
    def test_api_create_rnc(self):
        """Testar endpoint principal de criação de RNC"""
        logger.info("\n🧪 Testando criação de RNC via API principal")
        
        # Dados de teste padrão
        rnc_data = {
            'title': f'RNC Teste API {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
            'description': 'RNC criada automaticamente via teste de API',
            'equipment': 'Equipamento de teste',
            'client': 'Cliente teste',
            'priority': 'Média',
            'price': 100.50,
            'cause_rnc': 'Causa de teste via API',
            'action_rnc': 'Ação de teste via API'
        }
        
        try:
            # Fazer requisição de criação
            create_url = urljoin(self.base_url, "/api/rnc/create")
            response = self.session.post(
                create_url,
                json=rnc_data,
                headers=self.json_headers
            )
            
            result = {
                'test_name': 'API Principal',
                'endpoint': '/api/rnc/create',
                'status_code': response.status_code,
                'success': False,
                'data': rnc_data,
                'response': None,
                'error': None,
                'rnc_id': None,
                'rnc_number': None
            }
            
            if response.status_code == 200:
                data = response.json()
                result['response'] = data
                
                if data.get('success'):
                    result['success'] = True
                    result['rnc_id'] = data.get('rnc_id')
                    result['rnc_number'] = data.get('rnc_number')
                    logger.info(f"✅ RNC criada com sucesso: {data.get('rnc_number')}")
                else:
                    result['error'] = data.get('message')
                    logger.error(f"❌ Erro na criação: {data.get('message')}")
            else:
                result['error'] = f"HTTP {response.status_code}"
                result['response'] = response.text[:200]
                logger.error(f"❌ Erro HTTP {response.status_code}")
                logger.debug(f"Resposta: {response.text[:200]}")
            
            self.test_results.append(result)
            return result['success']
            
        except Exception as e:
            logger.error(f"❌ Exceção: {e}")
            self.test_results.append({
                'test_name': 'API Principal',
                'endpoint': '/api/rnc/create',
                'success': False,
                'data': rnc_data,
                'error': str(e)
            })
            return False
    
    def test_api_create_simple_rnc(self):
        """Testar endpoint simplificado de criação de RNC"""
        logger.info("\n🧪 Testando criação de RNC via API simplificada")
        
        # Dados mínimos
        rnc_data = {
            'title': f'RNC Simples {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
            'description': 'RNC criada via API simplificada'
        }
        
        try:
            # Fazer requisição de criação
            create_url = urljoin(self.base_url, "/api/rnc/create-simple")
            response = self.session.post(
                create_url,
                json=rnc_data,
                headers=self.json_headers
            )
            
            result = {
                'test_name': 'API Simplificada',
                'endpoint': '/api/rnc/create-simple',
                'status_code': response.status_code,
                'success': False,
                'data': rnc_data,
                'response': None,
                'error': None,
                'rnc_id': None,
                'rnc_number': None
            }
            
            if response.status_code == 200:
                data = response.json()
                result['response'] = data
                
                if data.get('success'):
                    result['success'] = True
                    result['rnc_id'] = data.get('rnc_id')
                    result['rnc_number'] = data.get('rnc_number')
                    logger.info(f"✅ RNC simplificada criada: {data.get('rnc_number')}")
                else:
                    result['error'] = data.get('message')
                    logger.error(f"❌ Erro na criação simplificada: {data.get('message')}")
            else:
                result['error'] = f"HTTP {response.status_code}"
                result['response'] = response.text[:200]
                logger.error(f"❌ Erro HTTP {response.status_code}")
                logger.debug(f"Resposta: {response.text[:200]}")
            
            self.test_results.append(result)
            return result['success']
            
        except Exception as e:
            logger.error(f"❌ Exceção: {e}")
            self.test_results.append({
                'test_name': 'API Simplificada',
                'endpoint': '/api/rnc/create-simple',
                'success': False,
                'data': rnc_data,
                'error': str(e)
            })
            return False
    
    def test_debug_create_rnc(self):
        """Testar endpoint de debug para criação de RNC"""
        logger.info("\n🧪 Testando endpoint de debug de RNC")
        
        # Dados para teste de debug
        rnc_data = {
            'title': f'RNC Debug {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
            'description': 'RNC para debug de API',
            'debug_mode': True,
            'verbose': True
        }
        
        try:
            # Fazer requisição de debug
            debug_url = urljoin(self.base_url, "/api/rnc/debug-create")
            response = self.session.post(
                debug_url,
                json=rnc_data,
                headers=self.json_headers
            )
            
            result = {
                'test_name': 'API Debug',
                'endpoint': '/api/rnc/debug-create',
                'status_code': response.status_code,
                'success': False,
                'data': rnc_data,
                'response': None,
                'error': None,
                'debug_info': None
            }
            
            if response.status_code == 200:
                data = response.json()
                result['response'] = data
                
                if data.get('success'):
                    result['success'] = True
                    result['debug_info'] = data.get('debug_info')
                    logger.info(f"✅ Teste de debug concluído")
                else:
                    result['error'] = data.get('message')
                    logger.error(f"❌ Erro no debug: {data.get('message')}")
            else:
                result['error'] = f"HTTP {response.status_code}"
                result['response'] = response.text[:200]
                logger.error(f"❌ Erro HTTP {response.status_code}")
                logger.debug(f"Resposta: {response.text[:200]}")
            
            self.test_results.append(result)
            return result['success']
            
        except Exception as e:
            logger.error(f"❌ Exceção: {e}")
            self.test_results.append({
                'test_name': 'API Debug',
                'endpoint': '/api/rnc/debug-create',
                'success': False,
                'data': rnc_data,
                'error': str(e)
            })
            return False
    
    def test_form_create_rnc(self):
        """Testar criação de RNC via submissão de formulário"""
        logger.info("\n🧪 Testando criação de RNC via formulário")
        
        # Dados para formulário
        form_data = {
            'title': f'RNC Formulário {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
            'description': 'RNC criada via formulário HTML',
            'equipment': 'Equipamento form',
            'client': 'Cliente form',
            'priority': 'Alta',
            'price': '150.75',
            'cause_rnc': 'Causa form',
            'action_rnc': 'Ação form'
        }
        
        try:
            # Primeiro obter a página do formulário para CSRF
            form_page_url = urljoin(self.base_url, "/create-rnc")
            page_response = self.session.get(form_page_url)
            
            # Configurar headers de formulário
            form_headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Referer': form_page_url
            }
            
            # Enviar formulário
            submit_url = urljoin(self.base_url, "/api/rnc/create")
            response = self.session.post(
                submit_url,
                data=form_data,
                headers=form_headers
            )
            
            result = {
                'test_name': 'Formulário HTML',
                'endpoint': '/api/rnc/create (form)',
                'status_code': response.status_code,
                'success': False,
                'data': form_data,
                'response': None,
                'error': None,
                'rnc_id': None,
                'rnc_number': None
            }
            
            # Analisar resposta (pode ser redirecionamento ou JSON)
            if response.status_code in (200, 302):
                result['success'] = True
                
                # Tentar obter JSON se for resposta direta
                if response.headers.get('Content-Type', '').startswith('application/json'):
                    data = response.json()
                    result['response'] = data
                    if data.get('success'):
                        result['rnc_id'] = data.get('rnc_id')
                        result['rnc_number'] = data.get('rnc_number')
                else:
                    # Se for redirecionamento, considerar sucesso
                    result['response'] = {'redirect': response.headers.get('Location', '')}
                
                logger.info(f"✅ Formulário processado: {response.status_code}")
            else:
                result['error'] = f"HTTP {response.status_code}"
                result['response'] = response.text[:200]
                logger.error(f"❌ Erro HTTP {response.status_code}")
                logger.debug(f"Resposta: {response.text[:200]}")
            
            self.test_results.append(result)
            return result['success']
            
        except Exception as e:
            logger.error(f"❌ Exceção: {e}")
            self.test_results.append({
                'test_name': 'Formulário HTML',
                'endpoint': '/api/rnc/create (form)',
                'success': False,
                'data': form_data,
                'error': str(e)
            })
            return False
    
    def generate_report(self):
        """Gerar relatório dos testes"""
        logger.info("\n📊 Gerando relatório de testes")
        
        # Estatísticas
        total = len(self.test_results)
        successful = sum(1 for r in self.test_results if r.get('success'))
        failed = total - successful
        
        # Exibir relatório
        print("\n" + "=" * 70)
        print(f"📝 RELATÓRIO DE TESTES DE RNC - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print("=" * 70)
        print(f"URL Base: {self.base_url}")
        print(f"Usuário: {self.user_info.get('name', 'N/A') if self.user_info else 'Não autenticado'}")
        print(f"Total de testes: {total}")
        print(f"Sucesso: {successful}")
        print(f"Falhas: {failed}")
        print("-" * 70)
        
        # Detalhes dos testes
        for i, test in enumerate(self.test_results, 1):
            status = "✅" if test.get('success') else "❌"
            print(f"{i}. {status} {test.get('test_name')} - {test.get('endpoint')}")
            if not test.get('success'):
                print(f"   Erro: {test.get('error', 'Desconhecido')}")
            
            if test.get('rnc_number'):
                print(f"   RNC: {test.get('rnc_number')} (ID: {test.get('rnc_id')})")
            
            print()
        
        # Salvar em arquivo
        report_file = f"rnc_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'base_url': self.base_url,
                'stats': {
                    'total': total,
                    'successful': successful,
                    'failed': failed
                },
                'results': self.test_results
            }, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📄 Relatório salvo em: {report_file}")
        print(f"📄 Relatório completo salvo em: {report_file}")
        print("=" * 70)


def main():
    """Função principal"""
    # Configurar parser de argumentos
    parser = argparse.ArgumentParser(
        description='Teste completo de criação de RNCs no sistema IPPEL'
    )
    
    parser.add_argument(
        '--url', 
        default='http://localhost:5001',
        help='URL base do sistema (default: http://localhost:5001)'
    )
    
    parser.add_argument(
        '--email', 
        default='admin@ippel.com.br',
        help='Email para login (default: admin@ippel.com.br)'
    )
    
    parser.add_argument(
        '--password', 
        default='admin123',
        help='Senha para login (default: admin123)'
    )
    
    parser.add_argument(
        '--only', 
        choices=['api', 'simple', 'debug', 'form', 'all'],
        default='all',
        help='Executar apenas teste específico'
    )
    
    # Processar argumentos
    args = parser.parse_args()
    
    # Configurar credenciais
    credentials = {
        'email': args.email,
        'password': args.password
    }
    
    # Inicializar tester
    tester = RNCTester(
        base_url=args.url,
        login_credentials=credentials
    )
    
    # Executar testes
    if args.only == 'all':
        tester.run_all_tests()
    else:
        # Autenticar primeiro
        if not tester.authenticate():
            logger.error("❌ Falha na autenticação - Abortando testes")
            return 1
        
        # Executar teste específico
        if args.only == 'api':
            tester.test_api_create_rnc()
        elif args.only == 'simple':
            tester.test_api_create_simple_rnc()
        elif args.only == 'debug':
            tester.test_debug_create_rnc()
        elif args.only == 'form':
            tester.test_form_create_rnc()
        
        # Gerar relatório
        tester.generate_report()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
