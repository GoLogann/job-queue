import logging
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, HTTPException, status

from app.core.redis_client import redis_client
from app.models.schemas import (RequisicaoOperacao,
                                RequisicaoOperacaoCustomizada,
                                RespostaCriacaoJob, RespostaStatusJob)
from app.workers.job_storage import JobStorage

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["Jobs"])


@router.post(
    "/operacao-longa",
    response_model=RespostaCriacaoJob,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Criar operação longa",
    description="Cria uma operação que será processada assincronamente (35+ segundos)"
)
async def criar_operacao(requisicao: RequisicaoOperacao):
    """
    Endpoint para criar operação longa que excede timeout do WAF.
    
    - **Retorna imediatamente** com job_id
    - **Processa em background** sem restrição de tempo
    - **Use polling** no endpoint de status para acompanhar progresso
    """
    try:
        job_id = str(uuid4())
        
        JobStorage.create_job(job_id, {"dados_entrada": requisicao.dados})
        
        redis_client.queue.enqueue(
            'app.workers.processors.processar_operacao',
            job_id,
            requisicao.dados,
            job_timeout='10m',
            result_ttl=86400
        )
        
        logger.info(f"Job {job_id} criado e enfileirado com sucesso")
        
        return RespostaCriacaoJob(
            job_id=job_id,
            status="pending",
            url_status=f"/api/jobs/{job_id}"
        )
        
    except Exception as e:
        logger.error(f"Erro ao criar job: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar job: {str(e)}"
        )


@router.post(
    "/operacao-customizada",
    response_model=RespostaCriacaoJob,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Criar operação customizada",
    description="Cria uma operação com tempo de processamento customizado"
)
async def criar_operacao_customizada(requisicao: RequisicaoOperacaoCustomizada):
    """
    Endpoint para criar operação com tempo de processamento customizado.
    
    - **Tempo configurável** entre 1 e 300 segundos
    - Útil para testes com diferentes durações
    """
    try:
        job_id = str(uuid4())
        
        JobStorage.create_job(job_id, {
            "dados_entrada": requisicao.dados,
            "tempo_processamento": requisicao.tempo_processamento
        })
        
        redis_client.queue.enqueue(
            'app.workers.processors.processar_operacao_customizada',
            job_id,
            requisicao.dados,
            requisicao.tempo_processamento,
            job_timeout='10m',
            result_ttl=86400
        )
        
        logger.info(f"Job customizado {job_id} criado ({requisicao.tempo_processamento}s)")
        
        return RespostaCriacaoJob(
            job_id=job_id,
            status="pending",
            url_status=f"/api/jobs/{job_id}",
            mensagem=f"Job criado. Processamento estimado: {requisicao.tempo_processamento}s"
        )
        
    except Exception as e:
        logger.error(f"Erro ao criar job customizado: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar job: {str(e)}"
        )


@router.get(
    "/jobs/{job_id}",
    response_model=RespostaStatusJob,
    summary="Obter status do job",
    description="Consulta o status e resultado de um job em processamento"
)
async def obter_status(job_id: str):
    """
    Endpoint para polling do status do job.
    
    **Status possíveis:**
    - `pending`: Aguardando processamento
    - `processing`: Em processamento
    - `completed`: Concluído com sucesso
    - `failed`: Falhou com erro
    
    **Recomendação:** Fazer polling a cada 2-5 segundos.
    """
    try:
        job_data = JobStorage.get_job(job_id)
        
        if not job_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job {job_id} não encontrado ou expirado"
            )
        
        return RespostaStatusJob(**job_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter status do job {job_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter status: {str(e)}"
        )


@router.get(
    "/health",
    summary="Health check",
    description="Verifica saúde da API e conexão com Redis"
)
async def health_check():
    """Endpoint de health check."""
    redis_status = "healthy" if redis_client.ping() else "unhealthy"
    
    return {
        "status": "healthy" if redis_status == "healthy" else "degraded",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "services": {
            "redis": redis_status
        }
    }