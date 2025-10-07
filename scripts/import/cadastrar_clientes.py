#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para cadastrar clientes no banco de dados
"""
import sqlite3

# Path do banco de dados
DB_PATH = 'database.db'

# Lista de clientes para cadastrar
CLIENTES = [
    "Mello",
    "Transriver",
    "Orsa N.C.",
    "Tropico",
    "Irany",
    "Sepac",
    "Paema",
    "3A",
    "Paraibuna",
    "Tedesco",
    "Lubeck",
    "Inpa Uberaba",
    "Prefeitura Municipal P.S.",
    "Jotape",
    "Isidoro e Moraes",
    "Batavo",
    "Harolpel",
    "Bruno Biagioni",
    "Jari N.C.",
    "Gayatri",
    "Iguaçu F.R.",
    "ASCI",
    "Intec",
    "Accer",
    "Ecopaper",
    "Motrice",
    "Trombini S.A.",
    "Manancial",
    "Cipel",
    "Orsa Paulinea",
    "PCE",
    "Pasa",
    "Tidland",
    "B.B.T.",
    "Carvalheira",
    "Sudeste",
    "Dopel",
    "Nutrimental",
    "Pisa",
    "JBS",
    "Abbaspel",
    "Cocelpa",
    "Inpel",
    "Estrela",
    "Arjowiggins",
    "Plaskaper",
    "Incopa",
    "Omya",
    "Interprint",
    "Inpress Decor",
    "Arauco Pien",
    "Santa Rita",
    "Reginaldo",
    "Cepasa",
    "Tetrapel",
    "Fernandez",
    "Pecém",
    "Aguas Negras",
    "Mundial",
    "Cobap",
    "Guapi Papéis",
    "La mattos",
    "Coprocess",
    "Iberkraft",
    "Watanabe",
    "Convertipap",
    "Andritz",
    "Lotus Metal",
    "Fedrigoni",
    "Ponte Nova",
    "D'ouro",
    "Ibema Embú",
    "B.O Paper",
    "Braslumber",
    "Int. Paper",
    "Dallegrave",
    "VH Paper",
    "Auti",
    "Promaco",
    "Trombini Curitiba",
    "Copapa",
    "Primo Tedesco",
    "Ippel",
    "Lutepel",
    "Sopasta",
    "Iguaçu S.J.P",
    "Iguaçu C.N.",
    "Iguaçu P.S.",
    "Inpa Pirapetinga",
    "Sonoco",
    "Canoinhas",
    "Valinhos",
    "Valpasa",
    "Klabin T.B.",
    "Pinho Past",
    "Trombini F.B.",
    "Bragagnolo",
    "Cibrapel",
    "São Carlos",
    "Sengés",
    "Polpa de Madeiras",
    "Paulispell",
    "Mili",
    "Madepar",
    "Sovel",
    "Ondunorte",
    "Orsa F.R.",
    "Colley",
    "Bonet",
    "Penha C.V.",
    "Penha B.A.",
    "Damapel",
    "Papelão União",
    "Stora Enso",
    "Ibersul",
    "Araucária",
    "Kimberly",
    "Kartotec",
    "Imporpel",
    "Citroplast",
    "Bio Papel",
    "Ibema",
    "Crisoba",
    "Santapel",
    "Isdralit",
    "Norske Skog",
    "Castrolanda Castro",
    "Castrolanda Piraí",
    "Huhtamaki",
    "Saint Gobain",
    "Braspine",
    "Vale do Tambau",
    "Vinhedos",
    "Fapolpa",
    "Eternit",
    "Difrane",
    "Sapelba",
    "Jaepel",
    "Miraluz",
    "CVG",
    "Rio verde",
    "AFT do Brasil",
    "Ciper",
    "Novaprom",
    "Placibras",
    "Leal",
    "Rio Jordão",
    "Santa Clara Ivaí",
    "Porto Feliz",
    "Balke",
    "Inpopel",
    "Novacki",
    "Bethania",
]

def cadastrar_clientes():
    """Cadastrar todos os clientes no banco de dados"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Verificar se a tabela existe
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                contact TEXT,
                phone TEXT,
                email TEXT,
                address TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        cadastrados = 0
        duplicados = 0
        erros = 0
        
        print("🚀 Iniciando cadastro de clientes...")
        print("=" * 60)
        
        for nome in CLIENTES:
            if not nome or nome.strip() == "":
                continue
                
            try:
                cursor.execute('''
                    INSERT INTO clients (name)
                    VALUES (?)
                ''', (nome.strip(),))
                
                cadastrados += 1
                print(f"✅ {cadastrados:3d}. {nome}")
                
            except sqlite3.IntegrityError:
                duplicados += 1
                print(f"⚠️  {nome:50s} - JÁ EXISTE")
                
            except Exception as e:
                erros += 1
                print(f"❌ {nome:50s} - ERRO: {e}")
        
        conn.commit()
        conn.close()
        
        print("=" * 60)
        print(f"\n📊 RESUMO:")
        print(f"   ✅ Cadastrados com sucesso: {cadastrados}")
        print(f"   ⚠️  Duplicados (ignorados):  {duplicados}")
        print(f"   ❌ Erros:                    {erros}")
        print(f"   📝 Total processado:         {len(CLIENTES)}")
        print("\n✅ Processo concluído!")
        
        return cadastrados
        
    except Exception as e:
        print(f"\n❌ ERRO FATAL: {e}")
        return 0

if __name__ == '__main__':
    cadastrar_clientes()
