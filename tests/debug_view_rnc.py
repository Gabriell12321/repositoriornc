import sqlite3

# Simula exatamente a query do view_rnc
conn = sqlite3.connect('ippel_system.db')
cursor = conn.cursor()

print("=== TESTE DE DEBUG DO VIEW_RNC ===")

# Primeira: query exata do view_rnc
cursor.execute('''
    SELECT r.*,
           u.name as user_name,
           au.name as assigned_user_name,
           u.department as user_department,
           au.department as assigned_user_department
    FROM rncs r
    LEFT JOIN users u ON r.user_id = u.id
    LEFT JOIN users au ON r.assigned_user_id = au.id
    WHERE r.id = (SELECT id FROM rncs WHERE rnc_number = 'RNC-2025-08-28-104553')
''')
rnc_data = cursor.fetchone()

# Segunda: info das colunas da tabela rncs
cursor.execute('PRAGMA table_info(rncs)')
base_columns = [row[1] for row in cursor.fetchall()]

print(f"Número de colunas base: {len(base_columns)}")
print(f"Número de dados retornados: {len(rnc_data) if rnc_data else 0}")

# Mapeia os dados
columns = base_columns + ['user_name', 'assigned_user_name', 'user_department', 'assigned_user_department']

if rnc_data and len(rnc_data) < len(columns):
    rnc_data = list(rnc_data) + [None] * (len(columns) - len(rnc_data))

