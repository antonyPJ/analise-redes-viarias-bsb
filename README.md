# Análise de Redes Viárias - Brasília

Projeto acadêmico de análise da malha viária de Brasília usando Teoria dos Grafos.

## Descrição

Análise estrutural da rede viária de Brasília utilizando algoritmos de grafos para identificar pontos críticos, avaliar o impacto de bloqueios e propor melhorias no planejamento urbano.

**Dataset:**
- 179 nós (interseções)
- 230 arestas (segmentos de rua)
- Coordenadas geográficas (X, Y)
- Distâncias em metros

## Objetivos

1. **Análise de Conectividade**
   - Identificar pontes (arestas críticas)
   - Identificar pontos de articulação (vértices críticos)
   - Verificar conectividade do grafo

2. **Medidas de Centralidade**
   - Centralidade de Grau
   - Centralidade de Intermediação (Betweenness)
   - Centralidade de Proximidade (Closeness)

3. **Caminhos Mínimos**
   - Algoritmo de Dijkstra
   - Rotas ótimas entre pontos estratégicos

4. **Simulação de Impacto**
   - Cenários de bloqueio de vias críticas
   - Análise comparativa antes/depois

## Instalação

### Pré-requisitos
- Python 3.8+
- pip

### Setup

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/trabalho_final_grafos.git
cd trabalho_final_grafos

# Crie o ambiente virtual
python -m venv venv

# Ative o ambiente virtual
# No Windows:
venv\Scripts\activate
# No Linux/Mac:
source venv/bin/activate

# Instale as dependências
pip install -r requirements.txt
```

## Uso

### Executar todas as análises
```bash
python main.py
```

### Análises individuais
```bash
# Análise exploratória
python src/analise_exploratoria.py

# Análise estrutural (pontes e articulações)
python src/analise_estrutural.py

# Análise de centralidade
python src/analise_centralidades.py

# Simulação de impacto
python src/analise_impacto.py
```

### Simulação de Fluxo Viário
```bash
cd simular
python simulacao_fluxo.py
```

Este módulo realiza uma **simulação simplificada de tráfego** sobre a rede viária:
- Lê o fluxo total diário
- Distribui o fluxo ao longo de 24 horas
- Simula agentes percorrendo caminhos mínimos
- Calcula o índice de saturação de cada via
- Gera arquivo `resultado_fluxo.csv` com carga estimada por segmento

**Parâmetros configuráveis:**
- `VEIC_POR_AGENT`: Veículos representados por agente
- `CAPACIDADE`: Capacidade estimada de cada via (veículos/hora)
- `MAX_AGENTES`: Número máximo de agentes por hora
- `DIA`: Data do fluxo a ser analisado

## Estrutura do Projeto

```
trabalho_final_grafos/
├── base_conhecimento_projeto/     # Dataset de entrada
│   ├── brasilia.net               # Lista de arestas (grafo)
│   ├── brasilia_edge_info.txt     # Metadados (coordenadas, distâncias)
│   └── README.txt                 # Descrição do dataset
├── src/                           # Código fonte das análises
│   ├── __init__.py
│   ├── analise_exploratoria.py    # Análise inicial da rede
│   ├── analise_estrutural.py      # Pontes e pontos de articulação
│   ├── analise_centralidades.py   # Medidas de centralidade
│   └── analise_impacto.py         # Simulação de bloqueios
├── simular/                       # Simulação de fluxo viário
│   ├── simulacao_fluxo.py         # Script de simulação de tráfego
│   ├── brasilia_edge_info.txt     # Informações da malha viária
│   ├── fluxo_total_por_dia.csv    # Fluxo total por data
│   └── resultado_fluxo.csv        # Saída da simulação
├── resultados/                    # Outputs gerados (criado na execução)
│   ├── graficos/                  # Visualizações em PNG
│   └── *.txt                      # Relatórios textuais
├── main.py                        # Script principal
├── requirements.txt               # Dependências Python
├── LICENSE                        # MIT License
└── README.md                      # Este arquivo
```

## Algoritmos Implementados

- **NetworkX**: Manipulação e análise de grafos
- **Tarjan**: Identificação de pontes e pontos de articulação
- **Dijkstra**: Caminhos mínimos ponderados
- **Centralidade**: Grau, Betweenness, Closeness

## Resultados

Os resultados das análises são salvos automaticamente em:
- `resultados/graficos/*.png` - Visualizações da rede
- `resultados/*.txt` - Relatórios técnicos
- `resultados/*.csv` - Métricas de centralidade

**Relatório Acadêmico:**  
[📥 Download do Relatório (PDF)]([URL_RELATORIO.pdf](https://www.overleaf.com/download/project/6924ea752461d203e7b2dc95/build/19ac260434e-a785ef3ef92a61d3/output/output.pdf?compileGroup=standard&clsiserverid=clsi-pre-emp-c3d-d-f-5tlj&enable_pdf_caching=true&popupDownload=true))

**Apresentação (Slides):**  
[📊 Download dos Slides (PDF)](URL_SLIDES.pdf)

**Vídeo de Apresentação:**  
[▶️ Assistir no YouTube](https://youtube.com/watch?v=SEU_VIDEO_ID)

## Licença

MIT License - Projeto acadêmico desenvolvido para fins educacionais.

## Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou pull requests.
