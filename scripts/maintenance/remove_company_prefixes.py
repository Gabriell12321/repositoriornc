#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import re

def remove_company_prefixes():
    """Remove prefixos de empresas dos campos responsavel e signature_engineering_name em RNCs finalizadas"""
    
    conn = sqlite3.connect('ippel_system.db')
    cursor = conn.cursor()
    
    print('=== REMOÇÃO DE PREFIXOS DE EMPRESAS ===\n')
    
    company_prefixes = [
        'Sonoco', 'Klabin', 'Araucária', 'Valinhos', 'Citroplast', 'Bragagnolo', 
        'Papelão União', 'São Carlos', 'Rio Jordão', 'Harolpel', 'Dallegrave',
        'Ippel', 'Cibrapel', 'Sopasta', 'Trombini', 'Pisa', 'Ibersul', 'AFT',
        'Cobap', 'HP Papéis', 'Klingele', 'BRF', 'Fapolpa', 'Sulamericana',
        'ADF', 'Damapel', 'Abbaspel', 'Cocelpa', 'Santapel', 'CMPC', 'Suzano',
        'Smurfit Kappa', 'Vinhedos', 'Guapi Papéis', 'Iberkraft', 'Irani',
        'Penapolis', 'Caieiras', 'Porto Feliz', 'Mello', 'CVG', 'Paulispell',
        'Transriver', 'Jotape', 'Promaco', 'Colley', 'Castrolanda', 'Bio Papel',
        'Asci', 'Simapel', 'Accer', 'Sapelba', 'Miraluz', 'Embacorp', 'Onze',
        'Arauco', 'Santelisa', 'Ibema', 'Novaprom', 'Lübeck', 'Lutepel',
        'Santa Clara', 'Carvalheira', 'Batavo', 'Paema', 'Sbravatti', 'Anin',
        'Schweitzer', 'Adami', 'Annin', 'Bellmer', 'Bigardi', 'Bonet', 'Caiera',
        'Caieras', 'Colley', 'Diordan', 'Ecopaper', 'Fapolpa', 'Fernandez',
        'Fultec', 'Fultech', 'Gregori', 'Hudson', 'Iguaçu', 'Irany', 'Jaepel',
        'Kadant', 'Kamylla', 'Klabin CP', 'Klabin OC', 'Klimapel', 'Leal',
        'Mauri', 'MD papéis', 'MD Papéis', 'Nei', 'Nova Conpel', 'Novacki',
        'Palli', 'Pasa', 'PCE', 'Penha CV', 'Pinho Past', 'Plácibras',
        'Rexrhout', 'Santelisa', 'Scholler', 'Smurfitt', 'Sociesc', 'Sovel',
        'ST tubo', 'Techdalls', 'Tratmatic', 'Trópicos', 'Tropicos', 'US',
        'Usinagem Estrela', 'VH', 'Watanabe'
    ]
    
    corrections = 0
    
    # Corrigir campo responsavel
    for company in company_prefixes:
        cursor.execute(f"""
            SELECT id, responsavel FROM rncs
            WHERE status = 'Finalizado'
            AND responsavel LIKE '{company} %'
        """)
        records = cursor.fetchall()
        for rnc_id, responsavel in records:
            # Remove o prefixo da empresa
            clean_resp = re.sub(rf'^{re.escape(company)}\s+', '', responsavel).strip()
            if clean_resp and clean_resp != responsavel:
                cursor.execute("""
                    UPDATE rncs SET responsavel = ? WHERE id = ?
                """, (clean_resp, rnc_id))
                print(f'✅ RNC {rnc_id}: "{responsavel}" → "{clean_resp}"')
                corrections += 1
    
    # Corrigir campo signature_engineering_name
    for company in company_prefixes:
        cursor.execute(f"""
            SELECT DISTINCT signature_engineering_name FROM rncs
            WHERE status = 'Finalizado'
            AND signature_engineering_name LIKE '{company} %'
        """)
        signatures = cursor.fetchall()
        for signature in signatures:
            original = signature[0]
            clean_sig = re.sub(rf'^{re.escape(company)}\s+', '', original).strip()
            if clean_sig and clean_sig != original:
                cursor.execute("""
                    UPDATE rncs SET signature_engineering_name = ?
                    WHERE status = 'Finalizado' AND signature_engineering_name = ?
                """, (clean_sig, original))
                print(f'✅ Assinatura: "{original}" → "{clean_sig}"')
                corrections += 1
    
    conn.commit()
    conn.close()
    print(f'\n🎉 Remoção de prefixos concluída! Total de correções: {corrections}')
    return corrections

if __name__ == "__main__":
    total = remove_company_prefixes()
    if total > 0:
        print(f'\n✅ {total} prefixos de empresas removidos!')
    else:
        print('\n✅ Nenhum prefixo de empresa encontrado!')
