#!/usr/bin/env python3
"""
Módulo de formatação monetária e numérica para o sistema IPPEL RNC
Fornece formatação consistente em todo o projeto
"""

import re

def format_currency(value):
    """
    Formata valor monetário com separador de milhares e símbolo de moeda
    
    Args:
        value: Valor numérico para formatar
        
    Returns:
        str: Valor formatado como "$ 32.070,25"
    """
    try:
        if value == 0 or value is None:
            return "$ 0,00"
        
        # Converter para float se necessário
        if isinstance(value, str):
            value = safe_float(value)
        
        # Formatar com separador de milhares (ponto) e decimais (vírgula)
        formatted = f"{value:,.2f}"
        # Trocar ponto por vírgula para decimais e vírgula por ponto para milhares (padrão brasileiro)
        parts = formatted.split('.')
        if len(parts) == 2:
            # Separar parte inteira e decimal
            integer_part = parts[0].replace(',', '.')  # Vírgulas viram pontos (separador de milhares)
            decimal_part = parts[1]
            formatted = f"{integer_part},{decimal_part}"  # Vírgula para decimais
        
        return f"$ {formatted}"
    except:
        return "$ 0,00"

def format_number(value):
    """
    Formata número sem símbolo de moeda
    
    Args:
        value: Valor numérico para formatar
        
    Returns:
        str: Valor formatado como "32.070,25"
    """
    try:
        if value == 0 or value is None:
            return "0,00"
        
        if isinstance(value, str):
            value = safe_float(value)
        
        # Formatar com separador de milhares e decimais
        formatted = f"{value:,.2f}"
        # Converter para padrão brasileiro
        parts = formatted.split('.')
        if len(parts) == 2:
            integer_part = parts[0].replace(',', '.')
            decimal_part = parts[1]
            formatted = f"{integer_part},{decimal_part}"
        
        return formatted
    except:
        return "0,00"

def format_percentage(value):
    """
    Formata valor como porcentagem
    
    Args:
        value: Valor numérico para formatar (ex: 75.5)
        
    Returns:
        str: Valor formatado como "75,5%"
    """
    try:
        if value == 0 or value is None:
            return "0%"
        
        if isinstance(value, str):
            value = safe_float(value)
        
        # Formatar com uma casa decimal se necessário
        if value == int(value):
            return f"{int(value)}%"
        else:
            return f"{value:.1f}%".replace('.', ',')
    except:
        return "0%"

def safe_float(value):
    """
    Converte valor para float de forma segura
    
    Args:
        value: Valor a ser convertido
        
    Returns:
        float: Valor convertido ou 0.0 se houver erro
    """
    try:
        if value is None or value == '':
            return 0.0
        
        # Se for string, tentar converter removendo caracteres não numéricos
        if isinstance(value, str):
            # Remover caracteres não numéricos exceto ponto e vírgula
            cleaned = re.sub(r'[^\d.,\-]', '', value)
            if cleaned:
                # Substituir vírgula por ponto para conversão
                cleaned = cleaned.replace(',', '.')
                # Se houver múltiplos pontos, manter apenas o último como decimal
                if cleaned.count('.') > 1:
                    parts = cleaned.split('.')
                    cleaned = ''.join(parts[:-1]) + '.' + parts[-1]
                return float(cleaned)
        
        return float(value)
    except:
        return 0.0

def format_data_for_dashboard(data_dict):
    """
    Aplica formatação monetária a um dicionário de dados do dashboard
    
    Args:
        data_dict: Dicionário com dados do dashboard
        
    Returns:
        dict: Dicionário com valores formatados
    """
    if not isinstance(data_dict, dict):
        return data_dict
    
    formatted_data = data_dict.copy()
    
    # Formatar dados mensais se existirem
    if 'monthlyData' in formatted_data and isinstance(formatted_data['monthlyData'], list):
        for month_data in formatted_data['monthlyData']:
            if isinstance(month_data, dict):
                # Preservar valores brutos para cálculos
                if 'meta' in month_data and not isinstance(month_data['meta'], str):
                    month_data['meta_raw'] = month_data['meta']
                    month_data['meta'] = format_currency(month_data['meta'])
                if 'realizado' in month_data and not isinstance(month_data['realizado'], str):
                    month_data['realizado_raw'] = month_data['realizado']
                    month_data['realizado'] = format_currency(month_data['realizado'])
    
    # Formatar dados departamentais se existirem
    if 'departments' in formatted_data and isinstance(formatted_data['departments'], list):
        for dept_data in formatted_data['departments']:
            if isinstance(dept_data, dict):
                # Preservar valores brutos para cálculos
                if 'meta' in dept_data and not isinstance(dept_data['meta'], str):
                    dept_data['meta_raw'] = dept_data['meta']
                    dept_data['meta'] = format_currency(dept_data['meta'])
                if 'realizado' in dept_data and not isinstance(dept_data['realizado'], str):
                    dept_data['realizado_raw'] = dept_data['realizado']
                    dept_data['realizado'] = format_currency(dept_data['realizado'])
                if 'efficiency' in dept_data and not isinstance(dept_data['efficiency'], str):
                    dept_data['efficiency_raw'] = dept_data['efficiency']
                    dept_data['efficiency'] = format_percentage(dept_data['efficiency'])
    
    # Formatar totais se existirem
    if 'totals' in formatted_data and isinstance(formatted_data['totals'], dict):
        totals = formatted_data['totals']
        for key in ['meta', 'realizado', 'variacao', 'acumulado']:
            if key in totals and not isinstance(totals[key], str):
                totals[f'{key}_raw'] = totals[key]
                totals[key] = format_currency(totals[key])
    
    return formatted_data

def format_table_data(data_list, currency_fields=None, percentage_fields=None, number_fields=None):
    """
    Formata dados de tabela aplicando formatação apropriada aos campos
    
    Args:
        data_list: Lista de dicionários com dados
        currency_fields: Lista de campos que devem ser formatados como moeda
        percentage_fields: Lista de campos que devem ser formatados como porcentagem
        number_fields: Lista de campos que devem ser formatados como número
        
    Returns:
        list: Lista com dados formatados
    """
    if not isinstance(data_list, list):
        return data_list
    
    currency_fields = currency_fields or []
    percentage_fields = percentage_fields or []
    number_fields = number_fields or []
    
    formatted_list = []
    
    for item in data_list:
        if isinstance(item, dict):
            formatted_item = item.copy()
            
            # Formatar campos monetários
            for field in currency_fields:
                if field in formatted_item and not isinstance(formatted_item[field], str):
                    formatted_item[f'{field}_raw'] = formatted_item[field]
                    formatted_item[field] = format_currency(formatted_item[field])
            
            # Formatar campos de porcentagem
            for field in percentage_fields:
                if field in formatted_item and not isinstance(formatted_item[field], str):
                    formatted_item[f'{field}_raw'] = formatted_item[field]
                    formatted_item[field] = format_percentage(formatted_item[field])
            
            # Formatar campos numéricos
            for field in number_fields:
                if field in formatted_item and not isinstance(formatted_item[field], str):
                    formatted_item[f'{field}_raw'] = formatted_item[field]
                    formatted_item[field] = format_number(formatted_item[field])
            
            formatted_list.append(formatted_item)
        else:
            formatted_list.append(item)
    
    return formatted_list
