"""
Módulo para enviar el CSV final por correo electrónico vía Gmail SMTP
"""
import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_FROM = os.getenv("EMAIL_FROM", "alvarocrispin0604@gmail.com")
EMAIL_TO = os.getenv("EMAIL_TO", "alvaroecrispin@yape.com.pe")
EMAIL_APP_PASSWORD = os.getenv("EMAIL_APP_PASSWORD", "")


def send_csv_email(csv_path: Path) -> bool:
    """
    Envía el CSV final como adjunto por correo electrónico.

    Args:
        csv_path: Ruta al archivo CSV a enviar

    Returns:
        True si el envío fue exitoso, False en caso contrario
    """
    if not EMAIL_APP_PASSWORD:
        print("EMAIL_APP_PASSWORD no configurado en .env — se omite el envío de correo")
        print("   Genera un App Password en: https://myaccount.google.com/apppasswords")
        return False

    if not csv_path.exists():
        print(f"Archivo CSV no encontrado: {csv_path}")
        return False

    try:
        now = datetime.now()
        msg = MIMEMultipart()
        msg["From"] = EMAIL_FROM
        msg["To"] = EMAIL_TO
        msg["Subject"] = f"Gaming Price Scraper - Reporte {now.strftime('%Y-%m-%d %H:%M')}"

        body = (
            f"Se adjunta el reporte de precios gaming generado el "
            f"{now.strftime('%d/%m/%Y a las %H:%M:%S')}.\n\n"
            f"Archivo: {csv_path.name}\n\n"
            "Gaming Price Scraper"
        )
        msg.attach(MIMEText(body, "plain", "utf-8"))

        with open(csv_path, "rb") as f:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            f'attachment; filename="{csv_path.name}"',
        )
        msg.attach(part)

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.login(EMAIL_FROM, EMAIL_APP_PASSWORD)
            server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())

        print(f"Reporte enviado a {EMAIL_TO}")
        return True

    except smtplib.SMTPAuthenticationError:
        print("Error de autenticación Gmail — verifica EMAIL_APP_PASSWORD en .env")
        return False
    except Exception as e:
        print(f"Error enviando correo: {e}")
        return False
