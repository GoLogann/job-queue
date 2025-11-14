import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router as app_router
from app.core.config import settings

logger = logging.getLogger("job-queue.main")

def configure_logging() -> None:
    """Configura o sistema de logging da aplicação."""
    if not logging.getLogger().handlers:
        log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        logging.basicConfig(
            level=log_level,
            format=log_format
        )

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Documentação disponível em: http://localhost:8000/docs")
    try:
        yield
    finally:
        from app.core.redis_client import redis_client
        redis_client.close()
        logger.info("Aplicação encerrada")

def create_app() -> FastAPI:
    """Cria e configura a aplicação FastAPI."""
    configure_logging()
    
    app = FastAPI(
        title=settings.API_TITLE,
        description=settings.API_DESCRIPTION,
        version=settings.API_VERSION,
        contact={
            "name": "Logan Cardoso",
            "email": "logan.cc@outlook.com"
        },
        lifespan=lifespan
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    app.include_router(app_router)

    return app

app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
        log_level="info"
    )
