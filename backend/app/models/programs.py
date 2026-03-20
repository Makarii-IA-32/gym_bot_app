from sqlalchemy import Column, String, Integer, ForeignKey, Enum, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
import enum

class SelectionType(str, enum.Enum):
    FIXED = "fixed"   # Конкретна вправа
    CHOICE = "choice" # Вибір зі списку

class Program(Base):
    __tablename__ = "programs"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    name: Mapped[str] = mapped_column(String)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False)

    days = relationship("ProgramDay", back_populates="program")

class ProgramDay(Base):
    __tablename__ = "program_days"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    program_id: Mapped[int] = mapped_column(ForeignKey("programs.id"))
    name: Mapped[str] = mapped_column(String)
    order_index: Mapped[int] = mapped_column(Integer)

    program = relationship("Program", back_populates="days")
    slots = relationship("ProgramSlot", back_populates="day")

class ProgramSlot(Base):
    __tablename__ = "program_slots"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    day_id: Mapped[int] = mapped_column(ForeignKey("program_days.id"))
    order_index: Mapped[int] = mapped_column(Integer)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    selection_type: Mapped[SelectionType] = mapped_column(Enum(SelectionType), default=SelectionType.FIXED)

    day = relationship("ProgramDay", back_populates="slots")
    options = relationship("SlotOption", back_populates="slot")
    planned_sets = relationship("PlannedSet", back_populates="slot")

class SlotOption(Base):
    __tablename__ = "slot_options"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    slot_id: Mapped[int] = mapped_column(ForeignKey("program_slots.id"))
    exercise_id: Mapped[int] = mapped_column(ForeignKey("exercises.id"))

    slot = relationship("ProgramSlot", back_populates="options")

class PlannedSet(Base):
    __tablename__ = "planned_sets"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    slot_id: Mapped[int] = mapped_column(ForeignKey("program_slots.id"))
    set_order: Mapped[int] = mapped_column(Integer)
    number_of_sets: Mapped[int] = mapped_column(Integer, default=1)
    target_reps: Mapped[str] = mapped_column(String) # String, бо може бути "10-12" або "max"
    target_weight: Mapped[str | None] = mapped_column(String, nullable=True) # String, бо може бути "80%"
    rpe: Mapped[int | None] = mapped_column(Integer, nullable=True)

    slot = relationship("ProgramSlot", back_populates="planned_sets")