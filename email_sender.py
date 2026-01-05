"""
Módulo para envío de reportes de inventario por email
"""
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
from typing import List, Dict
import streamlit as st


class EmailSender:
    """Gestiona el envío de reportes por email"""

    def __init__(self):
        """Inicializa configuración de email desde secrets"""
        try:
            self.smtp_server = st.secrets["email"]["smtp_server"]
            self.smtp_port = st.secrets["email"]["smtp_port"]
            self.sender_email = st.secrets["email"]["sender_email"]
            self.sender_password = st.secrets["email"]["sender_password"]
            self.configured = True
        except (KeyError, FileNotFoundError):
            self.configured = False

    def generate_email_body(self, session_status: Dict, validation_results: Dict,
                           missing_files: List[str]) -> str:
        """
        Genera el cuerpo HTML del email

        Args:
            session_status: Estado de la sesión
            validation_results: Resultados de validación
            missing_files: Lista de archivos faltantes

        Returns:
            HTML del email
        """
        # Fecha y hora actual
        now = datetime.now().strftime("%d/%m/%Y %H:%M")

        # Construir tabla de errores principales
        errors_table = ""
        if validation_results and validation_results.get("results"):
            errors_table = """
            <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                <thead>
                    <tr style="background-color: #003087; color: white;">
                        <th style="padding: 10px; text-align: left; border: 1px solid #ddd;">Archivo</th>
                        <th style="padding: 10px; text-align: center; border: 1px solid #ddd;">Errores</th>
                        <th style="padding: 10px; text-align: center; border: 1px solid #ddd;">Advertencias</th>
                    </tr>
                </thead>
                <tbody>
            """

            for result in validation_results["results"]:
                if result["errors"] or result["warnings"]:
                    errors_table += f"""
                    <tr>
                        <td style="padding: 10px; border: 1px solid #ddd;">{result['filename']}</td>
                        <td style="padding: 10px; text-align: center; border: 1px solid #ddd; color: #dc3545;">{len(result['errors'])}</td>
                        <td style="padding: 10px; text-align: center; border: 1px solid #ddd; color: #856404;">{len(result['warnings'])}</td>
                    </tr>
                    """

            errors_table += "</tbody></table>"
        else:
            errors_table = "<p style='color: #28a745;'>✅ No se encontraron errores</p>"

        # Construir lista de archivos faltantes
        missing_list = ""
        if missing_files:
            missing_list = "<ul style='margin: 10px 0; padding-left: 20px;'>"
            for file in missing_files:
                missing_list += f"<li style='margin: 5px 0;'>🍺 {file}</li>"
            missing_list += "</ul>"
        else:
            missing_list = "<p style='color: #28a745;'>✅ No hay archivos faltantes</p>"

        # Template HTML
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .header {{
                    background: linear-gradient(135deg, #003087 0%, #004ba0 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                    border-radius: 10px 10px 0 0;
                }}
                .content {{
                    padding: 20px;
                    background-color: #ffffff;
                }}
                .section {{
                    margin: 20px 0;
                    padding: 15px;
                    background-color: #f8f9fa;
                    border-left: 4px solid #FDB71A;
                    border-radius: 5px;
                }}
                .section h3 {{
                    color: #003087;
                    margin-top: 0;
                }}
                .metrics {{
                    display: table;
                    width: 100%;
                    margin: 15px 0;
                }}
                .metric {{
                    display: table-row;
                }}
                .metric-label {{
                    display: table-cell;
                    padding: 8px;
                    font-weight: bold;
                    color: #003087;
                }}
                .metric-value {{
                    display: table-cell;
                    padding: 8px;
                    text-align: right;
                }}
                .footer {{
                    background-color: #f8f9fa;
                    padding: 20px;
                    text-align: center;
                    border-radius: 0 0 10px 10px;
                    margin-top: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1 style="margin: 0; font-size: 28px;">🍺 AB InBev Perú</h1>
                <p style="margin: 10px 0 0 0; color: #FDB71A; font-size: 18px;">Reporte de Revisión de Inventarios</p>
            </div>

            <div class="content">
                <div class="section">
                    <h3>📊 RESUMEN EJECUTIVO</h3>
                    <div class="metrics">
                        <div class="metric">
                            <span class="metric-label">📅 Sesión:</span>
                            <span class="metric-value">{session_status['session_id']}</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">🍺 Total Esperados:</span>
                            <span class="metric-value">{session_status['total_expected']}</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">✅ Recibidos:</span>
                            <span class="metric-value" style="color: #28a745;">{session_status['total_received']}</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">⏳ Faltantes:</span>
                            <span class="metric-value" style="color: #dc3545;">{session_status['total_missing']}</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">🎯 Completado:</span>
                            <span class="metric-value" style="color: #FDB71A; font-weight: bold;">{session_status['completion_percentage']:.1f}%</span>
                        </div>
                    </div>
                </div>

                <div class="section">
                    <h3>⚠️ ERRORES PRINCIPALES</h3>
                    {errors_table}
                </div>

                <div class="section">
                    <h3>🍺⏳ ARCHIVOS FALTANTES</h3>
                    {missing_list}
                </div>

                <div style="margin: 30px 0; padding: 20px; background-color: #e7f3ff; border-radius: 5px; text-align: center;">
                    <p style="margin: 0; color: #003087;">📎 <strong>Ver detalles completos en el archivo adjunto</strong></p>
                </div>
            </div>

            <div class="footer">
                <p style="margin: 0; color: #003087; font-weight: bold;">AB InBev Perú | Sistema de Revisión de Inventarios</p>
                <p style="margin: 5px 0 0 0; color: #6c757d; font-size: 12px;">Generado automáticamente el {now}</p>
            </div>
        </body>
        </html>
        """

        return html

    def send_report(self, recipients: List[str], cc: List[str], session_id: str,
                   session_status: Dict, validation_results: Dict,
                   missing_files: List[str], attachment_data: bytes) -> bool:
        """
        Envía el reporte por email

        Args:
            recipients: Lista de destinatarios
            cc: Lista de destinatarios en copia
            session_id: ID de la sesión (formato: YYYY-MM)
            session_status: Estado de la sesión
            validation_results: Resultados de validación
            missing_files: Lista de archivos faltantes
            attachment_data: Datos del archivo Excel adjunto

        Returns:
            True si se envió correctamente, False en caso contrario
        """
        if not self.configured:
            return False

        try:
            # Crear mensaje
            msg = MIMEMultipart('alternative')

            # Asunto con formato específico
            year, month = session_id.split('-')
            month_names = {
                '01': 'Enero', '02': 'Febrero', '03': 'Marzo', '04': 'Abril',
                '05': 'Mayo', '06': 'Junio', '07': 'Julio', '08': 'Agosto',
                '09': 'Septiembre', '10': 'Octubre', '11': 'Noviembre', '12': 'Diciembre'
            }
            month_name = month_names.get(month, month)

            msg['Subject'] = f"*PE Control Interno - Revisión de Inventarios - {month_name} {year}"
            msg['From'] = self.sender_email
            msg['To'] = ', '.join(recipients)
            if cc:
                msg['Cc'] = ', '.join(cc)

            # Cuerpo del email
            html_body = self.generate_email_body(session_status, validation_results, missing_files)
            msg.attach(MIMEText(html_body, 'html'))

            # Adjuntar archivo Excel
            if attachment_data:
                attachment = MIMEBase('application', 'vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                attachment.set_payload(attachment_data)
                encoders.encode_base64(attachment)

                filename = f"reporte_validacion_{session_id}_{datetime.now().strftime('%Y%m%d')}.xlsx"
                attachment.add_header('Content-Disposition', f'attachment; filename={filename}')
                msg.attach(attachment)

            # Enviar email
            all_recipients = recipients + (cc if cc else [])

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)

            return True

        except Exception as e:
            st.error(f"Error al enviar email: {str(e)}")
            return False
