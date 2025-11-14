import logging
import sys

from app.core.config import settings


def setup_logging():
    """Configura o sistema de logging da aplicação."""

    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    uvicorn_access = logging.getLogger("uvicorn.access")
    uvicorn_access.disabled = True
    
    return logging.getLogger(__name__)