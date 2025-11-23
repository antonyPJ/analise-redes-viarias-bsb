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

## Licença

MIT License - Projeto acadêmico desenvolvido para fins educacionais.

## Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou pull requests.
