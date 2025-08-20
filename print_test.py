#!/usr/bin/env python3
"""
Script de Teste de Impressão para Sistema IPPEL RNC
Testa e otimiza a impressão para ficar igual ao modelo.pdf
"""

import os
import sys
import webbrowser
from datetime import datetime
from print_config import PrintConfig

class PrintTester:
    """Classe para testar e otimizar impressão"""
    
    def __init__(self):
        self.test_data = {
            'rnc_number': 'RNC2024-0001',
            'title': 'Teste de Impressão - Não Conformidade',
            'description': 'Este é um teste para verificar se a impressão está igual ao modelo.pdf',
            'equipment': 'Equipamento de Teste',
            'client': 'Cliente Teste',
            'inspector': 'Inspetor Teste',
            'date': datetime.now().strftime('%d/%m/%Y'),
            'location': 'Local de Teste',
            'severity': 'Alta',
            'status': 'Em Análise'
        }
    
    def generate_test_html(self):
        """Gera HTML de teste para impressão"""
        html = f"""
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Teste de Impressão RNC</title>
            <style>
                {PrintConfig.get_print_css()}
                
                /* Estilos para visualização na tela */
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: #f5f5f5;
                    margin: 0;
                    padding: 20px;
                }}
                
                .container {{
                    max-width: 800px;
                    margin: 0 auto;
                    background: white;
                    border-radius: 10px;
                    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
                    overflow: hidden;
                }}
                
                .header {{
                    background: linear-gradient(135deg, #dc2626, #b91c1c);
                    color: white;
                    padding: 30px;
                    text-align: center;
                }}
                
                .logo {{
                    width: 80px;
                    height: 80px;
                    margin: 0 auto 20px;
                    border-radius: 10px;
                    background: white;
                    padding: 10px;
                }}
                
                .header-text h1 {{
                    margin: 0 0 10px 0;
                    font-size: 24px;
                    font-weight: bold;
                }}
                
                .rnc-number {{
                    background: rgba(255,255,255,0.2);
                    padding: 10px 20px;
                    border-radius: 25px;
                    display: inline-block;
                    font-weight: bold;
                    font-size: 18px;
                }}
                
                .form-section {{
                    padding: 25px;
                    border-bottom: 1px solid #e9ecef;
                }}
                
                .section-title {{
                    color: #dc2626;
                    font-size: 18px;
                    font-weight: bold;
                    margin-bottom: 20px;
                    border-bottom: 2px solid #dc2626;
                    padding-bottom: 10px;
                }}
                
                .form-row {{
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 20px;
                    margin-bottom: 15px;
                }}
                
                .form-group {{
                    margin-bottom: 15px;
                }}
                
                .form-label {{
                    display: block;
                    font-weight: bold;
                    color: #374151;
                    margin-bottom: 5px;
                    font-size: 14px;
                }}
                
                .form-input, .form-select, .form-textarea {{
                    width: 100%;
                    padding: 10px;
                    border: 1px solid #d1d5db;
                    border-radius: 5px;
                    font-size: 14px;
                    background: white;
                }}
                
                .form-textarea {{
                    min-height: 100px;
                    resize: vertical;
                }}
                
                .disposicao-header {{
                    background: #333;
                    color: white;
                    text-align: center;
                    padding: 10px 0;
                    font-weight: bold;
                    display: flex;
                }}
                
                .disposicao-header > div {{
                    width: 50%;
                    text-align: center;
                    border-right: 1px solid white;
                    padding: 5px 0;
                }}
                
                .disposicao-header > div:last-child {{
                    border-right: none;
                }}
                
                .disposicao-content {{
                    border: 1px solid #d1d5db;
                    border-top: none;
                    display: flex;
                    min-height: 150px;
                }}
                
                .disposicao-content > div {{
                    width: 50%;
                    padding: 15px;
                    border-right: 1px solid #d1d5db;
                }}
                
                .disposicao-content > div:last-child {{
                    border-right: none;
                }}
                
                .signature-container {{
                    border: 1px solid #d1d5db;
                    border-radius: 5px;
                    margin-top: 20px;
                }}
                
                .signature-container > div {{
                    border: 1px solid #d1d5db;
                    padding: 15px;
                    text-align: center;
                    font-weight: bold;
                }}
                
                .signature-container > div:first-child {{
                    border-bottom: 1px solid #d1d5db;
                    background: #f8f9fa;
                }}
                
                .signature-container > div:first-child > div {{
                    width: 33.33%;
                    padding: 10px;
                    text-align: center;
                    font-weight: bold;
                    border-right: 1px solid #d1d5db;
                    display: inline-block;
                }}
                
                .signature-container > div:first-child > div:last-child {{
                    border-right: none;
                }}
                
                .signature-container > div:last-child > div {{
                    width: 33.33%;
                    padding: 30px 10px;
                    text-align: center;
                    font-weight: bold;
                    border-right: 1px solid #d1d5db;
                    display: inline-block;
                }}
                
                .signature-container > div:last-child > div:last-child {{
                    border-right: none;
                }}
                
                .test-buttons {{
                    text-align: center;
                    padding: 20px;
                    background: #f8f9fa;
                }}
                
                .test-btn {{
                    background: #007bff;
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 5px;
                    cursor: pointer;
                    margin: 0 10px;
                    font-size: 14px;
                }}
                
                .test-btn:hover {{
                    background: #0056b3;
                }}
                
                .test-btn.print {{
                    background: #28a745;
                }}
                
                .test-btn.print:hover {{
                    background: #1e7e34;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <!-- Header -->
                <div class="header">
                    <div class="logo">🏭</div>
                    <div class="header-text">
                        <h1>Relatório De Não Conformidades Internas - RNC</h1>
                        <div class="rnc-number">{self.test_data['rnc_number']}</div>
                    </div>
                </div>

                <!-- Informações Básicas -->
                <div class="form-section">
                    <div class="section-title">📋 Informações Básicas</div>
                    <div class="form-row">
                        <div class="form-group">
                            <label class="form-label">Título da Não Conformidade</label>
                            <input type="text" class="form-input" value="{self.test_data['title']}" readonly>
                        </div>
                        <div class="form-group">
                            <label class="form-label">Número do RNC</label>
                            <input type="text" class="form-input" value="{self.test_data['rnc_number']}" readonly>
                        </div>
                    </div>
                    <div class="form-row">
                        <div class="form-group">
                            <label class="form-label">Data de Identificação</label>
                            <input type="date" class="form-input" value="2024-01-15" readonly>
                        </div>
                        <div class="form-group">
                            <label class="form-label">Local</label>
                            <input type="text" class="form-input" value="{self.test_data['location']}" readonly>
                        </div>
                    </div>
                    <div class="form-row">
                        <div class="form-group">
                            <label class="form-label">Equipamento</label>
                            <input type="text" class="form-input" value="{self.test_data['equipment']}" readonly>
                        </div>
                        <div class="form-group">
                            <label class="form-label">Cliente</label>
                            <input type="text" class="form-input" value="{self.test_data['client']}" readonly>
                        </div>
                    </div>
                </div>

                <!-- Descrição -->
                <div class="form-section">
                    <div class="section-title">📝 Descrição da Não Conformidade</div>
                    <div class="form-group">
                        <label class="form-label">Descrição Detalhada</label>
                        <textarea class="form-textarea" readonly>{self.test_data['description']}

Detalhes adicionais:
- Problema identificado durante inspeção
- Possível impacto na qualidade do produto
- Necessidade de ação corretiva imediata</textarea>
                    </div>
                </div>

                <!-- Disposição e Inspeção -->
                <div class="form-section">
                    <div class="section-title">🔍 Disposição e Inspeção</div>
                    <div class="disposicao-header">
                        <div>Disposição</div>
                        <div>Inspeção</div>
                    </div>
                    <div class="disposicao-content">
                        <div>
                            <strong>Disposição Adotada:</strong><br>
                            • Produto isolado e identificado<br>
                            • Área de trabalho interditada<br>
                            • Equipe técnica notificada<br>
                            • Documentação iniciada
                        </div>
                        <div>
                            <strong>Inspeção Realizada:</strong><br>
                            • Verificação visual completa<br>
                            • Análise de amostras<br>
                            • Documentação fotográfica<br>
                            • Relatório técnico elaborado
                        </div>
                    </div>
                </div>

                <!-- Assinaturas -->
                <div class="form-section">
                    <div class="section-title">✍️ Assinaturas e Aprovações</div>
                    <div class="signature-container">
                        <div>
                            <div>Inspetor</div>
                            <div>Supervisor</div>
                            <div>Gerente</div>
                        </div>
                        <div>
                            <div>_________________</div>
                            <div>_________________</div>
                            <div>_________________</div>
                        </div>
                    </div>
                </div>

                <!-- Botões de Teste -->
                <div class="test-buttons">
                    <button class="test-btn" onclick="window.print()">🖨️ Testar Impressão</button>
                    <button class="test-btn print" onclick="printWithConfig()">📋 Impressão Otimizada</button>
                    <button class="test-btn" onclick="showInstructions()">ℹ️ Instruções</button>
                </div>
            </div>

            <script>
                function printWithConfig() {{
                    // Configurações específicas para impressão
                    const printWindow = window.open('', '_blank');
                    printWindow.document.write(document.documentElement.outerHTML);
                    printWindow.document.close();
                    printWindow.focus();
                    
                    // Aguarda o carregamento e imprime
                    setTimeout(() => {{
                        printWindow.print();
                    }}, 500);
                }}
                
                function showInstructions() {{
                    alert(`{PrintConfig.get_print_instructions()}`);
                }}
                
                // Configurações automáticas para impressão
                window.addEventListener('beforeprint', function() {{
                    console.log('Preparando para impressão...');
                }});
                
                window.addEventListener('afterprint', function() {{
                    console.log('Impressão concluída');
                }});
            </script>
        </body>
        </html>
        """
        
        return html
    
    def save_test_file(self):
        """Salva arquivo de teste"""
        html_content = self.generate_test_html()
        filename = "print_test.html"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ Arquivo de teste salvo: {filename}")
        return filename
    
    def open_test_file(self):
        """Abre arquivo de teste no navegador"""
        filename = self.save_test_file()
        webbrowser.open(f'file://{os.path.abspath(filename)}')
        print("🌐 Arquivo aberto no navegador")
    
    def run_tests(self):
        """Executa testes de impressão"""
        print("🧪 Iniciando testes de impressão...")
        print("\n" + "="*50)
        print("CONFIGURAÇÕES DE IMPRESSÃO")
        print("="*50)
        
        print(f"📄 Tamanho da página: {PrintConfig.PAGE_SETTINGS['size']}")
        print(f"📐 Orientação: {PrintConfig.PAGE_SETTINGS['orientation']}")
        print(f"📏 Margens: {PrintConfig.PAGE_SETTINGS['margin_top']}")
        print(f"🔤 Fonte: {PrintConfig.FONT_SETTINGS['family']}")
        print(f"📝 Tamanho base: {PrintConfig.FONT_SETTINGS['size_base']}")
        
        print("\n" + "="*50)
        print("INSTRUÇÕES PARA TESTE")
        print("="*50)
        print(PrintConfig.get_print_instructions())
        
        self.open_test_file()

def main():
    """Função principal"""
    print("🖨️ Sistema de Teste de Impressão IPPEL RNC")
    print("="*50)
    
    tester = PrintTester()
    tester.run_tests()

if __name__ == "__main__":
    main() 