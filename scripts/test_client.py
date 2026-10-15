"""
Script cliente de teste para simular o envio de imagens para a SupermarketVision API.
Pode ser executado com a API rodando para validar todas as 12 classes de amostra.
"""

import sys
import glob
from pathlib import Path
import requests

API_URL = "http://127.0.0.1:8000/detect"


def testar_todas_as_amostras(pasta_samples: str = "data/samples"):
    """Envia cada imagem da pasta samples para o endpoint /detect e exibe os resultados."""
    caminho = Path(pasta_samples)
    imagens = sorted(list(caminho.glob("*.jpg")) + list(caminho.glob("*.png")))

    if not imagens:
        print(f"❌ Nenhuma imagem encontrada em {caminho}.")
        return

    print("=" * 65)
    print(f"🛒 SUPERMARKETVISION API - TESTE DE DETECÇÃO EM LOTE")
    print(f"Testando {len(imagens)} imagens no endpoint: {API_URL}")
    print("=" * 65)

    sucessos = 0

    for img_path in imagens:
        nome_arquivo = img_path.name

        try:
            with open(img_path, "rb") as f:
                arquivos = {"file": (nome_arquivo, f, "image/jpeg")}
                resposta = requests.post(API_URL, files=arquivos, timeout=10)

            if resposta.status_code == 200:
                dados = resposta.json()
                total = dados.get("total_detections", 0)
                detalhes = [
                    f"{d['class_name']} ({int(d['confidence'] * 100)}%)"
                    for d in dados.get("detections", [])
                ]
                resumo_detalhes = ", ".join(detalhes[:3])
                if len(detalhes) > 3:
                    resumo_detalhes += f" (+{len(detalhes) - 3} outros)"

                print(f"✅ {nome_arquivo:15s} | {total:02d} detecções -> [{resumo_detalhes}]")
                sucessos += 1
            else:
                print(f"❌ {nome_arquivo:15s} | Erro HTTP {resposta.status_code}: {resposta.text}")

        except requests.exceptions.ConnectionError:
            print(f"❌ Não foi possível conectar a {API_URL}.")
            print("Certifique-se de que a API está rodando com:")
            print("  uvicorn app.main:app --reload")
            return
        except Exception as e:
            print(f"❌ Erro ao enviar {nome_arquivo}: {e}")

    print("=" * 65)
    print(f"Resultado final: {sucessos}/{len(imagens)} imagens processadas com sucesso.")
    print("=" * 65)


if __name__ == "__main__":
    pasta = sys.argv[1] if len(sys.argv) > 1 else "data/samples"
    testar_todas_as_amostras(pasta)
