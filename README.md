# SupermarketVision API 🛒🔍

> **Sistema Inteligente de Detecção de Itens de Supermercado em Tempo Real**  
> Projeto Avaliativo da disciplina **Machine Learning e Visão Computacional [T1]** (Módulo 2 - Semana 14)  
> **Autor:** Leandro Spricigo  
> **Instituição:** SENAI  
> **Orientador:** Prof. Welington Souza  

---

## 📌 1. Visão Geral e Desafio de Negócio

No varejo supermercadista moderno, o atendimento em caixas de autoatendimento (*self-checkout*) enfrenta dois desafios centrais:
1. **Lentidão na pesagem/registro:** Clientes precisam navegar manualmente por menus para encontrar itens avulsos (hortifrúti e padaria).
2. **Prevenção de perdas e erros:** Erros de seleção ou trocas acidentais de produtos podem gerar prejuízos operacionais.

O **SupermarketVision API** é um microserviço backend RESTful desenvolvido em **FastAPI** que utiliza a arquitetura de visão computacional **YOLOv8** para identificar e localizar automaticamente múltiplos itens em imagens capturadas por câmeras no ponto de venda (POS). O sistema abstrai o processamento matricial do modelo de inteligência artificial e retorna um payload **JSON universal, leve e estruturado**, pronto para ser integrado a qualquer frente de caixa, aplicativo móvel ou sistema ERP.

---

## 🎯 2. As Classes do Dataset

O sistema foi preparado e validado para detectar **12 classes representativas** de itens de supermercado (hortifrúti, mercearia, bebidas e padaria), superando o requisito mínimo de 10 classes do edital:

| # | Classe (Inglês) | Categoria | Descrição / Exemplo de Aplicação |
|---|---|---|---|
| **01** | `apple` | Hortifrúti | Maçãs no ponto de pesagem |
| **02** | `banana` | Hortifrúti | Bananas soltas ou em pencas |
| **03** | `orange` | Hortifrúti | Laranjas e frutas cítricas |
| **04** | `carrot` | Hortifrúti | Cenouras e legumes |
| **05** | `broccoli` | Hortifrúti | Brócolis e vegetais verdes |
| **06** | `bottle` | Bebidas | Garrafas de água, refrigerantes e sucos |
| **07** | `cup` | Bebidas | Copos térmicos e canecas |
| **08** | `sandwich` | Lanches | Sanduíches prontos e wraps |
| **09** | `pizza` | Congelados | Pizzas e massas prontas |
| **10** | `donut` | Padaria | Rosquinhas e doces de confeitaria |
| **11** | `cake` | Confeitaria | Bolos e tortas inteiras/fatiadas |
| **12** | `bowl` | Mercearia | Potes, tigelas de açaí e saladas |

---

## 🧠 3. Arquitetura de IA: Justificativa do YOLOv8 Nano

A família **YOLO (You Only Look Once)** é o estado da arte para detecção de objetos em tempo real. Para este projeto, foi selecionada a versão **YOLOv8 Nano (`yolov8n`)** da Ultralytics pelas seguintes razões técnicas:

1. **Baixa latência em CPU:** Apresenta tempo de inferência médio de apenas **~75ms por imagem** em processadores convencionais (sem necessidade de GPU dedicada), viabilizando o uso em computadores comuns de PDV.
2. **Eficiência de parâmetros:** O modelo possui apenas **3,15 milhões de parâmetros** e tamanho de arquivo reduzido (~6,2 MB), permitindo inicialização quase instantânea e baixo consumo de memória RAM.
3. **Equilíbrio entre precisão e velocidade:** Oferece excelente mAP (mean Average Precision) para detecções multiclasse, identificando com precisão as coordenadas da *bounding box* mesmo em ângulos variados.

---

## 🛠️ 4. Instalação e Execução Local

### Pré-requisitos
* Python 3.10 ou superior (testado na versão 3.12)
* Git instalado

### Passo a Passo

1. **Clonar o repositório:**
   ```bash
   git clone <URL_DO_SEU_REPOSITORIO_GITHUB>
   cd mini_projeto_fase2_2
   ```

2. **Criar e ativar o ambiente virtual:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # No Linux/macOS
   # No Windows: .venv\Scripts\activate
   ```

3. **Instalar as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Executar a API com Uvicorn:**
   ```bash
   uvicorn app.main:app --reload
   ```

5. **Acessar a aplicação no navegador:**
   * **Dashboard Web Interativo:** [http://127.0.0.1:8000/](http://127.0.0.1:8000/) (Permite upload, amostras rápidas e desenho das bounding boxes em Canvas).
   * **Documentação Swagger UI:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
   * **Documentação ReDoc:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 📡 5. Exemplo de Uso da API

### Endpoint: `POST /detect`
Recebe um arquivo de imagem binário (`multipart/form-data`) através do campo `file`.

#### Exemplo de requisição via cURL:
```bash
curl -X POST "http://127.0.0.1:8000/detect" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@data/samples/maca.jpg"
```

#### Exemplo de Payload de Retorno (JSON):
```json
{
  "status": "success",
  "total_detections": 2,
  "detections": [
    {
      "class_name": "apple",
      "confidence": 0.89,
      "box": {
        "x_min": 145,
        "y_min": 210,
        "x_max": 312,
        "y_max": 395
      }
    },
    {
      "class_name": "apple",
      "confidence": 0.82,
      "box": {
        "x_min": 330,
        "y_min": 215,
        "x_max": 490,
        "y_max": 388
      }
    }
  ]
}
```

---

## 🧪 6. Testes Automatizados

O projeto inclui testes automatizados para validar a integridade dos endpoints:

```bash
# Executar a suíte de testes:
.venv/bin/python -m pytest tests/test_api.py -v
```

Para testar o envio em lote das imagens de amostra com a API ativa:
```bash
.venv/bin/python scripts/test_client.py
```

---

## 📋 7. Metodologia Ágil e Kanban (Trello)

O planejamento e gerenciamento de todas as etapas foi estruturado no **Trello** utilizando o fluxo Kanban clássico:
* **Colunas:** `Backlog` ➔ `To Do` ➔ `Doing` ➔ `Blocked` ➔ `Review` ➔ `Done`.
* **Link do Quadro Kanban:** [SupermarketVision no Trello](https://trello.com/invite/b/6ad156713c09729e4de9ebb0/ATTI7e61be643e8cc384bed1c8005e38b42574627C27/supermarketvision-deteccao-de-objetos)
* **Acesso concedido para:** `welington.souza@edu.sc.senai.br`

---

## 🌿 8. Estrutura de Branches (GitFlow)

O desenvolvimento seguiu rigorosamente o padrão **GitFlow**, com commits concisos e separação por funcionalidades:

* `main`: Código final homologado e estável.
* `develop`: Branch integradora de desenvolvimento.
  * `feature/setup-project`: Configuração inicial de ambiente, `.gitignore` e dependências.
  * `feature/dataset-prep`: Seleção e validação das classes e imagens de amostra.
  * `feature/api-fastapi`: Implementação do microserviço FastAPI e esquemas Pydantic.
  * `feature/frontend-ui`: Desenvolvimento da interface web com canvas para rotulagem visual.
  * `feature/docs-readme`: Documentação completa do projeto e guias de execução.
