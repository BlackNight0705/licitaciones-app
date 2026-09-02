from fastapi import APIRouter, UploadFile, File, HTTPException
from backend.app.services.upload_service import subir_archivo_general

router = APIRouter(prefix="/upload", tags=["Upload"])

@router.post("/")
async def upload_file(file: UploadFile = File(...)):
    try:
        contenido = await file.read()
        url = await subir_archivo_general(contenido, file.filename)
        return {"url": url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))