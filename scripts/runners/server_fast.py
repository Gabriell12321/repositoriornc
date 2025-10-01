from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import json
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Permite requisições do frontend

# Configurações de E-mail
EMAIL_CONFIG = {
    'smtp_server': 'smtp.gmail.com',  # Para Outlook: 'smtp-mail.outlook.com'
    'smtp_port': 587,
    'email': 'seu-email@gmail.com',  # ⚠️ MUDE PARA SEU E-MAIL REAL
    'password': 'sua-senha-de-app'   # ⚠️ MUDE PARA SUA SENHA DE APP
}

def send_email(recipient_email, subject, content, email_type):
    """Função para enviar e-mail"""
    try:
        # Criar mensagem
        msg = MIMEMultipart('alternative')
        msg['From'] = EMAIL_CONFIG['email']
        msg['To'] = recipient_email
        msg['Subject'] = subject
        msg['Reply-To'] = EMAIL_CONFIG['email']

        # Versão texto simples
        text_content = content

        # Versão HTML formatada
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background: #4CAF50; color: white; padding: 15px; text-align: center; }}
                .content {{ padding: 20px; background: #f9f9f9; }}
                .footer {{ text-align: center; color: #666; font-size: 12px; padding: 10px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h2>{subject}</h2>
            </div>
            <div class="content">
                <pre>{content}</pre>
            </div>
            <div class="footer">
                Sistema IPPEL - Relatórios de Não Conformidade
            </div>
        </body>
        </html>
        """

        # Anexar as partes
        part1 = MIMEText(text_content, 'plain', 'utf-8')
        part2 = MIMEText(html_content, 'html', 'utf-8')
        
        msg.attach(part1)
        msg.attach(part2)

        # Conectar e enviar
        with smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port']) as server:
            server.starttls()
            server.login(EMAIL_CONFIG['email'], EMAIL_CONFIG['password'])
            server.send_message(msg)
            
        return {"success": True, "message": "E-mail enviado com sucesso!"}
        
    except Exception as e:
        return {"success": False, "message": f"Erro ao enviar e-mail: {str(e)}"}

@app.route('/send-email', methods=['POST'])
def send_email_route():
    """Endpoint para enviar e-mail"""
    try:
        data = request.get_json()
        
        # Validar campos obrigatórios
        required_fields = ['recipient_email', 'subject', 'content', 'email_type']
        missing_fields = [field for field in required_fields if field not in data or not data[field]]
        
        if missing_fields:
            return jsonify({
                'success': False,
                'message': f'Campos obrigatórios faltando: {", ".join(missing_fields)}'
            }), 400
        
        # Enviar e-mail
        result = send_email(
            data['recipient_email'],
            data['subject'], 
            data['content'],
            data['email_type']
        )
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro interno do servidor: {str(e)}'
        }), 500

@app.route('/test-email', methods=['GET'])
def test_email():
    """Endpoint para testar configuração de e-mail"""
    try:
        test_result = send_email(
            EMAIL_CONFIG['email'],  # Enviar para si mesmo
            "Teste - Sistema IPPEL",
            "Este é um teste de configuração do sistema de e-mail.\n\nSe você recebeu esta mensagem, o sistema está funcionando corretamente!",
            "test"
        )
        return jsonify(test_result)
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro no teste de e-mail: {str(e)}'
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint de health check"""
    return jsonify({
        'status': 'ok',
        'service': 'IPPEL Email Service',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("🚀 Iniciando servidor de e-mail IPPEL...")
    print(f"📧 Servidor: {EMAIL_CONFIG['smtp_server']}")
    print(f"🔗 Endpoints disponíveis:")
    print("   - POST /send-email")
    print("   - GET /test-email")
    print("   - GET /health")
    print("🌐 Servidor rodando em: http://localhost:5000")
    
    # Verificar configuração de e-mail
    if EMAIL_CONFIG['email'] == 'seu-email@gmail.com':
        print("⚠️  ATENÇÃO: Configure suas credenciais de e-mail no arquivo server_fast.py")
        print("   - Linha 12: EMAIL_CONFIG['email']")
        print("   - Linha 13: EMAIL_CONFIG['password']")
    
    # OTIMIZAÇÃO: Desabilitar debug mode para startup mais rápido
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
