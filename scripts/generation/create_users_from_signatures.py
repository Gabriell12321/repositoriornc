#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import re
from collections import Counter

def create_users_from_signatures():
    try:
        conn = sqlite3.connect('ippel_system.db')
        cursor = conn.cursor()
        
        print("=== CRIANDO USUÁRIOS BASEADOS NAS ASSINATURAS ===")
        
        # Coletar todos os nomes únicos das assinaturas
        all_names = set()
        
        # Buscar nomes de inspeção
        cursor.execute('''
            SELECT DISTINCT signature_inspection_name
            FROM rncs 
            WHERE signature_inspection_name IS NOT NULL 
              AND signature_inspection_name != ''
              AND TRIM(signature_inspection_name) != ''
        ''')
        for row in cursor.fetchall():
            name = row[0].strip()
            if name and len(name) > 2:  # Filtrar nomes muito curtos
                all_names.add(name)
        
        # Buscar nomes de engenharia
        cursor.execute('''
            SELECT DISTINCT signature_engineering_name
            FROM rncs 
            WHERE signature_engineering_name IS NOT NULL 
              AND signature_engineering_name != ''
              AND TRIM(signature_engineering_name) != ''
        ''')
        for row in cursor.fetchall():
            name = row[0].strip()
            if name and len(name) > 2:  # Filtrar nomes muito curtos
                all_names.add(name)
        
        # Buscar nomes de inspeção2
        cursor.execute('''
            SELECT DISTINCT signature_inspection2_name
            FROM rncs 
            WHERE signature_inspection2_name IS NOT NULL 
              AND signature_inspection2_name != ''
              AND TRIM(signature_inspection2_name) != ''
        ''')
        for row in cursor.fetchall():
            name = row[0].strip()
            if name and len(name) > 2:  # Filtrar nomes muito curtos
                all_names.add(name)
        
        # Filtrar nomes que parecem ser empresas ou códigos em vez de pessoas
        person_names = []
        company_keywords = ['ltda', 'me', 'eireli', 'sa', 'indústria', 'industrial', 'metalúrgica', 'engenharia']
        
        for name in all_names:
            name_lower = name.lower()
            # Filtrar empresas e códigos
            if any(keyword in name_lower for keyword in company_keywords):
                continue
            # Filtrar códigos alfanuméricos curtos
            if len(name) < 4 or (len(name) < 6 and not ' ' in name):
                continue
            # Aceitar nomes que parecem de pessoas
            person_names.append(name)
        
        print(f"Encontrados {len(person_names)} nomes de pessoas válidos")
        
        # Mapear departamentos baseado no contexto
        department_mapping = {
            'inspeção': 'Qualidade',
            'qualidade': 'Qualidade',
            'engenharia': 'Engenharia',
            'produção': 'Produção',
            'manutenção': 'Manutenção',
            'default': 'Produção'  # departamento padrão
        }
        
        created_users = []
        user_id_counter = 10  # Começar do ID 10
        
        # Criar usuários para cada nome encontrado
        for name in sorted(person_names):
            # Determinar departamento baseado no contexto onde o nome mais aparece
            cursor.execute('''
                SELECT 
                    SUM(CASE WHEN signature_inspection_name = ? THEN 1 ELSE 0 END) as inspection_count,
                    SUM(CASE WHEN signature_engineering_name = ? THEN 1 ELSE 0 END) as engineering_count,
                    SUM(CASE WHEN signature_inspection2_name = ? THEN 1 ELSE 0 END) as inspection2_count
                FROM rncs
            ''', (name, name, name))
            
            result = cursor.fetchone()
            inspection_count, engineering_count, inspection2_count = result
            
            # Determinar departamento baseado em onde mais aparece
            if engineering_count > inspection_count and engineering_count > inspection2_count:
                department = 'Engenharia'
            elif inspection_count > 0 or inspection2_count > 0:
                department = 'Qualidade'
            else:
                department = 'Produção'
            
            # Criar email baseado no nome
            email_name = re.sub(r'[^a-zA-Z\s]', '', name.lower())  # Remover caracteres especiais
            email_name = re.sub(r'\s+', '.', email_name.strip())  # Substituir espaços por pontos
            email = f"{email_name}@ippel.com.br"
            
            # Inserir usuário
            cursor.execute('''
                INSERT INTO users (id, name, email, password_hash, department, role, permissions, created_at, is_active)
                VALUES (?, ?, ?, 'temp_hash', ?, 'user', '["create_rnc"]', datetime('now'), 1)
            ''', (user_id_counter, name, email, department))
            
            created_users.append({
                'id': user_id_counter,
                'name': name,
                'email': email,
                'department': department,
                'inspection_count': inspection_count,
                'engineering_count': engineering_count,
                'inspection2_count': inspection2_count
            })
            
            user_id_counter += 1
        
        conn.commit()
        
        print(f"\n✅ Criados {len(created_users)} usuários!")
        print("\nPrimeiros 20 usuários criados:")
        for i, user in enumerate(created_users[:20]):
            print(f"ID {user['id']}: {user['name']} - {user['department']} (I:{user['inspection_count']}, E:{user['engineering_count']}, I2:{user['inspection2_count']})")
        
        # Agora atribuir RNCs baseado nas assinaturas
        print(f"\n=== ATRIBUINDO RNCs BASEADO NAS ASSINATURAS ===")
        
        updates_made = 0
        
        for user in created_users:
            name = user['name']
            user_id = user['id']
            
            # Atribuir RNCs onde esta pessoa assinou como inspeção
            cursor.execute('''
                UPDATE rncs 
                SET user_id = ? 
                WHERE signature_inspection_name = ?
            ''', (user_id, name))
            inspection_updates = cursor.execute('SELECT changes()').fetchone()[0]
            
            # Atribuir RNCs onde esta pessoa assinou como engenharia (se não já atribuída)
            cursor.execute('''
                UPDATE rncs 
                SET user_id = ? 
                WHERE signature_engineering_name = ? AND user_id = 1
            ''', (user_id, name))
            engineering_updates = cursor.execute('SELECT changes()').fetchone()[0]
            
            # Atribuir RNCs onde esta pessoa assinou como inspeção2 (se não já atribuída)
            cursor.execute('''
                UPDATE rncs 
                SET user_id = ? 
                WHERE signature_inspection2_name = ? AND user_id = 1
            ''', (user_id, name))
            inspection2_updates = cursor.execute('SELECT changes()').fetchone()[0]
            
            total_updates = inspection_updates + engineering_updates + inspection2_updates
            updates_made += total_updates
            
            if total_updates > 0:
                print(f"{user['name']}: {total_updates} RNCs atribuídas (I:{inspection_updates}, E:{engineering_updates}, I2:{inspection2_updates})")
        
        conn.commit()
        
        # Verificar resultado final
        print(f"\n=== RESULTADO FINAL ===")
        print(f"Total de RNCs reatribuídas: {updates_made}")
        
        cursor.execute('''
            SELECT r.user_id, u.name, u.department, COUNT(*) as total 
            FROM rncs r 
            LEFT JOIN users u ON r.user_id = u.id 
            GROUP BY r.user_id, u.name, u.department 
            HAVING total > 0
            ORDER BY total DESC
            LIMIT 20
        ''')
        top_users = cursor.fetchall()
        
        print("\nTop 20 usuários com mais RNCs:")
        for user_id, name, department, count in top_users:
            user_info = f"{name} ({department})" if name else f"ID {user_id}"
            print(f"User ID {user_id} - {user_info}: {count} RNCs")
        
        conn.close()
        print("\n✅ Usuários criados e RNCs atribuídas com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro durante o processo: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    create_users_from_signatures()
