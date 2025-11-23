import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
import numpy as np # Importado para cálculos de normalização de cores

# --- 1. Carregamento e Construção do Grafo a partir de 'brasilia_edge_info.txt' ---
edge_info_file = "brasilia_edge_info.txt"

G = nx.Graph()
pos = {}

print(f"Lendo o arquivo: {edge_info_file}")
try:
    with open(edge_info_file, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()

            # Conversão segura dos tipos de dados
            try:
                edge_num = int(parts[0])
                n1 = int(parts[1])
                x1 = float(parts[2])
                y1 = float(parts[3])
                n2 = int(parts[4])
                x2 = float(parts[5])
                y2 = float(parts[6])
                length = float(parts[7])
            except (ValueError, IndexError):
                print(f"Linha ignorada por formato inválido: {line}")
                continue
            
            # Adiciona coordenadas e aresta ao grafo
            pos[n1] = (x1, y1)
            pos[n2] = (x2, y2)
            G.add_edge(n1, n2, weight=length)
    print(f"Grafo construído com {G.number_of_nodes()} nós e {G.number_of_edges()} arestas.")

except FileNotFoundError:
    print(f"Erro: Arquivo '{edge_info_file}' não encontrado.")
    exit() 


# --- 2. Cálculo das Métricas de Centralidade ---

# 2.1. Métricas de Nó (Cruzamentos)
degree = dict(G.degree())
print("Calculando Betweenness Centrality (ponderada)...")
betweenness_weighted = nx.betweenness_centrality(G, weight='length')
print("Calculando Closeness Centrality (ponderada)...")
closeness_weighted = nx.closeness_centrality(G, distance='length')

# 2.2. Métricas de Aresta (Vias/Ruas)
print("Calculando Edge Betweenness Centrality (ponderada)...")
edge_betweenness_weighted = nx.edge_betweenness_centrality(G, weight='length')

# Prepara a lista de valores de Edge Betweenness para plotagem
# (Garante que os valores estejam na mesma ordem das arestas do grafo)
edge_colors_data = [edge_betweenness_weighted.get((u, v), 0.0) 
                    for u, v, data in G.edges(data=True)]

# --- 3. Plotagem do Grafo com Coordenadas Reais ---

# 3.1. PLOTAGEM 1: NÓS COLORIDOS POR GRAU (Seu gráfico original)
# =================================================================
plt.figure(1, figsize=(12, 12)) 
nodes_in_pos = [n for n in G.nodes() if n in pos]
node_colors_data = [degree.get(n, 0) for n in nodes_in_pos] 
cmap_nodes = plt.cm.viridis

# Desenha os nós
nx.draw_networkx_nodes(
    G, pos, node_color=node_colors_data, cmap=cmap_nodes,                   
    node_size=20, linewidths=0.05, edgecolors='black', alpha=0.8
)
# Desenha as arestas
nx.draw_networkx_edges(G, pos, width=0.8, edge_color="gray", alpha=0.6)

# Adiciona a barra de cores para o Grau
sm_nodes = plt.cm.ScalarMappable(cmap=cmap_nodes, norm=plt.Normalize(vmin=min(node_colors_data), vmax=max(node_colors_data)))
sm_nodes.set_array(np.array(node_colors_data)) 
cbar_nodes = plt.colorbar(sm_nodes, ax=plt.gca(), fraction=0.02, pad=0.04)
cbar_nodes.set_label('Grau do Nó (Número de Conexões)', rotation=270, labelpad=15)

plt.title("Rede Viária — Nós Coloridos por Grau", fontsize=16)
plt.gca().set_aspect("equal", adjustable="box")
plt.grid(True, linestyle="--", alpha=0.3)


# 3.2. PLOTAGEM 2: ARESTAS COLORIDAS POR EDGE BETWEENNESS (O que você pediu)
# ==========================================================================
plt.figure(2, figsize=(12, 12))
cmap_edges = plt.cm.viridis # Escolhe um bom mapa de cores para o fluxo (ou viridis/magma)

# Desenha os nós (menores e cinzas para dar foco nas arestas)
nx.draw_networkx_nodes(G, pos, node_size=5, node_color='lightgray')

# Desenha as arestas, colorindo-as pela métrica
nx.draw_networkx_edges(
    G,
    pos,
    edge_color=edge_colors_data, # Usa os valores de Edge Betweenness para colorir
    edge_cmap=cmap_edges,        # Aplica o mapa de cores
    width=2.0,                   # Aumenta um pouco a largura para melhor visualização
    alpha=0.7
)

# Adiciona a barra de cores para o Edge Betweenness
sm_edges = plt.cm.ScalarMappable(cmap=cmap_edges, norm=plt.Normalize(vmin=min(edge_colors_data), vmax=max(edge_colors_data)))
sm_edges.set_array(np.array(edge_colors_data))
cbar_edges = plt.colorbar(sm_edges, ax=plt.gca(), fraction=0.02, pad=0.04)
cbar_edges.set_label('Edge Betweenness Centrality Ponderada', rotation=270, labelpad=15)

plt.title("Rede Viária — Vias Críticas (Edge Betweenness Ponderada)", fontsize=16)
plt.gca().set_aspect("equal", adjustable="box")
plt.grid(True, linestyle="--", alpha=0.3)
plt.show() # Mostra ambas as figuras

# --- 4. Exportação das Métricas para CSV ---

## 4.1. Exportação de Métricas de NÓS (Cruzamentos)
# ===================================================
print("\n--- Exportando Métricas de NÓS (Cruzamentos) ---")
df_metrics = pd.DataFrame({
    'Node': list(G.nodes()),
    'Grau': [degree.get(n, 0) for n in G.nodes()], 
    'Betweenness_Centrality_Weighted': [betweenness_weighted.get(n, 0.0) for n in G.nodes()],
    'Closeness_Centrality_Weighted': [closeness_weighted.get(n, 0.0) for n in G.nodes()]
})

# Adiciona as coordenadas X e Y
df_pos = pd.DataFrame(pos).T.reset_index()
df_pos.columns = ['Node', 'X_Coord', 'Y_Coord']
df_metrics = pd.merge(df_metrics, df_pos, on='Node', how='left')

# Salva em CSV com ponto e vírgula
output_csv_file = "brasilia_node_metrics_semicolon.csv"
df_metrics.to_csv(output_csv_file, index=False, sep=';')
print(f"Métricas dos NÓS salvas em '{output_csv_file}'")
print(df_metrics.head())


## 4.2. Exportação de Métricas de ARESTAS (Vias/Ruas)
# ===================================================
print("\n--- Exportando Métricas de ARESTAS (Vias) ---")

# Converte o dicionário de Edge Betweenness para um DataFrame
df_edges = pd.DataFrame(
    edge_betweenness_weighted.items(), 
    columns=['Edge', 'Edge_Betweenness_Centrality_Weighted']
)

# Adiciona o comprimento da via (Length) e os IDs dos nós nas pontas
df_edges['Node1'] = df_edges['Edge'].apply(lambda x: x[0])
df_edges['Node2'] = df_edges['Edge'].apply(lambda x: x[1])

# Mapeia o peso (length) da aresta
length_map = {(u, v): d['weight'] for u, v, d in G.edges(data=True)}
# Função para obter o peso, tratando arestas não direcionadas (tuplas (u,v) e (v,u))
def get_length(edge):
    u, v = edge
    return length_map.get((u, v)) or length_map.get((v, u))

df_edges['Length_of_Edge'] = df_edges['Edge'].apply(get_length)

# Remove a coluna 'Edge' intermediária e reordena
df_edges = df_edges.drop(columns=['Edge'])
df_edges = df_edges[['Node1', 'Node2', 'Length_of_Edge', 'Edge_Betweenness_Centrality_Weighted']]

# Salva em CSV com ponto e vírgula
output_edge_csv_file = "brasilia_edge_metrics_semicolon.csv"
df_edges.to_csv(output_edge_csv_file, index=False, sep=';') 

print(f"Métricas das VIAS salvas em '{output_edge_csv_file}'")
print(df_edges.head())