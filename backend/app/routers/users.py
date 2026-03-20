from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app import crud, schemas

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=schemas.UserResponse)
async def register_user(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    # 1. Перевіряємо, чи такий юзер вже є
    db_user = await crud.get_user_by_tg_id(db, tg_id=user.tg_id)
    if db_user:
        return db_user # Якщо є - просто повертаємо його дані
    
    # 2. Якщо немає - створюємо
    return await crud.create_user(db=db, user=user)