import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict

from app.core.config import settings
from app.core.redis_client import redis_client

logger = logging.getLogger(__name__)


class JobStorage:
    """Gerenciador de armazenamento de jobs no Redis."""
    
    @staticmethod
    def _get_job_key(job_id: str) -> str:
        """Gera chave Redis para o job."""
        return f"job:{job_id}"
    
    @staticmethod
    def get_job(job_id: str) -> Dict[str, Any]:
        """Recupera informações do job do Redis."""
        key = JobStorage._get_job_key(job_id)
        data = redis_client.connection.get(key)
        if data:
            return json.loads(data)
        return {}
    
    @staticmethod
    def update_job(job_id: str, data: Dict[str, Any]):
        """Atualiza informações do job no Redis."""
        key = JobStorage._get_job_key(job_id)
        current_data = JobStorage.get_job(job_id)
        current_data.update(data)
        
        for k, v in current_data.items():
            if isinstance(v, datetime):
                current_data[k] = v.isoformat()
        
        redis_client.connection.setex(
            key,
            settings.JOB_TTL_SECONDS,
            json.dumps(current_data)
        )
    
    @staticmethod
    def create_job(job_id: str, initial_data: Dict[str, Any]):
        """Cria um novo job no Redis."""
        key = JobStorage._get_job_key(job_id)
        data = {
            "job_id": job_id,
            "status": "pending",
            "criado_em": datetime.now(timezone.utc).isoformat(),
            **initial_data
        }
        redis_client.connection.setex(
            key,
            settings.JOB_TTL_SECONDS,
            json.dumps(data)
        )