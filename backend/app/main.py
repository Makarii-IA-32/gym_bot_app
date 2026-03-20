from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.database import engine, Base

# Імпортуємо ВСІ моделі, щоб SQLAlchemy їх побачила і створила
from app.models.user import User
from app.models.exercises import Muscle, Exercise, ExerciseMuscleMap, Tag, ExerciseTag
from app.models.programs import Program, ProgramDay, ProgramSlot, SlotOption, PlannedSet
from app.models.sessions import Session, SessionExercise, SessionSet
from app.models.relationships import CoachingRelationship, AssignedProgram, FavoriteProgram, FavoriteExercise

from app.routers import users, exercises

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Створюємо всі таблиці в базі даних при старті
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(lifespan=lifespan)

# <--- 2. Додаємо ці налаштування CORS --->
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # "*" означає "дозволити всім" (для розробки це ок)
    allow_credentials=True,
    allow_methods=["*"],  # Дозволити GET, POST, DELETE і т.д.
    allow_headers=["*"],
)
# <--- Кінець налаштувань CORS --->

os.makedirs("static/images", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(users.router)
app.include_router(exercises.router)

@app.get("/")
async def root():
    return {"message": "Gym Bot Backend is Running!"}