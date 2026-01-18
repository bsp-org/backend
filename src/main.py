import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api import api_router
from src.config import settings
from src.users.api import auth_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.debug("Starting app in %s mode", settings.env)
    yield


app = FastAPI(
    title="Bible Search API",
    version="0.0.0",
    description="API for searching and accessing Bible content with user authentication",
    lifespan=lifespan,
    contact={
        "name": "BSP Org",
        "email": "biblesearchproject@gmail.com",
    },
    license_info={
        "name": "MIT",
    },
    root_path=settings.root_path,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["health"])
async def health() -> dict[str, str]:
    return {"status": "ok"}


# Include routers in the main app
app.include_router(auth_router)
app.include_router(api_router)