if rnc_data:
    rnc_dict = dict(zip(columns, rnc_data))
    
    print("\n=== DADOS DO RNC ===")
    print(f"ID: {rnc_dict.get('id')}")
    print(f"RNC Number: {rnc_dict.get('rnc_number')}")
    print(f"Title: {rnc_dict.get('title')}")
    print(f"Equipment: {rnc_dict.get('equipment')}")
    print(f"Client: {rnc_dict.get('client')}")
    print(f"Description: {rnc_dict.get('description')}")
    
    print("\n=== CAMPOS ESPECÍFICOS ===")
    print(f"instruction_retrabalho: '{rnc_dict.get('instruction_retrabalho')}'")
    print(f"cause_rnc: '{rnc_dict.get('cause_rnc')}'")
    print(f"action_rnc: '{rnc_dict.get('action_rnc')}'")
    
    print("\n=== VERIFICAÇÃO DE CHAVES ===")
    print(f"'instruction_retrabalho' in rnc_dict: {'instruction_retrabalho' in rnc_dict}")
    print(f"'cause_rnc' in rnc_dict: {'cause_rnc' in rnc_dict}")
    print(f"'action_rnc' in rnc_dict: {'action_rnc' in rnc_dict}")
    
    print("\n=== POSIÇÕES DAS COLUNAS ===")
    for i, col in enumerate(base_columns):
        if col in ['instruction_retrabalho', 'cause_rnc', 'action_rnc']:
            print(f"  {col} está na posição {i}")
    
    print("\n=== DADOS NAS POSIÇÕES ===")
    if len(rnc_data) > 32:
        print(f"Posição 33 (instruction_retrabalho): '{rnc_data[32]}'")
        print(f"Posição 34 (cause_rnc): '{rnc_data[33]}'")
        print(f"Posição 35 (action_rnc): '{rnc_data[34]}'")
    
    print("\n=== ASSINATURAS ===")
    print(f"signature_inspection_name: '{rnc_dict.get('signature_inspection_name')}'")
    print(f"signature_engineering_name: '{rnc_dict.get('signature_engineering_name')}'")
    print(f"signature_inspection2_name: '{rnc_dict.get('signature_inspection2_name')}'")
    
    print("\n=== DISPOSIÇÕES ===")
    print(f"disposition_usar: {rnc_dict.get('disposition_usar')}")
    print(f"disposition_retrabalhar: {rnc_dict.get('disposition_retrabalhar')}")
    print(f"disposition_rejeitar: {rnc_dict.get('disposition_rejeitar')}")
    
    print("\n=== INSPEÇÕES ===")
    print(f"inspection_aprovado: {rnc_dict.get('inspection_aprovado')}")
    print(f"inspection_reprovado: {rnc_dict.get('inspection_reprovado')}")
    
    # Simular a função parse_label_map
    def parse_label_map(text: str):
        """Extract key=value style pairs from description, tolerant to separators."""
        import re, unicodedata
        if not text:
            return {}
        def _norm(s: str) -> str:
            s = unicodedata.normalize('NFD', s)
            s = ''.join(ch for ch in s if unicodedata.category(ch) != 'Mn')
            s = s.lower()
            s = re.sub(r'[^a-z0-9]', '', s)
            return s
        sep_re = re.compile(r'^\s*([A-Za-zÀ-ÿ\.\s/_-]{2,}?)\s*(?:[:=\-–—]+|\s{2,})\s*(.+)$')
        token_re = re.compile(r'^\s*([A-Za-zÀ-ÿ\.]{2,})\s+(.+)$')
        mapping: dict[str, str] = {}
        lines = [ln.rstrip() for ln in str(text).split('\n') if ln.strip()]
        for ln in lines:
            m = sep_re.match(ln)
            if not m:
                m = token_re.match(ln)
            if not m:
                continue
            label, val = m.group(1).strip(), m.group(2).strip()
            n = _norm(label)
            if n in {'des', 'desenho'}:
                mapping['Desenho'] = val
            elif n in {'mp'}:
                mapping['MP'] = val
            elif n in {'rev', 'revisao'}:
                mapping['Revisão'] = val
            elif n == 'cv' or 'cv' in n:
                mapping['CV'] = val
            elif n == 'pos' or 'pos' in n:
                mapping['POS'] = val
            elif 'conjunto' in n or n == 'conj':
                mapping['Conjunto'] = val
            elif n in {'modelo', 'mod'}:
                mapping['Modelo'] = val
            elif n in {'quantidade', 'qtde', 'qtd'}:
                mapping['Quantidade'] = val
            elif 'material' in n or n == 'mat':
                mapping['Material'] = val
            elif n in {'oc', 'ordemdecompra', 'ordemcompra'}:
                mapping['OC'] = val
            elif ('area' in n and 'responsavel' in n) or n in {'arearesponsavel'}:
                mapping['Área responsável'] = val
            elif 'descricao' in n and 'rnc' in n:
                mapping['Descrição da RNC'] = val
            elif 'instrucao' in n and 'retrabalho' in n:
                mapping['Instrução para retrabalho'] = val
            elif n in {'valor', 'vlr'}:
                mapping['Valor'] = val
            elif n in {'causa'}:
                mapping['Causa'] = val
            elif 'acao' in n or 'acaosertomada' in n:
                mapping['Ação'] = val
            else:
                mapping[label] = val
        return mapping

    txt_fields = parse_label_map(rnc_dict.get('description') or '')
    
    print("\n=== TXT_FIELDS EXTRAÍDOS ===")
    print(f"Chaves encontradas: {list(txt_fields.keys())}")
    for key, value in txt_fields.items():
        print(f"  {key}: '{value}'")
    
    print("\n=== VERIFICAÇÃO FINAL ===")
    print("Para exibir no template:")
    print(f"  Descrição: {txt_fields.get('Descrição da RNC') or rnc_dict.get('description') or '-'}")
    print(f"  Instrução: {rnc_dict.get('instruction_retrabalho') or txt_fields.get('Instrução para retrabalho') or '-'}")
    print(f"  Causa: {rnc_dict.get('cause_rnc') or txt_fields.get('Causa') or '-'}")
    print(f"  Ação: {rnc_dict.get('action_rnc') or txt_fields.get('Ação') or '-'}")

else:
    print("❌ RNC não encontrada")

conn.close()
