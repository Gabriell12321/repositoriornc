import sqlite3

conn = sqlite3.connect('ippel_system.db')
cursor = conn.cursor()

# Pegar a RNC mais recente
cursor.execute('SELECT * FROM rncs ORDER BY id DESC LIMIT 1')
rnc = cursor.fetchone()

if rnc:
    print(f"=== RNC ID: {rnc[0]} ===")
    print(f"RNC Number: {rnc[1]}")
    print(f"Title: {rnc[2]}")
    print(f"Description: {rnc[3]}")
    print(f"Equipment: {rnc[4]}")
    print(f"Client: {rnc[5]}")
    print(f"Priority: {rnc[6]}")
    print(f"Status: {rnc[7]}")
    print(f"User ID: {rnc[8]}")
    print(f"Assigned User ID: {rnc[9]}")
    
    # Verificar assinaturas
    print(f"\n=== Assinaturas ===")
    print(f"signature_inspection_name: {rnc[26]}")
    print(f"signature_engineering_name: {rnc[27]}")
    print(f"signature_inspection2_name: {rnc[29]}")
    
    # Verificar disposições
    print(f"\n=== Disposições ===")
    print(f"disposition_usar: {rnc[15]}")
    print(f"disposition_retrabalhar: {rnc[16]}")
    print(f"disposition_rejeitar: {rnc[17]}")
    
    # Verificar inspeções
    print(f"\n=== Inspeções ===")
    print(f"inspection_aprovado: {rnc[28]}")
    print(f"inspection_reprovado: {rnc[21]}")
    print(f"inspection_ver_rnc: {rnc[22]}")
    
    # Novos campos
    print(f"\n=== Campos Específicos ===")
    print(f"department: {rnc[31]}")
    print(f"instruction_retrabalho: {rnc[32]}")
    print(f"cause_rnc: {rnc[33]}")
    print(f"action_rnc: {rnc[34]}")

else:
    print("Nenhuma RNC encontrada")

conn.close()
