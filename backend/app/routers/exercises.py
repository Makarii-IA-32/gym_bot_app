from app.models import exercises
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
import shutil
import os
import uuid

from app.database import get_db
from app.models.exercises import Exercise, Muscle, Tag, ExerciseTag, ExerciseMuscleMap
from app.models.relationships import FavoriteExercise
from app.models.user import User
from app import schemas

router = APIRouter(prefix="/exercises", tags=["exercises"])

# Створюємо папку для фотографій при старті роутера (на всякий випадок)
os.makedirs("static/images", exist_ok=True)

# --- ДОПОМІЖНА ФУНКЦІЯ ---
async def get_user_by_tg_id(tg_id: int, db: AsyncSession) -> int:
    result = await db.execute(select(User).where(User.tg_id == tg_id))
    user = result.scalar()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user.id

# --- ФАЙЛИ ---
@router.post("/upload_image")
async def upload_image(file: UploadFile = File(...)):
    file_extension = file.filename.split(".")[-1]
    new_filename = f"{uuid.uuid4()}.{file_extension}"
    file_location = f"static/images/{new_filename}"
    
    with open(file_location, "wb+") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    return {"path": f"/{file_location}"}

# --- GET DATA ---
@router.get("/muscles", response_model=list[schemas.MuscleRead])
async def get_muscles(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Muscle))
    return result.scalars().all()

@router.get("/tags", response_model=list[schemas.TagResponse])
async def get_tags(tg_id: int, db: AsyncSession = Depends(get_db)):
    user_id = await get_user_by_tg_id(tg_id, db)
    query = select(Tag).where((Tag.is_global == True) | (Tag.created_by_user_id == user_id))
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/", response_model=list[schemas.ExerciseResponse])
async def get_exercises(
    tg_id: int,
    muscle_id: int | None = None,
    tag_id: int | None = None,
    db: AsyncSession = Depends(get_db)
):
    user_id = await get_user_by_tg_id(tg_id, db)

    query = select(Exercise).where(
        (Exercise.is_global == True) | (Exercise.created_by_user_id == user_id)
    ).options(selectinload(Exercise.tags).selectinload(ExerciseTag.tag))

    if muscle_id:
        query = query.where(Exercise.main_muscle_id == muscle_id)
    
    if tag_id:
        # Шукаємо вправи, де цей тег прив'язаний глобально АБО цим юзером
        query = query.join(ExerciseTag).where(
            (ExerciseTag.tag_id == tag_id) & 
            ((ExerciseTag.user_id == None) | (ExerciseTag.user_id == user_id))
        )

    result = await db.execute(query)
    exercises = result.scalars().all()

    # Перевіряємо лайки
    fav_query = select(FavoriteExercise.exercise_id).where(FavoriteExercise.user_id == user_id)
    fav_result = await db.execute(fav_query)
    fav_ids = set(fav_result.scalars().all())

    response_list = []
    for ex in exercises:
        ex_dict = ex.__dict__.copy()
        ex_dict["is_favorite"] = ex.id in fav_ids
        # ДОДАЙ ЦЕЙ РЯДОК:
        ex_dict["is_mine"] = (ex.created_by_user_id == user_id) 
        
        tags_list = []
        seen_tag_ids = set()
        
        for t_link in ex.tags:
            if t_link.tag and (t_link.user_id is None or t_link.user_id == user_id):
                if t_link.tag.id not in seen_tag_ids:
                    tags_list.append(t_link.tag)
                    seen_tag_ids.add(t_link.tag.id)
                    
        ex_dict["tags"] = tags_list
        response_list.append(ex_dict)

    return response_list

# --- ACTIONS ---
@router.post("/toggle_favorite")
async def toggle_favorite(tg_id: int, exercise_id: int, db: AsyncSession = Depends(get_db)):
    user_id = await get_user_by_tg_id(tg_id, db)

    query = select(FavoriteExercise).where(
        (FavoriteExercise.user_id == user_id) & (FavoriteExercise.exercise_id == exercise_id)
    )
    result = await db.execute(query)
    existing = result.scalar()

    if existing:
        await db.delete(existing)
        await db.commit()
        return {"status": "removed"}
    else:
        new_fav = FavoriteExercise(user_id=user_id, exercise_id=exercise_id)
        db.add(new_fav)
        await db.commit()
        return {"status": "added"}

