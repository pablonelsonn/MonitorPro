"""Schemas Pydantic da API MonitorPro.

Os schemas de Agent ficam aqui junto dos schemas administrativos para evitar
conflito entre `app/schemas.py` e uma pasta `app/schemas/`.
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class OSInfo(BaseModel):
    name: str
    version: Optional[str] = None
    build: Optional[str] = None


class MetricsPayload(BaseModel):
    cpu_percent: float = Field(ge=0, le=100)
    ram_percent: float = Field(ge=0, le=100)
    disk_percent: float = Field(ge=0, le=100)
    net_sent_kbps: Optional[float] = Field(default=None, ge=0)
    net_recv_kbps: Optional[float] = Field(default=None, ge=0)


class AgentRegisterRequest(BaseModel):
    machine_id: str = Field(min_length=1, max_length=64)
    hostname: str = Field(min_length=1, max_length=255)
    os_info: Optional[OSInfo] = None


class AgentRegisterResponse(BaseModel):
    computer_id: int
    agent_key: str


class AgentHeartbeatRequest(BaseModel):
    machine_id: str = Field(min_length=1, max_length=64)
    agent_key: str = Field(min_length=1, max_length=128)
    metrics: Optional[MetricsPayload] = None


class ComputerHeartbeat(BaseModel):
    """Compatibilidade com clientes antigos; novo Agent usa /agents/heartbeat."""
    hostname: str
    agent_key: str
    cpu_percent: float
    ram_percent: float
    disk_percent: float


class ComputerOut(BaseModel):
    id: int
    machine_id: Optional[str] = None
    hostname: str
    last_ip: Optional[str] = None
    last_seen: Optional[datetime] = None
    status: str
    is_online: bool
    os_info: Optional[dict] = None
    cpu_percent: Optional[float] = None
    ram_percent: Optional[float] = None
    disk_percent: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)


class MetricOut(BaseModel):
    cpu_percent: float
    ram_percent: float
    disk_percent: float
    recorded_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class BlockedDomainCreate(BaseModel):
    domain: str


class BlockedDomainOut(BaseModel):
    id: int
    domain: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BrandingOut(BaseModel):
    brand_name: str
