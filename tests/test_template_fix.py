#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste para verificar se a correção do template view_rnc.html está funcionando
"""

import os
import sys

def test_template_syntax():
    """Testa se o template não possui erros de sintaxe JavaScript/Jinja2"""
    template_path = os.path.join(os.path.dirname(__file__), 'templates', 'view_rnc.html')
    
    print(f"Testando template: {template_path}")
    
    if not os.path.exists(template_path):
        print("❌ Arquivo template não encontrado!")
        return False
    
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar se não há mais variáveis Jinja2 misturadas no JavaScript
        script_start = content.find('<script>')
        script_end = content.rfind('</script>')
        
        if script_start != -1 and script_end != -1:
            # Extrair apenas o conteúdo do JavaScript (excluindo o script JSON)
            script_content = content[script_start:script_end]
            
            # Verificar se ainda existem padrões problemáticos
            problematic_patterns = [
                '{{ rnc.id',
                '{{ rnc.status',
                '{{ rnc.priority',
                '{{ rnc.created_at',
                '{{ rnc.finalized_at'
            ]
            
            issues_found = []
            for pattern in problematic_patterns:
                if pattern in script_content and 'application/json' not in script_content:
                    issues_found.append(pattern)
            
            if issues_found:
                print(f"❌ Ainda existem padrões Jinja2 misturados no JavaScript: {issues_found}")
                return False
            else:
                print("✅ Nenhum padrão Jinja2 problemático encontrado no JavaScript!")
        
        # Verificar se o script JSON existe
        if 'application/json' in content and 'rnc-data' in content:
            print("✅ Script JSON com dados do RNC encontrado!")
        else:
            print("❌ Script JSON com dados do RNC não encontrado!")
            return False
        
        print("✅ Template corrigido com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao ler template: {e}")
        return False

if __name__ == "__main__":
    success = test_template_syntax()
    sys.exit(0 if success else 1)
