#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, render_template
from server_form import app

# Teste simples para verificar se o template existe
try:
    with app.app_context():
        # Tentar renderizar o template
        html = render_template('admin_groups.html')
        print("✅ Template admin_groups.html renderizado com sucesso!")
        print(f"📄 Tamanho do HTML: {len(html)} caracteres")
        print("🔍 Primeiras 200 caracteres:")
        print(html[:200])
    print("\n✅ Teste concluído - template está funcionando!")
except Exception as e:
    print(f"❌ Erro ao renderizar template: {e}")
    import traceback
    traceback.print_exc() 