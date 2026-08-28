# MonitorPro — Backend Consolidado

Esta versão consolida o backend mantendo o banco SQLite existente e o `id` inteiro da tabela `computers`.

## O que foi corrigido

- `Computer` voltou a usar `Base` corretamente.
- `computers.id` permanece `INTEGER`, compatível com `metrics.computer_id`.
- `machine_id` persistente foi incorporado ao modelo.
- `status` e `os_info` foram incorporados ao modelo.
- `/agents/register` e `/agents/heartbeat` passaram a ser os endpoints oficiais do Agent.
- O router de Agent agora é registrado em `app/main.py`.
- O heartbeat grava histórico na tabela `metrics`.
- `/computers` ficou exclusivamente administrativo e protegido por JWT.
- O schema de Agent foi consolidado em `app/schemas.py`; a pasta conflitante `app/schemas/` foi removida.
- O status online/offline é calculado pelo último heartbeat.
- `get_current_user` também rejeita usuário inativo.
- Foi adicionada uma migração inicial que ALTERA o SQLite existente sem apagar as tabelas/dados.
- `health` foi adicionado em `/health`.
- O admin existente não é recriado nem tem a senha alterada automaticamente.

## Teste local

No PowerShell:

```powershell
cd D:\Projetos\MonitorPro\server
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Depois:

```text
http://127.0.0.1:8000/docs
http://127.0.0.1:8000/health
```

O Agent deve usar:

```text
MONITORPRO_SERVER_URL=http://127.0.0.1:8000
```

## Importante

`127.0.0.1` continua apenas para desenvolvimento. Na arquitetura final, o Agent e o Dashboard deverão apontar para o endereço do servidor central, por exemplo `https://api.seudominio.com`.

O backend consolidado não implementa ainda WebSocket, Windows Service ou suporte remoto; essas são etapas seguintes.
