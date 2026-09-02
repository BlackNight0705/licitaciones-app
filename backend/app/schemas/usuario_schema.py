from pydantic import BaseModel, EmailStr

class UsuarioBase(BaseModel):
    usuario_nombre: str
    usuario_email: EmailStr
    usuario_rol: str

class UsuarioCreate(UsuarioBase):
    usuario_hashed_password: str

class UsuarioResponse(UsuarioBase):
    usuario_id: int

    class Config:
        from_attributes = True
