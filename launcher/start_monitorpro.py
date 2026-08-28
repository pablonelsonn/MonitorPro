"""
Launcher do MonitorPro para uso em desenvolvimento / na mesma máquina.

O que faz:
  1. Verifica se o servidor (uvicorn) já está respondendo em SERVER_URL.
  2. Se não estiver, sobe o servidor como subprocesso, na pasta server/,
     e espera até ele responder (timeout configurável).
  3. Abre o Dashboard normalmente.

Isso é só uma conveniência para você testar tudo com um clique só. No
produto final, o servidor roda numa máquina central e o Dashboard do
cliente NUNCA deve tentar subir um servidor local — ele só se conecta ao
endereço configurado (ver agent/config.py e o mesmo padrão vale pro
dashboard). Quando chegar na Fase 6/7, é só parar de usar este launcher.

Ajuste SERVER_DIR e DASHBOARD_ENTRYPOINT para os caminhos reais do seu
projeto se a estrutura de pastas não bater exatamente.
"""
import os
import subprocess
import sys
import threading
import time
from pathlib import Path

import requests

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SERVER_DIR = PROJECT_ROOT / "server"
DASHBOARD_DIR = PROJECT_ROOT / "dashboard"

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 8000
SERVER_URL = f"http://{SERVER_HOST}:{SERVER_PORT}"

# Endpoint usado só para checar se o servidor já respondeu. /docs existe em
# qualquer FastAPI por padrão, então serve como health check sem precisar
# que você tenha criado um endpoint /health.
HEALTH_CHECK_PATH = "/docs"

STARTUP_TIMEOUT_SECONDS = 30


def _server_is_up() -> bool:
    try:
        resp = requests.get(f"{SERVER_URL}{HEALTH_CHECK_PATH}", timeout=1)
        return resp.status_code < 500
    except requests.RequestException:
        return False


def _stream_output(process: subprocess.Popen, collected: list[str]):
    """Lê a saída do uvicorn linha a linha e imprime em tempo real, prefixada,
    além de guardar tudo em `collected` para reexibir se der timeout/erro."""
    if process.stdout is None:
        return
    for line in process.stdout:
        line = line.rstrip("\n")
        collected.append(line)
        print(f"[uvicorn] {line}")


def start_server_if_needed() -> subprocess.Popen | None:
    """Sobe o uvicorn em segundo plano se ainda não estiver rodando. Retorna o processo (ou None se já estava de pé)."""
    if _server_is_up():
        print(f"[launcher] Servidor já está rodando em {SERVER_URL}")
        return None

    if not SERVER_DIR.exists():
        raise FileNotFoundError(
            f"Pasta do servidor não encontrada: {SERVER_DIR}\n"
            f"Ajuste SERVER_DIR no início deste arquivo se a estrutura de pastas for diferente."
        )

    cmd = [sys.executable, "-m", "uvicorn", "app.main:app", "--host", SERVER_HOST, "--port", str(SERVER_PORT)]
    print(f"[launcher] Servidor não encontrado em {SERVER_URL}. Subindo uvicorn...")
    print(f"[launcher] Comando: {' '.join(cmd)}")
    print(f"[launcher] Pasta:   {SERVER_DIR}")

    # CREATE_NO_WINDOW evita abrir um console extra no Windows.
    creationflags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0

    process = subprocess.Popen(
        cmd,
        cwd=str(SERVER_DIR),
        creationflags=creationflags,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    # Lê e imprime a saída do uvicorn em uma thread separada, em tempo real,
    # em vez de só ler tudo de uma vez no final (que é o que escondia o erro real).
    collected_lines: list[str] = []
    reader_thread = threading.Thread(target=_stream_output, args=(process, collected_lines), daemon=True)
    reader_thread.start()

    deadline = time.time() + STARTUP_TIMEOUT_SECONDS
    while time.time() < deadline:
        if _server_is_up():
            print("[launcher] Servidor no ar.")
            return process
        if process.poll() is not None:
            raise RuntimeError(
                f"O servidor encerrou sozinho antes de ficar pronto (código {process.returncode}). "
                f"Veja a saída [uvicorn] acima para o motivo real."
            )
        time.sleep(0.5)

    process.terminate()
    raise TimeoutError(
        f"Servidor não respondeu em {SERVER_URL}{HEALTH_CHECK_PATH} depois de {STARTUP_TIMEOUT_SECONDS}s.\n"
        f"Veja a saída [uvicorn] acima -- se não apareceu NADA prefixado com [uvicorn], "
        f"o processo pode estar travado num import ou numa conexão de banco que não retorna."
    )


def launch_dashboard():
    sys.path.insert(0, str(DASHBOARD_DIR.parent))
    from dashboard.main import main as dashboard_main  # ajuste se o entrypoint tiver outro nome
    dashboard_main()


def main():
    server_process = None
    try:
        server_process = start_server_if_needed()
        launch_dashboard()
    finally:
        # Se este launcher subiu o servidor, encerra junto quando o Dashboard fechar.
        # Se o servidor já estava rodando antes (ex: você mesmo subiu manualmente),
        # deixa ele rodando -- não mata processo que não foi este launcher quem criou.
        if server_process is not None:
            print("[launcher] Encerrando servidor...")
            server_process.terminate()


if __name__ == "__main__":
    main()
