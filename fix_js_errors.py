#!/usr/bin/env python3
"""
Script para corrigir erros de sintaxe JavaScript no dashboard_improved.html
"""
import re

def fix_js_errors():
    """Corrige erros de sintaxe JavaScript causados pela mistura com Jinja2"""
    
    with open('templates/dashboard_improved.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Padrões problemáticos que misturam JavaScript com Jinja2
    patterns = [
        # Padrão: {% if %} dentro de JavaScript
        (r'(\s+)({% if [^%]+%})\s*\n\s*([^%]+)\s*\n\s*({% else %})\s*\n\s*([^%]+)\s*\n\s*({% endif %})', 
         r'\1// \2\n\1\3\n\1// \4\n\1\5\n\1// \6'),
        
        # Padrão: {% endif %} em JavaScript
        (r'({% endif %})', r'// \1'),
        
        # Padrão: {% if %} em JavaScript  
        (r'({% if [^%]+%})', r'// \1'),
        
        # Padrão: {% else %} em JavaScript
        (r'({% else %})', r'// \1'),
    ]
    
    # Aplicar correções
    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
    
    # Salvar arquivo corrigido
    with open('templates/dashboard_improved_fixed.html', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Arquivo corrigido salvo como: templates/dashboard_improved_fixed.html")
    print("⚠️  Verifique se as correções estão corretas antes de usar!")

if __name__ == "__main__":
    fix_js_errors()
