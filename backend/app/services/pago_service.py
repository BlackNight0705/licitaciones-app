from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.app.models.pago import Pago
from backend.app.models.licitacion import Licitacion
from backend.app.schemas.pago_schema import PagoCreate

async def registrar_pago(session: AsyncSession, data: PagoCreate):
    licitacion = await session.get(Licitacion, data.pago_licitacion_id)

    if licitacion.licitacion_estado != "por_cobrar":
        raise ValueError("Solo se pueden registrar pagos en estado por_cobrar.")

    # Calcular saldo pendiente
    result = await session.execute(
        select(Pago).where(Pago.pago_licitacion_id == licitacion.licitacion_id)
    )
    pagos = result.scalars().all()
    total_pagado = sum(p.pago_monto for p in pagos)

    saldo = licitacion.licitacion_presupuesto_maximo - total_pagado

    if data.pago_monto > saldo:
        raise ValueError("El pago excede el saldo pendiente.")

    pago = Pago(**data.model_dump())
    session.add(pago)

    # Si saldo llega a cero → cobrada
    if data.pago_monto == saldo:
        licitacion.licitacion_estado = "cobrada"

    await session.commit()
    await session.refresh(pago)
    return pago
