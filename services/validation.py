#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Validação de Dados Avançada - IPPEL RNC
Sistema de validação robusto para APIs e formulários com melhorias de segurança
"""

from typing import Any, Dict, List, Optional, Union, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
import re
import html
import json
from datetime import datetime
import logging
import bleach

logger = logging.getLogger('ippel.validation')

class ValidationErrorType(Enum):
    """Tipos de erro de validação"""
    REQUIRED = "required"
    TYPE_ERROR = "type_error"
    LENGTH_ERROR = "length_error"
    FORMAT_ERROR = "format_error"
    RANGE_ERROR = "range_error"
    CUSTOM_ERROR = "custom_error"
    SECURITY_ERROR = "security_error"  # Novo tipo para erros de segurança

@dataclass
class ValidationError:
    """Erro de validação"""
    field: str
    error_type: ValidationErrorType
    message: str
    value: Any = None
    security_risk: bool = False  # Flag para indicar risco de segurança

@dataclass
class ValidationResult:
    """Resultado da validação"""
    is_valid: bool
    errors: List[ValidationError] = field(default_factory=list)
    cleaned_data: Dict[str, Any] = field(default_factory=dict)
    security_warnings: List[str] = field(default_factory=list)  # Avisos de segurança
    
    def add_error(self, field: str, error_type: ValidationErrorType, message: str, value: Any = None, security_risk: bool = False):
        """Adiciona um erro de validação"""
        self.errors.append(ValidationError(field, error_type, message, value, security_risk))
        self.is_valid = False
        
    def add_security_warning(self, warning: str):
        """Adiciona aviso de segurança"""
        self.security_warnings.append(warning)

class SecurityValidator:
    """Validador especializado em segurança"""
    
    # Padrões perigosos para detecção
    DANGEROUS_PATTERNS = [
        r'<script[^>]*>.*?</script>',  # Scripts
        r'javascript:',  # JavaScript URLs
        r'vbscript:',   # VBScript URLs
        r'on\w+\s*=',   # Event handlers
        r'eval\s*\(',   # eval() calls
        r'expression\s*\(',  # CSS expressions
    ]
    
    SQL_INJECTION_PATTERNS = [
        r'union\s+select',
        r'drop\s+table',
        r'delete\s+from',
        r'insert\s+into',
        r'update\s+.*set',
        r'exec\s*\(',
        r'execute\s*\(',
        r'sp_\w+',
        r'xp_\w+',
    ]
    
    @classmethod
    def sanitize_html_input(cls, value: str) -> str:
        """Sanitiza entrada HTML removendo conteúdo perigoso"""
        if not isinstance(value, str):
            return str(value) if value is not None else ''
        
        # Usar bleach para sanitização robusta
        allowed_tags = []  # Nenhuma tag permitida por padrão
        allowed_attributes = {}
        
        cleaned = bleach.clean(
            value, 
            tags=allowed_tags, 
            attributes=allowed_attributes,
            strip=True
        )
        
        return cleaned
    
    @classmethod
    def detect_xss_attempt(cls, value: str) -> bool:
        """Detecta tentativas de XSS"""
        if not isinstance(value, str):
            return False
        
        value_lower = value.lower()
        for pattern in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, value_lower, re.IGNORECASE):
                return True
        return False
    
    @classmethod
    def detect_sql_injection(cls, value: str) -> bool:
        """Detecta tentativas de SQL injection"""
        if not isinstance(value, str):
            return False
            
        value_lower = value.lower()
        for pattern in cls.SQL_INJECTION_PATTERNS:
            if re.search(pattern, value_lower, re.IGNORECASE):
                return True
        return False
    
    @classmethod
    def validate_file_upload_security(cls, filename: str, content: bytes) -> Tuple[bool, List[str]]:
        """Valida segurança de upload de arquivo"""
        issues = []
        
        # Verificar extensão dupla (ex: file.php.jpg)
        if filename.count('.') > 1:
            parts = filename.split('.')
            if len(parts) > 2:
                issues.append("Arquivo com múltiplas extensões detectado")
        
        # Verificar extensões perigosas
        dangerous_extensions = {
            '.php', '.asp', '.aspx', '.jsp', '.js', '.vbs', '.ps1',
            '.bat', '.cmd', '.com', '.exe', '.scr', '.pif'
        }
        
        filename_lower = filename.lower()
        for ext in dangerous_extensions:
            if filename_lower.endswith(ext):
                issues.append(f"Extensão perigosa detectada: {ext}")
        
        # Verificar magic bytes suspeitos
        if content:
            magic_bytes = content[:10]
            if magic_bytes.startswith(b'<?php') or magic_bytes.startswith(b'<script'):
                issues.append("Conteúdo executável detectado no arquivo")
        
        return len(issues) == 0, issues

class Validator:
    """Validador base"""
    
    def __init__(self, required: bool = False, allow_null: bool = False):
        self.required = required
        self.allow_null = allow_null
    
    def validate(self, value: Any, field_name: str) -> ValidationResult:
        """Valida um valor"""
        result = ValidationResult(is_valid=True)
        
        # Verificar se é obrigatório
        if self.required and (value is None or value == ""):
            result.add_error(field_name, ValidationErrorType.REQUIRED, f"Campo '{field_name}' é obrigatório")
            return result
        
        # Verificar se permite null
        if value is None:
            if self.allow_null:
                result.cleaned_data[field_name] = None
                return result
            else:
                result.add_error(field_name, ValidationErrorType.REQUIRED, f"Campo '{field_name}' não pode ser nulo")
                return result
        
        # Validação específica do tipo
        return self._validate_value(value, field_name, result)
    
    def _validate_value(self, value: Any, field_name: str, result: ValidationResult) -> ValidationResult:
        """Implementar validação específica em subclasses"""
        result.cleaned_data[field_name] = value
        return result

class StringValidator(Validator):
    """Validador de strings"""
    
    def __init__(self, min_length: int = 0, max_length: int = None, pattern: str = None, **kwargs):
        super().__init__(**kwargs)
        self.min_length = min_length
        self.max_length = max_length
        self.pattern = re.compile(pattern) if pattern else None
    
    def _validate_value(self, value: Any, field_name: str, result: ValidationResult) -> ValidationResult:
        # Converter para string se necessário
        if not isinstance(value, str):
            value = str(value)
        
        # Verificar comprimento
        if len(value) < self.min_length:
            result.add_error(field_name, ValidationErrorType.LENGTH_ERROR, 
                           f"Campo '{field_name}' deve ter pelo menos {self.min_length} caracteres")
        
        if self.max_length and len(value) > self.max_length:
            result.add_error(field_name, ValidationErrorType.LENGTH_ERROR, 
                           f"Campo '{field_name}' deve ter no máximo {self.max_length} caracteres")
        
        # Verificar padrão
        if self.pattern and not self.pattern.match(value):
            result.add_error(field_name, ValidationErrorType.FORMAT_ERROR, 
                           f"Campo '{field_name}' não atende ao formato exigido")
        
        if result.is_valid:
            result.cleaned_data[field_name] = value.strip()
        
        return result

class IntegerValidator(Validator):
    """Validador de inteiros"""
    
    def __init__(self, min_value: int = None, max_value: int = None, **kwargs):
        super().__init__(**kwargs)
        self.min_value = min_value
        self.max_value = max_value
    
    def _validate_value(self, value: Any, field_name: str, result: ValidationResult) -> ValidationResult:
        # Converter para int
        try:
            if isinstance(value, str):
                value = int(value)
            elif isinstance(value, float):
                value = int(value)
            elif not isinstance(value, int):
                raise ValueError()
        except (ValueError, TypeError):
            result.add_error(field_name, ValidationErrorType.TYPE_ERROR, 
                           f"Campo '{field_name}' deve ser um número inteiro")
            return result
        
        # Verificar range
        if self.min_value is not None and value < self.min_value:
            result.add_error(field_name, ValidationErrorType.RANGE_ERROR, 
                           f"Campo '{field_name}' deve ser maior ou igual a {self.min_value}")
        
        if self.max_value is not None and value > self.max_value:
            result.add_error(field_name, ValidationErrorType.RANGE_ERROR, 
                           f"Campo '{field_name}' deve ser menor ou igual a {self.max_value}")
        
        if result.is_valid:
            result.cleaned_data[field_name] = value
        
        return result

class FloatValidator(Validator):
    """Validador de números decimais"""
    
    def __init__(self, min_value: float = None, max_value: float = None, decimal_places: int = None, **kwargs):
        super().__init__(**kwargs)
        self.min_value = min_value
        self.max_value = max_value
        self.decimal_places = decimal_places
    
    def _validate_value(self, value: Any, field_name: str, result: ValidationResult) -> ValidationResult:
        # Converter para float
        try:
            if isinstance(value, str):
                # Suportar formato brasileiro (vírgula como separador decimal)
                value = value.replace(',', '.')
                value = float(value)
            elif not isinstance(value, (int, float)):
                raise ValueError()
        except (ValueError, TypeError):
            result.add_error(field_name, ValidationErrorType.TYPE_ERROR, 
                           f"Campo '{field_name}' deve ser um número")
            return result
        
        # Verificar range
        if self.min_value is not None and value < self.min_value:
            result.add_error(field_name, ValidationErrorType.RANGE_ERROR, 
                           f"Campo '{field_name}' deve ser maior ou igual a {self.min_value}")
        
        if self.max_value is not None and value > self.max_value:
            result.add_error(field_name, ValidationErrorType.RANGE_ERROR, 
                           f"Campo '{field_name}' deve ser menor ou igual a {self.max_value}")
        
        # Verificar casas decimais
        if self.decimal_places is not None:
            value = round(value, self.decimal_places)
        
        if result.is_valid:
            result.cleaned_data[field_name] = value
        
        return result

class EmailValidator(StringValidator):
    """Validador de email"""
    
    def __init__(self, **kwargs):
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        super().__init__(pattern=email_pattern, **kwargs)
    
    def _validate_value(self, value: Any, field_name: str, result: ValidationResult) -> ValidationResult:
        result = super()._validate_value(value, field_name, result)
        
        if result.is_valid and not self.pattern.match(value):
            result.add_error(field_name, ValidationErrorType.FORMAT_ERROR, 
                           f"Campo '{field_name}' deve ser um email válido")
        
        return result

class DateValidator(Validator):
    """Validador de data"""
    
    def __init__(self, date_format: str = "%Y-%m-%d", **kwargs):
        super().__init__(**kwargs)
        self.date_format = date_format
    
    def _validate_value(self, value: Any, field_name: str, result: ValidationResult) -> ValidationResult:
        if isinstance(value, datetime):
            result.cleaned_data[field_name] = value
            return result
        
        if isinstance(value, str):
            try:
                parsed_date = datetime.strptime(value, self.date_format)
                result.cleaned_data[field_name] = parsed_date
                return result
            except ValueError:
                pass
        
        result.add_error(field_name, ValidationErrorType.FORMAT_ERROR, 
                       f"Campo '{field_name}' deve ser uma data válida no formato {self.date_format}")
        return result

class ChoiceValidator(Validator):
    """Validador de escolhas (enum/select)"""
    
    def __init__(self, choices: List[Any], **kwargs):
        super().__init__(**kwargs)
        self.choices = choices
    
    def _validate_value(self, value: Any, field_name: str, result: ValidationResult) -> ValidationResult:
        if value not in self.choices:
            result.add_error(field_name, ValidationErrorType.RANGE_ERROR, 
                           f"Campo '{field_name}' deve ser uma das opções: {', '.join(map(str, self.choices))}")
        else:
            result.cleaned_data[field_name] = value
        
        return result

class CustomValidator(Validator):
    """Validador customizado com função"""
    
    def __init__(self, validate_func: Callable[[Any], bool], error_message: str = None, **kwargs):
        super().__init__(**kwargs)
        self.validate_func = validate_func
        self.error_message = error_message or "Valor inválido"
    
    def _validate_value(self, value: Any, field_name: str, result: ValidationResult) -> ValidationResult:
        try:
            if not self.validate_func(value):
                result.add_error(field_name, ValidationErrorType.CUSTOM_ERROR, 
                               f"Campo '{field_name}': {self.error_message}")
            else:
                result.cleaned_data[field_name] = value
        except Exception as e:
            result.add_error(field_name, ValidationErrorType.CUSTOM_ERROR, 
                           f"Campo '{field_name}': Erro na validação customizada - {str(e)}")
        
        return result

class Schema:
    """Schema de validação para múltiplos campos"""
    
    def __init__(self, fields: Dict[str, Validator]):
        self.fields = fields
    
    def validate(self, data: Dict[str, Any]) -> ValidationResult:
        """Valida um dicionário de dados"""
        result = ValidationResult(is_valid=True)
        
        # Validar cada campo definido no schema
        for field_name, validator in self.fields.items():
            field_value = data.get(field_name)
            field_result = validator.validate(field_value, field_name)
            
            if not field_result.is_valid:
                result.errors.extend(field_result.errors)
                result.is_valid = False
            else:
                result.cleaned_data.update(field_result.cleaned_data)
        
        return result

# === SCHEMAS PRÉ-DEFINIDOS PARA O SISTEMA ===

# Schema para criação de RNC
RNC_CREATE_SCHEMA = Schema({
    'title': StringValidator(min_length=3, max_length=200, required=True),
    'description': StringValidator(min_length=10, max_length=2000, required=True),
    'department': StringValidator(min_length=2, max_length=100, required=True),
    'priority': ChoiceValidator(choices=['Baixa', 'Média', 'Alta', 'Crítica'], required=True),
    'assigned_user_id': IntegerValidator(min_value=1, required=False, allow_null=True),
    'price': FloatValidator(min_value=0.0, decimal_places=2, required=False, allow_null=True),
    'due_date': DateValidator(required=False, allow_null=True),
})

# Schema para atualização de RNC
RNC_UPDATE_SCHEMA = Schema({
    'title': StringValidator(min_length=3, max_length=200, required=False),
    'description': StringValidator(min_length=10, max_length=2000, required=False),
    'department': StringValidator(min_length=2, max_length=100, required=False),
    'priority': ChoiceValidator(choices=['Baixa', 'Média', 'Alta', 'Crítica'], required=False),
    'status': ChoiceValidator(choices=['Aberto', 'Em Andamento', 'Pendente', 'Finalizado'], required=False),
    'assigned_user_id': IntegerValidator(min_value=1, required=False, allow_null=True),
    'price': FloatValidator(min_value=0.0, decimal_places=2, required=False, allow_null=True),
    'due_date': DateValidator(required=False, allow_null=True),
})

# Schema para criação de usuário
USER_CREATE_SCHEMA = Schema({
    'name': StringValidator(min_length=2, max_length=100, required=True),
    'email': EmailValidator(required=True),
    'password': StringValidator(min_length=8, max_length=128, required=True),
    'department': StringValidator(min_length=2, max_length=100, required=True),
    'role': ChoiceValidator(choices=['user', 'admin', 'manager'], required=True),
    'group_id': IntegerValidator(min_value=1, required=False, allow_null=True),
})

# Schema para login
LOGIN_SCHEMA = Schema({
    'email': EmailValidator(required=True),
    'password': StringValidator(min_length=1, required=True),
})

# Schema para relatórios
REPORT_SCHEMA = Schema({
    'start_date': DateValidator(required=True),
    'end_date': DateValidator(required=True),
    'report_type': ChoiceValidator(choices=['finalized', 'total_detailed', 'by_operator', 'by_sector'], required=True),
})

def validate_data(schema: Schema, data: Dict[str, Any]) -> ValidationResult:
    """Função utilitária para validar dados"""
    return schema.validate(data)

def create_api_response(success: bool = True, data: Any = None, message: str = None, 
                       errors: List[ValidationError] = None, status_code: int = 200) -> Dict[str, Any]:
    """Cria resposta padronizada para APIs"""
    response = {
        'success': success,
        'status_code': status_code
    }
    
    if data is not None:
        response['data'] = data
    
    if message:
        response['message'] = message
    
    if errors:
        response['errors'] = [
            {
                'field': error.field,
                'type': error.error_type.value,
                'message': error.message,
                'value': error.value
            } for error in errors
        ]
    
    return response
