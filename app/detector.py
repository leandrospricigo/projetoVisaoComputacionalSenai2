"""
Módulo responsável pelo carregamento do modelo YOLO e execução das inferências.
Mantém o código organizado e separado da lógica das rotas HTTP da API.
"""

import io
from pathlib import Path
from typing import List, Dict, Any
from PIL import Image
from ultralytics import YOLO


class ObjectDetector:
    """Classe simples para carregar o modelo YOLO e detectar objetos em imagens."""

    def __init__(self, model_path: str = "models/yolov8n.pt", confidence_threshold: float = 0.25):
        """
        Inicializa o detector carregando o modelo YOLO em memória.
        """
        self.model_path = Path(model_path)
        self.confidence_threshold = confidence_threshold

        # Se o arquivo não existir localmente na pasta models, o Ultralytics baixa automaticamente
        if not self.model_path.exists():
            print(f"⚠️ Modelo não encontrado em {self.model_path}. Baixando pesos pré-treinados...")
            self.model = YOLO("yolov8n.pt")
        else:
            print(f"✅ Carregando modelo local a partir de: {self.model_path}")
            self.model = YOLO(str(self.model_path))

    def predict_from_bytes(self, image_bytes: bytes) -> List[Dict[str, Any]]:
        """
        Recebe os bytes de uma imagem, executa a predição e retorna a lista de detecções estruturadas.
        """
        # Converte os bytes recebidos via upload em uma imagem PIL legível
        image = Image.open(io.BytesIO(image_bytes))

        # Executa a inferência com o YOLO
        results = self.model.predict(
            source=image,
            conf=self.confidence_threshold,
            verbose=False
        )

        detections = []
        primeiro_resultado = results[0]

        # Itera sobre cada caixa delimitadora detectada na imagem
        for box in primeiro_resultado.boxes:
            # Obtém o ID da classe e seu nome textual
            class_id = int(box.cls[0].item())
            class_name = self.model.names[class_id]

            # Nível de confiança da detecção arredondado para duas casas decimais
            confidence = round(float(box.conf[0].item()), 2)

            # Coordenadas da bounding box (x_min, y_min, x_max, y_max)
            coordenadas = box.xyxy[0].tolist()
            x_min = int(round(coordenadas[0]))
            y_min = int(round(coordenadas[1]))
            x_max = int(round(coordenadas[2]))
            y_max = int(round(coordenadas[3]))

            # Monta o dicionário no formato exato solicitado no PDF
            detections.append({
                "class_name": class_name,
                "confidence": confidence,
                "box": {
                    "x_min": x_min,
                    "y_min": y_min,
                    "x_max": x_max,
                    "y_max": y_max
                }
            })

        return detections
