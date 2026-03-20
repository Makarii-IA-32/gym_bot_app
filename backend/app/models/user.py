# backend/app/models/user.py

from sqlalchemy import Column, String, BigInteger, Enum, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column
import enum
# Імпортуємо Base з нашого нового файлу database.py
from app.database import Base 

class UserRole(str, enum.Enum):
    user = "user"
    admin = "admin"

class User(Base):
    __tablename__ = "users"
    # ... далі все без змін ...
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    username: Mapped[str | None] = mapped_column(String, nullable=True)
    full_name: Mapped[str] = mapped_column(String)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.user)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())