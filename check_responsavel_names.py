#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar correspondência entre responsáveis e usuários
"""

import sqlite3
from datetime import datetime, timedelta

def check_responsavel_names():
    """Verificar correspondência entre responsáveis e usuários"""
    
    print("🔍 Verificando Correspondência Responsáveis ↔ Usuários")
    print("="*60)
    
    # Conectar ao banco
    conn = sqlite3.connect('ippel_system.db')
    cursor = conn.cursor()
    
    # Período de teste (último mês)
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    print(f"📅 Período: {start_date} a {end_date}")
    print()
    
    # 1. Buscar todos os responsáveis únicos nos RNCs
    print("📋 RESPONSÁVEIS NOS RNCs:")
    cursor.execute("""
        SELECT DISTINCT responsavel, COUNT(*) as count
        FROM rncs 
        WHERE is_deleted = 0 
        AND DATE(created_at) BETWEEN ? AND ?
        AND responsavel IS NOT NULL AND responsavel != ''
        ORDER BY count DESC
    """, (start_date, end_date))
    
    responsaveis_rncs = cursor.fetchall()
    
    for responsavel, count in responsaveis_rncs:
        print(f"   • '{responsavel}': {count} RNCs")
    
    print()
    
    # 2. Buscar todos os nomes de usuários ativos
    print("👥 NOMES DE USUÁRIOS ATIVOS:")
    cursor.execute("""
        SELECT name, email, department, group_id
        FROM users 
        WHERE is_active = 1
        ORDER BY name
    """)
    
    usuarios = cursor.fetchall()
    
    for name, email, dept, group_id in usuarios:
        print(f"   • '{name}' ({email}) - {dept} - Grupo: {group_id}")
    
    print()
    
    # 3. Verificar correspondência exata
    print("🔍 VERIFICAÇÃO DE CORRESPONDÊNCIA:")
    
    responsaveis_set = {r[0] for r in responsaveis_rncs}
    usuarios_set = {u[0] for u in usuarios}
    
    # Encontrar correspondências exatas
    matches = responsaveis_set.intersection(usuarios_set)
    only_in_rncs = responsaveis_set - usuarios_set
    only_in_users = usuarios_set - responsaveis_set
    
    print(f"   ✅ Correspondências exatas ({len(matches)}):")
    for match in sorted(matches):
        print(f"      • '{match}'")
    
    print()
    print(f"   ⚠️ Apenas nos RNCs ({len(only_in_rncs)}):")
    for rnc_only in sorted(only_in_rncs):
        print(f"      • '{rnc_only}'")
    
    print()
    print(f"   👥 Apenas nos usuários ({len(only_in_users)}):")
    for user_only in sorted(only_in_users):
        print(f"      • '{user_only}'")
    
    print()
    
    # 4. Verificar RNCs com responsáveis que não correspondem
    if only_in_rncs:
        print("📊 RNCs COM RESPONSÁVEIS NÃO ENCONTRADOS:")
        
        placeholders = ','.join(['?' for _ in only_in_rncs])
        query = f"""
            SELECT responsavel, COUNT(*) as count, SUM(CAST(price AS REAL)) as total_value
            FROM rncs 
            WHERE is_deleted = 0 
            AND DATE(created_at) BETWEEN ? AND ?
            AND responsavel IN ({placeholders})
            GROUP BY responsavel
            ORDER BY count DESC
        """
        
        params = [start_date, end_date] + list(only_in_rncs)
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        for responsavel, count, value in results:
            print(f"   • '{responsavel}': {count} RNCs, R$ {value or 0:,.2f}")
    
    print()
    
    # 5. Proposta de solução: usar correspondência parcial
    print("🔧 PROPOSTA DE SOLUÇÃO:")
    print("   Usar correspondência parcial para encontrar responsáveis:")
    
    # Exemplo de correspondência parcial
    print("   Exemplos de correspondência:")
    for rnc_only in list(only_in_rncs)[:5]:  # Primeiros 5
        # Buscar usuários que contenham parte do nome
        cursor.execute("""
            SELECT name, email, department 
            FROM users 
            WHERE is_active = 1 
            AND (name LIKE ? OR name LIKE ? OR name LIKE ?)
        """, (f"%{rnc_only}%", f"%{rnc_only.split()[0]}%", f"%{rnc_only.split()[-1]}%"))
        
        matches = cursor.fetchall()
        if matches:
            print(f"      '{rnc_only}' → {[m[0] for m in matches]}")
        else:
            print(f"      '{rnc_only}' → Nenhuma correspondência")
    
    print()
    
    # 6. Query alternativa usando correspondência parcial
    print("🔧 QUERY ALTERNATIVA (correspondência parcial):")
    
    query_alternative = """
        SELECT 
            g.id as group_id,
            g.name as group_name,
            g.description as group_description,
            COUNT(r.id) as total_rncs,
            SUM(CAST(r.price AS REAL)) as total_value,
            GROUP_CONCAT(DISTINCT u.name) as group_members
        FROM groups g
        LEFT JOIN users u ON g.id = u.group_id AND u.is_active = 1
        LEFT JOIN rncs r ON (
            r.responsavel = u.name OR 
            r.responsavel LIKE '%' || u.name || '%' OR
            u.name LIKE '%' || r.responsavel || '%'
        )
            AND r.is_deleted = 0 
            AND DATE(r.created_at) BETWEEN ? AND ?
        WHERE g.id IS NOT NULL
        GROUP BY g.id, g.name, g.description
        ORDER BY total_value DESC, total_rncs DESC
    """
    
    print("   Query com correspondência parcial:")
    print("   " + query_alternative.replace('\n', '\n   '))
    print()
    
    # 7. Testar query alternativa
    print("🧪 TESTANDO QUERY ALTERNATIVA:")
    cursor.execute(query_alternative, (start_date, end_date))
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
    check_responsavel_names()
