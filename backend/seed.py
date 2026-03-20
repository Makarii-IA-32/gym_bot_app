import asyncio
from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models.user import User
from app.models.exercises import Muscle, Exercise, ExerciseMuscleMap

async def seed_data():
    async with AsyncSessionLocal() as session:
        print("🌱 Починаємо наповнення бази...")

        # 1. Додаємо М'язи
        muscles_data = ["Груди", "Спина", "Ноги (Квадріцепс)", "Ноги (Біцепс)", "Плечі", "Тріцепс", "Біцепс", "Прес"]
        muscles_db = {} # Щоб запам'ятати ID

        for name in muscles_data:
            # Перевіряємо, чи вже є такий м'яз
            exists = await session.execute(select(Muscle).where(Muscle.name == name))
            if not exists.scalar():
                m = Muscle(name=name)
                session.add(m)
                print(f"Додано м'яз: {name}")
                muscles_db[name] = m
            else:
                muscles_db[name] = exists.scalar()
        
        await session.flush() # Щоб отримати ID створених записів

        # 2. Додаємо Базові Вправи
        exercises_data = [
            {"name": "Жим штанги лежачи", "muscle": "Груди", "desc": "Базова вправа на груди"},
            {"name": "Жим гантелей під кутом", "muscle": "Груди", "desc": "Акцент на верх грудних"},
            {"name": "Підтягування", "muscle": "Спина", "desc": "Базова вправа на спину"},
            {"name": "Тяга верхнього блоку", "muscle": "Спина", "desc": "Імітація підтягувань"},
            {"name": "Присідання зі штангою", "muscle": "Ноги (Квадріцепс)", "desc": "Король вправ"},
            {"name": "Жим ногами", "muscle": "Ноги (Квадріцепс)", "desc": "Платформа"},
            {"name": "Махи гантелями в сторони", "muscle": "Плечі", "desc": "Середня дельта"},
        ]

        for ex in exercises_data:
            exists = await session.execute(select(Exercise).where(Exercise.name == ex["name"]))
            if not exists.scalar():
                # Знаходимо ID м'яза
                muscle_obj = await session.execute(select(Muscle).where(Muscle.name == ex["muscle"]))
                muscle_id = muscle_obj.scalar().id

                new_ex = Exercise(
                    name=ex["name"],
                    description=ex["desc"],
                    main_muscle_id=muscle_id,
                    is_global=True # Це бачать всі
                )
                session.add(new_ex)
                print(f"Додано вправу: {ex['name']}")
        
        await session.commit()
        print("✅ База успішно наповнена!")

if __name__ == "__main__":
    asyncio.run(seed_data())