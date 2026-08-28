"""
MonitorPro Agent -- ponto de entrada.

Fluxo:
  1. Obtém (ou gera) o machine_id persistente.
  2. Se ainda não tiver um agent_key salvo, chama /agents/register.
  3. Entra em loop: coleta métricas e envia /agents/heartbeat a cada
     HEARTBEAT_INTERVAL_SECONDS.

Este arquivo assume uma execução "sempre rodando" (processo em primeiro
plano). Para produção, empacote como Windows Service (Fase 4 do plano --
posso montar isso com o pywin32 quando chegarmos lá) em vez de depender de
um atalho na pasta Startup.

Dependências: pip install requests psutil
"""
import json
import logging
import time
from pathlib import Path

import requests

from agent.config import SERVER_URL, HEARTBEAT_INTERVAL_SECONDS
from agent.identity import get_or_create_machine_id, get_hostname, get_os_info, _data_dir
from agent.metrics_collector import MetricsCollector

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("monitorpro-agent")

AGENT_KEY_PATH = _data_dir() / "agent_key"


def _load_agent_key() -> str | None:
    if AGENT_KEY_PATH.exists():
        key = AGENT_KEY_PATH.read_text(encoding="utf-8").strip()
        return key or None
    return None


def _save_agent_key(key: str) -> None:
    AGENT_KEY_PATH.write_text(key, encoding="utf-8")


def register(machine_id: str) -> str:
    """Registra a máquina no servidor e devolve o agent_key. Tenta indefinidamente até conseguir."""
    payload = {
        "machine_id": machine_id,
        "hostname": get_hostname(),
        "os_info": get_os_info(),
    }

    while True:
        try:
            resp = requests.post(f"{SERVER_URL}/agents/register", json=payload, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            log.info("Registrado no servidor com sucesso (computer_id=%s)", data["computer_id"])
            return data["agent_key"]
        except requests.RequestException as exc:
            log.warning("Falha ao registrar no servidor (%s). Tentando novamente em 10s...", exc)
            time.sleep(10)


def run():
    machine_id = get_or_create_machine_id()
    log.info("machine_id: %s", machine_id)

    agent_key = _load_agent_key()
    if not agent_key:
        agent_key = register(machine_id)
        _save_agent_key(agent_key)

    collector = MetricsCollector()

    while True:
        metrics = collector.collect()
        payload = {
            "machine_id": machine_id,
            "agent_key": agent_key,
            "metrics": metrics,
        }

        try:
            resp = requests.post(f"{SERVER_URL}/agents/heartbeat", json=payload, timeout=10)
            if resp.status_code == 404:
                # Servidor não reconhece mais esta máquina (ex: banco recriado) -> registra de novo
                log.warning("Servidor não reconhece machine_id. Registrando novamente...")
                agent_key = register(machine_id)
                _save_agent_key(agent_key)
            elif resp.status_code == 401:
                log.error("agent_key rejeitada pelo servidor. Apague %s e reinicie o agente.", AGENT_KEY_PATH)
            else:
                resp.raise_for_status()
                log.info(
                    "Heartbeat OK -- CPU %.1f%% RAM %.1f%% Disco %.1f%%",
                    metrics["cpu_percent"], metrics["ram_percent"], metrics["disk_percent"],
                )
        except requests.RequestException as exc:
            log.warning("Falha ao enviar heartbeat (%s). Vai tentar de novo no próximo ciclo.", exc)

        time.sleep(HEARTBEAT_INTERVAL_SECONDS)


if __name__ == "__main__":
    run()
