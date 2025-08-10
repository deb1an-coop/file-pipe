from fastapi import APIRouter, Depends, HTTPException
from app.api.endpoints.authentication import router as auth_router
from app.api.endpoints.tasks import router as tasks_router
router = APIRouter()

# Include the authentication router
router.include_router(auth_router, prefix="/auth", tags=["authentication"])

# Include the tasks router
router.include_router(tasks_router, prefix="/tasks", tags=["tasks"])

