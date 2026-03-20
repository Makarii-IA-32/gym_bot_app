from sqlalchemy import Column, Integer, ForeignKey, Enum, DateTime, Date, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from app.database import Base
import enum

class CoachingStatus(str, enum.Enum):
    PENDING = "pending"
    ACTIVE = "active"
    REJECTED = "rejected"

class CoachingRelationship(Base):
    __tablename__ = "coaching_relationships"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    coach_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    student_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    status: Mapped[CoachingStatus] = mapped_column(Enum(CoachingStatus), default=CoachingStatus.PENDING)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

class AssignedProgram(Base):
    __tablename__ = "assigned_programs"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    program_id: Mapped[int] = mapped_column(ForeignKey("programs.id"))
    assigned_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    start_date: Mapped[Date] = mapped_column(Date, server_default=func.current_date())

class FavoriteProgram(Base):
    __tablename__ = "favorite_programs"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    program_id: Mapped[int] = mapped_column(ForeignKey("programs.id"))

class FavoriteExercise(Base):
    __tablename__ = "favorite_exercises"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    exercise_id: Mapped[int] = mapped_column(ForeignKey("exercises.id"))