"""
Tool de envío de email vía Resend (API HTTPS).

Se usa la API HTTP de Resend en vez de SMTP porque algunos proveedores de
hosting (p. ej. droplets de DigitalOcean sin desbloqueo explícito) bloquean
el tráfico saliente en los puertos SMTP (587/465), pero el puerto 443 (HTTPS)
siempre está disponible.
"""

import os

import resend
from langchain_core.tools import tool


@tool
def send_email(recipient_email: str, subject: str, body: str) -> str:
    """Envia un email vía Resend al destinatario indicado

    Args:
        recipient_email: Direccion de correo del destinatario
        subject: Asunto del email
        body: Cuerpo del email en texto plano.
    """
    api_key = os.getenv("RESEND_API_KEY")
    sender_email = os.getenv("RESEND_FROM_EMAIL")

    if not api_key or not sender_email:
        return "Error: Variables RESEND_API_KEY o RESEND_FROM_EMAIL no configuradas en .env"

    resend.api_key = api_key

    try:
        resend.Emails.send({
            "from": sender_email,
            "to": [recipient_email],
            "subject": subject,
            "text": body,
        })
        return f"Email enviado exitosamente a {recipient_email}"
    except Exception as e:
        return f"Error al enviar email: {str(e)}"
