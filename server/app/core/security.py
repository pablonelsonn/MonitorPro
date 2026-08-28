"""
core/security.py
------------------
Funções de autenticação: hash de senha, criação e validação de token JWT.

Fluxo de autenticação usado no MonitorPro:
1. O administrador faz login em POST /auth/login com usuário e senha.
2. Se a senha bater com o hash salvo no banco, geramos um JWT contendo
   o ID do usuário e uma data de expiração.
3. O dashboard e o agente passam a enviar esse token no header
   "Authorization: Bearer <token>" em todas as requisições protegidas.
4. `get_current_user` decodifica o token em cada requisição e recupera
   o usuário correspondente, negando acesso se o token for inválido/expirado.
"""

from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User

# CryptContext cuida do hashing de senha com bcrypt (nunca guardamos senha em texto puro).
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Diz ao FastAPI onde fica o endpoint de login, para gerar a documentação /docs corretamente.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def hash_password(password: str) -> str:
    """Gera o hash bcrypt de uma senha em texto puro."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Compara uma senha em texto puro com um hash salvo no banco."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    """
    Cria um JWT assinado contendo os dados fornecidos (normalmente
    {"sub": <id do usuário>}) mais uma data de expiração.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """
    Dependency que protege rotas administrativas. Decodifica o token
    JWT enviado pelo cliente, busca o usuário no banco e o retorna.
    Lança 401 se o token for inválido, expirado, ou o usuário não existir mais.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.get(User, int(user_id))
    if user is None or not user.is_active:
        raise credentials_exception
    return user
