import os
from typing import Optional


class Settings:
    """Configurações centralizadas da aplicação."""
    
    API_TITLE: str = "API de Operações Longas"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = """
    API para processamento assíncrono de operações que excedem timeout do WAF.
    
    ## Fluxo de Uso
    
    1. **Criar Job**: POST /api/operacao-longa
       - Retorna `job_id` imediatamente (< 1s)
       - Job é processado em background
    
    2. **Consultar Status**: GET /api/jobs/{job_id}
       - Fazer polling a cada 2-5 segundos
       - Status possíveis: pending, processing, completed, failed
    
    3. **Obter Resultado**: Quando status = completed
       - Campo `resultado` contém dados processados
    
    ## Características
    
    - ✅ Resposta imediata (< 1s)
    - ✅ Processamento assíncrono (35+ segundos)
    - ✅ Retry automático (até 3 tentativas)
    - ✅ TTL de 24h para jobs
    - ✅ Idempotência com job_id único
    """
    
    REDIS_HOST: str = os.getenv('REDIS_HOST', 'redis')
    REDIS_PORT: int = int(os.getenv('REDIS_PORT', 6379))
    REDIS_DB: int = int(os.getenv('REDIS_DB', 0))
    
    JOB_TTL_SECONDS: int = int(os.getenv('JOB_TTL_SECONDS', 86400))  # 24h
    JOB_TIMEOUT: str = os.getenv('JOB_TIMEOUT', '10m')
    JOB_MAX_RETRIES: int = int(os.getenv('JOB_MAX_RETRIES', 3))
    
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    
    HOST: str = os.getenv('HOST', '0.0.0.0')
    PORT: int = int(os.getenv('PORT', 8000))
    RELOAD: bool = os.getenv('RELOAD', 'True').lower() == 'true'

settings = Settings()