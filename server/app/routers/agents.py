"""Endpoints exclusivos do MonitorPro Agent."""
import secrets
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.computer import Computer
from app.models.metric import Metric
from app.schemas import (
    AgentHeartbeatRequest,
    AgentRegisterRequest,
    AgentRegisterResponse,
    ComputerOut,
)

router = APIRouter(prefix="/agents", tags=["agents"])


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _is_online(last_seen: datetime | None) -> bool:
    if last_seen is None:
        return False
    if last_seen.tzinfo is None:
        last_seen = last_seen.replace(tzinfo=timezone.utc)
    return (_utc_now() - last_seen).total_seconds() <= settings.AGENT_OFFLINE_THRESHOLD


def _generate_agent_key() -> str:
    return secrets.token_urlsafe(32)


def _computer_out(db: Session, computer: Computer) -> ComputerOut:
    latest = (
        db.query(Metric)
        .filter(Metric.computer_id == computer.id)
        .order_by(Metric.recorded_at.desc())
        .first()
    )
    online = _is_online(computer.last_seen)
    if computer.status != ("online" if online else "offline"):
        computer.status = "online" if online else "offline"

    return ComputerOut(
        id=computer.id,
        machine_id=computer.machine_id,
        hostname=computer.hostname,
        last_ip=computer.last_ip,
        last_seen=computer.last_seen,
        status=computer.status,
        is_online=online,
        os_info=computer.os_info,
        cpu_percent=latest.cpu_percent if latest else None,
        ram_percent=latest.ram_percent if latest else None,
        disk_percent=latest.disk_percent if latest else None,
    )


@router.post("/register", response_model=AgentRegisterResponse)
def register_agent(
    payload: AgentRegisterRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    """Registra a máquina ou recupera sua identidade persistente."""
    computer = db.query(Computer).filter(Computer.machine_id == payload.machine_id).first()
    client_ip = request.client.host if request.client else None

    if computer is None:
        computer = Computer(
            machine_id=payload.machine_id,
            hostname=payload.hostname,
            agent_key=_generate_agent_key(),
            os_info=payload.os_info.model_dump() if payload.os_info else None,
            last_ip=client_ip,
            last_seen=_utc_now(),
            status="online",
        )
        db.add(computer)
    else:
        computer.hostname = payload.hostname
        if payload.os_info:
            computer.os_info = payload.os_info.model_dump()
        computer.last_ip = client_ip
        computer.last_seen = _utc_now()
        computer.status = "online"

    db.commit()
    db.refresh(computer)
    return AgentRegisterResponse(computer_id=computer.id, agent_key=computer.agent_key)


@router.post("/heartbeat", response_model=ComputerOut)
def agent_heartbeat(
    payload: AgentHeartbeatRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    """Atualiza presença e grava uma leitura de métricas."""
    computer = db.query(Computer).filter(Computer.machine_id == payload.machine_id).first()
    if computer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Máquina não registrada")

    if not secrets.compare_digest(computer.agent_key, payload.agent_key):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="agent_key inválida")

    computer.last_ip = request.client.host if request.client else computer.last_ip
    computer.last_seen = _utc_now()
    computer.status = "online"

    if payload.metrics:
        db.add(
            Metric(
                computer_id=computer.id,
                cpu_percent=payload.metrics.cpu_percent,
                ram_percent=payload.metrics.ram_percent,
                disk_percent=payload.metrics.disk_percent,
            )
        )

    db.commit()
    db.refresh(computer)
    return _computer_out(db, computer)
