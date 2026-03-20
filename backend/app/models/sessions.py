from sqlalchemy import Column, String, Integer, Float, ForeignKey, DateTime, Text, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.database import Base
import enum

class SessionStatus(str, enum.Enum):
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

class Session(Base):
    __tablename__ = "sessions"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    date: Mapped[DateTime] = mapped_column(DateTime(timezone=True))
    coach_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    program_day_id: Mapped[int | None] = mapped_column(ForeignKey("program_days.id"), nullable=True)
    status: Mapped[SessionStatus] = mapped_column(Enum(SessionStatus), default=SessionStatus.PLANNED)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    finished_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=True)

    exercises = relationship("SessionExercise", back_populates="session")

class SessionExercise(Base):
    __tablename__ = "session_exercises"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("sessions.id"))
    exercise_id: Mapped[int] = mapped_column(ForeignKey("exercises.id"))
    slot_id: Mapped[int | None] = mapped_column(ForeignKey("program_slots.id"), nullable=True)
    order_index: Mapped[int] = mapped_column(Integer)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)

    session = relationship("Session", back_populates="exercises")
    sets = relationship("SessionSet", back_populates="session_exercise")

class SessionSet(Base):
    __tablename__ = "session_sets"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    session_exercise_id: Mapped[int] = mapped_column(ForeignKey("session_exercises.id"))
    set_order: Mapped[int] = mapped_column(Integer)
    number_of_sets: Mapped[int] = mapped_column(Integer, default=1)
    reps: Mapped[int] = mapped_column(Integer)
    weight: Mapped[float] = mapped_column(Float)
    rpe: Mapped[int | None] = mapped_column(Integer, nullable=True)

    session_exercise = relationship("SessionExercise", back_populates="sets")