"""
Testes automatizados para a API FastAPI.
Valida se as rotas / e /detect estão respondendo conforme o contrato estabelecido.
"""

from fastapi.testclient import TestClient
from app.main import app

# Inicializa o cliente de testes da FastAPI
client = TestClient(app)


def test_root_endpoint():
    """Valida se a rota raiz responde com status 200 e mensagem de online."""
    with client:
        response = client.get("/")
        assert response.status_code == 200
        dados = response.json()
        assert dados["status"] == "online"
        assert "SupermarketVision" in dados["message"]


def test_detect_endpoint_valid_image():
    """Valida se a rota /detect processa com sucesso uma imagem de maçã."""
    with client:
        with open("data/samples/maca.jpg", "rb") as img:
            response = client.post(
                "/detect",
                files={"file": ("maca.jpg", img, "image/jpeg")}
            )

        assert response.status_code == 200
        dados = response.json()
        assert dados["status"] == "success"
        assert "detections" in dados
        assert isinstance(dados["detections"], list)
        assert len(dados["detections"]) > 0

        # Valida a estrutura da primeira detecção
        primeira = dados["detections"][0]
        assert "class_name" in primeira
        assert "confidence" in primeira
        assert "box" in primeira
        assert "x_min" in primeira["box"]
        assert "y_min" in primeira["box"]
        assert "x_max" in primeira["box"]
        assert "y_max" in primeira["box"]


def test_detect_endpoint_invalid_file():
    """Valida se a rota /detect recusa adequadamente arquivos de texto."""
    with client:
        response = client.post(
            "/detect",
            files={"file": ("documento.txt", b"conteudo de texto", "text/plain")}
        )
        assert response.status_code == 400
        assert "Formato de arquivo inválido" in response.json()["detail"]
