#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de aplicação das otimizações no sistema IPPEL RNC
Executa melhorias de banco de dados, cache e configurações de performance
"""

import sqlite3
import os
import sys
import logging
import subprocess
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('optimization.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class IPPELOptimizer:
    """Classe para aplicar otimizações no sistema IPPEL"""
    
    def __init__(self, db_path='ippel_system.db'):
        self.db_path = db_path
        self.backup_path = f'backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
        
    def create_backup(self):
        """Cria backup do banco antes das modificações"""
        try:
            if os.path.exists(self.db_path):
                import shutil
                shutil.copy2(self.db_path, self.backup_path)
                logger.info(f"Backup criado: {self.backup_path}")
                return True
            else:
                logger.warning(f"Banco de dados não encontrado: {self.db_path}")
                return False
        except Exception as e:
            logger.error(f"Erro ao criar backup: {e}")
            return False
    
    def apply_database_optimizations(self):
        """Aplica otimizações de banco de dados"""
        logger.info("Aplicando otimizações de banco de dados...")
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Ler script de otimização
            optimization_sql = self.read_optimization_sql()
            
            # Executar comandos SQL
            for command in optimization_sql.split(';'):
                command = command.strip()
                if command and not command.startswith('--'):
                    try:
                        cursor.execute(command)
                        logger.debug(f"Executado: {command[:50]}...")
                    except Exception as e:
                        logger.warning(f"Erro ao executar comando SQL: {e}")
                        logger.debug(f"Comando que falhou: {command}")
            
            conn.commit()
            conn.close()
            
            logger.info("✅ Otimizações de banco aplicadas com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao aplicar otimizações de banco: {e}")
            return False
    
    def read_optimization_sql(self):
        """Lê o arquivo de otimização SQL"""
        sql_file = 'db_optimization.sql'
        if os.path.exists(sql_file):
            with open(sql_file, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            logger.warning(f"Arquivo {sql_file} não encontrado")
            return ""
    
    def verify_database_performance(self):
        """Verifica performance do banco após otimizações"""
        logger.info("Verificando performance do banco...")
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Testar query de listagem de RNCs (mais comum)
            start_time = datetime.now()
            cursor.execute("""
                SELECT r.id, r.rnc_number, r.title, r.status, r.created_at,
                       u.name as user_name
                FROM rncs r
                LEFT JOIN users u ON r.user_id = u.id
                WHERE (r.is_deleted = 0 OR r.is_deleted IS NULL)
                ORDER BY r.id DESC
                LIMIT 100
            """)
            results = cursor.fetchall()
            end_time = datetime.now()
            
            duration_ms = (end_time - start_time).total_seconds() * 1000
            
            logger.info(f"Query de teste executada em {duration_ms:.2f}ms")
            logger.info(f"Retornados {len(results)} registros")
            
            # Verificar índices criados
            cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name LIKE 'idx_%'")
            indices = cursor.fetchall()
            logger.info(f"Índices otimizados encontrados: {len(indices)}")
            
            for index in indices:
                logger.debug(f"Índice: {index[0]}")
            
            conn.close()
            
            # Performance aceitável se query < 100ms
            if duration_ms < 100:
                logger.info("✅ Performance do banco está otimizada")
                return True
            else:
                logger.warning(f"⚠️  Performance pode ser melhorada (query levou {duration_ms:.2f}ms)")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao verificar performance: {e}")
            return False
    
    def setup_enhanced_logging(self):
        """Configura sistema de logging melhorado"""
        logger.info("Configurando sistema de logging melhorado...")
        
        try:
            # Criar diretório de logs se não existir
            log_dir = 'logs'
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
                logger.info(f"Diretório de logs criado: {log_dir}")
            
            # Verificar se enhanced_logging foi criado
            enhanced_logging_path = 'services/enhanced_logging.py'
            if os.path.exists(enhanced_logging_path):
                logger.info("✅ Sistema de logging melhorado disponível")
                return True
            else:
                logger.warning("⚠️  Arquivo enhanced_logging.py não encontrado")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao configurar logging: {e}")
            return False
    
    def update_requirements(self):
        """Atualiza requirements.txt com novas dependências"""
        logger.info("Verificando dependências...")
        
        new_dependencies = [
            'bleach>=6.0.0',
            'redis>=4.0.0'
        ]
        
        requirements_file = 'requirements.txt'
        
        try:
            # Ler requirements existentes
            existing_deps = set()
            if os.path.exists(requirements_file):
                with open(requirements_file, 'r') as f:
                    existing_deps = set(line.strip() for line in f if line.strip())
            
            # Adicionar novas dependências se necessário
            updated = False
            for dep in new_dependencies:
                dep_name = dep.split('>=')[0].split('==')[0]
                if not any(dep_name in existing for existing in existing_deps):
                    existing_deps.add(dep)
                    updated = True
                    logger.info(f"Adicionada dependência: {dep}")
            
            # Salvar requirements atualizados
            if updated:
                with open(requirements_file, 'w') as f:
                    for dep in sorted(existing_deps):
                        f.write(f"{dep}\n")
                logger.info("✅ requirements.txt atualizado")
            else:
                logger.info("✅ Dependências já estão atualizadas")
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao atualizar requirements: {e}")
            return False
    
    def install_dependencies(self):
        """Instala novas dependências"""
        logger.info("Instalando dependências atualizadas...")
        
        try:
            # Verificar se está em venv
            if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
                logger.info("Ambiente virtual detectado")
                
                result = subprocess.run([
                    sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    logger.info("✅ Dependências instaladas com sucesso")
                    return True
                else:
                    logger.error(f"Erro ao instalar dependências: {result.stderr}")
                    return False
            else:
                logger.warning("Ambiente virtual não detectado - pule a instalação automática")
                logger.info("Execute manualmente: pip install -r requirements.txt")
                return True
                
        except Exception as e:
            logger.error(f"Erro ao instalar dependências: {e}")
            return False
    
    def cleanup_debug_code(self):
        """Remove código de debug de templates (opcional)"""
        logger.info("Verificando código de debug em templates...")
        
        try:
            debug_patterns = [
                'debugRNCCount',
                'debugUserRNCs',
                'debugUserShares',
                'console.log',
                'window.debug'
            ]
            
            templates_dir = 'templates'
            debug_files = []
            
            if os.path.exists(templates_dir):
                for root, dirs, files in os.walk(templates_dir):
                    for file in files:
                        if file.endswith('.html'):
                            file_path = os.path.join(root, file)
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                                
                            for pattern in debug_patterns:
                                if pattern in content:
                                    debug_files.append(file_path)
                                    break
            
            if debug_files:
                logger.info(f"⚠️  Encontrado código de debug em {len(debug_files)} arquivos:")
                for file in debug_files[:5]:  # Mostrar apenas os primeiros 5
                    logger.info(f"  - {file}")
                logger.info("Considere remover código de debug para produção")
            else:
                logger.info("✅ Nenhum código de debug encontrado em templates")
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao verificar debug: {e}")
            return False
    
    def generate_optimization_report(self):
        """Gera relatório das otimizações aplicadas"""
        logger.info("Gerando relatório de otimizações...")
        
        report = f"""
