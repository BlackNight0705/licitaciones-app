from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.core.database import get_session
from backend.app.schemas.user_schema import UserCreate, UserResponse
from backend.app.services.user_service import create_user

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/", response_model=UserResponse)
async def create_user_route(
    data: UserCreate,
    session: AsyncSession = Depends(get_session)
):
    return await create_user(session, data)
