from sqlalchemy import Column, String, Integer, Float, Boolean, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

class Muscle(Base):
    __tablename__ = "muscles"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, unique=True)

class Tag(Base):
    __tablename__ = "tags"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, index=True) # Прибрав unique=True, бо різні юзери можуть створити тег з однією назвою
    is_global: Mapped[bool] = mapped_column(Boolean, default=False)
    created_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)

    # Зв'язок з вправами
    exercises = relationship("ExerciseTag", back_populates="tag")

class Exercise(Base):
    __tablename__ = "exercises"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    photo_path: Mapped[str | None] = mapped_column(String, nullable=True)
    is_global: Mapped[bool] = mapped_column(Boolean, default=False)
    created_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    main_muscle_id: Mapped[int] = mapped_column(ForeignKey("muscles.id"))

    # Зв'язки
    muscle_map = relationship("ExerciseMuscleMap", back_populates="exercise")
    tags = relationship("ExerciseTag", back_populates="exercise")

class ExerciseMuscleMap(Base):
    __tablename__ = "exercise_muscle_maps"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    exercise_id: Mapped[int] = mapped_column(ForeignKey("exercises.id"))
    muscle_id: Mapped[int] = mapped_column(ForeignKey("muscles.id"))
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True) # Якщо NULL - це стандартний коефіцієнт
    coefficient: Mapped[float] = mapped_column(Float, default=1.0)

    exercise = relationship("Exercise", back_populates="muscle_map")

class ExerciseTag(Base):
    __tablename__ = "exercise_tags"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    exercise_id: Mapped[int] = mapped_column(ForeignKey("exercises.id"))
    tag_id: Mapped[int] = mapped_column(ForeignKey("tags.id"))
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    # ОСЬ ЦІ ДВА РЯДКИ КРИТИЧНО ВАЖЛИВІ:
    exercise = relationship("Exercise", back_populates="tags")
    tag = relationship("Tag", back_populates="exercises")  # <--- Цього рядка у тебе, швидше за все, немає або там помилка