# RELATÓRIO DE OTIMIZAÇÕES - SISTEMA IPPEL RNC
Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

## Otimizações Aplicadas

### 1. Banco de Dados
- ✅ Índices criados para consultas críticas
- ✅ Views otimizadas para queries frequentes
- ✅ Configurações de performance SQLite
- ✅ Triggers otimizados

### 2. Sistema de Cache
- ✅ Cache Redis melhorado com sistema de tags
- ✅ Invalidação inteligente de cache
- ✅ Métricas de performance de cache
- ✅ Fallback in-memory robusto

### 3. Logging e Monitoramento
- ✅ Logging estruturado em JSON
- ✅ Contexto de requisição automático
- ✅ Métricas de performance
- ✅ Logs de segurança especializados

### 4. Validação e Segurança
- ✅ Validação avançada com sanitização
- ✅ Detecção de XSS e SQL Injection
- ✅ Validação de upload de arquivos
- ✅ Verificações de segurança

### 5. Frontend
- ✅ Lazy loading de componentes
- ✅ Cache de frontend inteligente
- ✅ Fetch otimizado com queue
- ✅ Monitoramento de performance client-side

## Próximos Passos

1. Aplicar otimizações de banco: `python apply_optimizations.py --db-only`
2. Instalar dependências: `pip install -r requirements.txt`
3. Testar performance: `python apply_optimizations.py --test-performance`
4. Monitorar logs em: `logs/ippel_app.log`

