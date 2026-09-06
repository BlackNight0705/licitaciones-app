import base64
import asyncio
import resend
import httpx
from backend.app.core.config import settings

resend.api_key = settings.EMAIL_API_KEY

#este servicio es para enviar correos de activación de licitaciones a los clientes. Se utiliza en el endpoint que activa la licitación formal y envía el correo con el documento adjunto.
async def enviar_correo(destinatario: str, asunto: str, contenido: str, adjunto_url: str = None, nombre_archivo: str = "propuesta.pdf"):
    params = {
        "from": settings.EMAIL_FROM,
        "to": [destinatario],
        "subject": asunto,
        "html": contenido,
    }

    # Si hay una URL de documento adjunto, lo descargamos y convertimos a Base64 de forma segura
    if adjunto_url:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(adjunto_url)
                if response.status_code == 200:
                    file_bytes = response.content
                    encoded_file = base64.b64encode(file_bytes).decode("utf-8")
                    params["attachments"] = [
                        {
                            "filename": nombre_archivo,
                            "content": encoded_file
                        }
                    ]
        except Exception as e:
            print(f"No se pudo adjuntar el archivo al correo: {e}")

    # Ejecutamos de forma no bloqueante utilizando asyncio.to_thread para la llamada síncrona de Resend
    try:
        response = await asyncio.to_thread(resend.Emails.send, params)
        return response
    except Exception as e:
        print(f"Error al enviar el correo con Resend: {e}")
        return None

#este servicio es para enviar correos de activación de licitaciones a los clientes. Se utiliza en el endpoint que activa la licitación formal y envía el correo con el documento adjunto.
async def enviar_correo_activacion(cliente_email: str, titulo: str, fecha_limite: str, documento_url: str):
    contenido = f"""
        <h3>Propuesta de Licitación</h3>
        <p>Se ha activado la licitación formal: <b>{titulo}</b></p>
        <p>Fecha límite de presentación: {fecha_limite}</p>
        <p>Encuentra el documento oficial adjunto a este correo o descárgalo desde el siguiente enlace: <a href="{documento_url}">Ver Documento</a></p>
    """
    return await enviar_correo(
        destinatario=cliente_email,
        asunto="Nueva Licitación Activa - Propuesta Adjunta",
        contenido=contenido,
        adjunto_url=documento_url,
        nombre_archivo=f"propuesta_{titulo.replace(' ', '_')}.pdf"
    )

#Este servicio es para enviar recordatorios y notificaciones de licitaciones vencidas. Se utiliza en el cron job que procesa las licitaciones activas y envía correos según la fecha límite.
async def enviar_recordatorio(destinatarios: str | list[str], titulo: str, fecha_limite: str):
    # Si pasan un string único, lo convertimos a lista
    if isinstance(destinatarios, str):
        destinatarios = [destinatarios]

    contenido = f"""
        <h3>Recordatorio de Licitación</h3>
        <p>La licitación <b>{titulo}</b> está próxima a vencer.</p>
        <p>Fecha límite: {fecha_limite}</p>
    """
    params = {
        "from": settings.EMAIL_FROM,
        "to": destinatarios,
        "subject": "Recordatorio de Licitación",
        "html": contenido,
    }
    try:
        response = await asyncio.to_thread(resend.Emails.send, params)
        return response
    except Exception as e:
        print(f"Error al enviar el correo con Resend: {e}")
        return None


#este servicio es para enviar notificaciones de licitaciones vencidas. Se utiliza en el cron job que procesa las licitaciones activas y envía correos según la fecha límite.
async def enviar_correo_vencida(cliente_email: str, titulo: str):
    contenido = f"""
        <h3>Licitación Vencida</h3>
        <p>La licitación <b>{titulo}</b> ha vencido y fue marcada automáticamente como perdida.</p>
    """
    return await enviar_correo(cliente_email, "Licitación Vencida", contenido)