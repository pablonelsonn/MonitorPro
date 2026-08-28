"""Migrações mínimas para manter o SQLite existente sem apagar dados.

O projeto ainda não usa Alembic no fluxo de desenvolvimento. Este módulo
faz somente a evolução inicial necessária da tabela `computers`. Quando o
produto passar para PostgreSQL, estas mudanças devem ser convertidas para
migrações Alembic versionadas.
"""
import uuid

from sqlalchemy import inspect, text

from app.core.database import engine


def _columns(table: str) -> set[str]:
    return {c["name"] for c in inspect(engine).get_columns(table)}


def migrate_existing_database() -> None:
    """Adiciona colunas novas ao banco SQLite antigo sem recriá-lo."""
    inspector = inspect(engine)
    if "computers" not in inspector.get_table_names():
        return

    columns = _columns("computers")
    additions = []
    if "machine_id" not in columns:
        additions.append("ALTER TABLE computers ADD COLUMN machine_id VARCHAR(64)")
    if "status" not in columns:
        additions.append("ALTER TABLE computers ADD COLUMN status VARCHAR(16) DEFAULT 'offline'")
    if "os_info" not in columns:
        additions.append("ALTER TABLE computers ADD COLUMN os_info JSON")

    with engine.begin() as conn:
        for statement in additions:
            conn.execute(text(statement))

        # Registros antigos recebem uma identidade própria. O banco atual do
        # projeto está vazio de computadores, mas isso torna a migração segura.
        rows = conn.execute(
            text("SELECT id FROM computers WHERE machine_id IS NULL")
        ).fetchall()
        for row in rows:
            conn.execute(
                text("UPDATE computers SET machine_id=:machine_id, status='offline' WHERE id=:id"),
                {"machine_id": str(uuid.uuid4()), "id": row[0]},
            )

        conn.execute(text("UPDATE computers SET status='offline' WHERE status IS NULL"))
        conn.execute(
            text("CREATE UNIQUE INDEX IF NOT EXISTS ux_computers_machine_id ON computers(machine_id)")
        )
        conn.execute(
            text("CREATE UNIQUE INDEX IF NOT EXISTS ux_computers_agent_key ON computers(agent_key)")
        )
