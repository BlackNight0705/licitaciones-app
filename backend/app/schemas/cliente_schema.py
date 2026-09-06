from pydantic import BaseModel, EmailStr, Field

class ClienteBase(BaseModel):
    cliente_nombre: str = Field(
        ..., 
        min_length=2, 
        max_length=150, 
        description="El nombre es obligatorio y no puede estar vacío."
    )
    cliente_email: EmailStr = Field(
        ..., 
        description="Debe ser un correo electrónico válido."
    )
    cliente_telefono: str | None = Field(
        None, 
        max_length=30, 
        description="Teléfono de contacto opcional."
    )
    cliente_empresa: str | None = Field(
        None, 
        max_length=150, 
        description="Nombre de la empresa opcional."
    )

class ClienteCreate(ClienteBase):
    pass

class ClienteResponse(ClienteBase):
    cliente_id: int = Field(..., gt=0)

    class Config:
        from_attributes = True