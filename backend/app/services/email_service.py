import resend
from backend.app.core.config import settings

resend.api_key = settings.EMAIL_API_KEY

async def enviar_correo(destinatario: str, asunto: str, contenido: str):
    return resend.Emails.send({
        "from": "notificaciones@licitaciones.com",
        "to": destinatario,
        "subject": asunto,
        "html": contenido
    })


async def enviar_correo_activacion(cliente_email: str, titulo: str, fecha_limite: str, documento_url: str):
    contenido = f"""
        <h3>Propuesta de Licitación</h3>
        <p>Se ha activado la licitación: <b>{titulo}</b></p>
        <p>Fecha límite: {fecha_limite}</p>
        <p>Documento adjunto: <a href="{documento_url}">Descargar</a></p>
    """
    return await enviar_correo(cliente_email, "Nueva Licitación Activa", contenido)


async def enviar_recordatorio(cliente_email: str, titulo: str, fecha_limite: str):
    contenido = f"""
        <h3>Recordatorio de Licitación</h3>
        <p>La licitación <b>{titulo}</b> está próxima a vencer.</p>
        <p>Fecha límite: {fecha_limite}</p>
    """
    return await enviar_correo(cliente_email, "Recordatorio de Licitación", contenido)


async def enviar_correo_vencida(cliente_email: str, titulo: str):
    contenido = f"""
        <h3>Licitación Vencida</h3>
        <p>La licitación <b>{titulo}</b> ha vencido y fue marcada como perdida.</p>
    """
    return await enviar_correo(cliente_email, "Licitación Vencida", contenido)
