"""
Reúne todos os modelos em um único lugar para que
`Base.metadata.create_all()` (chamado em main.py) enxergue todas as
tabelas na hora de criar o banco de dados.
"""

from app.models.user import User
from app.models.computer import Computer
from app.models.metric import Metric
from app.models.blocked_domain import BlockedDomain

__all__ = ["User", "Computer", "Metric", "BlockedDomain"]
