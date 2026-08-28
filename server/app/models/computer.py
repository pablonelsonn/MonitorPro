"""Modelo SQLAlchemy para computadores monitorados pelo MonitorPro."""
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, JSON, String, func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Computer(Base):
    __tablename__ = "computers"

    # Mantemos INTEGER porque o banco existente e a tabela metrics já usam
    # computer_id INTEGER. Isso evita quebrar os dados atuais.
    id = Column(Integer, primary_key=True, index=True)

    # Identidade persistente da instalação do Agent.
    machine_id = Column(String(64), unique=True, nullable=True, index=True)
    hostname = Column(String(255), nullable=False)
    agent_key = Column(String(128), unique=True, nullable=False)

    last_ip = Column(String(45), nullable=True)
    last_seen = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(16), nullable=False, default="offline", server_default="offline")

    os_info = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    metrics = relationship("Metric", back_populates="computer", cascade="all, delete-orphan")
