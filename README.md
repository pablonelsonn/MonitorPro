# MonitorPro — Fase 1: Agent + registro + heartbeat

Estes arquivos implementam a Etapa 1 do plano: `machine_id` persistente,
registro automático do Agent e heartbeat periódico com métricas.

## Como integrar ao seu projeto existente

1. **server/app/models/computer.py**
   Você já tem um modelo `Computer` (ou equivalente) com `hostname`,
   `agent_key`, `last_ip`, `last_seen`. Não sobrescreva o seu — compare
   campo a campo e adicione o que estiver faltando (`machine_id`, `os_info`,
   `status`). Troque `Base` na linha da classe pelo import real do seu
   `Base` declarativo (provavelmente `from app.core.database import Base`).

2. **server/app/schemas/agent.py**
   Pode copiar direto — não deve conflitar com schemas existentes.

3. **server/app/routers/agents.py**
   Ajuste os dois imports no topo (`get_db`, `settings`) para o caminho
   real do seu projeto. Adicione ao `server/app/main.py`:
   ```python
   from app.routers import agents
   app.include_router(agents.router)
   ```
   Em `app/core/config.py`, adicione (se ainda não existir):
   ```python
   OFFLINE_THRESHOLD_SECONDS: int = 90
   ```

4. **Migração do banco**
   Se estiver usando Alembic, gere uma migração para a nova coluna
   `machine_id` (e `os_info`/`status`, se ainda não existirem) na tabela
   `computers`. Se não estiver usando Alembic ainda, crie as tabelas de
   novo (`Base.metadata.create_all`) — mas isso apaga dados existentes em
   SQLite, então cuidado se já tiver computadores cadastrados.

5. **agent/identity.py, agent/metrics_collector.py, agent/config.py, agent/main.py**
   Coloque na sua pasta `agent/` (você já tem `identity.py` e
   `metrics_collector.py` — compare com os seus antes de substituir, pode
   ser que você já tenha lógica que eu não conheço). Instale as
   dependências: `pip install requests psutil`.

## Testando localmente

```bash
# Terminal 1 — servidor (like você já faz hoje)
uvicorn app.main:app --reload

# Terminal 2 — agente
set MONITORPRO_SERVER_URL=http://127.0.0.1:8000
python -m agent.main
```

Você deve ver no terminal do agente: `machine_id: ...`, depois
`Registrado no servidor com sucesso`, e a cada 30s `Heartbeat OK`.

No banco, a tabela `computers` deve ganhar uma linha com `status=online`
e `last_seen` atualizando a cada heartbeat.

## O que NÃO está nesta fase (de propósito)

- WebSocket (Fase 4 do plano) — por enquanto o heartbeat é HTTP simples,
  que já é suficiente pra validar registro + métricas funcionando.
- Windows Service (Fase 6) — hoje o agente roda como processo Python
  comum, pra facilitar o teste. Empacotamos como serviço depois que o
  fluxo de registro/heartbeat estiver validado no seu ambiente.
- Dashboard (PySide6) consumindo `/agents/computers` — é rápido de fazer
  assim que você confirmar que o registro/heartbeat está funcionando.
- Módulo de suporte remoto (tipo AnyDesk) e monitoramento de atividade
  (tipo Teramind) — ficam pra depois do monitoramento básico estar
  redondo, como o plano original sugeriu.

## Subir o servidor automaticamente ao iniciar (launcher)

Se você quer abrir uma coisa só e o servidor subir sozinho antes do login
(em vez de precisar de dois terminais), use `launcher/start_monitorpro.py`:

```bash
python launcher/start_monitorpro.py
```

ou, no Windows, dá duplo-clique em `launcher/start_monitorpro.bat`.

O que ele faz: checa se `http://127.0.0.1:8000/docs` já responde; se não
responder, sobe o `uvicorn` como subprocesso na pasta `server/`, espera
até 20s ele ficar pronto, e só então abre o Dashboard. Ajuste
`DASHBOARD_ENTRYPOINT`/o import de `dashboard.main` dentro do arquivo se o
ponto de entrada do seu Dashboard tiver outro nome de função.

**Isso é só para desenvolvimento**, com server e dashboard na mesma
máquina. No produto final o servidor roda numa máquina central (Fase
6/7) e o Dashboard do cliente só se conecta ao endereço configurado —
ele nunca deve tentar subir um servidor local.

## Próximo passo

Testa esse fluxo com um agente rodando e me conta o resultado (ou manda
erros que aparecerem). Depois seguimos pra Fase 3 (várias máquinas reais
aparecendo na lista) e Fase 5 (tela do Dashboard puxando
`GET /agents/computers`).

Se quiser que eu já mexa diretamente no seu código em vez de te entregar
módulos soltos, me manda o `MonitorPro.zip` (sem `.venv`, `__pycache__`,
`dist`, `build`, e sem segredos reais no `.env`).
