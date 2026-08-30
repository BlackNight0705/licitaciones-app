from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.core.database import get_session

router = APIRouter(prefix="/test", tags=["Test"])

@router.get("/test-db")
async def test_db(session: AsyncSession = Depends(get_session)):
    result = await session.execute("SELECT 1")
    return {"db": result.scalar()}
