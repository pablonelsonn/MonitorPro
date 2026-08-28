"""Endpoints administrativos de computadores monitorados."""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.computer import Computer
from app.models.metric import Metric
from app.schemas import ComputerOut, MetricOut

router = APIRouter(prefix="/computers", tags=["computers"])


def _is_online(last_seen: datetime | None) -> bool:
    if last_seen is None:
        return False
    if last_seen.tzinfo is None:
        last_seen = last_seen.replace(tzinfo=timezone.utc)
    return (datetime.now(timezone.utc) - last_seen).total_seconds() <= settings.AGENT_OFFLINE_THRESHOLD


def _to_out(db: Session, computer: Computer) -> ComputerOut:
    online = _is_online(computer.last_seen)
    computer.status = "online" if online else "offline"
    latest = (
        db.query(Metric)
        .filter(Metric.computer_id == computer.id)
        .order_by(Metric.recorded_at.desc())
        .first()
    )
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


@router.get("", response_model=list[ComputerOut])
def list_computers(
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    computers = db.query(Computer).order_by(Computer.hostname).all()
    result = [_to_out(db, c) for c in computers]
    db.commit()
    return result


@router.get("/{computer_id}", response_model=ComputerOut)
def get_computer(
    computer_id: int,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    computer = db.get(Computer, computer_id)
    if not computer:
        raise HTTPException(status_code=404, detail="Computador não encontrado")
    result = _to_out(db, computer)
    db.commit()
    return result


@router.get("/{computer_id}/metrics", response_model=list[MetricOut])
def get_computer_metrics(
    computer_id: int,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    if db.get(Computer, computer_id) is None:
        raise HTTPException(status_code=404, detail="Computador não encontrado")

    return (
        db.query(Metric)
        .filter(Metric.computer_id == computer_id)
        .order_by(Metric.recorded_at.desc())
        .limit(100)
        .all()
    )
