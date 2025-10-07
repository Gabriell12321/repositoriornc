#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar a relação entre grupos de usuários e RNCs
"""

import sqlite3
from datetime import datetime, timedelta

def check_groups_rncs():
    """Verificar relação entre grupos e RNCs"""
    
    print("🔍 Verificando Relação Grupos ↔ RNCs")
    print("="*50)
    
    # Conectar ao banco
    conn = sqlite3.connect('ippel_system.db')
    cursor = conn.cursor()
    
    # Período de teste (último mês)
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    print(f"📅 Período: {start_date} a {end_date}")
    print()
    
    # 1. Verificar grupos disponíveis
    print("🏢 GRUPOS DISPONÍVEIS:")
    cursor.execute("SELECT id, name, description FROM groups ORDER BY name")
    groups = cursor.fetchall()
    
    for group_id, name, description in groups:
        print(f"   {group_id}: {name} - {description}")
    
    print()
    
    # 2. Verificar usuários por grupo
    print("👥 USUÁRIOS POR GRUPO:")
    for group_id, group_name, description in groups:
        cursor.execute("""
            SELECT id, name, email, department 
            FROM users 
            WHERE group_id = ? AND is_active = 1
            ORDER BY name
        """, (group_id,))
        
        users = cursor.fetchall()
        print(f"   📋 {group_name} ({len(users)} usuários):")
        for user_id, name, email, dept in users:
            print(f"      • {name} ({email}) - {dept}")
        print()
    
    # 3. Verificar RNCs por grupo (baseado no responsável)
    print("📊 RNCs POR GRUPO (baseado no responsável):")
    
    for group_id, group_name, description in groups:
        # Buscar usuários do grupo
        cursor.execute("""
            SELECT id, name FROM users 
            WHERE group_id = ? AND is_active = 1
        """, (group_id,))
        
        group_users = cursor.fetchall()
        user_names = [user[1] for user in group_users]
        
        if user_names:
            # Buscar RNCs onde o responsável é um usuário do grupo
            placeholders = ','.join(['?' for _ in user_names])
            query = f"""
                SELECT COUNT(*) as total_rncs, 
                       SUM(CAST(price AS REAL)) as total_value
                FROM rncs 
                WHERE is_deleted = 0 
                AND DATE(created_at) BETWEEN ? AND ?
                AND responsavel IN ({placeholders})
            """
            
            params = [start_date, end_date] + user_names
            cursor.execute(query, params)
            result = cursor.fetchone()
            
            total_rncs = result[0] or 0
            total_value = result[1] or 0
            
            print(f"   🏢 {group_name}:")
            print(f"      📊 RNCs: {total_rncs}")
            print(f"      💰 Valor: R$ {total_value:,.2f}")
            print(f"      👥 Responsáveis: {', '.join(user_names)}")
            print()
    
    # 4. Verificar RNCs sem responsável ou com responsável não encontrado
    print("⚠️ RNCs SEM RESPONSÁVEL OU RESPONSÁVEL NÃO ENCONTRADO:")
    
    # Buscar todos os responsáveis únicos
    cursor.execute("""
        SELECT DISTINCT responsavel 
        FROM rncs 
        WHERE is_deleted = 0 
        AND DATE(created_at) BETWEEN ? AND ?
        AND responsavel IS NOT NULL AND responsavel != ''
    """, (start_date, end_date))
    
    responsaveis = [row[0] for row in cursor.fetchall()]
    
    # Buscar todos os nomes de usuários ativos
    cursor.execute("""
        SELECT name FROM users WHERE is_active = 1
    """)
    
    user_names = [row[0] for row in cursor.fetchall()]
    
    # Encontrar responsáveis não encontrados
    not_found = [r for r in responsaveis if r not in user_names]
    
    if not_found:
        print(f"   📋 Responsáveis não encontrados: {', '.join(not_found)}")
        
        # Contar RNCs desses responsáveis
        placeholders = ','.join(['?' for _ in not_found])
        query = f"""
            SELECT COUNT(*) 
            FROM rncs 
            WHERE is_deleted = 0 
            AND DATE(created_at) BETWEEN ? AND ?
            AND responsavel IN ({placeholders})
        """
        
        params = [start_date, end_date] + not_found
        cursor.execute(query, params)
        count = cursor.fetchone()[0]
        
        print(f"   📊 Total de RNCs: {count}")
    else:
        print("   ✅ Todos os responsáveis foram encontrados!")
    
    print()
    
    # 5. Proposta de query para relatório por grupo
    print("🔧 PROPOSTA DE QUERY PARA RELATÓRIO POR GRUPO:")
    
    query_proposal = """
        SELECT 
            g.id as group_id,
            g.name as group_name,
            g.description as group_description,
            COUNT(r.id) as total_rncs,
            SUM(CAST(r.price AS REAL)) as total_value,
            GROUP_CONCAT(DISTINCT u.name) as group_members
        FROM groups g
        LEFT JOIN users u ON g.id = u.group_id AND u.is_active = 1
        LEFT JOIN rncs r ON r.responsavel = u.name 
            AND r.is_deleted = 0 
            AND DATE(r.created_at) BETWEEN ? AND ?
        WHERE g.id IS NOT NULL
        GROUP BY g.id, g.name, g.description
        ORDER BY total_value DESC, total_rncs DESC
    """
    
    print("   Query proposta:")
    print("   " + query_proposal.replace('\n', '\n   '))
    print()
    
    # 6. Testar a query proposta
    print("🧪 TESTANDO QUERY PROPOSTA:")
    cursor.execute(query_proposal, (start_date, end_date))
    results = cursor.fetchall()
    
    for group_id, group_name, description, total_rncs, total_value, members in results:
        print(f"   🏢 {group_name}:")
        print(f"      📊 RNCs: {total_rncs or 0}")
        print(f"      💰 Valor: R$ {total_value or 0:,.2f}")
        print(f"      👥 Membros: {members or 'Nenhum'}")
        print()
    
    conn.close()
    
    print("✅ Análise concluída!")

if __name__ == "__main__":
    check_groups_rncs()
