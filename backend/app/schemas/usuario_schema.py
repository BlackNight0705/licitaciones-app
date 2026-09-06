from pydantic import BaseModel, EmailStr, Field

class UsuarioBase(BaseModel):
    usuario_nombre: str = Field(
        ..., 
        min_length=2, 
        max_length=150, 
        description="El nombre de usuario es obligatorio y no puede estar vacío."
    )
    usuario_email: EmailStr = Field(
        ..., 
        description="Debe ser un correo electrónico válido."
    )
    usuario_rol: str = Field(
        "usuario", 
        min_length=1, 
        max_length=50, 
        description="Rol asignado al usuario."
    )

class UsuarioCreate(UsuarioBase):
    usuario_hashed_password: str = Field(
        ..., 
        min_length=1, 
        description="La contraseña hasheada no puede estar vacía."
    )

class UsuarioResponse(UsuarioBase):
    usuario_id: int = Field(
        ..., 
        gt=0, 
        description="ID único del usuario."
    )

    class Config:
        from_attributes = True