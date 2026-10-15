"""
Script para download automático de dataset do Roboflow Universe formatado para YOLOv8.
Você só precisa de uma chave de API gratuita do Roboflow (gerada em roboflow.com).
"""

import os
import sys
from roboflow import Roboflow


def baixar_dataset(api_key: str, workspace: str, project_name: str, version: int = 1):
    """Baixa o dataset diretamente para a pasta data/ em formato YOLOv8."""
    print(f"Iniciando download do projeto '{project_name}' (versão {version})...")
    
    rf = Roboflow(api_key=api_key)
    project = rf.workspace(workspace).project(project_name)
    dataset = project.version(version).download("yolov8", location="data")
    
    print("\n✅ Download concluído com sucesso!")
    print(f"Arquivos salvos em: {dataset.location}")
    print("Agora você pode rodar 'python scripts/validate_dataset.py' para checar os dados.")


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("\nUso do script:")
        print("python scripts/download_dataset.py <SUA_API_KEY> <WORKSPACE> <PROJECT_NAME> [VERSAO]")
        print("\nExemplo:")
        print("python scripts/download_dataset.py abc123XYZ cse299 fruit-and-vegetable 1\n")
        sys.exit(1)

    key = sys.argv[1]
    ws = sys.argv[2]
    proj = sys.argv[3]
    ver = int(sys.argv[4]) if len(sys.argv) > 4 else 1

    baixar_dataset(key, ws, proj, ver)
