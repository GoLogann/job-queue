from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class RequisicaoOperacao(BaseModel):
    """Schema para requisição de operação longa."""
    dados: Dict[str, Any] = Field(
        ...,
        description="Dados a serem processados",
        example={"parametro1": "valor1", "parametro2": 123}
    )


class RequisicaoOperacaoCustomizada(BaseModel):
    """Schema para requisição de operação com tempo customizado."""
    dados: Dict[str, Any] = Field(
        ...,
        description="Dados a serem processados"
    )
    tempo_processamento: int = Field(
        default=35,
        ge=1,
        le=300,
        description="Tempo de processamento em segundos (1-300)"
    )


class RespostaCriacaoJob(BaseModel):
    """Schema para resposta de criação de job."""
    job_id: str
    status: str
    url_status: str
    mensagem: str = "Job criado com sucesso. Use a URL de status para acompanhar o progresso."


class RespostaStatusJob(BaseModel):
    """Schema para resposta de status do job."""
    job_id: str
    status: str
    criado_em: Optional[str] = None
    iniciado_em: Optional[str] = None
    completado_em: Optional[str] = None
    falhou_em: Optional[str] = None
    resultado: Optional[Dict[str, Any]] = None
    erro: Optional[str] = None