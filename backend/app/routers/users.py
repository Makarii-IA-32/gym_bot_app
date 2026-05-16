from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app import crud, schemas

router = APIRouter(prefix="/users", tags=["Управління користувачами"])

@router.post(
    "/", 
    response_model=schemas.UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Реєстрація або авторизація користувача",
    description=(
        "Ендпоінт для автоматичного входу/реєстрації користувача через Telegram Web App або бот. "
        "Перевіряє наявність користувача за його `tg_id`. Якщо він уже є в базі — повертає його дані, "
        "якщо немає — створює новий запис."
    )
)
async def register_user(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Реєструє нового користувача бота або повертає профіль існуючого.

    :param user: Об'єкт schemas.UserCreate з даними користувача (tg_id, username, full_name).
    :param db: Асинхронна сесія SQLAlchemy для роботи з базою даних.
    :return: Об'єкт schemas.UserResponse з повною інформацією про користувача (включаючи ID та роль).
    """
    # 1. Перевіряємо, чи такий юзер вже є
    db_user = await crud.get_user_by_tg_id(db, tg_id=user.tg_id)
    if db_user:
        return db_user # Якщо є - просто повертаємо його дані
    
    # 2. Якщо немає - створюємо
    return await crud.create_user(db=db, user=user)