"""Ponto de entrada da API MonitorPro."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import Base, SessionLocal, engine
from app.core.migrations import migrate_existing_database
from app.core.security import hash_password
from app.models.blocked_domain import BlockedDomain  # noqa: F401
from app.models.computer import Computer  # noqa: F401
from app.models.metric import Metric  # noqa: F401
from app.models.user import User
from app.routers import agents, auth, branding, computers, domains


# Importar todos os modelos acima garante que Base.metadata conheça as tabelas.
Base.metadata.create_all(bind=engine)
migrate_existing_database()


def ensure_default_admin() -> None:
    """Cria admin/admin123 somente em banco sem usuários.

    Não altera a senha de um administrador existente.
    """
    db = SessionLocal()
    try:
        if db.query(User).count() == 0:
            db.add(
                User(
                    username="admin",
                    hashed_password=hash_password("admin123"),
                    is_active=True,
                )
            )
            db.commit()
    finally:
        db.close()


ensure_default_admin()


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title=f"{settings.BRAND_NAME} API",
    description="API central do servidor de monitoramento MonitorPro.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Auth: login sem JWT para obter o token.
app.include_router(auth.router)
# Agent: registro e heartbeat sem JWT; usam machine_id + agent_key.
app.include_router(agents.router)
# Dashboard: endpoints administrativos protegidos por JWT.
app.include_router(computers.router)
app.include_router(domains.router)
app.include_router(branding.router)


@app.get("/")
def root():
    return {"status": "online", "brand": settings.BRAND_NAME, "version": app.version}


@app.get("/health")
def health():
    return {"status": "ok", "service": "monitorpro-api"}
