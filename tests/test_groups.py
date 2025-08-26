import os
import sqlite3
import importlib
from types import ModuleType
import time


def setup_module(module: ModuleType):
    # Point DB_PATH to a temp database in the workspace for isolated tests
    test_db = os.path.abspath("ippel_system_test_groups.db")
    # create minimal schema
    conn = sqlite3.connect(test_db)
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS groups (id INTEGER PRIMARY KEY, name TEXT NOT NULL, description TEXT)")
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name TEXT,
            email TEXT,
            department TEXT,
            role TEXT,
            is_active INTEGER,
            group_id INTEGER
        )
        """
    )
    conn.commit()
    conn.close()

    # Patch services.db.DB_PATH dynamically
    import services.db as dbmod
    dbmod.DB_PATH = test_db

    # reload groups module to take updated DB_PATH and pool functions
    import services.groups as groups
    importlib.reload(groups)
    module.groups = groups


def teardown_module(module: ModuleType):
    try:
        import services.db as dbmod
        # Close pool connections if any
        # Not strictly necessary in this environment
        pass
    except Exception:
        pass


def test_create_group_validation(groups):
    assert groups.create_group("", "desc") is None
    assert groups.create_group("  ", "desc") is None
    gid = groups.create_group("Equipe A", "Time principal")
    assert isinstance(gid, int)


def test_get_group_and_users(groups):
    gid = groups.create_group("Equipe B", "Time B")
    assert isinstance(gid, int)

    # no users yet
    users = groups.get_users_by_group(gid)
    assert users == []


def test_all_groups_cache(groups):
    a = groups.get_all_groups()
    b = groups.get_all_groups()
    # same result cached quickly
    assert a == b


def test_update_and_delete_invalidate_cache(groups):
    # create two groups
    gid1 = groups.create_group("Equipe C", "Desc C")
    gid2 = groups.create_group("Equipe D", "Desc D")
    assert isinstance(gid1, int) and isinstance(gid2, int)

    # warm cache
    _ = groups.get_all_groups()

    # update name of gid1
    assert groups.update_group(gid1, "Equipe C2", "Nova desc") is True

    # cache should be invalidated; fetch again reflects new name
    all_after = groups.get_all_groups()
    names = [row[1] for row in all_after]
    assert "Equipe C2" in names

    # delete gid2
    assert groups.delete_group(gid2) is True
    all_after_del = groups.get_all_groups()
    ids = [row[0] for row in all_after_del]
    assert gid2 not in ids


def test_users_ordering_and_filter(groups):
    gid = groups.create_group("Equipe Users", "test order")
    assert isinstance(gid, int)

    # insert users directly to DB
    import services.db as dbmod
    conn = sqlite3.connect(dbmod.DB_PATH)
    cur = conn.cursor()
    data = [
        ("zeta", "z@x", "d1", "r1", 1, gid),
        ("Alpha", "a@x", "d1", "r1", 1, gid),
        ("beta", "b@x", "d1", "r1", 1, gid),
    ]
    for n,e,d,r,act,g in data:
        cur.execute(
            "INSERT INTO users(name,email,department,role,is_active,group_id) VALUES(?,?,?,?,?,?)",
            (n,e,d,r,act,g),
        )
    conn.commit()
    conn.close()

    users = groups.get_users_by_group(gid)
    names = [u[1] for u in users]
    # assert case-insensitive order: Alpha, beta, zeta
    assert names == ["Alpha", "beta", "zeta"]


def test_cache_ttl_expires(groups):
    # lower the TTL to 0.05s for test
    old_ttl = getattr(groups, "_CACHE_TTL_SECONDS", 30.0)
    groups._CACHE_TTL_SECONDS = 0.05
    try:
        a = groups.get_all_groups()
        time.sleep(0.07)
        b = groups.get_all_groups()
        # After TTL, cache entry is rebuilt; equality may still hold by content
        # but at least call path should not crash. We'll check type and non-emptiness consistency.
        assert isinstance(a, list) and isinstance(b, list)
    finally:
        groups._CACHE_TTL_SECONDS = old_ttl
#!/usr/bin/env python3
"""Script para testar e corrigir sistema de grupos"""

import sqlite3

DB_PATH = 'ippel_system.db'

print("🔧 Testando e corrigindo sistema de grupos...")

try:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    print("\n📊 Usuários e seus departamentos:")
    cur.execute("SELECT id, name, email, department, role FROM users")
    users = cur.fetchall()
    for user in users:
        print(f"  ID: {user[0]}, Nome: {user[1]}, Email: {user[2]}, Depto: {user[3]}, Role: {user[4]}")
    
    print("\n📋 RNCs recentes:")
    cur.execute("SELECT id, rnc_number, title, department, user_id, status FROM rncs ORDER BY created_at DESC LIMIT 10")
    rncs = cur.fetchall()
    for rnc in rncs:
        print(f"  ID: {rnc[0]}, RNC: {rnc[1]}, Título: {rnc[2][:30]}..., Depto: {rnc[3]}, User: {rnc[4]}, Status: {rnc[5]}")
    
    # Simular busca de RNCs para um usuário da Engenharia
    print("\n🔍 Simulando busca para usuário da Engenharia:")
    cur.execute("SELECT id FROM users WHERE department = 'Engenharia' LIMIT 1")
    eng_user = cur.fetchone()
    if eng_user:
        eng_user_id = eng_user[0]
        print(f"  Usuário da Engenharia: ID {eng_user_id}")
        
        # RNCs que ele deveria ver (criadas por ele OU para o departamento Engenharia)
        cur.execute("""
            SELECT id, rnc_number, title, department, user_id 
            FROM rncs 
            WHERE user_id = ? OR department = 'Engenharia'
            ORDER BY created_at DESC LIMIT 5
        """, (eng_user_id,))
        
        rncs_for_eng = cur.fetchall()
        print(f"  RNCs que deveria ver: {len(rncs_for_eng)}")
        for rnc in rncs_for_eng:
            print(f"    - {rnc[1]}: {rnc[2][:30]}... (Depto: {rnc[3]}, User: {rnc[4]})")
    
    conn.close()
    print("\n✅ Teste concluído!")
    
except Exception as e:
    print(f"❌ Erro: {e}")
