"""
Configuração de Impressão para Sistema IPPEL RNC
Garante que a impressão seja exatamente igual ao modelo.pdf
"""

class PrintConfig:
    """Configurações específicas para impressão de RNCs"""
    
    # Configurações de página
    PAGE_SETTINGS = {
        'size': 'A4',
        'orientation': 'portrait',
        'margin_top': '1.5cm',
        'margin_bottom': '1.5cm',
        'margin_left': '1.5cm',
        'margin_right': '1.5cm'
    }
    
    # Configurações de fonte
    FONT_SETTINGS = {
        'family': 'Times New Roman, serif',
        'size_base': '12pt',
        'size_small': '10pt',
        'size_large': '14pt',
        'size_title': '16pt',
        'line_height': '1.2'
    }
    
    # Configurações de cores
    COLOR_SETTINGS = {
        'text': 'black',
        'background': 'white',
        'border': 'black',
        'header_bg': '#333',
        'header_text': 'white'
    }
    
    # Configurações de layout
    LAYOUT_SETTINGS = {
        'header_logo_size': '80px',
        'header_spacing': '25px',
        'section_spacing': '15px',
        'field_spacing': '8px',
        'border_width': '1px',
        'border_style': 'solid'
    }
    
    @staticmethod
    def get_print_css():
        """Retorna o CSS completo para impressão"""
        return f"""
        @media print {{
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
                -webkit-print-color-adjust: exact !important;
                print-color-adjust: exact !important;
                color-adjust: exact !important;
            }}

            body {{
                background: {PrintConfig.COLOR_SETTINGS['background']} !important;
                font-family: {PrintConfig.FONT_SETTINGS['family']} !important;
                font-size: {PrintConfig.FONT_SETTINGS['size_base']} !important;
                line-height: {PrintConfig.FONT_SETTINGS['line_height']} !important;
                color: {PrintConfig.COLOR_SETTINGS['text']} !important;
                margin: 0 !important;
                padding: 0 !important;
            }}

            .container {{
                width: 100% !important;
                max-width: none !important;
                background: {PrintConfig.COLOR_SETTINGS['background']} !important;
                padding: 15px !important;
                box-shadow: none !important;
                border: none !important;
                border-radius: 0 !important;
                margin: 0 !important;
            }}

            .header {{
                text-align: center !important;
                margin-bottom: {PrintConfig.LAYOUT_SETTINGS['header_spacing']} !important;
                border-bottom: 2px solid {PrintConfig.COLOR_SETTINGS['border']} !important;
                padding-bottom: 15px !important;
                page-break-inside: avoid !important;
            }}

            .logo {{
                width: {PrintConfig.LAYOUT_SETTINGS['header_logo_size']} !important;
                height: {PrintConfig.LAYOUT_SETTINGS['header_logo_size']} !important;
                margin: 0 auto 15px !important;
                display: block !important;
                object-fit: contain !important;
            }}

            .header-text h1 {{
                font-size: {PrintConfig.FONT_SETTINGS['size_title']} !important;
                font-weight: bold !important;
                text-transform: uppercase !important;
                margin-bottom: 8px !important;
                color: {PrintConfig.COLOR_SETTINGS['text']} !important;
                letter-spacing: 1px !important;
            }}

            .rnc-number {{
                font-size: {PrintConfig.FONT_SETTINGS['size_large']} !important;
                font-weight: bold !important;
                background: {PrintConfig.COLOR_SETTINGS['background']} !important;
                border: 2px solid {PrintConfig.COLOR_SETTINGS['border']} !important;
                padding: 8px 20px !important;
                display: inline-block !important;
                color: {PrintConfig.COLOR_SETTINGS['text']} !important;
                margin-top: 10px !important;
            }}

            .action-buttons {{
                display: none !important;
            }}

            .form-section {{
                background: {PrintConfig.COLOR_SETTINGS['background']} !important;
                border: {PrintConfig.LAYOUT_SETTINGS['border_width']} solid {PrintConfig.COLOR_SETTINGS['border']} !important;
                border-radius: 0 !important;
                padding: 12px !important;
                margin-bottom: {PrintConfig.LAYOUT_SETTINGS['section_spacing']} !important;
                box-shadow: none !important;
                page-break-inside: avoid !important;
                break-inside: avoid !important;
            }}

            .section-title {{
                font-size: 13pt !important;
                font-weight: bold !important;
                color: {PrintConfig.COLOR_SETTINGS['text']} !important;
                margin-bottom: 12px !important;
                text-transform: uppercase !important;
                border-bottom: {PrintConfig.LAYOUT_SETTINGS['border_width']} solid {PrintConfig.COLOR_SETTINGS['border']} !important;
                padding-bottom: 4px !important;
                letter-spacing: 0.5px !important;
            }}

            .form-row {{
                display: block !important;
                margin-bottom: 12px !important;
                page-break-inside: avoid !important;
            }}

            .form-group {{
                margin-bottom: {PrintConfig.LAYOUT_SETTINGS['field_spacing']} !important;
                display: block !important;
                page-break-inside: avoid !important;
            }}

            .form-label {{
                font-weight: bold !important;
                color: {PrintConfig.COLOR_SETTINGS['text']} !important;
                margin-bottom: 3px !important;
                font-size: {PrintConfig.FONT_SETTINGS['size_small']} !important;
                text-transform: uppercase !important;
                display: block !important;
            }}

            .form-input, .form-select, .form-textarea {{
                border: {PrintConfig.LAYOUT_SETTINGS['border_width']} solid {PrintConfig.COLOR_SETTINGS['border']} !important;
                border-radius: 0 !important;
                padding: 4px 6px !important;
                font-size: {PrintConfig.FONT_SETTINGS['size_small']} !important;
                background: {PrintConfig.COLOR_SETTINGS['background']} !important;
                color: {PrintConfig.COLOR_SETTINGS['text']} !important;
                width: 100% !important;
                font-family: {PrintConfig.FONT_SETTINGS['family']} !important;
            }}

            .form-input[readonly], .form-select[disabled], .form-textarea[readonly] {{
                background: #f8f8f8 !important;
                color: {PrintConfig.COLOR_SETTINGS['text']} !important;
                border: {PrintConfig.LAYOUT_SETTINGS['border_width']} solid #666 !important;
            }}

            .form-textarea {{
                min-height: 60px !important;
                resize: none !important;
            }}

            .disposicao-header {{
                background: {PrintConfig.COLOR_SETTINGS['header_bg']} !important;
                color: {PrintConfig.COLOR_SETTINGS['header_text']} !important;
                text-align: center !important;
                padding: 6px 0 !important;
                font-weight: bold !important;
                font-size: 11pt !important;
                text-transform: uppercase !important;
                border: {PrintConfig.LAYOUT_SETTINGS['border_width']} solid {PrintConfig.COLOR_SETTINGS['border']} !important;
                border-radius: 0 !important;
                display: flex !important;
                letter-spacing: 0.5px !important;
            }}

            .disposicao-header > div {{
                width: 50% !important;
                text-align: center !important;
                border-right: {PrintConfig.LAYOUT_SETTINGS['border_width']} solid white !important;
                padding: 4px 0 !important;
            }}

            .disposicao-header > div:last-child {{
                border-right: none !important;
            }}

            .disposicao-content {{
                border: {PrintConfig.LAYOUT_SETTINGS['border_width']} solid {PrintConfig.COLOR_SETTINGS['border']} !important;
                border-top: none !important;
                border-radius: 0 !important;
                background: {PrintConfig.COLOR_SETTINGS['background']} !important;
                display: flex !important;
                padding: 8px !important;
                min-height: 120px !important;
            }}

            .disposicao-content > div {{
                width: 50% !important;
                padding: 8px !important;
                border-right: {PrintConfig.LAYOUT_SETTINGS['border_width']} solid {PrintConfig.COLOR_SETTINGS['border']} !important;
                font-size: {PrintConfig.FONT_SETTINGS['size_small']} !important;
            }}

            .disposicao-content > div:last-child {{
                border-right: none !important;
            }}

            input[type="checkbox"] {{
                width: 12px !important;
                height: 12px !important;
                margin-right: 5px !important;
                accent-color: {PrintConfig.COLOR_SETTINGS['text']} !important;
                -webkit-appearance: checkbox !important;
                appearance: checkbox !important;
            }}

            .signature-container {{
                border: {PrintConfig.LAYOUT_SETTINGS['border_width']} solid {PrintConfig.COLOR_SETTINGS['border']} !important;
                border-radius: 0 !important;
                background: {PrintConfig.COLOR_SETTINGS['background']} !important;
                margin-top: 8px !important;
                page-break-inside: avoid !important;
            }}

            .signature-container > div {{
                border: {PrintConfig.LAYOUT_SETTINGS['border_width']} solid {PrintConfig.COLOR_SETTINGS['border']} !important;
                padding: 6px !important;
                text-align: center !important;
                font-size: 9pt !important;
                font-weight: bold !important;
            }}

            .signature-container > div:first-child {{
                border-bottom: {PrintConfig.LAYOUT_SETTINGS['border_width']} solid {PrintConfig.COLOR_SETTINGS['border']} !important;
            }}

            .signature-container > div:first-child > div {{
                width: 33.33% !important;
                padding: 4px !important;
                text-align: center !important;
                font-size: 8pt !important;
                font-weight: bold !important;
                border-right: {PrintConfig.LAYOUT_SETTINGS['border_width']} solid {PrintConfig.COLOR_SETTINGS['border']} !important;
            }}

            .signature-container > div:first-child > div:last-child {{
                border-right: none !important;
            }}

            .signature-container > div:last-child > div {{
                width: 33.33% !important;
                padding: 12px 4px !important;
                text-align: center !important;
                font-size: 9pt !important;
                font-weight: bold !important;
                border-right: {PrintConfig.LAYOUT_SETTINGS['border_width']} solid {PrintConfig.COLOR_SETTINGS['border']} !important;
                min-height: 40px !important;
            }}

            .signature-container > div:last-child > div:last-child {{
                border-right: none !important;
            }}

            .modal, .modal-backdrop {{
                display: none !important;
            }}

            .form-section + .form-section {{
                margin-top: {PrintConfig.LAYOUT_SETTINGS['section_spacing']} !important;
            }}

            .form-input[type="date"], .form-input[type="datetime-local"] {{
                font-family: {PrintConfig.FONT_SETTINGS['family']} !important;
                font-size: {PrintConfig.FONT_SETTINGS['size_small']} !important;
            }}

            table {{
                border-collapse: collapse !important;
                width: 100% !important;
            }}

            th, td {{
                border: {PrintConfig.LAYOUT_SETTINGS['border_width']} solid {PrintConfig.COLOR_SETTINGS['border']} !important;
                padding: 4px 6px !important;
                font-size: {PrintConfig.FONT_SETTINGS['size_small']} !important;
                text-align: left !important;
            }}

            th {{
                background: #f0f0f0 !important;
                font-weight: bold !important;
            }}

            @page {{
                margin: {PrintConfig.PAGE_SETTINGS['margin_top']} {PrintConfig.PAGE_SETTINGS['margin_right']} {PrintConfig.PAGE_SETTINGS['margin_bottom']} {PrintConfig.PAGE_SETTINGS['margin_left']} !important;
                size: {PrintConfig.PAGE_SETTINGS['size']} !important;
                orientation: {PrintConfig.PAGE_SETTINGS['orientation']} !important;
            }}
        }}
        """
    
    @staticmethod
    def get_print_instructions():
        """Retorna instruções para impressão perfeita"""
        return """
        INSTRUÇÕES PARA IMPRESSÃO PERFEITA:
        
        1. Use o botão "🖨️ Imprimir" no sistema
        2. Configure a impressora para:
           - Tamanho: A4
           - Orientação: Retrato
           - Margens: Padrão (1.5cm)
           - Qualidade: Normal ou Alta
        3. Certifique-se de que "Imprimir fundos" está ativado
        4. Use papel branco de 75g/m² ou superior
        5. Verifique se a impressora está bem calibrada
        
        DICAS IMPORTANTES:
        - Teste primeiro com uma impressão de teste
        - Verifique se todas as bordas estão visíveis
        - Confirme se o texto está legível
        - Certifique-se de que as cores estão corretas
        """

# Configuração para diferentes tipos de impressora
class PrinterConfig:
    """Configurações específicas por tipo de impressora"""
    
    @staticmethod
    def get_hp_config():
        """Configurações para impressoras HP"""
        return {
            'dpi': 600,
            'color_mode': 'color',
            'paper_size': 'A4',
            'orientation': 'portrait',
            'margins': 'normal'
        }
    
    @staticmethod
    def get_canon_config():
        """Configurações para impressoras Canon"""
        return {
            'dpi': 600,
            'color_mode': 'color',
            'paper_size': 'A4',
            'orientation': 'portrait',
            'margins': 'normal'
        }
    
    @staticmethod
    def get_epson_config():
        """Configurações para impressoras Epson"""
        return {
            'dpi': 600,
            'color_mode': 'color',
            'paper_size': 'A4',
            'orientation': 'portrait',
            'margins': 'normal'
        } 