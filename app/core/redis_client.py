import os
from typing import Optional

from redis import Redis
from rq import Queue


class RedisClient:
    """Cliente singleton para gerenciar conexões Redis e filas RQ."""
    
    _instance: Optional['RedisClient'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self.host = os.getenv('REDIS_HOST', 'redis')
        self.port = int(os.getenv('REDIS_PORT', 6379))
        self.db = int(os.getenv('REDIS_DB', 0))
        
        self._connection: Optional[Redis] = None
        self._queue: Optional[Queue] = None
        self._initialized = True
    
    @property
    def connection(self) -> Redis:
        """Retorna a conexão Redis ativa."""
        if self._connection is None:
            self._connection = Redis(
                host=self.host,
                port=self.port,
                db=self.db,
                decode_responses=False
            )
        return self._connection
    
    @property
    def queue(self) -> Queue:
        """Retorna a fila RQ para processamento de jobs."""
        if self._queue is None:
            self._queue = Queue('default', connection=self.connection)
        return self._queue
    
    def ping(self) -> bool:
        """Verifica se a conexão Redis está ativa."""
        try:
            return self.connection.ping()
        except Exception:
            return False
    
    def close(self):
        """Fecha a conexão Redis."""
        if self._connection:
            self._connection.close()
            self._connection = None
            self._queue = None

redis_client = RedisClient()