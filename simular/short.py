import networkx as nx
import csv
import random
import math

# ----- ARQUIVOS -----
ARQ_EDGE = "brasilia_edge_info.txt"
ARQ_FLUXO = "fluxo_total_por_dia.csv"
DIA = "2025-05-01"

# ----- CARREGAR GRAFO -----
G = nx.Graph()
pos = {}
with open(ARQ_EDGE, "r", encoding="utf-8") as f:
    for linha in f:
        p = linha.split()
        if len(p) < 8 or p[0].startswith("#"):
            continue
        n1, x1, y1 = int(p[1]), float(p[2]), float(p[3])
        n2, x2, y2 = int(p[4]), float(p[5]), float(p[6])
        dist = float(p[7])
        pos[n1] = (x1, y1)
        pos[n2] = (x2, y2)
        G.add_edge(n1, n2, weight=dist)

# ----- LER FLUXO DIÁRIO -----
fluxo_dia = 0
with open(ARQ_FLUXO, "r", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        if row["Dia"] == DIA:
            fluxo_dia = int(row["Fluxo"])
            break

fluxo_hora = fluxo_dia // 24

# ----- PARÂMETROS -----
VEIC_POR_AGENT = 1000
CAPACIDADE = 1500   # por hora
MAX_AGENTES = 400

nodes = list(G.nodes())
arestas = list(G.edges())
carga = {e: 0 for e in arestas}

# ----- SIMULAÇÃO -----
for hora in range(24):
    agentes = fluxo_hora // VEIC_POR_AGENT
    agentes = min(agentes, MAX_AGENTES)

    for _ in range(agentes):
        o = random.choice(nodes)
        d = random.choice(nodes)
        if o == d: 
            continue
        try:
            caminho = nx.shortest_path(G, o, d, weight="weight")
        except:
            continue
        
        veic = fluxo_hora / max(1, agentes)

        for i in range(len(caminho)-1):
            u, v = caminho[i], caminho[i+1]
            e = (u, v) if (u, v) in carga else (v, u)
            carga[e] += veic

# ----- CALCULAR SATURAÇÃO -----
resultados = []
for (u, v), qtd in carga.items():
    sat = qtd / CAPACIDADE
    resultados.append([u, v, round(qtd,2), round(sat,3)])

# ----- SALVAR -----
with open("resultado_fluxo.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["Node1", "Node2", "Carga", "Saturacao"])
    w.writerows(resultados)

print("Simulação concluída. Arquivo gerado: resultado_fluxo.csv")