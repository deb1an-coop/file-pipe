from fastapi import APIRouter, Depends, HTTPException
from app.core.config import get_settings, Settings
from app.security.auth import TokenManager

router = APIRouter()

@router.post("/login")
async def login(username: str, password: str, settings: Settings = Depends(get_settings)):
    # Here you would typically verify the username and password
    # For demonstration, we assume they are valid
    if username == "admin" and password == "admin":
        token_manager = TokenManager(settings)
        access_token = token_manager.create_access_token(data={"sub": username})
        return {"access_token": access_token, "token_type": "bearer"}
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
@router.get("/verify-token")
async def verify_token(token: str, settings: Settings = Depends(get_settings)):
    token_manager = TokenManager(settings)
    payload = token_manager.verify_token(token)
    if payload:
        return {"message": "Token is valid", "user": payload.get("sub")}
    else:
        raise HTTPException(status_code=401, detail="Invalid token")