@router.post("/create", response_model=schemas.ExerciseResponse)
async def create_exercise(ex_data: schemas.ExerciseCreate, db: AsyncSession = Depends(get_db)):
    real_user_id = await get_user_by_tg_id(ex_data.user_id, db)

    new_ex = Exercise(
        name=ex_data.name,
        description=ex_data.description,
        main_muscle_id=ex_data.main_muscle_id,
        is_global=False,
        created_by_user_id=real_user_id,
        photo_path=ex_data.photo_path
    )
    db.add(new_ex)
    await db.flush()

    db.add(ExerciseMuscleMap(exercise_id=new_ex.id, muscle_id=ex_data.main_muscle_id, coefficient=1.0))

    # Додаємо теги
    for t_id in ex_data.tag_ids:
        db.add(ExerciseTag(exercise_id=new_ex.id, tag_id=t_id, user_id=real_user_id))
    
    await db.commit()
    
    # --- ВИПРАВЛЕННЯ: Завантажуємо вправу зі зв'язками ---
    query = select(Exercise).where(Exercise.id == new_ex.id).options(
        selectinload(Exercise.tags).selectinload(ExerciseTag.tag)
    )
    result = await db.execute(query)
    created_ex = result.scalar()

    # Формуємо правильний словник для Pydantic
    ex_dict = created_ex.__dict__.copy()
    ex_dict["is_favorite"] = False # Нова вправа ще не може бути в улюблених
    # ДОДАЙ ЦЕЙ РЯДОК (бо щойно створена тобою вправа - 100% твоя):
    ex_dict["is_mine"] = True
    # Витягуємо самі теги зі зв'язуючої таблиці
    ex_dict["tags"] = [t_link.tag for t_link in created_ex.tags if t_link.tag]
    
    return ex_dict

@router.put("/{exercise_id}")
async def update_exercise(
    exercise_id: int, 
    ex_data: schemas.ExerciseCreate, 
    db: AsyncSession = Depends(get_db)
):
    query = select(Exercise).where(Exercise.id == exercise_id)
    result = await db.execute(query)
    exercise = result.scalar()
    
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")

    real_user_id = await get_user_by_tg_id(ex_data.user_id, db)

    # 1. Завжди оновлюємо теги ДЛЯ ЦЬОГО ЮЗЕРА (незалежно глобальна вправа чи ні)
    # Видаляємо старі зв'язки САМЕ ЦЬОГО юзера для ЦІЄЇ вправи
    await db.execute(delete(ExerciseTag).where(
        (ExerciseTag.exercise_id == exercise_id) & 
        (ExerciseTag.user_id == real_user_id)
    ))
    
    # Додаємо нові теги від юзера
    for t_id in ex_data.tag_ids:
        db.add(ExerciseTag(exercise_id=exercise.id, tag_id=t_id, user_id=real_user_id))

    # 2. Оновлюємо решту інфи, ТІЛЬКИ якщо це його власна вправа
    if exercise.created_by_user_id == real_user_id and not exercise.is_global:
        exercise.name = ex_data.name
        exercise.description = ex_data.description
        exercise.main_muscle_id = ex_data.main_muscle_id
        exercise.photo_path = ex_data.photo_path

    await db.commit()
    return {"status": "updated"}

@router.delete("/{exercise_id}")
async def delete_exercise(exercise_id: int, tg_id: int, db: AsyncSession = Depends(get_db)):
    real_user_id = await get_user_by_tg_id(tg_id, db)
    
    query = select(Exercise).where(Exercise.id == exercise_id)
    result = await db.execute(query)
    exercise = result.scalar()
    
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")
        
    if exercise.created_by_user_id != real_user_id:
        raise HTTPException(status_code=403, detail="Не можна видалити чужу вправу")
        
    # Каскадне видалення зв'язків
    await db.execute(delete(ExerciseTag).where(ExerciseTag.exercise_id == exercise_id))
    await db.execute(delete(ExerciseMuscleMap).where(ExerciseMuscleMap.exercise_id == exercise_id))
    await db.execute(delete(FavoriteExercise).where(FavoriteExercise.exercise_id == exercise_id))
    
    await db.delete(exercise)
    await db.commit()
    return {"status": "deleted"}

@router.post("/tags/create", response_model=schemas.TagResponse)
async def create_tag(tag: schemas.TagCreate, tg_id: int, db: AsyncSession = Depends(get_db)):
    user_id = await get_user_by_tg_id(tg_id, db)
    new_tag = Tag(name=tag.name, is_global=False, created_by_user_id=user_id)
    db.add(new_tag)
    await db.commit()
    await db.refresh(new_tag)
    return new_tag