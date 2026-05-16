from app.models import exercises
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, status
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

router = APIRouter(prefix="/exercises", tags=["Каталог вправ та тегів"])

os.makedirs("static/images", exist_ok=True)

# --- ДОПОМІЖНА ФУНКЦІЯ ---
async def get_user_by_tg_id(tg_id: int, db: AsyncSession) -> int:
    """
    Внутрішня утиліта для отримання внутрішнього ID користувача за його Telegram ID.
    Raises HTTPException 404, якщо користувача не знайдено.
    """
    result = await db.execute(select(User).where(User.tg_id == tg_id))
    user = result.scalar()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user.id

# --- ФАЙЛИ ---
@router.post(
    "/upload_image",
    status_code=status.HTTP_201_CREATED,
    summary="Завантаження фотографії для вправи",
    description="Приймає файл зображення, генерує для нього унікальне ім'я за допомогою UUID та зберігає у папку `static/images/`."
)
async def upload_image(file: UploadFile = File(...)):
    """
    Завантажує зображення на сервер.

    :param file: Бінарний файл зображення (multipart/form-data).
    :return: Словник із відносним шляхом до збереженого файлу.
    """
    file_extension = file.filename.split(".")[-1]
    new_filename = f"{uuid.uuid4()}.{file_extension}"
    file_location = f"static/images/{new_filename}"
    
    with open(file_location, "wb+") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    return {"path": f"/{file_location}"}

# --- GET DATA ---
@router.get(
    "/muscles", 
    response_model=list[schemas.MuscleRead],
    summary="Отримання списку всіх груп м'язів",
    description="Повертає повний список груп м'язів (напр. Груди, Спина, Прес), які існують у базі даних для класифікації вправ."
)
async def get_muscles(db: AsyncSession = Depends(get_db)):
    """
    Повертає всі доступні групи м'язів.
    """
    result = await db.execute(select(Muscle))
    return result.scalars().all()

@router.get(
    "/tags", 
    response_model=list[schemas.TagResponse],
    summary="Отримання списку тегів для користувача",
    description="Повертає список тегів, які включають глобальні теги застосунку АБО персональні теги, створені конкретним користувачем."
)
async def get_tags(tg_id: int, db: AsyncSession = Depends(get_db)):
    """
    Отримує теги користувача за його Telegram ID.

    :param tg_id: Telegram ID користувача для фільтрації кастомних тегів.
    """
    user_id = await get_user_by_tg_id(tg_id, db)
    query = select(Tag).where((Tag.is_global == True) | (Tag.created_by_user_id == user_id))
    result = await db.execute(query)
    return result.scalars().all()

