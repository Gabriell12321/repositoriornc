const express = require('express');
const nodemailer = require('nodemailer');
const cors = require('cors');
const path = require('path');

const app = express();
const PORT = 3000;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static('.'));

// Configuração do Nodemailer
const transporter = nodemailer.createTransporter({
    service: 'gmail', // Você pode mudar para outro provedor
    auth: {
        user: 'seu-email@gmail.com', // Substitua pelo seu e-mail
        pass: 'sua-senha-de-app' // Substitua pela sua senha de app
    }
});

// Rota principal - serve o arquivo HTML
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'index.html'));
});

// Rota para enviar e-mail
app.post('/send-email', async (req, res) => {
    try {
        const { recipientEmail, subject, content, emailType } = req.body;

        // Validação básica
        if (!recipientEmail || !subject || !content) {
            return res.status(400).json({
                success: false,
                message: 'Dados obrigatórios não fornecidos'
            });
        }

        // Configuração do e-mail
        const mailOptions = {
            from: 'seu-email@gmail.com', // Substitua pelo seu e-mail
            to: recipientEmail,
            subject: subject,
            text: content,
            html: `
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <div style="background: linear-gradient(135deg, #dc2626, #b91c1c); color: white; padding: 20px; border-radius: 10px 10px 0 0;">
                        <h1 style="margin: 0; text-align: center;">IPPEL - Relatório RNC</h1>
                    </div>
                    <div style="background: #f9fafb; padding: 20px; border-radius: 0 0 10px 10px;">
                        <div style="background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                            <h2 style="color: #dc2626; margin-top: 0;">Relatório de Não Conformidade Interna - RNC</h2>
                            <p style="color: #6b7280; font-size: 14px;">
                                <strong>Tipo de Relatório:</strong> ${emailType}<br>
                                <strong>Data de Envio:</strong> ${new Date().toLocaleDateString('pt-BR')}
                            </p>
                        </div>
                        <div style="background: white; padding: 20px; border-radius: 8px; border-left: 4px solid #dc2626;">
                            <pre style="font-family: 'Courier New', monospace; white-space: pre-wrap; margin: 0; color: #374151;">${content}</pre>
                        </div>
                        <div style="text-align: center; margin-top: 20px; color: #6b7280; font-size: 12px;">
                            <p>Este e-mail foi enviado automaticamente pelo sistema RNC da IPPEL.</p>
                        </div>
                    </div>
                </div>
            `
        };

        // Enviar e-mail
        const info = await transporter.sendMail(mailOptions);

        console.log('E-mail enviado:', {
            messageId: info.messageId,
            to: recipientEmail,
            subject: subject,
            type: emailType,
            timestamp: new Date().toISOString()
        });

        res.json({
            success: true,
            message: 'E-mail enviado com sucesso!',
            messageId: info.messageId
        });

    } catch (error) {
        console.error('Erro ao enviar e-mail:', error);
        res.status(500).json({
            success: false,
            message: 'Erro ao enviar e-mail. Tente novamente.',
            error: error.message
        });
    }
});

// Rota para verificar status do servidor
app.get('/status', (req, res) => {
    res.json({
        status: 'online',
        timestamp: new Date().toISOString(),
        message: 'Servidor RNC funcionando corretamente'
    });
});

// Iniciar servidor
app.listen(PORT, () => {
    console.log(`🚀 Servidor RNC rodando em http://localhost:${PORT}`);
    console.log(`📧 Sistema de e-mail configurado`);
    console.log(`📄 Acesse: http://localhost:${PORT}`);
});

module.exports = app; 