import re

# Ler arquivo atual
with open('templates/view_rnc_full.html', 'r', encoding='utf-8') as f:
    content = f.read()

# CSS DE IMPRESSÃO CORRETO PARA VIEW_RNC_FULL
new_media_print = '''@media print {
            /* REMOVER BOTÕES E CONTROLES */
            .action-bar,
            .create-mode-banner,
            .no-print,
            .print-controls,
            button {
                display: none !important;
            }
            
            body {
                background: white;
                margin: 0;
                padding: 0;
                -webkit-print-color-adjust: exact !important;
                print-color-adjust: exact !important;
            }
            
            .container {
                box-shadow: none !important;
                border: none !important;
                padding: 6mm !important;
                margin: 0 !important;
                width: 100%;
                height: auto;
                overflow: visible;
                border-radius: 0 !important;
            }
            
            @page {
                size: A4;
                margin: 3mm 5mm;
            }
            
            html {
                zoom: 0.95;
            }
            
            /* Logos */
            .logos img {
                width: 30px !important;
                height: 30px !important;
            }
            
            .logos {
                margin-bottom: 2px !important;
                margin-top: 0 !important;
                padding-top: 0 !important;
                border: none !important;
            }
            
            .header {
                border: none !important;
                box-shadow: none !important;
            }
            
            /* Títulos */
            .title-section {
                margin: 0 !important;
                padding: 0 !important;
            }
            
            .main-title {
                font-size: 12px !important;
                margin-bottom: 1px !important;
                margin-top: 0 !important;
                padding-top: 0 !important;
                color: #000 !important;
                line-height: 1 !important;
                font-weight: normal !important;
            }
            
            .subtitle,
            .form-code {
                display: none !important;
            }
            
            .rnc-number {
                margin-bottom: 2px !important;
                margin-top: 1px !important;
                padding: 2px !important;
                border-radius: 0 !important;
                text-align: center !important;
                font-size: 9px !important;
                font-weight: normal !important;
            }
            
            /* Seções */
            div[style*="margin: 25px 0"] {
                margin: 3px 0 !important;
                border: 1px solid #000 !important;
                border-radius: 0 !important;
            }
            
            /* Headers de seção */
            div[style*="background: linear-gradient"],
            div[style*="background: #6c757d"] {
                background: #fff !important;
                color: #000 !important;
                padding: 2px 4px !important;
                font-size: 9px !important;
                font-weight: normal !important;
                border: 1px solid #000 !important;
                line-height: 1.1 !important;
            }
            
            /* Padding das seções */
            div[style*="padding: 20px"] {
                padding: 3px 4px !important;
                background: #fff !important;
            }
            
            /* Tabelas */
            table {
                width: 100% !important;
                border-collapse: collapse !important;
                margin-bottom: 2px !important;
                font-size: 8px !important;
            }
            
            table td, table th {
                border: 1px solid #000 !important;
                padding: 2px 3px !important;
                color: #000 !important;
                font-weight: normal !important;
            }
            
            .field-label {
                background: #f5f5f5 !important;
                font-weight: normal !important;
                font-size: 8px !important;
                padding: 1px 2px !important;
            }
            
            .input-field {
                border: none !important;
                padding: 1px 2px !important;
                font-size: 8px !important;
                color: #000 !important;
            }
            
            textarea.input-field {
                min-height: 20px !important;
                height: 20px !important;
                line-height: 1.2 !important;
            }
            
            textarea.large-text-area {
                min-height: 30px !important;
                height: 30px !important;
            }
            
            textarea.medium-text-area {
                min-height: 25px !important;
                height: 25px !important;
            }
            
            /* Checkboxes */
            input[type="checkbox"] {
                width: 10px !important;
                height: 10px !important;
                margin: 1px !important;
            }
            
            /* Remover espaços extras */
            body * {
                line-height: 1 !important;
            }
            
            /* Forçar quebra de página no final */
            .container {
                page-break-after: avoid !important;
            }
            
            * {
                page-break-inside: avoid !important;
            }
            
            /* Tudo em preto e sem negrito */
            * {
                color: #000 !important;
                font-weight: normal !important;
                font-weight: 400 !important;
            }
        }'''

# Substituir @media print block
pattern = r'@media print \{[\s\S]*?\n        \}'
new_content = re.sub(pattern, new_media_print, content, count=1, flags=re.DOTALL)

# Salvar
with open('templates/view_rnc_full.html', 'w', encoding='utf-8') as f:
    f.write(new_content)

print('CSS restaurado e corrigido!')
