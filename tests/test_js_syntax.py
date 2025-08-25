import re

def check_js_syntax():
    print("🔍 Verificando sintaxe JavaScript...")
    
    try:
        with open('templates/dashboard_improved.html', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extrair apenas o JavaScript
        script_pattern = r'<script>(.*?)</script>'
        scripts = re.findall(script_pattern, content, re.DOTALL)
        
        if not scripts:
            print("❌ Nenhum script encontrado")
            return
        
        js_code = scripts[0]
        
        # Verificar declarações duplicadas
        print("\n📋 Verificando declarações duplicadas...")
        
        # Verificar 'let currentTab'
        current_tab_count = js_code.count('let currentTab')
        if current_tab_count > 1:
            print(f"❌ 'let currentTab' declarado {current_tab_count} vezes")
        else:
            print("✅ 'let currentTab' declarado apenas uma vez")
        
        # Verificar 'let currentFilters'
        current_filters_count = js_code.count('let currentFilters')
        if current_filters_count > 1:
            print(f"❌ 'let currentFilters' declarado {current_filters_count} vezes")
        else:
            print("✅ 'let currentFilters' declarado apenas uma vez")
        
        # Verificar 'function switchTab'
        switch_tab_count = js_code.count('function switchTab')
        if switch_tab_count > 1:
            print(f"❌ 'function switchTab' declarado {switch_tab_count} vezes")
        else:
            print("✅ 'function switchTab' declarado apenas uma vez")
        
        # Verificar variáveis não declaradas
        print("\n🔍 Verificando uso de variáveis...")
        
        # Verificar se currentFilters é usado antes de ser declarado
        current_filters_declaration = js_code.find('let currentFilters')
        current_filters_usage = js_code.find('currentFilters.')
        
        if current_filters_declaration != -1 and current_filters_usage != -1:
            if current_filters_usage < current_filters_declaration:
                print("❌ 'currentFilters' usado antes de ser declarado")
            else:
                print("✅ 'currentFilters' declarado antes de ser usado")
        
        # Verificar se currentTab é usado antes de ser declarado
        current_tab_declaration = js_code.find('let currentTab')
        current_tab_usage = js_code.find('currentTab')
        
        if current_tab_declaration != -1 and current_tab_usage != -1:
            if current_tab_usage < current_tab_declaration:
                print("❌ 'currentTab' usado antes de ser declarado")
            else:
                print("✅ 'currentTab' declarado antes de ser usado")
        
        print("\n✅ Verificação de sintaxe concluída!")
        
    except Exception as e:
        print(f"❌ Erro ao verificar sintaxe: {e}")

if __name__ == "__main__":
    check_js_syntax() 