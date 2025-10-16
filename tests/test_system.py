#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Testes Automatizados - IPPEL RNC Sistema
Suite completa de testes para validação do sistema
"""

import unittest
import sqlite3
import tempfile
import os
import json
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
import sys

# Adicionar o diretório raiz ao path para importações
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.validation import (
    StringValidator, IntegerValidator, FloatValidator, EmailValidator, 
    DateValidator, ChoiceValidator, Schema, ValidationErrorType,
    RNC_CREATE_SCHEMA, USER_CREATE_SCHEMA, LOGIN_SCHEMA
)

class TestValidation(unittest.TestCase):
    """Testes para o sistema de validação"""
    
    def test_string_validator_valid(self):
        """Testa StringValidator com entrada válida"""
        validator = StringValidator(min_length=3, max_length=10, required=True)
        result = validator.validate("teste", "campo")
        
        self.assertTrue(result.is_valid)
        self.assertEqual(result.cleaned_data["campo"], "teste")
        self.assertEqual(len(result.errors), 0)
    
    def test_string_validator_too_short(self):
        """Testa StringValidator com string muito curta"""
        validator = StringValidator(min_length=5, required=True)
        result = validator.validate("ab", "campo")
        
        self.assertFalse(result.is_valid)
        self.assertEqual(len(result.errors), 1)
        self.assertEqual(result.errors[0].error_type, ValidationErrorType.LENGTH_ERROR)
    
    def test_string_validator_too_long(self):
        """Testa StringValidator com string muito longa"""
        validator = StringValidator(max_length=5, required=True)
        result = validator.validate("abcdefghij", "campo")
        
        self.assertFalse(result.is_valid)
        self.assertEqual(len(result.errors), 1)
        self.assertEqual(result.errors[0].error_type, ValidationErrorType.LENGTH_ERROR)
    
    def test_string_validator_required_empty(self):
        """Testa StringValidator com campo obrigatório vazio"""
        validator = StringValidator(required=True)
        result = validator.validate("", "campo")
        
        self.assertFalse(result.is_valid)
        self.assertEqual(result.errors[0].error_type, ValidationErrorType.REQUIRED)
    
    def test_integer_validator_valid(self):
        """Testa IntegerValidator com entrada válida"""
        validator = IntegerValidator(min_value=1, max_value=100, required=True)
        result = validator.validate(50, "numero")
        
        self.assertTrue(result.is_valid)
        self.assertEqual(result.cleaned_data["numero"], 50)
    
    def test_integer_validator_string_conversion(self):
        """Testa conversão de string para int"""
        validator = IntegerValidator()
        result = validator.validate("123", "numero")
        
        self.assertTrue(result.is_valid)
        self.assertEqual(result.cleaned_data["numero"], 123)
    
    def test_integer_validator_invalid_string(self):
        """Testa string não numérica"""
        validator = IntegerValidator()
        result = validator.validate("abc", "numero")
        
        self.assertFalse(result.is_valid)
        self.assertEqual(result.errors[0].error_type, ValidationErrorType.TYPE_ERROR)
    
    def test_integer_validator_out_of_range(self):
        """Testa valor fora do range"""
        validator = IntegerValidator(min_value=10, max_value=20)
        result = validator.validate(5, "numero")
        
        self.assertFalse(result.is_valid)
        self.assertEqual(result.errors[0].error_type, ValidationErrorType.RANGE_ERROR)
    
    def test_float_validator_valid(self):
        """Testa FloatValidator com entrada válida"""
        validator = FloatValidator(decimal_places=2)
        result = validator.validate(12.345, "preco")
        
        self.assertTrue(result.is_valid)
        self.assertEqual(result.cleaned_data["preco"], 12.35)  # Arredondado
    
    def test_float_validator_brazilian_format(self):
        """Testa conversão do formato brasileiro (vírgula)"""
        validator = FloatValidator()
        result = validator.validate("12,50", "preco")
        
        self.assertTrue(result.is_valid)
        self.assertEqual(result.cleaned_data["preco"], 12.5)
    
    def test_email_validator_valid(self):
        """Testa EmailValidator com email válido"""
        validator = EmailValidator()
        result = validator.validate("teste@exemplo.com", "email")
        
        self.assertTrue(result.is_valid)
        self.assertEqual(result.cleaned_data["email"], "teste@exemplo.com")
    
    def test_email_validator_invalid(self):
        """Testa EmailValidator com email inválido"""
        validator = EmailValidator()
        result = validator.validate("email_invalido", "email")
        
        self.assertFalse(result.is_valid)
        self.assertEqual(result.errors[0].error_type, ValidationErrorType.FORMAT_ERROR)
    
    def test_date_validator_valid(self):
        """Testa DateValidator com data válida"""
        validator = DateValidator()
        result = validator.validate("2025-09-15", "data")
        
        self.assertTrue(result.is_valid)
        self.assertIsInstance(result.cleaned_data["data"], datetime)
    
    def test_date_validator_invalid_format(self):
        """Testa DateValidator com formato inválido"""
        validator = DateValidator()
        result = validator.validate("15/09/2025", "data")
        
        self.assertFalse(result.is_valid)
        self.assertEqual(result.errors[0].error_type, ValidationErrorType.FORMAT_ERROR)
    
    def test_choice_validator_valid(self):
        """Testa ChoiceValidator com escolha válida"""
        validator = ChoiceValidator(choices=['A', 'B', 'C'])
        result = validator.validate('B', "opcao")
        
        self.assertTrue(result.is_valid)
        self.assertEqual(result.cleaned_data["opcao"], 'B')
    
    def test_choice_validator_invalid(self):
        """Testa ChoiceValidator com escolha inválida"""
        validator = ChoiceValidator(choices=['A', 'B', 'C'])
        result = validator.validate('D', "opcao")
        
        self.assertFalse(result.is_valid)
        self.assertEqual(result.errors[0].error_type, ValidationErrorType.RANGE_ERROR)
    
    def test_schema_validation_valid(self):
        """Testa validação de schema completo"""
        data = {
            'title': 'Teste RNC',
            'description': 'Descrição detalhada do problema encontrado',
            'department': 'Qualidade',
            'priority': 'Alta',
            'price': 150.75
        }
        
        result = RNC_CREATE_SCHEMA.validate(data)
        
        self.assertTrue(result.is_valid)
        self.assertEqual(len(result.errors), 0)
        self.assertEqual(result.cleaned_data['title'], 'Teste RNC')
        self.assertEqual(result.cleaned_data['price'], 150.75)
    
    def test_schema_validation_invalid(self):
        """Testa validação de schema com erros"""
        data = {
            'title': 'T',  # Muito curto
            'description': 'Desc',  # Muito curto
            'department': '',  # Vazio
            'priority': 'Inválida',  # Não está nas opções
            'price': -10  # Valor negativo
        }
        
        result = RNC_CREATE_SCHEMA.validate(data)
        
        self.assertFalse(result.is_valid)
        self.assertGreater(len(result.errors), 0)
        
        # Verificar tipos específicos de erro
        error_types = [error.error_type for error in result.errors]
        self.assertIn(ValidationErrorType.LENGTH_ERROR, error_types)
        self.assertIn(ValidationErrorType.RANGE_ERROR, error_types)


class TestDatabaseOperations(unittest.TestCase):
    """Testes para operações de banco de dados"""
    
    def setUp(self):
        """Setup para cada teste"""
        # Criar banco temporário para testes
        self.test_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.test_db_path = self.test_db.name
        self.test_db.close()
        
        # Criar estrutura básica do banco
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        
        # Tabela de usuários
        cursor.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                department TEXT NOT NULL,
                role TEXT DEFAULT 'user',
                is_active INTEGER DEFAULT 1,
                group_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de RNCs
        cursor.execute('''
            CREATE TABLE rncs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rnc_number TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                department TEXT NOT NULL,
                priority TEXT NOT NULL,
                status TEXT DEFAULT 'Aberto',
                user_id INTEGER NOT NULL,
                assigned_user_id INTEGER,
                price REAL,
                due_date DATE,
                finalized_at TIMESTAMP,
                is_deleted INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (assigned_user_id) REFERENCES users (id)
            )
        ''')
        
        # Inserir dados de teste
        cursor.execute('''
            INSERT INTO users (name, email, password_hash, department, role)
            VALUES ('Usuário Teste', 'teste@exemplo.com', 'hash123', 'Qualidade', 'user')
        ''')
        
        cursor.execute('''
            INSERT INTO rncs (rnc_number, title, description, department, priority, user_id, price)
            VALUES ('RNC-2025-001', 'RNC Teste', 'Descrição da RNC de teste', 'Qualidade', 'Alta', 1, 100.50)
        ''')
        
        conn.commit()
        conn.close()
    
    def tearDown(self):
        """Cleanup após cada teste"""
        if os.path.exists(self.test_db_path):
            os.unlink(self.test_db_path)
    
    def test_user_creation(self):
        """Testa criação de usuário no banco"""
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO users (name, email, password_hash, department, role)
            VALUES (?, ?, ?, ?, ?)
        ''', ('Novo Usuario', 'novo@exemplo.com', 'hash456', 'TI', 'admin'))
        
        conn.commit()
        
        # Verificar se foi inserido
        cursor.execute('SELECT * FROM users WHERE email = ?', ('novo@exemplo.com',))
        user = cursor.fetchone()
        
        self.assertIsNotNone(user)
        self.assertEqual(user[1], 'Novo Usuario')  # name
        self.assertEqual(user[4], 'TI')  # department
        
        conn.close()
    
    def test_rnc_creation(self):
        """Testa criação de RNC"""
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO rncs (rnc_number, title, description, department, priority, user_id, price)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', ('RNC-2025-002', 'Segunda RNC', 'Descrição detalhada', 'Produção', 'Média', 1, 75.25))
        
        conn.commit()
        
        # Verificar se foi inserido
        cursor.execute('SELECT * FROM rncs WHERE rnc_number = ?', ('RNC-2025-002',))
        rnc = cursor.fetchone()
        
        self.assertIsNotNone(rnc)
        self.assertEqual(rnc[2], 'Segunda RNC')  # title
        self.assertEqual(rnc[9], 75.25)  # price
        
        conn.close()
    
    def test_rnc_update_status(self):
        """Testa atualização de status da RNC"""
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        
        # Atualizar status
        cursor.execute('''
            UPDATE rncs SET status = ?, finalized_at = ? WHERE id = ?
        ''', ('Finalizado', datetime.now(), 1))
        
        conn.commit()
        
        # Verificar atualização
        cursor.execute('SELECT status, finalized_at FROM rncs WHERE id = 1')
        result = cursor.fetchone()
        
        self.assertEqual(result[0], 'Finalizado')
        self.assertIsNotNone(result[1])
        
        conn.close()
    
    def test_rnc_soft_delete(self):
        """Testa exclusão lógica (soft delete) da RNC"""
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        
        # Marcar como deletado
        cursor.execute('UPDATE rncs SET is_deleted = 1 WHERE id = 1')
        conn.commit()
        
        # Verificar que ainda existe mas está marcado como deletado
        cursor.execute('SELECT is_deleted FROM rncs WHERE id = 1')
        result = cursor.fetchone()
        self.assertEqual(result[0], 1)
        
        # Verificar que não aparece em consultas normais
        cursor.execute('SELECT COUNT(*) FROM rncs WHERE is_deleted = 0')
        count = cursor.fetchone()[0]
        self.assertEqual(count, 0)
        
        conn.close()


class TestAPIResponses(unittest.TestCase):
    """Testes para respostas da API"""
    
    def test_create_api_response_success(self):
        """Testa criação de resposta de sucesso"""
        from services.validation import create_api_response
        
        response = create_api_response(
            success=True,
            data={'id': 1, 'title': 'Teste'},
            message='Operação realizada com sucesso'
        )
        
        self.assertTrue(response['success'])
        self.assertEqual(response['status_code'], 200)
        self.assertEqual(response['data']['id'], 1)
        self.assertEqual(response['message'], 'Operação realizada com sucesso')
    
    def test_create_api_response_error(self):
        """Testa criação de resposta de erro"""
        from services.validation import create_api_response, ValidationError, ValidationErrorType
        
        errors = [
            ValidationError('campo1', ValidationErrorType.REQUIRED, 'Campo obrigatório', None)
        ]
        
        response = create_api_response(
            success=False,
            message='Dados inválidos',
            errors=errors,
            status_code=400
        )
        
        self.assertFalse(response['success'])
        self.assertEqual(response['status_code'], 400)
        self.assertEqual(len(response['errors']), 1)
        self.assertEqual(response['errors'][0]['field'], 'campo1')
        self.assertEqual(response['errors'][0]['type'], 'required')


class TestReportGeneration(unittest.TestCase):
    """Testes para geração de relatórios"""
    
    def setUp(self):
        """Setup com dados de teste para relatórios"""
        self.test_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.test_db_path = self.test_db.name
        self.test_db.close()
        
        # Criar estrutura e dados de teste
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        
        # Estrutura simplificada
        cursor.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY,
                name TEXT,
                department TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE rncs (
                id INTEGER PRIMARY KEY,
                title TEXT,
                status TEXT,
                priority TEXT,
                price REAL,
                user_id INTEGER,
                created_at TIMESTAMP,
                finalized_at TIMESTAMP,
                is_deleted INTEGER DEFAULT 0
            )
        ''')
        
        # Inserir dados de teste
        users_data = [
            (1, 'João Silva', 'Qualidade'),
            (2, 'Maria Santos', 'Produção'),
            (3, 'Pedro Costa', 'Administração')
        ]
        
        rncs_data = [
            (1, 'RNC Equipamento', 'Finalizado', 'Alta', 500.0, 1, '2025-09-01', '2025-09-10', 0),
            (2, 'RNC Processo', 'Aberto', 'Média', 200.0, 2, '2025-09-05', None, 0),
            (3, 'RNC Documentação', 'Finalizado', 'Baixa', 50.0, 1, '2025-09-08', '2025-09-12', 0),
            (4, 'RNC Deletada', 'Aberto', 'Alta', 300.0, 3, '2025-09-09', None, 1)
        ]
        
        cursor.executemany('INSERT INTO users VALUES (?, ?, ?)', users_data)
        cursor.executemany('INSERT INTO rncs VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', rncs_data)
        
        conn.commit()
        conn.close()
    
    def tearDown(self):
        """Cleanup"""
        if os.path.exists(self.test_db_path):
            os.unlink(self.test_db_path)
    
    def test_calculate_report_stats(self):
        """Testa cálculo de estatísticas para relatórios"""
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        
        # Simular função de cálculo de estatísticas
        cursor.execute("SELECT COUNT(*) FROM rncs WHERE is_deleted = 0")
        total_rncs = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM rncs WHERE is_deleted = 0 AND status = 'Finalizado'")
        finalized_rncs = cursor.fetchone()[0]
        
        cursor.execute("SELECT SUM(price) FROM rncs WHERE is_deleted = 0")
        total_value = cursor.fetchone()[0]
        
        self.assertEqual(total_rncs, 3)  # Excluindo a RNC deletada
        self.assertEqual(finalized_rncs, 2)
        self.assertEqual(total_value, 750.0)  # 500 + 200 + 50
        
        conn.close()
    
    def test_report_by_department(self):
        """Testa relatório por departamento"""
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT u.department, COUNT(r.id), SUM(r.price)
            FROM rncs r
            JOIN users u ON r.user_id = u.id
            WHERE r.is_deleted = 0
            GROUP BY u.department
        ''')
        
        results = cursor.fetchall()
        
        # Verificar resultados
        dept_stats = {dept: {'count': count, 'total': total} for dept, count, total in results}
        
        self.assertIn('Qualidade', dept_stats)
        self.assertEqual(dept_stats['Qualidade']['count'], 2)  # 2 RNCs
        self.assertEqual(dept_stats['Qualidade']['total'], 550.0)  # 500 + 50
        
        self.assertIn('Produção', dept_stats)
        self.assertEqual(dept_stats['Produção']['count'], 1)
        self.assertEqual(dept_stats['Produção']['total'], 200.0)
        
        conn.close()


def run_tests():
    """Executa todos os testes"""
    # Configurar logging para testes
    logging.basicConfig(level=logging.WARNING)
    
    # Descobrir e executar todos os testes
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Retornar resultado
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    
    if success:
        print("\n✅ TODOS OS TESTES PASSARAM!")
        sys.exit(0)
    else:
        print("\n❌ ALGUNS TESTES FALHARAM!")
        sys.exit(1)
