"""
core/config.py
----------------
Configurações centrais do servidor MonitorPro.

Tudo que é "ajustável" (segredo do JWT, tempo de expiração do token,
nome da empresa/marca exibida no dashboard, caminho do banco de dados)
fica concentrado aqui, lido de variáveis de ambiente quando existirem,
com valores padrão sensatos para rodar localmente em modo de teste.

Isso evita "números mágicos" espalhados pelo código e facilita a
futura configuração multiempresa (cada empresa poderá ter seu próprio
arquivo .env ou registro de configuração no banco).
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Nome da empresa/produto exibido no dashboard e nos e-mails/relatórios.
    # Pense nisso como o "branding" do sistema: pode ser trocado por
    # empresa que revender o MonitorPro com identidade própria.
    BRAND_NAME: str = "MonitorPro"

    # Caminho do banco SQLite (troque por uma URL do Postgres/MySQL em produção).
    DATABASE_URL: str = "sqlite:///./monitorpro.db"

    # Segredo usado para assinar os tokens JWT. EM PRODUÇÃO, defina isso
    # via variável de ambiente (nunca deixe o valor padrão abaixo).
    JWT_SECRET: str = "troque-esta-chave-em-producao"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 8  # 8 horas de sessão

    # Intervalo esperado (em segundos) entre os "heartbeats" que o agente
    # Windows envia ao servidor. Usado para decidir quando um computador
    # deve ser marcado como "offline" no dashboard.
    AGENT_HEARTBEAT_INTERVAL: int = 30
    AGENT_OFFLINE_THRESHOLD: int = 90

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


# Instância única (singleton) usada em todo o servidor via import direto:
#   from app.core.config import settings
settings = Settings()
