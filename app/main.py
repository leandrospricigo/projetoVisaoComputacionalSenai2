"""
Aplicação Principal FastAPI - SupermarketVision API
Microserviço backend para detecção de objetos em imagens de supermercado via YOLO.
"""

from contextlib import asynccontextmanager
from typing import Dict, Any
from fastapi import FastAPI, UploadFile, File, HTTPException, status
from fastapi.responses import JSONResponse

from app.schemas import DetectionResponse
from app.detector import ObjectDetector

# Variável global para armazenar a instância do modelo YOLO carregado na memória
detector: ObjectDetector = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gerenciador de ciclo de vida da aplicação.
    Carrega o modelo uma única vez durante a inicialização para evitar lentidão nas requisições.
    """
    global detector
    print("🚀 Inicializando serviço e carregando modelo YOLOv8...")
    detector = ObjectDetector(model_path="models/yolov8n.pt", confidence_threshold=0.25)
    print("✅ Modelo pronto para receber inferências!")
    yield
    print("🛑 Encerrando aplicação...")


# Inicialização da aplicação FastAPI com documentação Swagger interativa
app = FastAPI(
    title="SupermarketVision API",
    description=(
        "Microserviço backend para detecção de objetos em itens de supermercado "
        "utilizando a arquitetura YOLOv8. Desenvolvido para a Situação de Aprendizagem "
        "do curso de Machine Learning e Visão Computacional [T1] - SENAI."
    ),
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/", summary="Health Check e Boas-Vindas")
async def root() -> Dict[str, Any]:
    """Rota raiz para verificar se a API está online e pronta para uso."""
    return {
        "status": "online",
        "message": "SupermarketVision API está operacional!",
        "docs_url": "/docs",
        "endpoint_inferencia": "/detect (método POST)",
        "modelo": "YOLOv8 Nano (Ultralytics)",
        "autor": "Leandro Spricigo"
    }


@app.post(
    "/detect",
    response_model=DetectionResponse,
    status_code=status.HTTP_200_OK,
    summary="Detectar objetos em uma imagem",
    description="Recebe um arquivo de imagem binário (UploadFile), executa a inferência YOLO e retorna as detecções em JSON."
)
async def detect_objects(file: UploadFile = File(...)):
    """
    Endpoint principal de inferência.
    Recebe uma imagem via POST multipart/form-data e retorna a lista de caixas delimitadoras e classes.
    """
    # 1. Validação do tipo de arquivo (garante que seja uma imagem)
    tipos_permitidos = ["image/jpeg", "image/png", "image/jpg", "image/webp"]
    if file.content_type not in tipos_permitidos:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Formato de arquivo inválido: '{file.content_type}'. "
                f"Envie uma imagem nos formatos: {', '.join(tipos_permitidos)}."
            )
        )

    try:
        # 2. Leitura dos bytes do arquivo enviado
        conteudo_bytes = await file.read()

        if len(conteudo_bytes) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="O arquivo enviado está vazio."
            )

        # 3. Execução da inferência no modelo YOLO
        deteccoes = detector.predict_from_bytes(conteudo_bytes)

        # 4. Retorno estruturado no formato exigido no edital
        return {
            "status": "success",
            "total_detections": len(deteccoes),
            "detections": deteccoes
        }

    except HTTPException:
        # Repassa exceções HTTP intencionais
        raise

    except Exception as erro:
        # Tratamento de erros inesperados durante o processamento da imagem
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno ao processar a imagem: {str(erro)}"
        )
