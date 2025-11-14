import logging
import time
from datetime import datetime, timezone

from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import settings
from app.workers.job_storage import JobStorage

logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL))
logger = logging.getLogger(__name__)


@retry(
    stop=stop_after_attempt(settings.JOB_MAX_RETRIES),
    wait=wait_exponential(min=4, max=10),
    reraise=True
)
def processar_operacao(job_id: str, payload: dict):
    """
    Processa operação longa de forma assíncrona.
    
    Args:
        job_id: ID único do job
        payload: Dados para processamento
    """
    inicio_processamento = datetime.now(timezone.utc)
    logger.info(f"Iniciando processamento do job {job_id}")
    
    try:
        JobStorage.update_job(job_id, {
            "status": "processing",
            "iniciado_em": inicio_processamento.isoformat()
        })
        
        logger.info(f"Job {job_id}: Executando operação longa...")
        time.sleep(35)
        
        resultado = {
            "dados_processados": payload,
            "status": "sucesso",
            "mensagem": "Operação concluída com sucesso",
            "tempo_processamento": "35s"
        }
        
        JobStorage.update_job(job_id, {
            "status": "completed",
            "resultado": resultado,
            "completado_em": datetime.now(timezone.utc).isoformat()
        })
        
        logger.info(f"Job {job_id} concluído com sucesso")
        
    except Exception as e:
        logger.error(f"Erro ao processar job {job_id}: {str(e)}")
        
        JobStorage.update_job(job_id, {
            "status": "failed",
            "erro": str(e),
            "falhou_em": datetime.now(timezone.utc).isoformat()
        })
        raise


def processar_operacao_customizada(job_id: str, payload: dict, tempo_processamento: int = 35):
    """
    Versão customizável do processador de operações.
    
    Args:
        job_id: ID único do job
        payload: Dados para processamento
        tempo_processamento: Tempo de processamento em segundos
    """
    inicio_processamento = datetime.now(timezone.utc)
    logger.info(f"Iniciando processamento customizado do job {job_id} ({tempo_processamento}s)")
    
    try:
        JobStorage.update_job(job_id, {
            "status": "processing",
            "iniciado_em": inicio_processamento.isoformat()
        })
        
        time.sleep(tempo_processamento)
        
        resultado = {
            "dados_processados": payload,
            "status": "sucesso",
            "mensagem": f"Operação customizada concluída em {tempo_processamento}s",
            "tempo_processamento": f"{tempo_processamento}s"
        }
        
        JobStorage.update_job(job_id, {
            "status": "completed",
            "resultado": resultado,
            "completado_em": datetime.now(timezone.utc).isoformat()
        })
        
        logger.info(f"Job {job_id} concluído com sucesso")
        
    except Exception as e:
        logger.error(f"Erro ao processar job {job_id}: {str(e)}")
        
        JobStorage.update_job(job_id, {
            "status": "failed",
            "erro": str(e),
            "falhou_em": datetime.now(timezone.utc).isoformat()
        })
        raise