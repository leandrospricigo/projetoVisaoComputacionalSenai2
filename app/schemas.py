"""
Esquemas Pydantic para validação e estruturação das respostas da API.
Garante que o retorno do endpoint /detect siga exatamente o formato exigido no edital.
"""

from typing import List
from pydantic import BaseModel, Field


class BoundingBox(BaseModel):
    """Coordenadas da caixa delimitadora do objeto detectado na imagem."""
    x_min: int = Field(..., description="Coordenada X inicial (canto superior esquerdo)")
    y_min: int = Field(..., description="Coordenada Y inicial (canto superior esquerdo)")
    x_max: int = Field(..., description="Coordenada X final (canto inferior direito)")
    y_max: int = Field(..., description="Coordenada Y final (canto inferior direito)")


class DetectionItem(BaseModel):
    """Representação de um único objeto detectado."""
    class_name: str = Field(..., description="Nome da classe do objeto identificado")
    confidence: float = Field(..., description="Nível de confiança da detecção (entre 0.0 e 1.0)")
    box: BoundingBox = Field(..., description="Caixa delimitadora da detecção")


class DetectionResponse(BaseModel):
    """Formato da resposta retornada pelo endpoint /detect."""
    status: str = Field(default="success", description="Status da requisição")
    total_detections: int = Field(..., description="Quantidade total de objetos detectados")
    detections: List[DetectionItem] = Field(..., description="Lista de objetos detectados na imagem")
