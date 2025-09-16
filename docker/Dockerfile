# IPPEL RNC System - Dockerfile
# Sistema de gestão de RNCs com Flask e SQLite

FROM python:3.11-slim

# Configurar variáveis de ambiente
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV FLASK_APP=main_system.py
ENV FLASK_ENV=production

# Criar usuário não-root para segurança
RUN groupadd -r ippel && useradd -r -g ippel ippel

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libc6-dev \
    libffi-dev \
    libssl-dev \
    sqlite3 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Criar estrutura de diretórios
WORKDIR /app

# Copiar arquivos de dependências
COPY requirements.txt requirements_production.txt ./

# Instalar dependências Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements_production.txt

# Copiar código da aplicação
COPY . .

# Criar diretórios necessários com permissões apropriadas
RUN mkdir -p /app/instance /app/logs /app/backups /app/uploads /app/data && \
    chown -R ippel:ippel /app && \
    chmod -R 755 /app

# Configurar permissões especiais para diretórios de dados
RUN chmod 777 /app/logs /app/backups /app/uploads /app/data

# Expor porta da aplicação
EXPOSE 5000

# Script de inicialização
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Alterar para usuário não-root
USER ippel

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Comando padrão
ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["python", "main_system.py"]
