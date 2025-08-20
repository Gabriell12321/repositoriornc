#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3

def create_users_from_sectors():
    try:
        conn = sqlite3.connect('ippel_system.db')
        cursor = conn.cursor()
        
        print("=== ANALISANDO TODOS OS SETORES DISPONÍVEIS ===")
        
        # Buscar todos os setores
        cursor.execute('SELECT * FROM sectors ORDER BY id')
        sectors = cursor.fetchall()
        
        print(f"Total de setores encontrados: {len(sectors)}")
        print("\nSetores disponíveis:")
        for sector in sectors:
            print(f"  ID {sector[0]}: {sector[1]}")
        
        # Mapear setores para departamentos/funções
        sector_to_department = {
            'engenharia': 'Engenharia',
            'Cliente': 'Comercial',
            'Montagem': 'Produção',
            'Corte': 'Produção', 
            'Conformação': 'Produção',
            'Caldeiraria de Carbono': 'Produção',
            'Caldeiraria de Inox': 'Produção',
            'Jato de Granalha': 'Produção',
            'Pintura': 'Produção',
            'Usin. Cilíndrica Convencional': 'Produção',
            'Usin. Cilíndrica CNC': 'Produção',
            'Usin. Mandriladora': 'Produção',
            'Usin. Fresa Convencional': 'Produção',
            'Usin. Fresa CNC': 'Produção',
            'Usin. Torno Convencional': 'Produção',
            'Usin. Torno CNC': 'Produção',
            'Usin. Furadeira': 'Produção',
            'Medição': 'Qualidade',
            'Terceiros': 'Terceiros',
            'Compras': 'Compras',
            'Comercial': 'Comercial',
            'PCP': 'PCP',
            'Expedição': 'Logística',
            'Qualidade': 'Qualidade',
            'Transporte': 'Logística',
            'Não definido': 'Geral'
        }
        
        print(f"\n=== CRIANDO USUÁRIOS BASEADOS NOS SETORES ===")
        
        user_id = 100  # Começar do ID 100 para não conflitar com usuários existentes
        created_users = []
        
        for sector in sectors:
            sector_id, sector_name = sector[0], sector[1]
            
            # Determinar departamento
            department = sector_to_department.get(sector_name, 'Produção')
            
            # Criar nome do usuário baseado no setor
            if sector_name == 'engenharia':
                user_name = f"Responsável Engenharia"
            elif 'Usin.' in sector_name:
                # Para usinagem, criar nome mais específico
                machine_type = sector_name.replace('Usin. ', '').replace(' Convencional', '').replace(' CNC', '')
                user_name = f"Operador {machine_type}"
            elif 'Caldeiraria' in sector_name:
                material = sector_name.replace('Caldeiraria de ', '')
                user_name = f"Caldeireiro {material}"
            else:
                user_name = f"Responsável {sector_name}"
            
            # Criar email baseado no setor
            email_name = sector_name.lower().replace(' ', '.').replace('ã', 'a').replace('ç', 'c')
            email_name = ''.join(c for c in email_name if c.isalnum() or c == '.')
            email = f"{email_name}@ippel.com.br"
            
            try:
                cursor.execute('''
                    INSERT INTO users (id, name, email, password_hash, department, role, permissions, created_at, is_active)
                    VALUES (?, ?, ?, 'pbkdf2:sha256:600000$temp$hash', ?, 'user', '["create_rnc"]', datetime('now'), 1)
                ''', (user_id, user_name, email, department))
                
                created_users.append({
                    'id': user_id,
                    'name': user_name,
                    'sector': sector_name,
                    'sector_id': sector_id,
                    'department': department,
                    'email': email
                })
                
                print(f"Criado usuário ID {user_id}: {user_name} - {department} (Setor: {sector_name})")
                user_id += 1
                
            except sqlite3.IntegrityError as e:
                print(f"Erro ao criar usuário para setor {sector_name}: {e}")
        
        conn.commit()
        
        print(f"\n=== ANÁLISE PARA ATRIBUIÇÃO DE RNCs ===")
        
        # Agora vamos analisar as RNCs para tentar identificar setores baseado em equipamentos
        equipment_to_sector = {
            # Equipamentos de produção
            'Mesa plana': 'Produção',
            'Rebobinadeira': 'Produção', 
            'Enroladeira': 'Produção',
            'Drum dryer': 'Produção',
            'Desenroladeira': 'Produção',
            'Setor prensas': 'Produção',
            'Setor secagem': 'Produção',
            'Cilindro secador': 'Produção',
            'Desagregador': 'Produção',
            'Engrossador': 'Produção',
            'Crescent former': 'Produção',
            'Size press': 'Produção',
            'Depurador vertical': 'Produção',
            
            # Equipamentos de usinagem
            'Torno': 'Usin. Torno Convencional',
            'Fresa': 'Usin. Fresa Convencional',
            'Furadeira': 'Usin. Furadeira',
            'Mandriladora': 'Usin. Mandriladora',
            
            # Equipamentos específicos
            'Caldeiraria': 'Caldeiraria de Carbono',
            'Pintura': 'Pintura',
            'Jato': 'Jato de Granalha',
            'Montagem': 'Montagem'
        }
        
        print(f"Mapeamento de equipamentos para setores criado")
        
        # Atribuir algumas RNCs baseado em equipamentos (como exemplo)
        assignments_made = 0
        
        for user in created_users[:10]:  # Fazer apenas alguns como exemplo
            sector_name = user['sector']
            user_id = user['id']
            
            # Buscar palavras-chave relacionadas ao setor
            keywords = [sector_name.lower()]
            if 'caldeiraria' in sector_name.lower():
                keywords.extend(['caldeiraria', 'solda', 'soldagem'])
            elif 'usin' in sector_name.lower():
                keywords.extend(['usinagem', 'torno', 'fresa'])
            elif 'pintura' in sector_name.lower():
                keywords.extend(['pintura', 'tinta'])
            elif 'montagem' in sector_name.lower():
                keywords.extend(['montagem', 'montador'])
            
            # Atribuir RNCs que mencionam essas palavras-chave
            for keyword in keywords:
                cursor.execute('''
                    UPDATE rncs 
                    SET user_id = ? 
                    WHERE (LOWER(equipment) LIKE ? OR LOWER(description) LIKE ?) 
                      AND user_id = 1
                    LIMIT 10
                ''', (user_id, f'%{keyword}%', f'%{keyword}%'))
                
                updates = cursor.execute('SELECT changes()').fetchone()[0]
                assignments_made += updates
                
                if updates > 0:
                    print(f"Atribuídas {updates} RNCs para {user['name']} (palavra-chave: {keyword})")
        
        conn.commit()
        
        print(f"\n=== RESULTADO FINAL ===")
        print(f"Usuários criados baseados em setores: {len(created_users)}")
        print(f"RNCs reatribuídas (exemplo): {assignments_made}")
        
        # Verificar distribuição atual
        cursor.execute('''
            SELECT r.user_id, u.name, u.department, COUNT(*) as total 
            FROM rncs r 
            LEFT JOIN users u ON r.user_id = u.id 
            GROUP BY r.user_id, u.name, u.department 
            HAVING total > 0
            ORDER BY total DESC
            LIMIT 20
        ''')
        
        print("\nTop 20 usuários com mais RNCs após criação dos setores:")
        for user_id, name, department, count in cursor.fetchall():
            user_info = f"{name} ({department})" if name else f"ID {user_id}"
            print(f"ID {user_id}: {user_info} - {count} RNCs")
        
        # Mostrar usuários criados
        print(f"\n=== USUÁRIOS CRIADOS POR SETOR ===")
        cursor.execute('''
            SELECT id, name, department 
            FROM users 
            WHERE id >= 100
            ORDER BY id
        ''')
        sector_users = cursor.fetchall()
        
        for user_id, name, department in sector_users:
            print(f"ID {user_id}: {name} - {department}")
        
        conn.close()
        print("\n✅ Usuários de setores criados com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro durante o processo: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    create_users_from_sectors()
