from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from database import create_indexes
from routes.login import router as auth_router
from routes.problems import router as problem_router
from routes.submissions import router as submission_router
from routes.roadmap import router as roadmap_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await create_indexes()
    yield
    # Shutdown (if needed)


app = FastAPI(lifespan=lifespan)

# CORS middleware for Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(problem_router)
app.include_router(submission_router)
app.include_router(roadmap_router)