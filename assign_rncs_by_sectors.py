#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import re

def assign_rncs_by_sectors():
    try:
        conn = sqlite3.connect('ippel_system.db')
        cursor = conn.cursor()
        
        print("=== ATRIBUINDO RNCs BASEADO EM SETORES/EQUIPAMENTOS ===")
        
        # Mapeamento de palavras-chave para usuários de setores
        sector_assignments = {
            # Caldeiraria
            105: ['caldeiraria', 'carbono', 'soldagem', 'solda'],  # Caldeireiro Carbono
            106: ['inox', 'aço inoxidável', 'soldagem inox'],     # Caldeireiro Inox
            
            # Usinagem
            109: ['cilindrica', 'retifica', 'torno cilindrico'],  # Operador Cilíndrica Conv
            110: ['cnc', 'torno cnc', 'cilindrica cnc'],          # Operador Cilíndrica CNC
            111: ['plana', 'fresadora', 'usinagem plana'],        # Usinagem Plana
            112: ['furação', 'furadeira', 'furo'],                # Furação
            
            # Processos específicos
            102: ['montagem', 'montador', 'assembly'],            # Montagem
            103: ['corte', 'plasma', 'oxicorte'],                 # Corte
            104: ['conformação', 'dobra', 'calandragem'],         # Conformação
            107: ['jato', 'granalha', 'jateamento'],              # Jato de Granalha
            108: ['pintura', 'tinta', 'primer'],                  # Pintura
            113: ['secador', 'secagem', 'cilindro secador'],      # Célula de Secadores
            114: ['balanceamento', 'equilibragem'],               # Balanceamento
            115: ['embalagem', 'empacotamento', 'expedição'],     # Embalagem
            
            # Engenharia e Comercial
            100: ['projeto', 'desenho', 'especificação', 'desenvolvimento'], # Engenharia
            101: ['cliente', 'comercial', 'vendas', 'pedido'],    # Cliente/Comercial
        }
        
        # Mapear equipamentos específicos
        equipment_to_user = {
            # Equipamentos de papel (geralmente produção geral)
            'mesa plana': 102,          # Montagem
            'rebobinadeira': 102,       # Montagem  
            'enroladeira': 102,         # Montagem
            'desenroladeira': 102,      # Montagem
            'cilindro secador': 113,    # Célula de Secadores
            'drum dryer': 113,          # Célula de Secadores
            'setor secagem': 113,       # Célula de Secadores
            
            # Equipamentos de corte
            'guilhotina': 103,          # Corte
            'cisalha': 103,             # Corte
            'plasma': 103,              # Corte
            
            # Equipamentos de conformação
            'calandra': 104,            # Conformação
            'dobradeira': 104,          # Conformação
            'prensa': 104,              # Conformação
            
            # Usinagem
            'torno': 109,               # Cilíndrica
            'fresadora': 111,           # Usinagem Plana
            'furadeira': 112,           # Furação
            'mandriladora': 111,        # Usinagem Plana
        }
        
        total_assigned = 0
        assignments_by_user = {}
        
        print("Iniciando atribuições por palavras-chave...")
        
        # Atribuir por palavras-chave
        for user_id, keywords in sector_assignments.items():
            user_assignments = 0
            
            for keyword in keywords:
                # Buscar em equipamentos
                cursor.execute('''
                    SELECT id FROM rncs 
                    WHERE LOWER(equipment) LIKE ? 
                      AND user_id = 1
                ''', (f'%{keyword.lower()}%',))
                
                equipment_rncs = cursor.fetchall()
                
                for rnc_id_tuple in equipment_rncs:
                    rnc_id = rnc_id_tuple[0]
                    cursor.execute('UPDATE rncs SET user_id = ? WHERE id = ?', (user_id, rnc_id))
                    user_assignments += 1
                
                # Buscar em descrições
                cursor.execute('''
                    SELECT id FROM rncs 
                    WHERE LOWER(description) LIKE ? 
                      AND user_id = 1
                ''', (f'%{keyword.lower()}%',))
                
                description_rncs = cursor.fetchall()[:50]  # Limitar para não sobrecarregar
                
                for rnc_id_tuple in description_rncs:
                    rnc_id = rnc_id_tuple[0]
                    cursor.execute('UPDATE rncs SET user_id = ? WHERE id = ?', (user_id, rnc_id))
                    user_assignments += 1
            
            if user_assignments > 0:
                assignments_by_user[user_id] = user_assignments
                total_assigned += user_assignments
                
                # Buscar nome do usuário
                cursor.execute('SELECT name FROM users WHERE id = ?', (user_id,))
                user_name = cursor.fetchone()[0]
                print(f"  {user_name}: {user_assignments} RNCs")
        
        print(f"\nAtribuições por equipamento específico...")
        
        # Atribuir por equipamentos específicos
        for equipment, user_id in equipment_to_user.items():
            cursor.execute('''
                SELECT id FROM rncs 
                WHERE LOWER(equipment) LIKE ? 
                  AND user_id = 1
            ''', (f'%{equipment}%',))
            
            rncs = cursor.fetchall()
            equipment_assignments = 0
            
            for rnc_id_tuple in rncs:
                rnc_id = rnc_id_tuple[0]
                cursor.execute('UPDATE rncs SET user_id = ? WHERE id = ?', (user_id, rnc_id))
                equipment_assignments += 1
            
            if equipment_assignments > 0:
                assignments_by_user[user_id] = assignments_by_user.get(user_id, 0) + equipment_assignments
                total_assigned += equipment_assignments
                
                cursor.execute('SELECT name FROM users WHERE id = ?', (user_id,))
                user_name = cursor.fetchone()[0]
                print(f"  {user_name} ({equipment}): {equipment_assignments} RNCs")
        
        conn.commit()
        
        print(f"\n=== RESULTADO FINAL ===")
        print(f"Total de RNCs reatribuídas: {total_assigned}")
        
        # Verificar distribuição atual
        cursor.execute('''
            SELECT r.user_id, u.name, u.department, COUNT(*) as total 
            FROM rncs r 
            LEFT JOIN users u ON r.user_id = u.id 
            GROUP BY r.user_id, u.name, u.department 
            HAVING total > 5
            ORDER BY total DESC
        ''')
        
        print(f"\nUsuários com mais de 5 RNCs:")
        for user_id, name, department, count in cursor.fetchall():
            user_info = f"{name} ({department})" if name else f"ID {user_id}"
            print(f"ID {user_id}: {user_info} - {count} RNCs")
        
        # Verificar quantas RNCs ainda estão com o administrador
        cursor.execute('SELECT COUNT(*) FROM rncs WHERE user_id = 1')
        admin_rncs = cursor.fetchone()[0]
        print(f"\nRNCs ainda com Administrador: {admin_rncs}")
        
        # Total de RNCs
        cursor.execute('SELECT COUNT(*) FROM rncs')
        total_rncs = cursor.fetchone()[0]
        attributed_percentage = ((total_rncs - admin_rncs) / total_rncs) * 100
        print(f"Total de RNCs: {total_rncs}")
        print(f"Percentual atribuído: {attributed_percentage:.1f}%")
        
        conn.close()
        print("\n✅ Atribuição por setores concluída!")
        
    except Exception as e:
        print(f"❌ Erro durante a atribuição: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    assign_rncs_by_sectors()
