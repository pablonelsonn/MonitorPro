"""Configuração do MonitorPro Agent."""
import os

SERVER_URL = os.environ.get("MONITORPRO_SERVER_URL", "http://127.0.0.1:8000").rstrip("/")
HEARTBEAT_INTERVAL_SECONDS = int(os.environ.get("MONITORPRO_HEARTBEAT_INTERVAL", "30"))
