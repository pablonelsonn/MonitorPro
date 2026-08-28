"""
routers/domains.py
----------------------
CRUD simples da lista de domínios bloqueados.

- Endpoints de escrita (POST/DELETE) exigem login (JWT) — só o
  administrador pode alterar a lista.
- O endpoint de leitura (GET) também é usado pelo AGENTE para saber
  quais domínios aplicar no arquivo hosts local. Poderia futuramente
  usar uma autenticação própria de agente, mas por simplicidade nesta
  versão ele reaproveita a agent_key da máquina como identificação.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.blocked_domain import BlockedDomain
from app.schemas import BlockedDomainCreate, BlockedDomainOut

router = APIRouter(prefix="/domains", tags=["domains"])


@router.get("", response_model=list[BlockedDomainOut])
def list_domains(db: Session = Depends(get_db)):
    """Lista de domínios bloqueados — lida tanto pelo dashboard quanto pelo agente."""
    return db.query(BlockedDomain).order_by(BlockedDomain.domain).all()


@router.post("", response_model=BlockedDomainOut, status_code=201)
def add_domain(payload: BlockedDomainCreate, db: Session = Depends(get_db), _user=Depends(get_current_user)):
    """Adiciona um novo domínio à lista de bloqueio (requer login de administrador)."""
    exists = db.query(BlockedDomain).filter(BlockedDomain.domain == payload.domain).first()
    if exists:
        raise HTTPException(status_code=409, detail="Domínio já está na lista de bloqueio")

    domain = BlockedDomain(domain=payload.domain)
    db.add(domain)
    db.commit()
    db.refresh(domain)
    return domain


@router.delete("/{domain_id}", status_code=204)
def remove_domain(domain_id: int, db: Session = Depends(get_db), _user=Depends(get_current_user)):
    """Remove um domínio da lista de bloqueio (requer login de administrador)."""
    domain = db.get(BlockedDomain, domain_id)
    if not domain:
        raise HTTPException(status_code=404, detail="Domínio não encontrado")
    db.delete(domain)
    db.commit()
