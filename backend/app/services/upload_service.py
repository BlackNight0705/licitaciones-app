import re
from supabase import create_client, Client
from backend.app.core.config import settings

supabase: Client = create_client(settings.STORAGE_URL, settings.STORAGE_KEY)

def limpiar_filename(filename: str) -> str:
    filename = filename.strip()
    filename = filename.replace(" ", "_")
    filename = re.sub(r"[^A-Za-z0-9._-]", "", filename)
    return filename

async def subir_archivo_general(contenido: bytes, filename: str, user_id: str) -> str:
    filename_limpio = limpiar_filename(filename)
    bucket = "licitaciones_archivos"
    
    # La ruta final será: Licitaciones/<user_id>/archivo.pdf
    ruta_en_bucket = f"Licitaciones/{user_id}/{filename_limpio}"

    try:
        supabase.storage.from_(bucket).upload(
            path=ruta_en_bucket,
            file=contenido,
            file_options={"content-type": "application/octet-stream", "upsert": "true"}
        )
    except Exception as e:
        print(f"Error subiendo archivo a Supabase: {e}")
        raise Exception("Error subiendo archivo al storage")

    # Obtener la URL pública usando la misma ruta estructurada
    public_url_response = supabase.storage.from_(bucket).get_public_url(ruta_en_bucket)
    
    public_url = public_url_response if isinstance(public_url_response, str) else public_url_response.get("publicUrl")
    
    return public_url