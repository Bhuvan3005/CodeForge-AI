from fastapi import APIRouter, Depends
from services.auth import (
    register_user,
    login_user,
    get_current_user
)
from schemas.users import UserRegister, UserLogin, Token, UserResponse
from fastapi.security import OAuth2PasswordRequestForm


router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

@router.post("/register", response_model=str)
async def register(user: UserRegister):
    """Register a new user with email and password"""
    return await register_user(user.email, user.password)



@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends()
):
    return await login_user(
        form_data.username,
        form_data.password
    )

@router.get("/me", response_model=UserResponse)
async def me(current_user=Depends(get_current_user)):
    """Get current authenticated user info"""
    return {
        "id": str(current_user["_id"]),
        "email": current_user["email"]
    }