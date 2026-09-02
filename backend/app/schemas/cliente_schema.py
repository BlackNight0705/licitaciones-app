from pydantic import BaseModel, EmailStr

class ClienteBase(BaseModel):
    cliente_nombre: str
    cliente_email: EmailStr
    cliente_telefono: str | None = None
    cliente_empresa: str | None = None

class ClienteCreate(ClienteBase):
    pass

class ClienteResponse(ClienteBase):
    cliente_id: int

    class Config:
        from_attributes = True
