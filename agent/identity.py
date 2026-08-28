"""
Identidade persistente da máquina monitorada.

Gera um machine_id (UUID4) na primeira execução e salva localmente, de forma
que a mesma instalação do Agent sempre se identifique da mesma forma para o
servidor -- mesmo que o IP mude (DHCP) ou o hostname seja alterado.

O arquivo é salvo em %PROGRAMDATA%\\MonitorPro\\machine_id (Windows) para que
sobreviva mesmo se o usuário reinstalar o Agent na mesma máquina, e para não
depender da pasta do usuário logado (o Agent deve rodar como Windows Service,
sem sessão de usuário interativa).
"""
import os
import platform
import socket
import uuid
from pathlib import Path


def _data_dir() -> Path:
    if platform.system() == "Windows":
        base = os.environ.get("PROGRAMDATA", r"C:\ProgramData")
    else:
        # Fallback para desenvolvimento em Linux/Mac
        base = os.environ.get("XDG_DATA_HOME", str(Path.home() / ".local" / "share"))
    path = Path(base) / "MonitorPro"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _machine_id_path() -> Path:
    return _data_dir() / "machine_id"


def get_or_create_machine_id() -> str:
    """Retorna o machine_id persistido, gerando um novo se ainda não existir."""
    path = _machine_id_path()
    if path.exists():
        saved = path.read_text(encoding="utf-8").strip()
        if saved:
            return saved

    new_id = str(uuid.uuid4())
    path.write_text(new_id, encoding="utf-8")
    return new_id


def get_hostname() -> str:
    return socket.gethostname()


def get_os_info() -> dict:
    return {
        "name": platform.system(),
        "version": platform.release(),
        "build": platform.version(),
    }
