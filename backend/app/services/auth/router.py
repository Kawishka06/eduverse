from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user_public
from app.database import get_db
from app.models.user import Token, UserLogin, UserPublic, UserRegister
from app.services.auth.service import AuthService

router = APIRouter(tags=["auth"])


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(db)


@router.post("/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
def register(
    payload: UserRegister,
    auth: AuthService = Depends(get_auth_service),
) -> UserPublic:
    return auth.register(payload)


@router.post("/login", response_model=Token)
def login(
    payload: UserLogin,
    auth: AuthService = Depends(get_auth_service),
) -> Token:
    return auth.login(payload)


@router.get("/me", response_model=UserPublic)
def me(current_user: UserPublic = Depends(get_current_user_public)) -> UserPublic:
    return current_user
