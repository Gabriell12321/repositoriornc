#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CONFIGURAÇÃO LOCAL PARA ACESSO VIA IP - IPPEL
Configurações para acesso aos RNCs via IP local
"""

import socket
import os
from datetime import datetime

class LocalConfig:
    """Configurações para acesso local"""
    
    @staticmethod
    def get_local_ip():
        """Obtém o IP local da máquina"""
        try:
            # Conectar a um servidor externo para descobrir IP local
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except:
            try:
                # Fallback: usar hostname
                hostname = socket.gethostname()
                local_ip = socket.gethostbyname(hostname)
                return local_ip
            except:
                # Último fallback
                return "127.0.0.1"
    
    @staticmethod
    def get_server_url():
        """Obtém URL completa do servidor"""
        ip = LocalConfig.get_local_ip()
        return f"http://{ip}:5000"
    
    @staticmethod
    def get_rnc_view_url(token):
        """Gera URL para visualização de RNC"""
        base_url = LocalConfig.get_server_url()
        return f"{base_url}/rnc/view/{token}"
    
    @staticmethod
    def print_network_info():
        """Imprime informações de rede"""
        print("=" * 60)
        print("🌐 INFORMAÇÕES DE REDE - SISTEMA IPPEL")
        print("=" * 60)
        
        local_ip = LocalConfig.get_local_ip()
        server_url = LocalConfig.get_server_url()
        
        print(f"📱 IP Local: {local_ip}")
        print(f"🌍 URL do Servidor: {server_url}")
        print(f"📋 Interface Web: {server_url}")
        print(f"📧 Links de RNC: {server_url}/rnc/view/[TOKEN]")
        print()
        print("🔗 Para acessar de outros dispositivos na rede:")
        print(f"   • Computador: {server_url}")
        print(f"   • Celular/Tablet: {server_url}")
        print(f"   • RNC específico: {server_url}/rnc/view/[TOKEN]")
        print()
        print("⚠️  IMPORTANTE:")
        print("   • Certifique-se de que o firewall permite conexões na porta 5000")
        print("   • Todos os dispositivos devem estar na mesma rede Wi-Fi")
        print("   • O servidor deve estar rodando para que os links funcionem")
        print("=" * 60)

class EmailConfig:
    """Configurações de email para links locais"""
    
    @staticmethod
    def get_email_template_with_local_ip():
        """Retorna template de email com IP local"""
        local_ip = LocalConfig.get_local_ip()
        base_url = f"http://{local_ip}:5000"
        
        return f"""
        <div style="background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%); 
                    border: 2px solid #2196f3; border-radius: 10px; padding: 20px; margin-bottom: 20px;">
            <h3 style="color: #1565c0; margin-top: 0; text-align: center;">🔗 Acesse o RNC Completo</h3>
            <div style="text-align: center; margin: 20px 0;">
                <a href="{base_url}/rnc/view/[TOKEN]" 
                   style="background: linear-gradient(135deg, #2196f3 0%, #1976d2 100%); 
                          color: white; padding: 15px 30px; text-decoration: none; 
                          border-radius: 25px; font-weight: bold; font-size: 16px;
                          display: inline-block; box-shadow: 0 4px 15px rgba(33, 150, 243, 0.3);">
                    📋 Ver RNC Completo
                </a>
            </div>
            <div style="text-align: center; color: #1565c0; font-size: 14px;">
                <strong>Código de Acesso:</strong> [CODIGO]
            </div>
            <div style="text-align: center; color: #1565c0; font-size: 12px; margin-top: 10px;">
                ⏰ Link válido até: [DATA_EXPIRACAO]
            </div>
            <div style="text-align: center; color: #1565c0; font-size: 11px; margin-top: 10px;">
                🌐 Acesse via: {base_url}
            </div>
        </div>
        """

class SecurityConfig:
    """Configurações de segurança para links locais"""
    
    @staticmethod
    def get_security_recommendations():
        """Retorna recomendações de segurança"""
        return {
            "firewall": "Configure o firewall para permitir conexões na porta 5000",
            "network": "Use apenas em redes confiáveis (rede corporativa)",
            "access_control": "Implemente controle de acesso por IP se necessário",
            "monitoring": "Monitore logs de acesso regularmente",
            "backup": "Faça backup regular do banco de dados",
            "updates": "Mantenha o sistema atualizado"
        }

# Função principal para mostrar informações
def main():
    """Função principal para mostrar informações de configuração"""
    LocalConfig.print_network_info()
    
    print("\n📧 TEMPLATE DE EMAIL COM IP LOCAL:")
    print(EmailConfig.get_email_template_with_local_ip())
    
    print("\n🔒 RECOMENDAÇÕES DE SEGURANÇA:")
    recommendations = SecurityConfig.get_security_recommendations()
    for key, value in recommendations.items():
        print(f"   • {value}")

if __name__ == "__main__":
    main() 