#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Serviço para geração de PDFs das RNCs
"""

import os
import tempfile
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from services.db import DB_PATH
import sqlite3

logger = logging.getLogger('ippel.services.pdf_generator')

class PDFGenerator:
    """Gerador de PDFs para RNCs"""
    
    def __init__(self):
        self.temp_dir = tempfile.gettempdir()
        self.pdf_dir = os.path.join(self.temp_dir, 'ippel_pdfs')
        os.makedirs(self.pdf_dir, exist_ok=True)
    
    def get_rnc_data(self, rnc_id: int) -> Optional[Dict[str, Any]]:
        """Obtém dados completos da RNC"""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Buscar dados da RNC com informações do usuário
            cursor.execute('''
                SELECT r.*, u.name as user_name, u.department as user_department,
                       au.name as assigned_user_name
                FROM rncs r
                LEFT JOIN users u ON r.user_id = u.id
                LEFT JOIN users au ON r.assigned_user_id = au.id
                WHERE r.id = ? AND r.is_deleted = 0
            ''', (rnc_id,))
            
            rnc_data = cursor.fetchone()
            if not rnc_data:
                conn.close()
                return None
            
            # Obter colunas
            columns = [desc[0] for desc in cursor.description]
            rnc_dict = dict(zip(columns, rnc_data))
            
            # Buscar dados de compartilhamento
            cursor.execute('''
                SELECT us.name, us.department
                FROM rnc_shares rs
                JOIN users us ON rs.shared_with_user_id = us.id
                WHERE rs.rnc_id = ?
            ''', (rnc_id,))
            
            shared_users = cursor.fetchall()
            rnc_dict['shared_users'] = [{'name': u[0], 'department': u[1]} for u in shared_users]
            
            conn.close()
            return rnc_dict
            
        except Exception as e:
            logger.error(f"Erro ao buscar dados da RNC {rnc_id}: {e}")
            return None
    
    def generate_pdf_reportlab(self, rnc_data: Dict[str, Any]) -> Optional[str]:
        """Gera PDF usando ReportLab (mais confiável)"""
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.lib import colors
            from reportlab.pdfgen import canvas
            
            # Criar arquivo temporário
            filename = f"RNC_{rnc_data.get('rnc_number', 'UNKNOWN')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            filepath = os.path.join(self.pdf_dir, filename)
            
            # Criar documento
            doc = SimpleDocTemplate(filepath, pagesize=A4)
            story = []
            
            # Estilos
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=18,
                spaceAfter=30,
                alignment=1,  # Centralizado
                textColor=colors.darkblue
            )
            
            subtitle_style = ParagraphStyle(
                'CustomSubtitle',
                parent=styles['Heading2'],
                fontSize=14,
                spaceAfter=20,
                textColor=colors.darkred
            )
            
            normal_style = styles['Normal']
            bold_style = ParagraphStyle(
                'Bold',
                parent=styles['Normal'],
                fontName='Helvetica-Bold'
            )
            
            # Título principal
            story.append(Paragraph("RELATÓRIO DE NÃO CONFORMIDADE INTERNA - RNC", title_style))
            story.append(Spacer(1, 20))
            
            # Informações básicas da RNC
            story.append(Paragraph(f"<b>RNC N°:</b> {rnc_data.get('rnc_number', 'N/A')}", subtitle_style))
            story.append(Spacer(1, 10))
            
            # Tabela de informações
            info_data = [
                ['Campo', 'Valor'],
                ['Título', rnc_data.get('title', 'N/A')],
                ['Equipamento', rnc_data.get('equipment', 'N/A')],
                ['Cliente', rnc_data.get('client', 'N/A')],
                ['Prioridade', rnc_data.get('priority', 'N/A')],
                ['Status', rnc_data.get('status', 'N/A')],
                ['Criado por', rnc_data.get('user_name', 'N/A')],
                ['Departamento', rnc_data.get('user_department', 'N/A')],
                ['Data de Criação', rnc_data.get('created_at', 'N/A')],
                ['Atribuído a', rnc_data.get('assigned_user_name', 'N/A') or 'Não atribuído']
            ]
            
            info_table = Table(info_data, colWidths=[2*inch, 4*inch])
            info_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(info_table)
            story.append(Spacer(1, 20))
            
            # Descrição
            story.append(Paragraph("<b>Descrição da RNC:</b>", bold_style))
            story.append(Paragraph(rnc_data.get('description', 'N/A'), normal_style))
            story.append(Spacer(1, 20))
            
            # Disposição
            story.append(Paragraph("<b>Disposição:</b>", bold_style))
            disposition_data = [
                ['Usar como está', '✓' if rnc_data.get('disposition_usar') else '✗'],
                ['Retrabalhar', '✓' if rnc_data.get('disposition_retrabalhar') else '✗'],
                ['Rejeitar', '✓' if rnc_data.get('disposition_rejeitar') else '✗'],
                ['Sucata', '✓' if rnc_data.get('disposition_sucata') else '✗'],
                ['Devolver ao estoque', '✓' if rnc_data.get('disposition_devolver_estoque') else '✗'],
                ['Devolver ao fornecedor', '✓' if rnc_data.get('disposition_devolver_fornecedor') else '✗']
            ]
            
            disp_table = Table(disposition_data, colWidths=[3*inch, 1*inch])
            disp_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey)
            ]))
            
            story.append(disp_table)
            story.append(Spacer(1, 20))
            
            # Inspeção
            story.append(Paragraph("<b>Resultado da Inspeção:</b>", bold_style))
            inspection_data = [
                ['Aprovado', '✓' if rnc_data.get('inspection_aprovado') else '✗'],
                ['Reprovado', '✓' if rnc_data.get('inspection_reprovado') else '✗'],
                ['Ver RNC', '✓' if rnc_data.get('inspection_ver_rnc') else '✗']
            ]
            
            insp_table = Table(inspection_data, colWidths=[3*inch, 1*inch])
            insp_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey)
            ]))
            
            story.append(insp_table)
            story.append(Spacer(1, 20))
            
            # Assinaturas
            story.append(Paragraph("<b>Assinaturas:</b>", bold_style))
            signatures_data = [
                ['Tipo', 'Nome', 'Data'],
                ['Inspeção', rnc_data.get('signature_inspection_name', 'N/A'), rnc_data.get('signature_inspection_date', 'N/A')],
                ['Engenharia', rnc_data.get('signature_engineering_name', 'N/A'), rnc_data.get('signature_engineering_date', 'N/A')],
                ['Inspeção 2', rnc_data.get('signature_inspection2_name', 'N/A'), rnc_data.get('signature_inspection2_date', 'N/A')]
            ]
            
            sig_table = Table(signatures_data, colWidths=[2*inch, 2.5*inch, 1.5*inch])
            sig_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(sig_table)
            story.append(Spacer(1, 20))
            
            # Usuários compartilhados
            if rnc_data.get('shared_users'):
                story.append(Paragraph("<b>Compartilhado com:</b>", bold_style))
                shared_data = [['Nome', 'Departamento']]
                for user in rnc_data['shared_users']:
                    shared_data.append([user['name'], user['department']])
                
                shared_table = Table(shared_data, colWidths=[3*inch, 3*inch])
                shared_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('GRID', (0, 0), (-1, -1), 1, colors.grey)
                ]))
                
                story.append(shared_table)
            
            # Rodapé
            story.append(Spacer(1, 30))
            story.append(Paragraph(f"Gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}", normal_style))
            story.append(Paragraph("Sistema IPPEL - Relatórios de Não Conformidade", normal_style))
            
            # Construir PDF
            doc.build(story)
            
            logger.info(f"PDF gerado com sucesso: {filepath}")
            return filepath
            
        except ImportError:
            logger.error("ReportLab não está instalado. Instalando dependências...")
            return None
        except Exception as e:
            logger.error(f"Erro ao gerar PDF com ReportLab: {e}")
            return None
    
    def generate_pdf_weasyprint(self, rnc_data: Dict[str, Any]) -> Optional[str]:
        """Gera PDF usando WeasyPrint com template completo da visualização"""
        try:
            from weasyprint import HTML, CSS
            from weasyprint.text.fonts import FontConfiguration
            
            # Criar arquivo temporário
            filename = f"RNC_{rnc_data.get('rnc_number', 'UNKNOWN')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            filepath = os.path.join(self.pdf_dir, filename)
            
            # Gerar HTML completo usando o template da visualização
            html_content = self._generate_complete_html(rnc_data)
            
            # Configurar fontes
            font_config = FontConfiguration()
            
            # Gerar PDF
            HTML(string=html_content).write_pdf(
                filepath,
                font_config=font_config
            )
            
            logger.info(f"PDF gerado com sucesso com WeasyPrint: {filepath}")
            return filepath
            
        except ImportError:
            logger.error("WeasyPrint não está instalado")
            return None
        except Exception as e:
            logger.error(f"Erro ao gerar PDF com WeasyPrint: {e}")
            return None
    
    def _generate_html_content(self, rnc_data: Dict[str, Any]) -> str:
        """Gera conteúdo HTML para conversão em PDF"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>RNC {rnc_data.get('rnc_number', 'N/A')}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ text-align: center; margin-bottom: 30px; }}
                .title {{ color: #1a365d; font-size: 24px; font-weight: bold; }}
                .subtitle {{ color: #c53030; font-size: 18px; margin: 20px 0; }}
                .info-table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                .info-table th, .info-table td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                .info-table th {{ background-color: #f2f2f2; font-weight: bold; }}
                .section {{ margin: 20px 0; }}
                .section-title {{ font-weight: bold; margin-bottom: 10px; }}
                .checkbox-table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
                .checkbox-table td {{ border: 1px solid #ddd; padding: 5px; }}
                .footer {{ margin-top: 40px; text-align: center; font-size: 12px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="header">
                <div class="title">RELATÓRIO DE NÃO CONFORMIDADE INTERNA - RNC</div>
                <div class="subtitle">RNC N°: {rnc_data.get('rnc_number', 'N/A')}</div>
            </div>
            
            <table class="info-table">
                <tr><th>Campo</th><th>Valor</th></tr>
                <tr><td>Título</td><td>{rnc_data.get('title', 'N/A')}</td></tr>
                <tr><td>Equipamento</td><td>{rnc_data.get('equipment', 'N/A')}</td></tr>
                <tr><td>Cliente</td><td>{rnc_data.get('client', 'N/A')}</td></tr>
                <tr><td>Prioridade</td><td>{rnc_data.get('priority', 'N/A')}</td></tr>
                <tr><td>Status</td><td>{rnc_data.get('status', 'N/A')}</td></tr>
                <tr><td>Criado por</td><td>{rnc_data.get('user_name', 'N/A')}</td></tr>
                <tr><td>Departamento</td><td>{rnc_data.get('user_department', 'N/A')}</td></tr>
                <tr><td>Data de Criação</td><td>{rnc_data.get('created_at', 'N/A')}</td></tr>
                <tr><td>Atribuído a</td><td>{rnc_data.get('assigned_user_name', 'N/A') or 'Não atribuído'}</td></tr>
            </table>
            
            <div class="section">
                <div class="section-title">Descrição da RNC:</div>
                <p>{rnc_data.get('description', 'N/A')}</p>
            </div>
            
            <div class="section">
                <div class="section-title">Disposição:</div>
                <table class="checkbox-table">
                    <tr><td>Usar como está</td><td>{'✓' if rnc_data.get('disposition_usar') else '✗'}</td></tr>
                    <tr><td>Retrabalhar</td><td>{'✓' if rnc_data.get('disposition_retrabalhar') else '✗'}</td></tr>
                    <tr><td>Rejeitar</td><td>{'✓' if rnc_data.get('disposition_rejeitar') else '✗'}</td></tr>
                    <tr><td>Sucata</td><td>{'✓' if rnc_data.get('disposition_sucata') else '✗'}</td></tr>
                    <tr><td>Devolver ao estoque</td><td>{'✓' if rnc_data.get('disposition_devolver_estoque') else '✗'}</td></tr>
                    <tr><td>Devolver ao fornecedor</td><td>{'✓' if rnc_data.get('disposition_devolver_fornecedor') else '✗'}</td></tr>
                </table>
            </div>
            
            <div class="section">
                <div class="section-title">Resultado da Inspeção:</div>
                <table class="checkbox-table">
                    <tr><td>Aprovado</td><td>{'✓' if rnc_data.get('inspection_aprovado') else '✗'}</td></tr>
                    <tr><td>Reprovado</td><td>{'✓' if rnc_data.get('inspection_reprovado') else '✗'}</td></tr>
                    <tr><td>Ver RNC</td><td>{'✓' if rnc_data.get('inspection_ver_rnc') else '✗'}</td></tr>
                </table>
            </div>
            
            <div class="section">
                <div class="section-title">Assinaturas:</div>
                <table class="info-table">
                    <tr><th>Tipo</th><th>Nome</th><th>Data</th></tr>
                    <tr><td>Inspeção</td><td>{rnc_data.get('signature_inspection_name', 'N/A')}</td><td>{rnc_data.get('signature_inspection_date', 'N/A')}</td></tr>
                    <tr><td>Engenharia</td><td>{rnc_data.get('signature_engineering_name', 'N/A')}</td><td>{rnc_data.get('signature_engineering_date', 'N/A')}</td></tr>
                    <tr><td>Inspeção 2</td><td>{rnc_data.get('signature_inspection2_name', 'N/A')}</td><td>{rnc_data.get('signature_inspection2_date', 'N/A')}</td></tr>
                </table>
            </div>
            
            <div class="footer">
                <p>Gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}</p>
                <p>Sistema IPPEL - Relatórios de Não Conformidade</p>
            </div>
        </body>
        </html>
        """
        return html
    
    def generate_pdf(self, rnc_id: int) -> Optional[str]:
        """Gera PDF da RNC usando o melhor método disponível"""
        # Buscar dados da RNC
        rnc_data = self.get_rnc_data(rnc_id)
        if not rnc_data:
            logger.error(f"RNC {rnc_id} não encontrada")
            return None
        
        # Tentar ReportLab primeiro (mais confiável)
        pdf_path = self.generate_pdf_reportlab(rnc_data)
        if pdf_path:
            return pdf_path
        
        # Fallback para WeasyPrint
        pdf_path = self.generate_pdf_weasyprint(rnc_data)
        if pdf_path:
            return pdf_path
        
        logger.error("Nenhum método de geração de PDF disponível")
        return None
    
    def cleanup_old_pdfs(self, max_age_hours: int = 24):
        """Remove PDFs antigos para economizar espaço"""
        try:
            current_time = datetime.now()
            for filename in os.listdir(self.pdf_dir):
                if filename.endswith('.pdf'):
                    filepath = os.path.join(self.pdf_dir, filename)
                    file_time = datetime.fromtimestamp(os.path.getctime(filepath))
                    if (current_time - file_time).total_seconds() > max_age_hours * 3600:
                        os.remove(filepath)
                        logger.info(f"PDF antigo removido: {filename}")
        except Exception as e:
            logger.error(f"Erro ao limpar PDFs antigos: {e}")

# Instância global
pdf_generator = PDFGenerator()
