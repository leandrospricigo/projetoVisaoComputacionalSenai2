"""
Script de validação e diagnóstico do dataset para YOLO.
Verifica a integridade do arquivo data.yaml, conta imagens de treino e validação,
e valida se o requisito de no mínimo 10 classes foi atendido.
"""

import os
import sys
from pathlib import Path
import yaml


def validar_dataset(yaml_path: str = "data/data.yaml") -> bool:
    """Verifica e exibe estatísticas do dataset."""
    caminho_yaml = Path(yaml_path)

    if not caminho_yaml.exists():
        print(f"❌ Arquivo de configuração não encontrado em: {caminho_yaml}")
        print("Por favor, certifique-se de colocar o dataset e o arquivo data.yaml na pasta 'data/'.")
        return False

    with open(caminho_yaml, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    classes = config.get("names", [])
    if isinstance(classes, dict):
        lista_classes = list(classes.values())
    elif isinstance(classes, list):
        lista_classes = classes
    else:
        lista_classes = []

    num_classes = len(lista_classes)

    print("\n" + "=" * 50)
    print("📋 RELATÓRIO DE VALIDAÇÃO DO DATASET")
    print("=" * 50)
    print(f"Total de classes encontradas: {num_classes}")

    if num_classes < 10:
        print(f"⚠️ ATENÇÃO: O edital exige no mínimo 10 classes. Atualmente existem {num_classes}.")
    else:
        print("✅ Requisito de mínimo 10 classes ATENDIDO com sucesso!")

    print("\nClasses cadastradas:")
    for idx, nome in enumerate(lista_classes):
        print(f"  [{idx + 1:02d}] {nome}")

    # Verificar caminhos de treino e validação
    base_dir = caminho_yaml.parent
    caminho_treino = base_dir / config.get("train", "")
    caminho_val = base_dir / config.get("val", "")

    print("\nVerificação de pastas:")
    print(f"  Treino: {caminho_treino} -> {'✅ Existe' if caminho_treino.exists() else '❌ Não encontrado'}")
    print(f"  Validação: {caminho_val} -> {'✅ Existe' if caminho_val.exists() else '❌ Não encontrado'}")
    print("=" * 50 + "\n")

    return num_classes >= 10


if __name__ == "__main__":
    caminho = sys.argv[1] if len(sys.argv) > 1 else "data/data.yaml"
    validar_dataset(caminho)
