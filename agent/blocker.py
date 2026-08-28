"""
agent/blocker.py
--------------------
Aplica o bloqueio administrativo de domínios editando o arquivo hosts
do Windows (C:\\Windows\\System32\\drivers\\etc\\hosts).

Como funciona: cada domínio bloqueado ganha uma linha redirecionando-o
para 127.0.0.1 (localhost). Isso faz o navegador tentar carregar o
site e falhar, efetivamente bloqueando o acesso sem precisar de
firewall ou proxy.

IMPORTANTE: editar o arquivo hosts requer privilégios de administrador
no Windows. O agente precisa ser instalado/executado como serviço com
permissões elevadas para que este módulo funcione.
"""

from pathlib import Path

HOSTS_PATH = Path(r"C:\Windows\System32\drivers\etc\hosts")

# Marcadores usados para delimitar o bloco de linhas que o MonitorPro
# controla dentro do arquivo hosts, sem mexer no restante do conteúdo
# (que pode ter entradas manuais do próprio usuário/TI).
BLOCK_START = "# >>> MonitorPro - domínios bloqueados (não editar manualmente) >>>"
BLOCK_END = "# <<< MonitorPro - fim do bloqueio <<<"


def apply_blocklist(domains: list[str]) -> None:
    """
    Reescreve o bloco de bloqueio do MonitorPro dentro do arquivo hosts,
    preservando todo o conteúdo que já existia fora desse bloco.
    """
    if not HOSTS_PATH.exists():
        raise FileNotFoundError(f"Arquivo hosts não encontrado em {HOSTS_PATH}")

    original = HOSTS_PATH.read_text(encoding="utf-8")

    # Remove um bloco antigo do MonitorPro, se existir, para não duplicar.
    if BLOCK_START in original:
        before = original.split(BLOCK_START)[0]
        after = original.split(BLOCK_END)[-1]
        original = before + after

    block_lines = [BLOCK_START]
    for domain in domains:
        domain = domain.strip()
        if not domain:
            continue
        block_lines.append(f"127.0.0.1 {domain}")
        block_lines.append(f"127.0.0.1 www.{domain}")
    block_lines.append(BLOCK_END)

    new_content = original.rstrip() + "\n\n" + "\n".join(block_lines) + "\n"
    HOSTS_PATH.write_text(new_content, encoding="utf-8")