@router.get(
    "/", 
    response_model=list[schemas.ExerciseResponse],
    summary="Отримання та фільтрація списку вправ",
    description="Повертає доступні користувачу вправи (базові + власні кастомні). Підтримує необов'язкову фільтрацію за групою м'язів або за тегом."
)
async def get_exercises(
    tg_id: int,
    muscle_id: int | None = None,
    tag_id: int | None = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Повертає список доступних вправ із позначками 'is_favorite' та 'is_mine'.

    :param tg_id: Telegram ID користувача.
    :param muscle_id: ID групи м'язів для фільтрації (опціонально).
    :param tag_id: ID тегу для фільтрації (опціонально).
    """
    user_id = await get_user_by_tg_id(tg_id, db)

    query = select(Exercise).where(
        (Exercise.is_global == True) | (Exercise.created_by_user_id == user_id)
    ).options(selectinload(Exercise.tags).selectinload(ExerciseTag.tag))

    if muscle_id:
        query = query.where(Exercise.main_muscle_id == muscle_id)
    
    if tag_id:
        query = query.join(ExerciseTag).where(
            (ExerciseTag.tag_id == tag_id) & 
            ((ExerciseTag.user_id == None) | (ExerciseTag.user_id == user_id))
        )

    result = await db.execute(query)
    exercises = result.scalars().all()

    fav_query = select(FavoriteExercise.exercise_id).where(FavoriteExercise.user_id == user_id)
    fav_result = await db.execute(fav_query)
    fav_ids = set(fav_result.scalars().all())

    response_list = []
    for ex in exercises:
        ex_dict = ex.__dict__.copy()
        ex_dict["is_favorite"] = ex.id in fav_ids
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
@router.post(
    "/toggle_favorite",
    summary="Перемикання статусу 'Обране' для вправи",
    description="Якщо вправа вже є в обраному — видаляє її звідти. Якщо немає — додає до списку улюблених вправ користувача."
)
async def toggle_favorite(tg_id: int, exercise_id: int, db: AsyncSession = Depends(get_db)):
    """
    Додає або видаляє вправу з обраного.

    :param tg_id: Telegram ID користувача.
    :param exercise_id: Ідентифікатор вправи.
    """
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

@router.post(
    "/create", 
    response_model=schemas.ExerciseResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Створення нової кастомної вправи",
    description="Створює приватну вправу для поточного користувача із прив'язкою до обраного м'яза та списку тегів."
)
async def create_exercise(ex_data: schemas.ExerciseCreate, db: AsyncSession = Depends(get_db)):
    """
    Створює нову користувацьку вправу.

    :param ex_data: Об'єкт схеми ExerciseCreate з даними форми.
    """
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

    for t_id in ex_data.tag_ids:
        db.add(ExerciseTag(exercise_id=new_ex.id, tag_id=t_id, user_id=real_user_id))
    
    await db.commit()
    
    query = select(Exercise).where(Exercise.id == new_ex.id).options(
        selectinload(Exercise.tags).selectinload(ExerciseTag.tag)
    )
    result = await db.execute(query)
    created_ex = result.scalar()

    ex_dict = created_ex.__dict__.copy()
    ex_dict["is_favorite"] = False 
    ex_dict["is_mine"] = True
    ex_dict["tags"] = [t_link.tag for t_link in created_ex.tags if t_link.tag]
    
    return ex_dict

@router.put(
    "/{exercise_id}",
    summary="Редагування вправи або оновлення її персональних тегів",
    description="Якщо вправа глобальна — дозволяє користувачу змінювати лише свої теги до неї. Якщо кастомна власна — оновлює також назву, опис та фото."
)
async def update_exercise(
    exercise_id: int, 
    ex_data: schemas.ExerciseCreate, 
    db: AsyncSession = Depends(get_db)
):
    """
    Оновлює існуючу вправу в базі даних.

    :param exercise_id: ID вправи, яку потрібно змінити.
    :param ex_data: Схема оновлених даних вправи.
    """
    query = select(Exercise).where(Exercise.id == exercise_id)
    result = await db.execute(query)
    exercise = result.scalar()
    
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")

    real_user_id = await get_user_by_tg_id(ex_data.user_id, db)

    await db.execute(delete(ExerciseTag).where(
        (ExerciseTag.exercise_id == exercise_id) & 
        (ExerciseTag.user_id == real_user_id)
    ))
    
    for t_id in ex_data.tag_ids:
        db.add(ExerciseTag(exercise_id=exercise.id, tag_id=t_id, user_id=real_user_id))

    if exercise.created_by_user_id == real_user_id and not exercise.is_global:
        exercise.name = ex_data.name
        exercise.description = ex_data.description
        exercise.main_muscle_id = ex_data.main_muscle_id
        exercise.photo_path = ex_data.photo_path

    await db.commit()
    return {"status": "updated"}

@router.delete(
    "/{exercise_id}",
    summary="Видалення власної кастомної вправи",
    description="Повністю видаляє приватну вправу користувача та всі її зв'язки в базі даних (теги, обране). Забороняє видаляти глобальні вправи (повертає 403)."
)
async def delete_exercise(exercise_id: int, tg_id: int, db: AsyncSession = Depends(get_db)):
    """
    Видаляє користувацьку вправу з каскадним очищенням зв'язків.

    :param exercise_id: ID вправи.
    :param tg_id: Telegram ID користувача, який ініціював видалення.
    """
    real_user_id = await get_user_by_tg_id(tg_id, db)
    
    query = select(Exercise).where(Exercise.id == exercise_id)
    result = await db.execute(query)
    exercise = result.scalar()
    
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")
        
    if exercise.created_by_user_id != real_user_id:
        raise HTTPException(status_code=403, detail="Не можна видалити чужу вправу")
        
    await db.execute(delete(ExerciseTag).where(ExerciseTag.exercise_id == exercise_id))
    await db.execute(delete(ExerciseMuscleMap).where(ExerciseMuscleMap.exercise_id == exercise_id))
    await db.execute(delete(FavoriteExercise).where(FavoriteExercise.exercise_id == exercise_id))
    
    await db.delete(exercise)
    await db.commit()
    return {"status": "deleted"}

@router.post(
    "/tags/create", 
    response_model=schemas.TagResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Створення кастомного тегу",
    description="Створює приватний тег для маркування вправ (наприклад '#Вдома', '#ЗіШтангою') персонально для цього користувача."
)
async def create_tag(tag: schemas.TagCreate, tg_id: int, db: AsyncSession = Depends(get_db)):
    """
    Додає новий тег користувача.

    :param tag: Об'єкт TagCreate з ім'ям тегу.
    :param tg_id: Telegram ID творця тегу.
    """
    user_id = await get_user_by_tg_id(tg_id, db)
    new_tag = Tag(name=tag.name, is_global=False, created_by_user_id=user_id)
    db.add(new_tag)
    await db.commit()
    await db.refresh(new_tag)
    return new_tag