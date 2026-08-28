"""
models/blocked_domain.py
---------------------------
Lista de domínios que o administrador quer bloquear nas máquinas
monitoradas (ex.: "facebook.com", "jogos-online.com").

O agente Windows consulta essa lista periodicamente e aplica o bloqueio
localmente editando o arquivo hosts do Windows (ver agent/blocker.py).
"""

from sqlalchemy import Column, Integer, String, DateTime, func

from app.core.database import Base


class BlockedDomain(Base):
    __tablename__ = "blocked_domains"

    id = Column(Integer, primary_key=True, index=True)
    domain = Column(String, unique=True, index=True, nullable=False)

    # Guardamos quem/quando adicionou o bloqueio — base para auditoria futura.
    created_at = Column(DateTime(timezone=True), server_default=func.now())
