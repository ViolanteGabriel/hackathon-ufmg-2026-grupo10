"""Router de métricas — implementação sob responsabilidade do Dev 2.

Stubs com contratos corretos para desbloquear o Dev 3 (MonitoringScreen).
"""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.deps import CurrentUser, DbDep

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


class MetricsResponse(BaseModel):
    total_processos: int
    total_decisoes: int
    aderencia_global: float | None
    economia_total: float | None
    casos_alto_risco: int
    aderencia_por_advogado: list[dict]
    drift_confianca: list[dict]


class RecommendationFeedItem(BaseModel):
    processo_id: str
    numero_processo: str
    decisao: str
    confidence: float
    valor_sugerido: float | None
    created_at: str


@router.get("/metrics", response_model=MetricsResponse)
def get_metrics(db: DbDep, current_user: CurrentUser) -> MetricsResponse:
    # TODO(DEV-2): implementar agregações via services/metrics/aggregator.py
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Métricas em desenvolvimento")


@router.get("/recommendations", response_model=list[RecommendationFeedItem])
def get_recommendations(db: DbDep, current_user: CurrentUser) -> list[RecommendationFeedItem]:
    # TODO(DEV-2): listar recomendações recentes para o feed do Monitoring
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Métricas em desenvolvimento")
