#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Atualizar admin para ter group_id
"""
import sqlite3

def update_admin_group():
    """Atualizar admin para ter group_id"""
    conn = sqlite3.connect('ippel_system.db')
    cursor = conn.cursor()
    
    # Atualizar admin para grupo TI
    cursor.execute('UPDATE users SET group_id = 3 WHERE email = ?', ('admin@ippel.com.br',))
    conn.commit()
    
    print("✅ Admin atualizado para grupo TI")
    
    # Verificar
    cursor.execute('SELECT name, group_id FROM users WHERE email = ?', ('admin@ippel.com.br',))
    admin = cursor.fetchone()
    print(f"👤 Admin agora no grupo: {admin[1]}")
    
    conn.close()

if __name__ == "__main__":
    update_admin_group()
