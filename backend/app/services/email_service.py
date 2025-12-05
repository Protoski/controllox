"""
Servicio de Email
Sistema de Gases Medicinales MSPBS
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

from app.core.config import settings


async def send_recovery_email(email: str, nombre: str, token: str):
    """
    Enviar email de recuperación de contraseña
    """
    # Verificar que SMTP esté configurado
    if not all([settings.SMTP_HOST, settings.SMTP_USER, settings.SMTP_PASSWORD]):
        print("SMTP no configurado, no se puede enviar email")
        return
    
    # Construir URL de recuperación
    # En producción, esto debería ser la URL del frontend
    recovery_url = f"{settings.BACKEND_CORS_ORIGINS[0]}/reset-password?token={token}"
    
    # Crear mensaje
    message = MIMEMultipart("alternative")
    message["Subject"] = "Recuperación de Contraseña - Sistema MSPBS"
    message["From"] = settings.EMAIL_FROM
    message["To"] = email
    
    # Texto plano
    text = f"""
    Hola {nombre},
    
    Has solicitado restablecer tu contraseña en el Sistema de Gases Medicinales MSPBS.
    
    Para crear una nueva contraseña, haz clic en el siguiente enlace:
    {recovery_url}
    
    Este enlace expirará en 24 horas.
    
    Si no solicitaste este cambio, ignora este mensaje.
    
    Saludos,
    Sistema de Gases Medicinales
    DGGIES - MSPBS
    """
    
    # HTML
    html = f"""
    <html>
      <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px;">
          <h2 style="color: #003366;">Recuperación de Contraseña</h2>
          <p>Hola <strong>{nombre}</strong>,</p>
          <p>Has solicitado restablecer tu contraseña en el <strong>Sistema de Gases Medicinales MSPBS</strong>.</p>
          <p>Para crear una nueva contraseña, haz clic en el siguiente botón:</p>
          <div style="text-align: center; margin: 30px 0;">
            <a href="{recovery_url}" 
               style="background-color: #003366; color: white; padding: 12px 30px; 
                      text-decoration: none; border-radius: 5px; display: inline-block;">
              Restablecer Contraseña
            </a>
          </div>
          <p style="font-size: 12px; color: #666;">
            Este enlace expirará en 24 horas.<br>
            Si no solicitaste este cambio, ignora este mensaje.
          </p>
          <hr style="margin: 30px 0; border: none; border-top: 1px solid #ddd;">
          <p style="font-size: 12px; color: #666; text-align: center;">
            Sistema de Gases Medicinales<br>
            DGGIES - Ministerio de Salud y Bienestar Social<br>
            Paraguay
          </p>
        </div>
      </body>
    </html>
    """
    
    # Adjuntar partes
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")
    message.attach(part1)
    message.attach(part2)
    
    # Enviar email
    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.EMAIL_FROM, email, message.as_string())
        print(f"Email enviado exitosamente a {email}")
    except Exception as e:
        print(f"Error enviando email: {e}")
        raise


async def send_notification_email(
    email: str,
    subject: str,
    message_text: str,
    message_html: Optional[str] = None
):
    """
    Enviar email de notificación genérico
    """
    if not all([settings.SMTP_HOST, settings.SMTP_USER, settings.SMTP_PASSWORD]):
        print("SMTP no configurado, no se puede enviar email")
        return
    
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = settings.EMAIL_FROM
    message["To"] = email
    
    part1 = MIMEText(message_text, "plain")
    message.attach(part1)
    
    if message_html:
        part2 = MIMEText(message_html, "html")
        message.attach(part2)
    
    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.EMAIL_FROM, email, message.as_string())
        print(f"Email de notificación enviado a {email}")
    except Exception as e:
        print(f"Error enviando email de notificación: {e}")
        raise
