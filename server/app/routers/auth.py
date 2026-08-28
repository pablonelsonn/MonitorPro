"""
routers/auth.py
------------------
Endpoint de login do dashboard. Não exige autenticação (é justamente
onde ela é criada).
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import verify_password, create_access_token
from app.models.user import User
from app.schemas import LoginRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    """
    Valida usuário/senha e devolve um JWT.
    Usamos a mesma mensagem de erro para "usuário não existe" e "senha errada"
    de propósito, para não dar dica a quem está tentando adivinhar credenciais.
    """
    user = db.query(User).filter(User.username == payload.username).first()

    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha inválidos",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário desativado",
        )

    token = create_access_token({"sub": str(user.id)})
    return TokenResponse(access_token=token)
