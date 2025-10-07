#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para cadastrar operadores no banco de dados
"""
import sqlite3
import sys
import os

# Path do banco de dados
DB_PATH = 'database.db'

# Lista de operadores para cadastrar
OPERADORES = [
    ("Ricardo Mauda", "582"),
    ("Roberto", ""),
    ("Thiago", ""),
    ("Mauricio", ""),
    ("Leopoldo", ""),
    ("Pedro", ""),
    ("Cleyson", ""),
    ("Rodrigo", ""),
    ("Marcio", ""),
    ("Rosinei", "525"),
    ("Alyson Carlota", ""),
    ("Bruno", ""),
    ("Claudio", ""),
    ("Marlon", ""),
    ("Felipe Santos", ""),
    ("Marcos", ""),
    ("Juliano", ""),
    ("Douglas", ""),
    ("Renato", ""),
    ("Rosivaldo", ""),
    ("Gilmar", ""),
    ("Fundibem", ""),
    ("Shiffer", ""),
    ("Nicron", ""),
    ("Carbomec", ""),
    ("SCA", ""),
    ("Intec", ""),
    ("Blades", ""),
    ("Aço Craft", ""),
    ("Tratmatic", ""),
    ("Pozelli", ""),
    ("Caçamba", ""),
    ("Sengés", ""),
    ("Rostec", ""),
    ("A.T.B.", ""),
    ("Sociesc", ""),
    ("Pechjet", ""),
    ("Lubeck", ""),
    ("Lucco", ""),
    ("Molas Ico", ""),
    ("Alumibron", ""),
    ("F.T.P", ""),
    ("Sandro", ""),
    ("Pedro Flugel", ""),
    ("Imbilinox", ""),
    ("Luciano Rosa Borges", ""),
    ("Hudson Lafayete Martins Carlota", ""),
    ("Carla Dalmaso", ""),
    ("A.F.T.P.", ""),
    ("A.F.M.", ""),
    ("Anderson Fábio Ferraz Lopes", ""),
    ("Michael Douglas de Oliveira", ""),
    ("Renato Bertocco", ""),
    ("Gian Marchiori", ""),
    ("Kioto", ""),
    ("Murilo de Oliveira Vale", ""),
    ("Fresadora Santana", ""),
    ("André Franciosi", ""),
    ("Tiairo", ""),
    ("Felipe Hiroshi", ""),
    ("Roma", ""),
    ("Oscar", ""),
    ("Nelson Luiz Ferreira", ""),
    ("William Standler", ""),
    ("Erick de Souza Olieira", ""),
    ("Luis Emanuel Prestes de Oliveira", ""),
    ("RUSPRI", ""),
    ("Vecon", ""),
    ("Poli New", ""),
    ("Marcio Brito", ""),
    ("Camila Bettega", ""),
    ("Lucas Martins Milleo", ""),
    ("5C Polias", ""),
    ("Lingobras", ""),
    ("Yosvany Perez", ""),
    ("Guilherme Dolatto", ""),
    ("Tetrapel", ""),
    ("Sulcromo", ""),
    ("Felipe Bueno Ferreira", ""),
    ("Yago Valencio", ""),
    ("Patrick Abreu", ""),
    ("Marcone", ""),
    ("Rogerio Franciulli", ""),
    ("Evandro", ""),
    ("Kely Ditzel", ""),
    ("Claudio Alves", ""),
    ("Luiz Guilherme Souza", ""),
    ("Gregori Paganella", ""),
    ("Josevaldo Gomes", ""),
    ("Edson Carlos Ferreira", ""),
    ("Elvis Roberto Souza", ""),
    ("Igor Corrêa", ""),
    ("Jovino Schreiner", ""),
    ("Roni Antonio Lima", ""),
    ("Nei Schimposki", ""),
    ("Rafael Aleixo", ""),
    ("Saulo da Silva Smala", ""),
    ("David Rodrigues", ""),
    ("Rodrigo Fanha Carneiro", ""),
    ("Antonio Augusto", ""),
    ("Fernando Melo", ""),
    ("Adriano Bueno", ""),
    ("Wilyeser Soares", ""),
    ("Jefson Joel dos Santos", ""),
    ("Ricardo Pedroso Bueno", ""),
    ("José Assis", ""),
    ("Diordan Felipe dos Santos", ""),
    ("Henrique Moreira", ""),
    ("Luiz Kenji do Amaral Saito", ""),
    ("Evandro Felipe Carneiro", ""),
    ("Osiel Alves Teixeira", ""),
    ("Willyan Carlos Melotti", ""),
    ("Isabely Barbosa", ""),
    ("Luis Kenji", ""),
    ("Silvio Moreira", ""),
    ("Anderson Cavalheiro", "506"),
    ("Luiz Gustavo Ribas", "510"),
    ("Daiane Pedroso Bueno", "503"),
    ("Gabriel Ferreira Mattos", "522"),
    ("André Bertequine", "526"),
    ("João Vitor Pucci", "524"),
    ("Matheus de Souza Silva", "525"),
    ("João Maria Carneiro", "492"),
    ("Bruno Henrique de Oliveira", "520"),
    ("Paulo Roberto Silvestre", "509"),
    ("Leonardo Kremer", "523"),
    ("Evellyn Taianara Mello", "546"),
    ("Alex Sandro Soares Mainardes", "539"),
    ("Rômulo Emanuel Mainardes", "532"),
    ("Fundimax", ""),
    ("Mário Dolato Neto", "585"),
    ("Fundição Campos Gerais", ""),
    ("Lucimar de Jesus de Azevedo", "10"),
    ("Wanderlei Martins Barbosa", "11"),
    ("José Valdemir Martins Barbosa", "13"),
    ("Edi Carlos de Souza Lima", "14"),
    ("Claudemir Bettega", "16"),
    ("Silvio Halat", "17"),
    ("Luciano José Carneiro Stella", "20"),
    ("Adenilson José de Oliveira", "22"),
    ("Leivas Aparecido do Nascimento", "23"),
    ("Rogério da Silva Brito", "24"),
    ("Maurício Maciel de Souza", "26"),
    ("Célio Antonio da Silva", "27"),
    ("Edson Antonio Alves", "33"),
    ("Waldemar Martins Barbosa", "36"),
    ("Maicon José de Oliveira", "39"),
    ("Clodoaldo Maciel de Souza", "41"),
    ("Luiz Wanderlei de Oliveira", "46"),
    ("Marcos Antonio Mainardes", "49"),
    ("Halan Rogério Ferraz", "50"),
    ("Cícero Roberto Paz", "59"),
    ("Paulo Roberto Simões", "65"),
    ("Vagner Martins", "72"),
    ("Mario Henrique Napoleão", "86"),
    ("Fabio André Mendes Maciel", "87"),
    ("Luiz Daniel de Andrade", "88"),
    ("Osvaldo Traci", "91"),
    ("José Josnei Pereira dos Santos", "98"),
    ("Edison André Ferreira Diniz", "99"),
    ("Demerval Felipe", "104"),
    ("Eleandro Biassio Valenga", "112"),
    ("Marcio das Brotas dos Santos", "113"),
    ("Celson Ferreira", "114"),
    ("Ezequias da Silva Oliveira", "115"),
    ("Edmilson Camargo", "125"),
    ("Josivaldo Valdevino da Silva", "130"),
    ("Emerson dos Santos", "132"),
    ("Marcio de Oliveira", "134"),
    ("Luciano da Silva", "135"),
    ("Eder", "137"),
    ("Cida", "138"),
    ("Joacir", "139"),
    ("José Israel", "140"),
    ("Cláudio Brandão", "141"),
    ("Lalinka", "142"),
    ("Elias Bianchi", "149"),
    ("Jackson Pereira dos Santos", "160"),
    ("Joselei Reis de Souza", "162"),
    ("Cintia das Graças Kosiba", "165"),
    ("Edson Pereira da Silva", "179"),
    ("Fernando Soleck", "182"),
    ("Rafael F. de Souza", "183"),
    ("Marlon José de Oliveira", "184"),
    ("Gilberto Luiz Vagner", "185"),
    ("José Ataide Napoleão", "196"),
    ("Valdomiro da Silva", "197"),
    ("José Ricardo B. Alves", "198"),
    ("Junior Teixeira da Silva", "199"),
    ("Juliano Rodrigues Ferreira", "200"),
    ("Luis F. Guimarães de Souza Junior", "203"),
    ("Emerson Diniz Ferreira", "204"),
    ("Rodrigo Machado de Mattos", "205"),
    ("Márcio C. Carneiro dos Santos", "208"),
    ("Jocemar Aracelis Kuzniewski", "210"),
    ("Elizeu Pacheco", "213"),
    ("Alessandro de Freitas", "214"),
    ("Rafael Bueno", "222"),
    ("Anor Canha Machado", "225"),
    ("Alex Pereira Bueno", "228"),
    ("Jorge Eziel Alves", "229"),
    ("Bruno de Oliveira", "235"),
    ("Rodrigo dos Santos ferreira", "243"),
    ("Wagner Pires", "244"),
    ("lalinka", "245"),
    ("Rodrigo da Silva", "246"),
    ("Marcio Neimar Podegorski", "247"),
    ("Anderson de Souza Carneiro", "250"),
    ("Danielson Pereira de Anhaia", "252"),
    ("Elon Andreu da Silva Oliveira", "253"),
    ("Gesse Blens", "255"),
    ("Pedro José Ferreira", "257"),
    ("Rosinei Paulo", "258"),
    ("Rosielio Kusdra da Silva", "259"),
    ("Robson Barbosa Pereira", "261"),
    ("Luciano Ferreira da Silva", "263"),
    ("Marcos Ferreira da Silva", "264"),
    ("Roger Bueno", "265"),
    ("Juliano das Brotas Proença", "267"),
    ("Cleomar Pereira", "269"),
    ("Elton Pereira da Anhaia", "271"),
    ("Michel Bueno Carneiro", "272"),
    ("Adenilson Lima Woichessak", "273"),
    ("Adriano José Ferreira de Souza", "275"),
    ("Márcio José M. de Souza", "276"),
    ("Pablo Walter Polopes", "277"),
    ("Marcio Mainardes de Brito", "278"),
    ("Adriano da Silva Almeida", "279"),
    ("Cleiton de Almeida Diniz", "281"),
    ("Carlos Eduardo da Silva", "282"),
    ("José Vanderlei de Oliveira", "285"),
    ("Jossemar Monteiro da Silva", "286"),
    ("Jonas Machado Carneiro", "287"),
    ("Paulo Henrique Alves da Silva", "288"),
    ("Paulo Henrique de Oliveira", "289"),
    ("Sérgio de Oliveira", "290"),
    ("Valdeci Teixeira", "291"),
    ("Jailson Bezerra Araujo", "292"),
    ("Adriano (Ajudante Jailson)", "293"),
    ("Carlos Henrique da Silva", "294"),
    ("Rodrigo Alves Ferreira", "296"),
    ("Gerbssom Paulo Simões", "297"),
    ("Patrick (Ajudante Jailson)", "298"),
    ("Cleiton Vagner Ramos", "301"),
    ("Ronaldo Maciel de Souza", "303"),
    ("Antonio Carlos de Oliveira Custódio", "306"),
    ("Ezequiel C. de Jesus", "308"),
    ("Paulo Henrique Alves da Silva", "310"),
    ("Valdomiro Vicente Cunha", "311"),
    ("Alex Takeshi", "312"),
    ("Everson Lubacheski", "315"),
    ("Jefferson Luis Gonçalves", "316"),
    ("Rosnei Pereira da Silva", "319"),
    ("Cleiton Roberto Mara", "321"),
    ("Vagner da Silva", "323"),
    ("Marcos Gabriel Oliveira", "326"),
    ("Robson Barbosa Pereira", "328"),
    ("Welliton Ribeiro dos Santos", "329"),
    ("Leonel Joselei da Silva", "330"),
    ("Leandro de Brito Barbosa", "333"),
    ("Adrian Gabriel", "340"),
    ("Everton de Brito Junior", "341"),
    ("Marcelo Ferreira", "342"),
    ("Renan mauda", "344"),
    ("Dione Pedroso Ribas", "348"),
    ("Ronival Anauri Ferraz", "349"),
    ("Alissom Nissola", "350"),
    ("Felipe de Abreu Santos", "351"),
    ("Maik Martins da Silva", "352"),
    ("Anor Machado Junior", "353"),
    ("Bruno Sergio da silva guiamarães", "354"),
    ("Douglas Felipe dos Santos", "355"),
    ("Cleyton Felipe de Mello", "356"),
    ("Jonathan Felipe da silva", "357"),
    ("Eleandro Pereira De Lima", "358"),
    ("Maikon Da Silva Pereira", "359"),
    ("Davison Golveia", "360"),
    ("Luiz Henrique Martins da Silva", "361"),
    ("Orlando da Silva", "362"),
    ("Wesley Ricardo Ribas Barbosa", "363"),
    ("Adão José Wardzinski", "364"),
    ("Jaime de Matos da Silva", "365"),
    ("Adeilton Carneiro", "366"),
    ("Luiz Fernando Barbosa", "367"),
    ("Amauri Mainardes", "368"),
    ("Alissom Maciel Gonsalves", "369"),
    ("Josinaldo Lopes da Silva", "370"),
    ("Giovane Del Ponte", "371"),
    ("Diego da Silva Brito", "372"),
    ("Adriani Melotti", "373"),
    ("Rafael Hundzinski de Paula", "374"),
    ("Mauri Pedro Nissola", "005"),
    ("Amadeus Martins", ""),
    ("Claudio Bettega", ""),
    ("Ronaldo Solek", ""),
    ("Ronaldo Brito", ""),
    ("Cleyton Delvoss", ""),
    ("Lino Edson de Oliveira", ""),
]

def cadastrar_operadores():
    """Cadastrar todos os operadores no banco de dados"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Verificar se a tabela existe
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS operators (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                number TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        cadastrados = 0
        duplicados = 0
        erros = 0
        
        print("🚀 Iniciando cadastro de operadores...")
        print("=" * 60)
        
        for nome, numero in OPERADORES:
            if not nome or nome.strip() == "":
                continue
                
            try:
                cursor.execute('''
                    INSERT INTO operators (name, number)
                    VALUES (?, ?)
                ''', (nome.strip(), numero.strip() if numero else None))
                
                cadastrados += 1
                numero_display = f"[{numero}]" if numero else "[Sem número]"
                print(f"✅ {cadastrados:3d}. {nome:50s} {numero_display}")
                
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
        print(f"   📝 Total processado:         {len(OPERADORES)}")
        print("\n✅ Processo concluído!")
        
        return cadastrados
        
    except Exception as e:
        print(f"\n❌ ERRO FATAL: {e}")
        return 0

if __name__ == '__main__':
    cadastrar_operadores()
