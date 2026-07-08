"""
Tool de envío de email por SMTP (Gmail).
Usa APP_PASSWORD_GMAIL para autenticación.
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from langchain_core.tools import tool


@tool
def send_email(recipient_email: str, subject: str, body: str) -> str:
    """Envia un email via SMTP de Gmail al destinatario indicado

    Args:
        recipient_email: Direccion de correo del destinatario
        subject: Asunto del email
        body: Cuerpo del email en texto plano.
    """
    sender_email = os.getenv("EMAIL_REMITENTE")
    app_password = os.getenv("APP_PASSWORD_GMAIL")

    if not sender_email or not app_password:
        return "Error: Variables EMAIL_REMITENTE o APP_PASSWORD_GMAIL no configuradas en .env"
    
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = recipient_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain", "utf-8"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, app_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())
        return f"Email enviado exitosamente a {recipient_email}"
    except Exception as e:
        return f"Error al enviar email: {str(e)}"