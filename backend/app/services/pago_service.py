from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from backend.app.models.pago import Pago
from backend.app.models.licitacion import Licitacion
from backend.app.schemas.pago_schema import PagoCreate

async def registrar_pago(session: AsyncSession, data: PagoCreate):
    licitacion = await session.get(Licitacion, data.pago_licitacion_id)
    if not licitacion:
        raise HTTPException(status_code=404, detail="Licitación no encontrada")

    if licitacion.licitacion_estado != "por_cobrar":
        raise HTTPException(
            status_code=400,
            detail="Solo se pueden registrar pagos en licitaciones con estado 'por_cobrar'."
        )

    result = await session.execute(
        select(Pago).where(Pago.pago_licitacion_id == licitacion.licitacion_id)
    )
    pagos = result.scalars().all()
    total_pagado = sum(p.pago_monto for p in pagos)
    saldo_pendiente = licitacion.licitacion_presupuesto_maximo - total_pagado

    if data.pago_monto > saldo_pendiente:
        raise HTTPException(
            status_code=400,
            detail=f"El pago excede el saldo pendiente ({saldo_pendiente})."
        )

    pago = Pago(**data.model_dump())
    session.add(pago)

    nuevo_saldo = saldo_pendiente - data.pago_monto
    if nuevo_saldo <= 0:
        licitacion.licitacion_estado = "cobrada"

    await session.commit()
    await session.refresh(pago)
    return pago