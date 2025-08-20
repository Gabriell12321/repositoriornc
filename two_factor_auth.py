#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔐 IPPEL Two-Factor Authentication System
Sistema de autenticação de dois fatores usando TOTP
"""

import qrcode
import io
import base64
import pyotp
import sqlite3
import json
from datetime import datetime, timedelta
from flask import jsonify, request, session
from typing import Dict, Any, Optional

class TwoFactorAuth:
    """Sistema de autenticação de dois fatores"""
    
    def __init__(self, db_path='ippel_system.db'):
        self.db_path = db_path
        self.setup_2fa_tables()
    
    def setup_2fa_tables(self):
        """Criar tabelas para 2FA"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Tabela de configuração 2FA por usuário
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_2fa (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER UNIQUE NOT NULL,
                    secret_key TEXT NOT NULL,
                    is_enabled BOOLEAN DEFAULT 0,
                    backup_codes TEXT,  -- JSON array de códigos de backup
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_used TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # Tabela de códigos de recuperação usados
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS used_backup_codes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    code_hash TEXT NOT NULL,
                    used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # Adicionar coluna 2FA na tabela users se não existir
            try:
                cursor.execute('ALTER TABLE users ADD COLUMN two_factor_enabled BOOLEAN DEFAULT 0')
            except sqlite3.OperationalError:
                pass  # Coluna já existe
            
            conn.commit()
    
    def generate_secret_key(self, user_email: str) -> str:
        """Gerar chave secreta para o usuário"""
        return pyotp.random_base32()
    
    def generate_qr_code(self, user_email: str, secret_key: str) -> str:
        """Gerar QR code para configuração do 2FA"""
        # Nome do serviço que aparecerá no app
        service_name = "IPPEL RNC System"
        
        # Criar URI TOTP
        totp_uri = pyotp.totp.TOTP(secret_key).provisioning_uri(
            name=user_email,
            issuer_name=service_name
        )
        
        # Gerar QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(totp_uri)
        qr.make(fit=True)
        
        # Converter para imagem
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Converter para base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        return f"data:image/png;base64,{img_base64}"
    
    def generate_backup_codes(self, count: int = 10) -> list:
        """Gerar códigos de backup"""
        import secrets
        import string
        
        codes = []
        for _ in range(count):
            # Gerar código de 8 caracteres
            code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) 
                          for _ in range(8))
            # Formatear como XXXX-XXXX
            formatted_code = f"{code[:4]}-{code[4:]}"
            codes.append(formatted_code)
        
        return codes
    
    def setup_2fa_for_user(self, user_id: int, user_email: str) -> Dict[str, Any]:
        """Configurar 2FA para usuário"""
        try:
            # Gerar chave secreta
            secret_key = self.generate_secret_key(user_email)
            
            # Gerar códigos de backup
            backup_codes = self.generate_backup_codes()
            
            # Salvar no banco (ainda não habilitado)
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO user_2fa (user_id, secret_key, backup_codes)
                    VALUES (?, ?, ?)
                ''', (user_id, secret_key, json.dumps(backup_codes)))
                conn.commit()
            
            # Gerar QR code
            qr_code = self.generate_qr_code(user_email, secret_key)
            
            return {
                'success': True,
                'secret_key': secret_key,
                'qr_code': qr_code,
                'backup_codes': backup_codes,
                'message': 'Configure seu app autenticador escaneando o QR code'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Erro ao configurar 2FA: {str(e)}'
            }
    
    def verify_and_enable_2fa(self, user_id: int, token: str) -> Dict[str, Any]:
        """Verificar token e habilitar 2FA"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT secret_key FROM user_2fa WHERE user_id = ?
                ''', (user_id,))
                
                result = cursor.fetchone()
                if not result:
                    return {'success': False, 'error': '2FA não configurado'}
                
                secret_key = result[0]
                
                # Verificar token TOTP
                totp = pyotp.TOTP(secret_key)
                if not totp.verify(token, valid_window=1):
                    return {'success': False, 'error': 'Token inválido'}
                
                # Habilitar 2FA
                cursor.execute('''
                    UPDATE user_2fa SET is_enabled = 1, last_used = CURRENT_TIMESTAMP 
                    WHERE user_id = ?
                ''', (user_id,))
                
                cursor.execute('''
                    UPDATE users SET two_factor_enabled = 1 WHERE id = ?
                ''', (user_id,))
                
                conn.commit()
                
                return {
                    'success': True,
                    'message': '2FA habilitado com sucesso!'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Erro ao habilitar 2FA: {str(e)}'
            }
    
    def verify_2fa_token(self, user_id: int, token: str) -> Dict[str, Any]:
        """Verificar token 2FA durante login"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT secret_key, backup_codes FROM user_2fa 
                    WHERE user_id = ? AND is_enabled = 1
                ''', (user_id,))
                
                result = cursor.fetchone()
                if not result:
                    return {'success': False, 'error': '2FA não configurado'}
                
                secret_key, backup_codes_json = result
                
                # Primeiro, tentar verificar como token TOTP
                totp = pyotp.TOTP(secret_key)
                if totp.verify(token, valid_window=1):
                    # Atualizar último uso
                    cursor.execute('''
                        UPDATE user_2fa SET last_used = CURRENT_TIMESTAMP 
                        WHERE user_id = ?
                    ''', (user_id,))
                    conn.commit()
                    
                    return {'success': True, 'method': 'totp'}
                
                # Se não funcionar, tentar códigos de backup
                if backup_codes_json:
                    backup_codes = json.loads(backup_codes_json)
                    
                    # Verificar se o código está na lista e não foi usado
                    if token.upper() in [code.upper() for code in backup_codes]:
                        # Verificar se já foi usado
                        import hashlib
                        code_hash = hashlib.sha256(token.upper().encode()).hexdigest()
                        
                        cursor.execute('''
                            SELECT id FROM used_backup_codes 
                            WHERE user_id = ? AND code_hash = ?
                        ''', (user_id, code_hash))
                        
                        if cursor.fetchone():
                            return {'success': False, 'error': 'Código de backup já utilizado'}
                        
                        # Marcar código como usado
                        cursor.execute('''
                            INSERT INTO used_backup_codes (user_id, code_hash)
                            VALUES (?, ?)
                        ''', (user_id, code_hash))
                        
                        # Remover código da lista
                        backup_codes = [code for code in backup_codes 
                                      if code.upper() != token.upper()]
                        
                        cursor.execute('''
                            UPDATE user_2fa SET backup_codes = ?, last_used = CURRENT_TIMESTAMP 
                            WHERE user_id = ?
                        ''', (json.dumps(backup_codes), user_id))
                        
                        conn.commit()
                        
                        return {
                            'success': True, 
                            'method': 'backup_code',
                            'remaining_codes': len(backup_codes)
                        }
                
                return {'success': False, 'error': 'Token inválido'}
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Erro ao verificar token: {str(e)}'
            }
    
    def disable_2fa(self, user_id: int) -> Dict[str, Any]:
        """Desabilitar 2FA para usuário"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    UPDATE user_2fa SET is_enabled = 0 WHERE user_id = ?
                ''', (user_id,))
                
                cursor.execute('''
                    UPDATE users SET two_factor_enabled = 0 WHERE id = ?
                ''', (user_id,))
                
                conn.commit()
                
                return {
                    'success': True,
                    'message': '2FA desabilitado com sucesso'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Erro ao desabilitar 2FA: {str(e)}'
            }
    
    def regenerate_backup_codes(self, user_id: int) -> Dict[str, Any]:
        """Regenerar códigos de backup"""
        try:
            # Gerar novos códigos
            new_codes = self.generate_backup_codes()
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Atualizar códigos no banco
                cursor.execute('''
                    UPDATE user_2fa SET backup_codes = ? WHERE user_id = ?
                ''', (json.dumps(new_codes), user_id))
                
                # Limpar códigos usados anteriores
                cursor.execute('''
                    DELETE FROM used_backup_codes WHERE user_id = ?
                ''', (user_id,))
                
                conn.commit()
                
                return {
                    'success': True,
                    'backup_codes': new_codes,
                    'message': 'Códigos de backup regenerados. Guarde-os em local seguro!'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Erro ao regenerar códigos: {str(e)}'
            }
    
    def get_2fa_status(self, user_id: int) -> Dict[str, Any]:
        """Obter status do 2FA para usuário"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT is_enabled, backup_codes, last_used FROM user_2fa 
                    WHERE user_id = ?
                ''', (user_id,))
                
                result = cursor.fetchone()
                if not result:
                    return {
                        'enabled': False,
                        'configured': False,
                        'backup_codes_count': 0
                    }
                
                is_enabled, backup_codes_json, last_used = result
                backup_codes = json.loads(backup_codes_json) if backup_codes_json else []
                
                # Contar códigos de backup usados
                cursor.execute('''
                    SELECT COUNT(*) FROM used_backup_codes WHERE user_id = ?
                ''', (user_id,))
                used_codes = cursor.fetchone()[0]
                
                return {
                    'enabled': bool(is_enabled),
                    'configured': True,
                    'backup_codes_count': len(backup_codes),
                    'used_backup_codes': used_codes,
                    'last_used': last_used
                }
                
        except Exception as e:
            return {
                'enabled': False,
                'configured': False,
                'error': str(e)
            }

# Decorador para exigir 2FA
def require_2fa(f):
    """Decorador para exigir 2FA em endpoints sensíveis"""
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Autenticação necessária'}), 401
        
        user_id = session['user_id']
        
        # Verificar se usuário tem 2FA habilitado
        tfa = TwoFactorAuth()
        status = tfa.get_2fa_status(user_id)
        
        if status['enabled'] and not session.get('2fa_verified', False):
            return jsonify({
                'error': 'Verificação 2FA necessária',
                'requires_2fa': True
            }), 403
        
        return f(*args, **kwargs)
    return decorated_function
