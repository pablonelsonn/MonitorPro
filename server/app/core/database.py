"""
core/database.py
------------------
Configura a conexão SQLAlchemy com o banco de dados definido em
`settings.DATABASE_URL`.

Por padrão usamos SQLite (arquivo local, zero configuração), ideal para
testes e para demonstrações no cliente. Para produção multiempresa,
basta trocar DATABASE_URL para uma string do Postgres/MySQL — o resto
do código não muda, porque SQLAlchemy abstrai o dialeto do banco.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.core.config import settings

# `check_same_thread=False` é necessário só para SQLite, pois o FastAPI
# pode acessar o banco a partir de threads diferentes.
connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Classe base da qual todos os modelos (tabelas) herdam.
Base = declarative_base()


def get_db():
    """
    Dependency do FastAPI que abre uma sessão de banco por requisição
    e garante que ela seja fechada no final, mesmo se der erro.

    Uso em uma rota:
        @router.get("/algo")
        def endpoint(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
