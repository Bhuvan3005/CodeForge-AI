from fastapi import FastAPI
from contextlib import asynccontextmanager
from database import create_indexes
from routes.login import router as auth_router
from routes.problems import router as problem_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await create_indexes()
    yield
    # Shutdown (if needed)


app = FastAPI(lifespan=lifespan)

app.include_router(auth_router)
app.include_router(problem_router)