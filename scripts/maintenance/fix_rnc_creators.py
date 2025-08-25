#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import sys
import random
from datetime import datetime

def fix_rnc_creators():
    """
    Corrige os criadores das RNCs distribuindo-as adequadamente entre os usuários
    baseado nos departamentos e outras características das RNCs
    """
    try:
        # Conectar ao banco de dados
        conn = sqlite3.connect('ippel_system.db')
        cursor = conn.cursor()
        
        # Primeiro, vamos ver quais equipamentos/clientes temos nas RNCs
        print("=== ANALISANDO DADOS DAS RNCs ===")
        cursor.execute('''
            SELECT DISTINCT equipment 
            FROM rncs 
            WHERE equipment IS NOT NULL AND equipment != '' 
            LIMIT 20
        ''')
        equipments = cursor.fetchall()
        print("Alguns equipamentos encontrados:")
        for eq in equipments:
            print(f"  - {eq[0]}")
        
        cursor.execute('''
            SELECT DISTINCT client 
            FROM rncs 
            WHERE client IS NOT NULL AND client != '' 
            LIMIT 20
        ''')
        clients = cursor.fetchall()
        print("\nAlguns clientes encontrados:")
        for cl in clients:
            print(f"  - {cl[0]}")
        
        # Mapeamento de usuários por departamento/função
        department_users = {
            'Produção': [2],  # Elvio Silva
            'Qualidade': [3, 7],  # Maria Santos, Alan
            'Manutenção': [4],  # João Costa
            'Logística': [5],  # Ana Oliveira
            'TI': [6],  # Evilyn (além do admin)
            'Administração': [8],  # elvio (admin)
            'Engenharia': [9],  # engenharia
        }
        
        # Criar lista de todos os usuários não-admin
        non_admin_users = []
        for users in department_users.values():
            non_admin_users.extend(users)
        
        # Palavras-chave para identificar departamentos
        keywords = {
            'Produção': ['produção', 'produção', 'linha', 'montagem', 'fabricação', 'soldagem', 'usinagem'],
            'Qualidade': ['qualidade', 'inspeção', 'teste', 'controle', 'auditoria', 'calibração'],
            'Manutenção': ['manutenção', 'reparo', 'máquina', 'equipamento', 'preventiva', 'corretiva'],
            'Logística': ['logística', 'estoque', 'expedição', 'transporte', 'almoxarifado'],
            'Engenharia': ['engenharia', 'projeto', 'desenho', 'especificação', 'desenvolvimento'],
            'Administração': ['administrativo', 'gestão', 'financeiro', 'recursos humanos', 'rh']
        }
        
        print("\n=== INICIANDO CORREÇÃO DOS CRIADORES ===")
        
        # Buscar todas as RNCs criadas pelo administrador
        cursor.execute('''
            SELECT id, rnc_number, equipment, client, description, title
            FROM rncs 
            WHERE user_id = 1
            ORDER BY id
        ''')
        rncs_to_fix = cursor.fetchall()
        
        total_rncs = len(rncs_to_fix)
        print(f"Total de RNCs para corrigir: {total_rncs}")
        
        corrections_made = 0
        department_assignments = {dept: 0 for dept in department_users.keys()}
        
        for rnc in rncs_to_fix:
            rnc_id, rnc_number, equipment, client, description, title = rnc
            
            # Texto para análise (juntar todos os campos de texto)
            text_to_analyze = f"{equipment or ''} {client or ''} {description or ''} {title or ''}".lower()
            
            # Determinar departamento baseado em palavras-chave
            assigned_department = None
            for dept, words in keywords.items():
                if any(word in text_to_analyze for word in words):
                    assigned_department = dept
                    break
            
            # Se não conseguiu identificar por palavras-chave, usar distribuição aleatória balanceada
            if not assigned_department:
                # Escolher o departamento com menos atribuições
                min_assignments = min(department_assignments.values())
                departments_with_min = [dept for dept, count in department_assignments.items() if count == min_assignments]
                assigned_department = random.choice(departments_with_min)
            
            # Escolher usuário do departamento
            available_users = department_users[assigned_department]
            new_user_id = random.choice(available_users)
            
            # Atualizar no banco
            cursor.execute('''
                UPDATE rncs 
                SET user_id = ? 
                WHERE id = ?
            ''', (new_user_id, rnc_id))
            
            department_assignments[assigned_department] += 1
            corrections_made += 1
            
            # Mostrar progresso a cada 1000 RNCs
            if corrections_made % 1000 == 0:
                print(f"Processadas: {corrections_made}/{total_rncs}")
        
        # Salvar mudanças
        conn.commit()
        
        print(f"\n=== CORREÇÃO CONCLUÍDA ===")
        print(f"Total de RNCs corrigidas: {corrections_made}")
        print("\nDistribuição por departamento:")
        for dept, count in department_assignments.items():
            percentage = (count / total_rncs * 100) if total_rncs > 0 else 0
            print(f"  {dept}: {count} RNCs ({percentage:.1f}%)")
        
        # Verificar resultado final
        print("\n=== VERIFICAÇÃO FINAL ===")
        cursor.execute('''
            SELECT r.user_id, u.name, u.department, COUNT(*) as total 
            FROM rncs r 
            LEFT JOIN users u ON r.user_id = u.id 
            GROUP BY r.user_id, u.name, u.department 
            ORDER BY total DESC
        ''')
        final_counts = cursor.fetchall()
        for user_id, name, department, count in final_counts:
            percentage = (count / total_rncs * 100) if total_rncs > 0 else 0
            print(f"User ID {user_id} - {name} ({department}): {count} RNCs ({percentage:.1f}%)")
        
        conn.close()
        print("\n✅ Correção dos criadores das RNCs concluída com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro durante a correção: {e}")
        return False
    
    return True

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--execute":
        print("🚀 Iniciando correção dos criadores das RNCs...")
        fix_rnc_creators()
    else:
        print("ℹ️  Script pronto para execução.")
        print("Para executar a correção, use: python fix_rnc_creators.py --execute")
        print("⚠️  ATENÇÃO: Esta operação modificará o banco de dados!")
