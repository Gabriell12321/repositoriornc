-- =====================================================
-- SISTEMA DE RELATÓRIOS DE NÃO CONFORMIDADES - IPPEL
-- Banco de Dados SQLite
-- =====================================================

-- Tabela de usuários do sistema
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    department TEXT NOT NULL,
    role TEXT NOT NULL, -- 'inspector', 'manager', 'supervisor', 'admin'
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela principal de relatórios RNC
CREATE TABLE rnc_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rnc_number TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    equipment TEXT,
    assembly TEXT,
    model TEXT,
    quantity INTEGER,
    client TEXT,
    material TEXT,
    purchase_order TEXT,
    responsible_name TEXT,
    inspector_id INTEGER,
    area_responsible TEXT,
    status TEXT DEFAULT 'open', -- 'open', 'in_progress', 'resolved', 'closed'
    priority TEXT DEFAULT 'medium', -- 'low', 'medium', 'high', 'critical'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (inspector_id) REFERENCES users(id)
);

-- Tabela de detalhes técnicos do RNC
CREATE TABLE rnc_details (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rnc_id INTEGER NOT NULL,
    item_number INTEGER NOT NULL,
    description TEXT NOT NULL,
    instruction TEXT,
    cause TEXT,
    action TEXT,
    disposition TEXT, -- 'use_as_is', 'scrap', 'rework', 'return_stock', 'reject', 'return_supplier'
    inspection_result TEXT, -- 'approved', 'rejected', 'pending'
    related_rnc TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (rnc_id) REFERENCES rnc_reports(id) ON DELETE CASCADE
);

-- Tabela de assinaturas e aprovações
CREATE TABLE rnc_signatures (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rnc_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    signature_type TEXT NOT NULL, -- 'inspector', 'manager', 'supervisor', 'engineering'
    signature_data TEXT, -- Base64 da assinatura digital
    signed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (rnc_id) REFERENCES rnc_reports(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Tabela de comunicação por email
CREATE TABLE email_threads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rnc_id INTEGER NOT NULL,
    thread_id TEXT UNIQUE NOT NULL, -- ID único da conversa
    subject TEXT NOT NULL,
    status TEXT DEFAULT 'active', -- 'active', 'closed', 'archived'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (rnc_id) REFERENCES rnc_reports(id) ON DELETE CASCADE
);

-- Tabela de mensagens de email
CREATE TABLE email_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    thread_id INTEGER NOT NULL,
    message_id TEXT UNIQUE NOT NULL, -- ID único da mensagem
    from_email TEXT NOT NULL,
    to_email TEXT NOT NULL,
    cc_email TEXT,
    bcc_email TEXT,
    subject TEXT NOT NULL,
    body TEXT NOT NULL,
    html_body TEXT,
    attachments TEXT, -- JSON com lista de anexos
    direction TEXT NOT NULL, -- 'outbound', 'inbound'
    status TEXT DEFAULT 'sent', -- 'sent', 'delivered', 'failed', 'bounced'
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    delivered_at TIMESTAMP,
    FOREIGN KEY (thread_id) REFERENCES email_threads(id) ON DELETE CASCADE
);

-- Tabela de notificações
CREATE TABLE notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    rnc_id INTEGER,
    type TEXT NOT NULL, -- 'new_rnc', 'update_rnc', 'email_received', 'approval_required'
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (rnc_id) REFERENCES rnc_reports(id) ON DELETE CASCADE
);

-- Tabela de configurações do sistema
CREATE TABLE system_config (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    config_key TEXT UNIQUE NOT NULL,
    config_value TEXT NOT NULL,
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de logs do sistema
CREATE TABLE system_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    level TEXT NOT NULL, -- 'info', 'warning', 'error', 'debug'
    category TEXT NOT NULL, -- 'email', 'database', 'auth', 'rnc'
    message TEXT NOT NULL,
    details TEXT, -- JSON com detalhes adicionais
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- ÍNDICES PARA PERFORMANCE
-- =====================================================

CREATE INDEX idx_rnc_reports_status ON rnc_reports(status);
CREATE INDEX idx_rnc_reports_inspector ON rnc_reports(inspector_id);
CREATE INDEX idx_rnc_reports_created ON rnc_reports(created_at);
CREATE INDEX idx_email_threads_rnc ON email_threads(rnc_id);
CREATE INDEX idx_email_messages_thread ON email_messages(thread_id);
CREATE INDEX idx_email_messages_direction ON email_messages(direction);
CREATE INDEX idx_notifications_user ON notifications(user_id);
CREATE INDEX idx_notifications_read ON notifications(is_read);
CREATE INDEX idx_system_logs_level ON system_logs(level);
CREATE INDEX idx_system_logs_category ON system_logs(category);

-- =====================================================
-- DADOS INICIAIS
-- =====================================================

-- Inserir usuários padrão
INSERT INTO users (name, email, department, role) VALUES
('João Silva', 'joao.silva@ippel.com', 'Qualidade', 'inspector'),
('Maria Santos', 'maria.santos@ippel.com', 'Engenharia', 'manager'),
('Pedro Costa', 'pedro.costa@ippel.com', 'Produção', 'supervisor'),
('Ana Oliveira', 'ana.oliveira@ippel.com', 'Administração', 'admin');

-- Inserir configurações do sistema
INSERT INTO system_config (config_key, config_value, description) VALUES
('smtp_host', 'smtp.gmail.com', 'Servidor SMTP'),
('smtp_port', '587', 'Porta SMTP'),
('smtp_username', 'sistema@ippel.com', 'Email do sistema'),
('smtp_password', '', 'Senha do email (criptografada)'),
('email_from_name', 'Sistema IPPEL', 'Nome do remetente'),
('auto_reply_enabled', 'true', 'Resposta automática habilitada'),
('notification_enabled', 'true', 'Notificações habilitadas'),
('max_attachments', '10', 'Máximo de anexos por email'),
('email_retry_attempts', '3', 'Tentativas de reenvio de email');

-- =====================================================
-- TRIGGERS PARA ATUALIZAÇÃO AUTOMÁTICA
-- =====================================================

-- Trigger para atualizar updated_at
CREATE TRIGGER update_rnc_reports_timestamp 
    AFTER UPDATE ON rnc_reports
    BEGIN
        UPDATE rnc_reports SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;

CREATE TRIGGER update_email_threads_timestamp 
    AFTER UPDATE ON email_threads
    BEGIN
        UPDATE email_threads SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;

CREATE TRIGGER update_system_config_timestamp 
    AFTER UPDATE ON system_config
    BEGIN
        UPDATE system_config SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END; 