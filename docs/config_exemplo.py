# EXEMPLO DE CONFIGURAÇÃO DO GMAIL
# Copie estas linhas e substitua no arquivo server.py

EMAIL_CONFIG = {
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'email': 'meu-email@gmail.com',        # ⚠️ SUBSTITUA PELO SEU E-MAIL
    'password': 'abcd efgh ijkl mnop'      # ⚠️ SUBSTITUA PELA SUA SENHA DE APP
}

# INSTRUÇÕES:
# 1. Vá em https://myaccount.google.com/
# 2. Ative "Verificação em 2 etapas"
# 3. Gere uma "Senha de app" para "Email"
# 4. Copie a senha de 16 caracteres
# 5. Substitua 'meu-email@gmail.com' pelo seu e-mail
# 6. Substitua 'abcd efgh ijkl mnop' pela senha de app
# 7. Salve o arquivo server.py
# 8. Reinicie o servidor 