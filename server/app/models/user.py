"""
models/user.py
----------------
Representa um administrador que faz login no dashboard MonitorPro.

Em uma futura versão multiempresa, esta tabela ganharia uma coluna
`company_id` (chave estrangeira para uma tabela `companies`), permitindo
que cada empresa cliente tenha seus próprios administradores isolados.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, func

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    # Permite desativar um admin sem apagar seu histórico de ações (útil para auditoria futura).
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
