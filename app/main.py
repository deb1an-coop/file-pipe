from fastapi import FastAPI, Depends, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings, Settings
from app.api.api import router as api_router
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
router = APIRouter()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@router.get("/")
async def read_root():
    return {"message": "Welcome to the FastAPI application!"}

@router.get("/config")
def get_config(settings: Settings = Depends(get_settings)):
    return {
        "environment": settings.environment,
        "debug": settings.debug,
        "jwt_algorithm": settings.jwt_algorithm,
        "jwt_expire_minutes": settings.access_token_expire_minutes,
        "jwt_secret_set": bool(settings.jwt_secret_key),
    }

app.include_router(router, prefix="/api")
app.include_router(api_router, prefix="/api")
if __name__ == "__main__":
    import uvicorn
    settings = get_settings()
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=settings.debug)