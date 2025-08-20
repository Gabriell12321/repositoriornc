#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
from flask import Flask, render_template
import os

app = Flask(__name__)

DB_PATH = 'ippel_system.db'

def test_print_rnc():
    """Testar função de impressão"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Buscar primeiro RNC
        cursor.execute('''
            SELECT r.*, u.name as user_name, au.name as assigned_user_name
            FROM rncs r 
            LEFT JOIN users u ON r.user_id = u.id 
            LEFT JOIN users au ON r.assigned_user_id = au.id
            LIMIT 1
        ''')
        
        rnc_data = cursor.fetchone()
        conn.close()
        
        if not rnc_data:
            print("❌ Nenhum RNC encontrado no banco de dados")
            return
        
        print(f"✅ RNC encontrado: {rnc_data[1]}")  # rnc_number
        
        # Converter para dicionário
        rnc_dict = {
            'id': rnc_data[0],
            'rnc_number': rnc_data[1],
            'title': rnc_data[2],
            'description': rnc_data[3],
            'equipment': rnc_data[4],
            'client': rnc_data[5],
            'priority': rnc_data[6],
            'status': rnc_data[7],
            'user_id': rnc_data[8],
            'assigned_user_id': rnc_data[9],
            'is_deleted': rnc_data[10] if len(rnc_data) > 10 else False,
            'deleted_at': rnc_data[11] if len(rnc_data) > 11 else None,
            'finalized_at': rnc_data[12] if len(rnc_data) > 12 else None,
            'created_at': rnc_data[13] if len(rnc_data) > 13 else None,
            'updated_at': rnc_data[14] if len(rnc_data) > 14 else None,
            'user_name': rnc_data[15] if len(rnc_data) > 15 else None,
            'assigned_user_name': rnc_data[16] if len(rnc_data) > 16 else None,
            # Campos de assinatura (se existirem)
            'signature_inspection_name': '',
            'signature_engineering_name': '',
            'signature_inspection2_name': '',
            # Campos de data de assinatura (se existirem)
            'signature_inspection_date': '',
            'signature_engineering_date': '',
            'signature_inspection2_date': '',
            # Campos de disposição (se existirem)
            'disposition_usar': False,
            'disposition_retrabalhar': False,
            'disposition_rejeitar': False,
            'disposition_sucata': False,
            'disposition_devolver_estoque': False,
            'disposition_devolver_fornecedor': False,
            # Campos de inspeção (se existirem)
            'inspection_aprovado': False,
            'inspection_reprovado': False,
            'inspection_ver_rnc': ''
        }
        
        print("✅ Dicionário RNC criado com sucesso")
        print(f"   Título: {rnc_dict['title']}")
        print(f"   Número: {rnc_dict['rnc_number']}")
        print(f"   Status: {rnc_dict['status']}")
        
        # Testar renderização do template
        with app.app_context():
            try:
                html = render_template('view_rnc_print.html', rnc=rnc_dict)
                print("✅ Template renderizado com sucesso")
                
                # Salvar HTML para verificação
                with open('test_print_output.html', 'w', encoding='utf-8') as f:
                    f.write(html)
                print("✅ HTML salvo em 'test_print_output.html'")
                
            except Exception as e:
                print(f"❌ Erro ao renderizar template: {e}")
                return
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")

if __name__ == '__main__':
    test_print_rnc() 