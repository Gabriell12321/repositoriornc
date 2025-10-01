#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3

def create_signature_users():
    try:
        conn = sqlite3.connect('ippel_system.db')
        cursor = conn.cursor()
        
        print("=== CRIANDO USUÁRIOS BASEADOS NAS ASSINATURAS MAIS COMUNS ===")
        
        # Buscar as 20 assinaturas mais comuns de inspeção
        cursor.execute('''
            SELECT signature_inspection_name, COUNT(*) as count
            FROM rncs 
            WHERE signature_inspection_name IS NOT NULL 
              AND signature_inspection_name != ''
              AND LENGTH(TRIM(signature_inspection_name)) > 3
            GROUP BY signature_inspection_name
            ORDER BY count DESC
            LIMIT 20
        ''')
        
        inspection_signatures = cursor.fetchall()
        print("Top 20 assinaturas de inspeção:")
        for name, count in inspection_signatures:
            print(f"  {name}: {count} RNCs")
        
        # Buscar as 20 assinaturas mais comuns de engenharia
        cursor.execute('''
            SELECT signature_engineering_name, COUNT(*) as count
            FROM rncs 
            WHERE signature_engineering_name IS NOT NULL 
              AND signature_engineering_name != ''
              AND LENGTH(TRIM(signature_engineering_name)) > 3
            GROUP BY signature_engineering_name
            ORDER BY count DESC
            LIMIT 20
        ''')
        
        engineering_signatures = cursor.fetchall()
        print("\nTop 20 assinaturas de engenharia:")
        for name, count in engineering_signatures:
            print(f"  {name}: {count} RNCs")
        
        # Coletar nomes únicos das top assinaturas
        all_top_names = set()
        
        # Adicionar top 10 de cada categoria
        for name, count in inspection_signatures[:10]:
            if len(name.strip()) > 3 and not any(char.isdigit() for char in name[:3]):
                all_top_names.add((name.strip(), 'Qualidade', count))
        
        for name, count in engineering_signatures[:10]:
            if len(name.strip()) > 3 and not any(char.isdigit() for char in name[:3]):
                all_top_names.add((name.strip(), 'Engenharia', count))
        
        print(f"\n=== CRIANDO USUÁRIOS PARA OS {len(all_top_names)} NOMES PRINCIPAIS ===")
        
        user_id = 10  # Começar do ID 10
        created_users = []
        
        for name, department, rnc_count in sorted(all_top_names, key=lambda x: x[2], reverse=True):
            # Criar email baseado no nome
            email_name = name.lower().replace(' ', '.').replace('ã', 'a').replace('ç', 'c').replace('ó', 'o')
            email_name = ''.join(c for c in email_name if c.isalnum() or c == '.')
            email = f"{email_name}@ippel.com.br"
            
            try:
                cursor.execute('''
                    INSERT INTO users (id, name, email, password_hash, department, role, permissions, created_at, is_active)
                    VALUES (?, ?, ?, 'pbkdf2:sha256:600000$temp$hash', ?, 'user', '["create_rnc"]', datetime('now'), 1)
                ''', (user_id, name, email, department))
                
                created_users.append({'id': user_id, 'name': name, 'department': department, 'rnc_count': rnc_count})
                print(f"Criado usuário ID {user_id}: {name} - {department} ({rnc_count} RNCs potenciais)")
                user_id += 1
                
            except sqlite3.IntegrityError as e:
                print(f"Erro ao criar usuário {name}: {e}")
        
        conn.commit()
        
        print(f"\n=== ATRIBUINDO RNCs BASEADO NAS ASSINATURAS ===")
        
        total_reassigned = 0
        
        # Atribuir RNCs baseado nas assinaturas
        for user in created_users:
            name = user['name']
            user_id = user['id']
            
            # Atribuir baseado na assinatura de inspeção
            cursor.execute('''
                UPDATE rncs 
                SET user_id = ? 
                WHERE signature_inspection_name = ? AND user_id = 1
            ''', (user_id, name))
            
            inspection_updates = cursor.execute('SELECT changes()').fetchone()[0]
            
            # Atribuir baseado na assinatura de engenharia
            cursor.execute('''
                UPDATE rncs 
                SET user_id = ? 
                WHERE signature_engineering_name = ? AND user_id = 1
            ''', (user_id, name))
            
            engineering_updates = cursor.execute('SELECT changes()').fetchone()[0]
            
            total_updates = inspection_updates + engineering_updates
            total_reassigned += total_updates
            
            if total_updates > 0:
                print(f"{name}: {total_updates} RNCs atribuídas (I:{inspection_updates}, E:{engineering_updates})")
        
        conn.commit()
        
        print(f"\n=== RESULTADO FINAL ===")
        print(f"Usuários criados: {len(created_users)}")
        print(f"RNCs reatribuídas: {total_reassigned}")
        
        # Verificar distribuição final
        cursor.execute('''
            SELECT r.user_id, u.name, u.department, COUNT(*) as total 
            FROM rncs r 
            LEFT JOIN users u ON r.user_id = u.id 
            GROUP BY r.user_id, u.name, u.department 
            ORDER BY total DESC
            LIMIT 15
        ''')
        
        print("\nDistribuição final das RNCs:")
        for user_id, name, department, count in cursor.fetchall():
            user_info = f"{name} ({department})" if name else f"ID {user_id}"
            print(f"ID {user_id}: {user_info} - {count} RNCs")
        
        conn.close()
        print("\n✅ Processo concluído!")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    create_signature_users()
