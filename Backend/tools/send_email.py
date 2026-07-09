"""
Tool de envío de email por SMTP (Gmail).
Usa APP_PASSWORD_GMAIL para autenticación.
"""

import os
import smtplib
import socket
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from langchain_core.tools import tool

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587


def _connect_smtp_ipv4(host: str, port: int, timeout: int = 15) -> smtplib.SMTP:
    """Conecta al SMTP forzando IPv4.

    Algunos hosts de contenedores (EasyPanel/Docker) tienen una interfaz IPv6
    sin ruta de salida real; si el DNS de smtp.gmail.com devuelve un registro
    AAAA, smtplib intenta esa IP primero y falla con
    OSError: [Errno 101] Network is unreachable. Resolver explícitamente a
    IPv4 evita ese fallo.
    """
    ipv4_addr = socket.getaddrinfo(host, port, socket.AF_INET)[0][4][0]
    server = smtplib.SMTP(timeout=timeout)
    server.connect(ipv4_addr, port)
    server.ehlo(host)
    return server


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
        with _connect_smtp_ipv4(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(sender_email, app_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())
        return f"Email enviado exitosamente a {recipient_email}"
    except Exception as e:
        return f"Error al enviar email: {str(e)}"