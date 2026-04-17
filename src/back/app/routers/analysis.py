"""Router de análise IA — implementação sob responsabilidade do Dev 2 (AI pipeline).

Stubs com contratos corretos para desbloquear o Dev 3 (frontend).
"""
import uuid

from fastapi import APIRouter, HTTPException, status

from app.deps import CurrentUser, DbDep
from app.schemas.analysis import AnaliseIAResponse, DecisaoAdvogadoRequest

router = APIRouter(prefix="/processes", tags=["analysis"])


@router.post("/{processo_id}/analyze", response_model=AnaliseIAResponse)
async def analyze_processo(
    processo_id: uuid.UUID,
    db: DbDep,
    current_user: CurrentUser,
) -> AnaliseIAResponse:
    # TODO(DEV-2): disparar pipeline IA (extractor → classifier → valuator)
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Pipeline IA em desenvolvimento")


@router.get("/{processo_id}/analysis", response_model=AnaliseIAResponse)
def get_analysis(
    processo_id: uuid.UUID,
    db: DbDep,
    current_user: CurrentUser,
) -> AnaliseIAResponse:
    # TODO(DEV-2): buscar analise_ia pelo processo_id
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Pipeline IA em desenvolvimento")


@router.post("/analysis/{analise_id}/decision", status_code=status.HTTP_204_NO_CONTENT)
def register_decision(
    analise_id: uuid.UUID,
    body: DecisaoAdvogadoRequest,
    db: DbDep,
    current_user: CurrentUser,
) -> None:
    # TODO(DEV-2): gravar decisao_advogado (ACEITAR | AJUSTAR | RECUSAR)
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Pipeline IA em desenvolvimento")
