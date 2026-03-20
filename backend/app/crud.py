from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.user import User
from app.schemas import UserCreate

async def get_user_by_tg_id(db: AsyncSession, tg_id: int):
    # Шукаємо користувача по Telegram ID
    result = await db.execute(select(User).where(User.tg_id == tg_id))
    return result.scalars().first()

async def create_user(db: AsyncSession, user: UserCreate):
    # Створюємо нового
    db_user = User(
        tg_id=user.tg_id,
        username=user.username,
        full_name=user.full_name
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user) # Оновлюємо об'єкт, щоб отримати його ID з бази
    return db_user