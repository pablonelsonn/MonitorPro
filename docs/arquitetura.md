# Arquitetura do MonitorPro

## Visão geral

```
 ┌─────────────┐        HTTPS/JSON        ┌──────────────┐
 │  Dashboard   │ ───────────────────────▶ │              │
 │  (PySide6)   │ ◀─────────────────────── │              │
 └─────────────┘                           │   Servidor   │
                                            │  (FastAPI)   │
 ┌─────────────┐        HTTPS/JSON         │              │
 │   Agente     │ ───────────────────────▶ │              │
 │  (Windows)   │ ◀─────────────────────── │              │
 └─────────────┘                           └──────┬───────┘
                                                    │
                                             ┌──────▼───────┐
                                             │   Banco de   │
                                             │    Dados     │
                                             │  (SQLite/PG) │
                                             └──────────────┘
```

## Fluxo de auto-cadastro de computador

1. O agente é instalado em um PC Windows e iniciado pela primeira vez.
2. Ele gera (e salva localmente) uma `agent_key` aleatória — a "identidade" da máquina.
3. A cada 30 segundos, envia `POST /computers/heartbeat` com hostname + agent_key + métricas.
4. O servidor verifica se já existe um computador com esse hostname:
   - **Não existe** → cria automaticamente (é aqui que acontece o "cadastro automático").
   - **Já existe** → confirma que a `agent_key` bate, e apenas atualiza `last_seen`/métricas.

## Fluxo de autenticação do dashboard

1. Administrador digita usuário/senha na tela de login.
2. `POST /auth/login` valida a senha (hash bcrypt) e devolve um JWT.
3. O dashboard guarda o token em memória e o envia em
   `Authorization: Bearer <token>` em toda chamada subsequente.
4. Rotas administrativas usam a dependency `get_current_user` para
   validar o token a cada requisição.

## Cálculo de status online/offline

Não existe uma coluna "is_online" no banco. Em vez disso, o servidor
calcula na hora, comparando `last_seen` com o momento atual:

```python
is_online = (agora - last_seen) <= AGENT_OFFLINE_THRESHOLD  # 90s por padrão
```

Essa abordagem evita ter dois lugares (coluna + heartbeat) que possam
ficar dessincronizados.

## Roadmap técnico (fora do escopo desta versão)

| Recurso          | Abordagem planejada                                                        |
|-------------------|-----------------------------------------------------------------------------|
| Multiempresa      | `company_id` em `User`/`Computer` + filtro automático por empresa logada   |
| Grupos            | Tabela `groups` + tabela associativa `computer_groups` (N:N)               |
| Auditoria         | Tabela `audit_log` (usuário, ação, alvo, timestamp) + middleware de log    |
| Licenciamento     | Tabela `license` + verificação periódica (local ou contra servidor externo)|
| Instalador Windows| PyInstaller (agente e dashboard) + Inno Setup (instalador) + NSSM (serviço)|
