"""
routers/branding.py
-----------------------
Endpoint simples que devolve o nome de marca configurado no servidor
(`settings.BRAND_NAME`), para que o dashboard e o agente exibam o
mesmo nome/identidade em vez de "MonitorPro" fixo no código deles.

Isso é o que permite, no futuro, que uma empresa revenda o sistema
com o próprio nome apenas trocando a variável de ambiente BRAND_NAME
no servidor — sem precisar recompilar dashboard/agente.
"""

from fastapi import APIRouter

from app.core.config import settings
from app.schemas import BrandingOut

router = APIRouter(prefix="/branding", tags=["branding"])


@router.get("", response_model=BrandingOut)
def get_branding():
    return BrandingOut(brand_name=settings.BRAND_NAME)
