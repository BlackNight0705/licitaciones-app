from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from backend.app.models.pago import Pago
from backend.app.models.licitacion import Licitacion
from backend.app.schemas.pago_schema import PagoCreate

async def registrar_pago(session: AsyncSession, data: PagoCreate, usuario_id: int):
    # Validar que la licitación exista, pertenezca al usuario y cargar sus productos
    result = await session.execute(
        select(Licitacion)
        .options(selectinload(Licitacion.productos))
        .where(
            Licitacion.licitacion_id == data.pago_licitacion_id,
            Licitacion.licitacion_usuario_id == usuario_id
        )
    )
    licitacion = result.scalars().first()
    if not licitacion:
        raise HTTPException(status_code=404, detail="Licitación no encontrada o no tienes permisos")

    # REGLA: No se puede pagar una licitación que no tenga productos asociados
    if not licitacion.productos or len(licitacion.productos) == 0:
        raise HTTPException(
            status_code=400,
            detail="No se pueden registrar pagos en una licitación que no tiene productos asociados."
        )

    if licitacion.licitacion_estado not in ["por_cobrar", "ganada"]:
        raise HTTPException(
            status_code=400,
            detail="Solo se pueden registrar pagos en licitaciones ganadas o por cobrar."
        )

    result_pagos = await session.execute(
        select(Pago).where(Pago.pago_licitacion_id == licitacion.licitacion_id)
    )
    pagos = result_pagos.scalars().all()
    total_pagado = sum(p.pago_monto for p in pagos)
    saldo_pendiente = licitacion.licitacion_presupuesto_maximo - total_pagado

    if data.pago_monto > saldo_pendiente:
        raise HTTPException(
            status_code=400,
            detail=f"El pago excede el saldo pendiente ({saldo_pendiente})."
        )

    # Inyectamos obligatoriamente el usuario actual y la fecha de hoy, 
    # ignorando lo que el cliente intente mandar o si venía vacío.
    pago_data = data.model_dump()
    pago_data["pago_usuario_id"] = usuario_id
    pago_data["pago_fecha_pago"] = date.today()

    pago = Pago(**pago_data)
    session.add(pago)

    nuevo_saldo = saldo_pendiente - data.pago_monto
    if nuevo_saldo <= 0:
        licitacion.licitacion_estado = "cobrada"

    await session.commit()
    await session.refresh(pago)
    return pago