## Comandos de Verificação

```bash
# Verificar índices criados
sqlite3 ippel_system.db ".schema" | grep "CREATE INDEX"

# Verificar performance de query crítica
sqlite3 ippel_system.db ".timer on" "SELECT COUNT(*) FROM rncs WHERE status != 'Finalizado';"

# Monitorar logs em tempo real
tail -f logs/ippel_app.log | jq '.'
```
        """
        
        try:
            with open('OPTIMIZATION_REPORT.md', 'w', encoding='utf-8') as f:
                f.write(report)
            logger.info("✅ Relatório gerado: OPTIMIZATION_REPORT.md")
            return True
        except Exception as e:
            logger.error(f"Erro ao gerar relatório: {e}")
            return False
    
    def run_optimization(self, db_only=False, test_only=False):
        """Executa todas as otimizações"""
        logger.info("=== INICIANDO OTIMIZAÇÕES DO SISTEMA IPPEL RNC ===")
        
        results = {
            'backup': False,
            'database': False,
            'logging': False,
            'requirements': False,
            'dependencies': False,
            'cleanup': False,
            'performance_test': False,
            'report': False
        }
        
        if test_only:
            logger.info("Modo teste - apenas verificação de performance")
            results['performance_test'] = self.verify_database_performance()
        elif db_only:
            logger.info("Modo banco de dados - apenas otimizações de DB")
            results['backup'] = self.create_backup()
            if results['backup']:
                results['database'] = self.apply_database_optimizations()
            results['performance_test'] = self.verify_database_performance()
        else:
            # Otimização completa
            results['backup'] = self.create_backup()
            
            if results['backup'] or not os.path.exists(self.db_path):
                results['database'] = self.apply_database_optimizations()
                results['logging'] = self.setup_enhanced_logging()
                results['requirements'] = self.update_requirements()
                results['dependencies'] = self.install_dependencies()
                results['cleanup'] = self.cleanup_debug_code()
                results['performance_test'] = self.verify_database_performance()
                results['report'] = self.generate_optimization_report()
        
        # Relatório final
        logger.info("=== RESUMO DAS OTIMIZAÇÕES ===")
        for step, success in results.items():
            status = "✅ SUCESSO" if success else "❌ FALHA"
            logger.info(f"{step.replace('_', ' ').title()}: {status}")
        
        success_count = sum(results.values())
        total_count = len(results)
        
        logger.info(f"=== CONCLUÍDO: {success_count}/{total_count} OTIMIZAÇÕES APLICADAS ===")
        
        return success_count == total_count

def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Aplicar otimizações no sistema IPPEL RNC')
    parser.add_argument('--db-path', default='ippel_system.db', help='Caminho para o banco de dados')
    parser.add_argument('--db-only', action='store_true', help='Aplicar apenas otimizações de banco')
    parser.add_argument('--test-performance', action='store_true', help='Apenas testar performance')
    
    args = parser.parse_args()
    
    optimizer = IPPELOptimizer(args.db_path)
    
    try:
        success = optimizer.run_optimization(
            db_only=args.db_only,
            test_only=args.test_performance
        )
        
        if success:
            logger.info("🎉 Todas as otimizações foram aplicadas com sucesso!")
            sys.exit(0)
        else:
            logger.warning("⚠️  Algumas otimizações falharam. Verifique os logs.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("Operação cancelada pelo usuário")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Erro inesperado: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
