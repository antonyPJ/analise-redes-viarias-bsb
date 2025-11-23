"""
Análise de Centralidades - Malha Viária de Brasília
Projeto de Teoria dos Grafos

Este módulo calcula e analisa diferentes medidas de centralidade para identificar
as vias e interseções mais importantes da malha viária:
- Degree Centrality (Centralidade de Grau)
- Betweenness Centrality (Centralidade de Intermediação)
- Closeness Centrality (Centralidade de Proximidade)
- Edge Betweenness Centrality (para identificar vias críticas)

Referência: Crucitti et al. (2006) - Centrality measures in spatial networks
"""

import sys
import io
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path
from scipy.stats import pearsonr

# Configurar encoding UTF-8 para saída (compatibilidade Windows)
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


class AnalisadorCentralidades:
    """
    Classe para análise de centralidades da rede viária de Brasília.
    """

    def __init__(self, caminho_net, caminho_edge_info):
        """
        Inicializa o analisador com os caminhos dos arquivos de dados.

        Args:
            caminho_net: Caminho para o arquivo brasilia.net (lista de arestas)
            caminho_edge_info: Caminho para brasilia_edge_info.txt (coordenadas e distâncias)
        """
        self.caminho_net = Path(caminho_net)
        self.caminho_edge_info = Path(caminho_edge_info)
        self.grafo = None
        self.coordenadas = {}  # {nó: (x, y)}
        self.distancias = {}   # {(nó1, nó2): distância}

        # Métricas de centralidade de nós
        self.degree_centrality = {}
        self.betweenness_centrality = {}
        self.closeness_centrality = {}

        # Métricas de centralidade de arestas
        self.edge_betweenness_centrality = {}

    def carregar_dados(self):
        """
        Carrega os dados dos arquivos e constrói o grafo.
        """
        print("=" * 70)
        print("CARREGANDO DADOS DA MALHA VIÁRIA DE BRASÍLIA")
        print("=" * 70)

        # Criar grafo não-direcionado
        self.grafo = nx.Graph()

        # Ler arquivo brasilia_edge_info.txt para obter coordenadas e distâncias
        print(f"\n[1/2] Lendo arquivo: {self.caminho_edge_info.name}")
        with open(self.caminho_edge_info, 'r', encoding='utf-8') as f:
            for linha in f:
                partes = linha.strip().split()
                if len(partes) >= 8:
                    # Formato: id nó1 x1 y1 nó2 x2 y2 distância
                    no1 = int(partes[1])
                    x1 = float(partes[2])
                    y1 = float(partes[3])
                    no2 = int(partes[4])
                    x2 = float(partes[5])
                    y2 = float(partes[6])
                    distancia = float(partes[7])

                    # Armazenar coordenadas
                    self.coordenadas[no1] = (x1, y1)
                    self.coordenadas[no2] = (x2, y2)

                    # Armazenar distância (garantindo ordem consistente)
                    chave = tuple(sorted([no1, no2]))
                    self.distancias[chave] = distancia

        print(f"   >> {len(self.coordenadas)} nós com coordenadas carregados")
        print(f"   >> {len(self.distancias)} distâncias carregadas")

        # Ler arquivo brasilia.net para construir o grafo
        print(f"\n[2/2] Lendo arquivo: {self.caminho_net.name}")
        arestas_adicionadas = 0
        with open(self.caminho_net, 'r', encoding='utf-8') as f:
            for linha in f:
                partes = linha.strip().split()
                if len(partes) >= 2:
                    no1 = int(partes[0])
                    no2 = int(partes[1])

                    # Obter distância
                    chave = tuple(sorted([no1, no2]))
                    distancia = self.distancias.get(chave, 0)

                    # Adicionar aresta com peso (distância)
                    self.grafo.add_edge(no1, no2, weight=distancia)
                    arestas_adicionadas += 1

        print(f"   >> {arestas_adicionadas} arestas adicionadas ao grafo")
        print(f"\n{'>> DADOS CARREGADOS COM SUCESSO' : ^70}")
        print("=" * 70)

    def calcular_centralidades(self):
        """
        Calcula todas as medidas de centralidade.
        """
        print("\n" + "=" * 70)
        print("CALCULANDO MEDIDAS DE CENTRALIDADE")
        print("=" * 70)

        # Degree Centrality
        print("\n[1/4] Calculando Degree Centrality...")
        print("      (Numero de conexoes de cada no)")
        graus = dict(self.grafo.degree())
        # Normalizar pelo grau máximo possível
        max_grau = self.grafo.number_of_nodes() - 1
        self.degree_centrality = {no: grau / max_grau for no, grau in graus.items()}
        print(f"      >> Concluido")

        # Betweenness Centrality (ESSENCIAL - baseado em Crucitti et al. 2006)
        print("\n[2/4] Calculando Betweenness Centrality (ponderada)...")
        print("      (Frequencia com que um no aparece nos caminhos minimos)")
        print("      Usando distancias como peso das arestas")
        print("      ATENCAO: Calculo computacionalmente intensivo...")
        self.betweenness_centrality = nx.betweenness_centrality(
            self.grafo,
            weight='weight',  # Usar distância como peso
            normalized=True
        )
        print(f"      >> Concluido")

        # Closeness Centrality
        print("\n[3/4] Calculando Closeness Centrality (ponderada)...")
        print("      (Quao 'proximo' um no esta de todos os outros)")
        self.closeness_centrality = nx.closeness_centrality(
            self.grafo,
            distance='weight'  # Usar distância como peso
        )
        print(f"      >> Concluido")

        # Edge Betweenness Centrality
        print("\n[4/4] Calculando Edge Betweenness Centrality (ponderada)...")
        print("      (Identifica vias mais importantes para fluxo)")
        print("      ATENCAO: Calculo computacionalmente intensivo...")
        self.edge_betweenness_centrality = nx.edge_betweenness_centrality(
            self.grafo,
            weight='weight',
            normalized=True
        )
        print(f"      >> Concluido")

        print("\n" + "=" * 70)

    def criar_rankings(self, top_n=10):
        """
        Cria rankings dos nós e arestas mais importantes.

        Args:
            top_n: Número de elementos no ranking
        """
        print("\n" + "=" * 70)
        print(f"RANKINGS TOP {top_n} - INTERSEÇÕES MAIS IMPORTANTES")
        print("=" * 70)

        # Ranking por Degree Centrality
        print(f"\nTOP {top_n} - DEGREE CENTRALITY (Grau):")
        print("-" * 70)
        print(f"{'Rank':<6} {'No':<10} {'Grau Real':<12} {'Centralidade':<15}")
        print("-" * 70)

        graus = dict(self.grafo.degree())
        top_degree = sorted(self.degree_centrality.items(),
                           key=lambda x: x[1], reverse=True)[:top_n]

        for idx, (no, centralidade) in enumerate(top_degree, 1):
            print(f"{idx:<6} {no:<10} {graus[no]:<12} {centralidade:<15.6f}")

        # Ranking por Betweenness Centrality (MAIS IMPORTANTE)
        print(f"\nTOP {top_n} - BETWEENNESS CENTRALITY (Intermediacao) - PRINCIPAL:")
        print("-" * 70)
        print(f"{'Rank':<6} {'No':<10} {'Centralidade':<15} {'Coord X':<12} {'Coord Y':<12}")
        print("-" * 70)

        top_betweenness = sorted(self.betweenness_centrality.items(),
                                key=lambda x: x[1], reverse=True)[:top_n]

        for idx, (no, centralidade) in enumerate(top_betweenness, 1):
            coord = self.coordenadas.get(no, (0, 0))
            print(f"{idx:<6} {no:<10} {centralidade:<15.6f} {coord[0]:<12.2f} {coord[1]:<12.2f}")

        # Ranking por Closeness Centrality
        print(f"\nTOP {top_n} - CLOSENESS CENTRALITY (Proximidade):")
        print("-" * 70)
        print(f"{'Rank':<6} {'No':<10} {'Centralidade':<15} {'Coord X':<12} {'Coord Y':<12}")
        print("-" * 70)

        top_closeness = sorted(self.closeness_centrality.items(),
                              key=lambda x: x[1], reverse=True)[:top_n]

        for idx, (no, centralidade) in enumerate(top_closeness, 1):
            coord = self.coordenadas.get(no, (0, 0))
            print(f"{idx:<6} {no:<10} {centralidade:<15.6f} {coord[0]:<12.2f} {coord[1]:<12.2f}")

        # Ranking de Edge Betweenness (Vias mais importantes)
        print(f"\nTOP {top_n} - VIAS MAIS CRITICAS (Edge Betweenness):")
        print("-" * 70)
        print(f"{'Rank':<6} {'No 1':<10} {'No 2':<10} {'Dist (m)':<12} {'Centralidade':<15}")
        print("-" * 70)

        top_edge_betweenness = sorted(self.edge_betweenness_centrality.items(),
                                      key=lambda x: x[1], reverse=True)[:top_n]

        for idx, ((no1, no2), centralidade) in enumerate(top_edge_betweenness, 1):
            chave = tuple(sorted([no1, no2]))
            dist = self.distancias.get(chave, 0)
            print(f"{idx:<6} {no1:<10} {no2:<10} {dist:<12.2f} {centralidade:<15.6f}")

        print("=" * 70)

    def visualizar_centralidades(self, salvar=True, mostrar=False):
        """
        Cria visualizações de heatmaps de centralidade.

        Args:
            salvar: Se True, salva a figura em arquivo
            mostrar: Se True, exibe a figura interativamente
        """
        print("\n" + "=" * 70)
        print("GERANDO VISUALIZAÇÕES DE CENTRALIDADES")
        print("=" * 70)

        # Criar figura com 4 subplots (2x2)
        fig, axes = plt.subplots(2, 2, figsize=(18, 16))

        pos = self.coordenadas

        # ===== SUBPLOT 1: Degree Centrality =====
        print("\n[1/4] Visualizando Degree Centrality...")
        ax = axes[0, 0]

        node_colors = [self.degree_centrality[n] for n in self.grafo.nodes()]

        nx.draw_networkx_nodes(
            self.grafo, pos,
            node_color=node_colors,
            node_size=150,
            cmap=plt.cm.YlOrRd,  # Melhor para impressao
            alpha=0.8,
            ax=ax
        )

        nx.draw_networkx_edges(
            self.grafo, pos,
            alpha=0.2,
            width=0.5,
            ax=ax
        )

        ax.set_title('Degree Centrality\n(Numero de Conexoes)',
                    fontsize=13, fontweight='bold')
        ax.set_xlabel('Coordenada X', fontsize=10)
        ax.set_ylabel('Coordenada Y', fontsize=10)
        ax.grid(True, alpha=0.3)
        ax.set_aspect('equal')

        # Colorbar
        sm = plt.cm.ScalarMappable(
            cmap=plt.cm.YlOrRd,
            norm=plt.Normalize(vmin=min(node_colors), vmax=max(node_colors))
        )
        sm.set_array([])
        cbar = plt.colorbar(sm, ax=ax, fraction=0.046, pad=0.04)
        cbar.set_label('Centralidade', rotation=270, labelpad=15)

        print("      >> Concluido")

        # ===== SUBPLOT 2: Betweenness Centrality =====
        print("[2/4] Visualizando Betweenness Centrality...")
        ax = axes[0, 1]

        node_colors = [self.betweenness_centrality[n] for n in self.grafo.nodes()]

        nx.draw_networkx_nodes(
            self.grafo, pos,
            node_color=node_colors,
            node_size=150,
            cmap=plt.cm.OrRd,  # Melhor que hot para impressao
            alpha=0.8,
            ax=ax
        )

        nx.draw_networkx_edges(
            self.grafo, pos,
            alpha=0.2,
            width=0.5,
            ax=ax
        )

        ax.set_title('Betweenness Centrality\n(Intermediacao - PRINCIPAL)',
                    fontsize=13, fontweight='bold')
        ax.set_xlabel('Coordenada X', fontsize=10)
        ax.set_ylabel('Coordenada Y', fontsize=10)
        ax.grid(True, alpha=0.3)
        ax.set_aspect('equal')

        # Colorbar
        sm = plt.cm.ScalarMappable(
            cmap=plt.cm.OrRd,
            norm=plt.Normalize(vmin=min(node_colors), vmax=max(node_colors))
        )
        sm.set_array([])
        cbar = plt.colorbar(sm, ax=ax, fraction=0.046, pad=0.04)
        cbar.set_label('Centralidade', rotation=270, labelpad=15)

        print("      >> Concluido")

        # ===== SUBPLOT 3: Closeness Centrality =====
        print("[3/4] Visualizando Closeness Centrality...")
        ax = axes[1, 0]

        node_colors = [self.closeness_centrality[n] for n in self.grafo.nodes()]

        nx.draw_networkx_nodes(
            self.grafo, pos,
            node_color=node_colors,
            node_size=150,
            cmap=plt.cm.BuPu,  # Alternativa ao viridis, melhor para impressao
            alpha=0.8,
            ax=ax
        )

        nx.draw_networkx_edges(
            self.grafo, pos,
            alpha=0.2,
            width=0.5,
            ax=ax
        )

        ax.set_title('Closeness Centrality\n(Proximidade)',
                    fontsize=13, fontweight='bold')
        ax.set_xlabel('Coordenada X', fontsize=10)
        ax.set_ylabel('Coordenada Y', fontsize=10)
        ax.grid(True, alpha=0.3)
        ax.set_aspect('equal')

        # Colorbar
        sm = plt.cm.ScalarMappable(
            cmap=plt.cm.BuPu,
            norm=plt.Normalize(vmin=min(node_colors), vmax=max(node_colors))
        )
        sm.set_array([])
        cbar = plt.colorbar(sm, ax=ax, fraction=0.046, pad=0.04)
        cbar.set_label('Centralidade', rotation=270, labelpad=15)

        print("      >> Concluido")

        # ===== SUBPLOT 4: Edge Betweenness Centrality =====
        print("[4/4] Visualizando Edge Betweenness Centrality...")
        ax = axes[1, 1]

        # Nós pequenos e cinzas para dar foco nas arestas
        nx.draw_networkx_nodes(
            self.grafo, pos,
            node_size=20,
            node_color='lightgray',
            alpha=0.5,
            ax=ax
        )

        # Arestas coloridas pela centralidade
        edge_colors = [self.edge_betweenness_centrality.get((u, v), 0)
                      for u, v in self.grafo.edges()]

        nx.draw_networkx_edges(
            self.grafo, pos,
            edge_color=edge_colors,
            edge_cmap=plt.cm.Reds,
            width=2.0,
            alpha=0.7,
            ax=ax
        )

        ax.set_title('Edge Betweenness Centrality\n(Vias Criticas para Fluxo)',
                    fontsize=13, fontweight='bold')
        ax.set_xlabel('Coordenada X', fontsize=10)
        ax.set_ylabel('Coordenada Y', fontsize=10)
        ax.grid(True, alpha=0.3)
        ax.set_aspect('equal')

        # Colorbar
        sm = plt.cm.ScalarMappable(
            cmap=plt.cm.Reds,
            norm=plt.Normalize(vmin=min(edge_colors), vmax=max(edge_colors))
        )
        sm.set_array([])
        cbar = plt.colorbar(sm, ax=ax, fraction=0.046, pad=0.04)
        cbar.set_label('Centralidade', rotation=270, labelpad=15)

        print("      >> Concluido")

        # Adicionar informações gerais
        info_text = f"Nós: {self.grafo.number_of_nodes()} | Arestas: {self.grafo.number_of_edges()}"
        fig.text(0.5, 0.02, info_text, ha='center', fontsize=10,
                style='italic', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))

        plt.tight_layout(rect=[0, 0.03, 1, 0.98])

        # Salvar figura
        if salvar:
            caminho_saida = Path(__file__).parent.parent / 'resultados' / 'graficos'
            caminho_saida.mkdir(parents=True, exist_ok=True)
            arquivo_saida = caminho_saida / '04_centralidades_heatmaps.png'
            plt.savefig(arquivo_saida, dpi=300, bbox_inches='tight')
            print(f"\n>> Figura salva em: {arquivo_saida}")

        # Mostrar figura
        if mostrar:
            plt.show()
        else:
            plt.close()

        print("=" * 70)

    def exportar_metricas(self):
        """
        Exporta métricas para CSV para análise posterior.
        """
        print("\n" + "=" * 70)
        print("EXPORTANDO MÉTRICAS PARA CSV")
        print("=" * 70)

        caminho_saida = Path(__file__).parent.parent / 'resultados'
        caminho_saida.mkdir(parents=True, exist_ok=True)

        # Exportar métricas de nós
        print("\n[1/2] Exportando métricas de nós...")

        graus = dict(self.grafo.degree())

        df_nodes = pd.DataFrame({
            'Node': list(self.grafo.nodes()),
            'Degree': [graus[n] for n in self.grafo.nodes()],
            'Degree_Centrality': [self.degree_centrality[n] for n in self.grafo.nodes()],
            'Betweenness_Centrality': [self.betweenness_centrality[n] for n in self.grafo.nodes()],
            'Closeness_Centrality': [self.closeness_centrality[n] for n in self.grafo.nodes()],
            'X_Coord': [self.coordenadas[n][0] for n in self.grafo.nodes()],
            'Y_Coord': [self.coordenadas[n][1] for n in self.grafo.nodes()]
        })

        arquivo_nodes = caminho_saida / '03_metricas_nodes_centralidades.csv'
        df_nodes.to_csv(arquivo_nodes, index=False, sep=';')
        print(f"      >> Salvo em: {arquivo_nodes}")

        # Exportar métricas de arestas
        print("[2/2] Exportando métricas de arestas...")

        edges_data = []
        for (u, v), centralidade in self.edge_betweenness_centrality.items():
            chave = tuple(sorted([u, v]))
            dist = self.distancias.get(chave, 0)
            edges_data.append({
                'Node1': u,
                'Node2': v,
                'Distance': dist,
                'Edge_Betweenness_Centrality': centralidade
            })

        df_edges = pd.DataFrame(edges_data)

        arquivo_edges = caminho_saida / '04_metricas_edges_centralidades.csv'
        df_edges.to_csv(arquivo_edges, index=False, sep=';')
        print(f"      >> Salvo em: {arquivo_edges}")

        print("=" * 70)

    def calcular_correlacoes(self):
        """
        Calcula correlações de Pearson entre as métricas de centralidade.

        Returns:
            dict: Dicionário com os resultados das correlações
        """
        # Extrair valores das métricas na mesma ordem de nós
        nos = sorted(self.grafo.nodes())

        degree_values = [self.degree_centrality[n] for n in nos]
        betweenness_values = [self.betweenness_centrality[n] for n in nos]
        closeness_values = [self.closeness_centrality[n] for n in nos]

        # Calcular correlações
        corr_deg_bet, p_deg_bet = pearsonr(degree_values, betweenness_values)
        corr_deg_clo, p_deg_clo = pearsonr(degree_values, closeness_values)
        corr_bet_clo, p_bet_clo = pearsonr(betweenness_values, closeness_values)

        return {
            'degree_betweenness': (corr_deg_bet, p_deg_bet),
            'degree_closeness': (corr_deg_clo, p_deg_clo),
            'betweenness_closeness': (corr_bet_clo, p_bet_clo)
        }

    def gerar_relatorio(self):
        """
        Gera relatório detalhado da análise de centralidades.
        """
        # Calcular correlações
        correlacoes = self.calcular_correlacoes()

        # Calcular estatísticas adicionais para a análise comparativa
        valores_betweenness = list(self.betweenness_centrality.values())
        media_bet = np.mean(valores_betweenness)
        max_bet = np.max(valores_betweenness)

        # Identificar pontes
        pontes = list(nx.bridges(self.grafo))
        num_pontes = len(pontes)
        perc_pontes = (num_pontes / self.grafo.number_of_edges()) * 100

        caminho_saida = Path(__file__).parent.parent / 'resultados'
        caminho_saida.mkdir(parents=True, exist_ok=True)
        arquivo_saida = caminho_saida / '03_relatorio_analise_centralidades.txt'

        with open(arquivo_saida, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("RELATÓRIO DE ANÁLISE DE CENTRALIDADES\n")
            f.write("Malha Viária de Brasília - Projeto de Teoria dos Grafos\n")
            f.write("=" * 80 + "\n\n")

            f.write("1. OBJETIVO\n")
            f.write("-" * 80 + "\n")
            f.write("   Identificar as interseções e vias mais importantes da malha viária usando\n")
            f.write("   diferentes medidas de centralidade.\n\n")

            f.write("2. MEDIDAS DE CENTRALIDADE CALCULADAS\n")
            f.write("-" * 80 + "\n\n")

            f.write("   2.1. DEGREE CENTRALITY (Centralidade de Grau)\n")
            f.write("   • Definição: Número de conexões diretas de cada interseção\n")
            f.write("   • Interpretação: Interseções com muitas vias conectadas\n")
            f.write("   • Normalização: Dividido pelo número máximo possível de conexões\n\n")

            f.write("   2.2. BETWEENNESS CENTRALITY (Centralidade de Intermediação) ⭐\n")
            f.write("   • Definição: Frequência com que um nó aparece em caminhos mínimos\n")
            f.write("   • Interpretação: Pontos por onde passa mais tráfego\n")
            f.write("   • Ponderação: Usa distâncias reais como peso\n")
            f.write("   • Importância: Medida ESSENCIAL segundo Crucitti et al. (2006)\n\n")

            f.write("   2.3. CLOSENESS CENTRALITY (Centralidade de Proximidade)\n")
            f.write("   • Definição: Quão 'próximo' um nó está de todos os outros\n")
            f.write("   • Interpretação: Pontos centrais geograficamente\n")
            f.write("   • Ponderação: Usa distâncias reais\n\n")

            f.write("   2.4. EDGE BETWEENNESS CENTRALITY (Centralidade de Arestas)\n")
            f.write("   • Definição: Identifica vias mais importantes para fluxo\n")
            f.write("   • Interpretação: Vias por onde passa mais tráfego\n")
            f.write("   • Aplicação: Planejamento de manutenção e expansão\n\n")

            f.write("3. ESTATÍSTICAS GERAIS\n")
            f.write("-" * 80 + "\n")

            # Estatísticas de Betweenness (mais importante)
            valores_betweenness = list(self.betweenness_centrality.values())
            f.write(f"   Betweenness Centrality:\n")
            f.write(f"   • Média:       {np.mean(valores_betweenness):.6f}\n")
            f.write(f"   • Mediana:     {np.median(valores_betweenness):.6f}\n")
            f.write(f"   • Máximo:      {np.max(valores_betweenness):.6f}\n")
            f.write(f"   • Mínimo:      {np.min(valores_betweenness):.6f}\n")
            f.write(f"   • Desvio pad:  {np.std(valores_betweenness):.6f}\n\n")

            f.write("4. TOP 10 INTERSEÇÕES - BETWEENNESS CENTRALITY (PRINCIPAL)\n")
            f.write("-" * 80 + "\n")

            top_betweenness = sorted(self.betweenness_centrality.items(),
                                    key=lambda x: x[1], reverse=True)[:10]

            f.write(f"   {'Rank':<6} {'Nó':<10} {'Centralidade':<15} {'Coord X':<12} {'Coord Y':<12}\n")
            f.write("   " + "-" * 70 + "\n")

            for idx, (no, centralidade) in enumerate(top_betweenness, 1):
                coord = self.coordenadas.get(no, (0, 0))
                f.write(f"   {idx:<6} {no:<10} {centralidade:<15.6f} {coord[0]:<12.2f} {coord[1]:<12.2f}\n")

            f.write("\n5. TOP 10 VIAS - EDGE BETWEENNESS CENTRALITY\n")
            f.write("-" * 80 + "\n")

            top_edge_betweenness = sorted(self.edge_betweenness_centrality.items(),
                                          key=lambda x: x[1], reverse=True)[:10]

            f.write(f"   {'Rank':<6} {'Nó 1':<10} {'Nó 2':<10} {'Dist (m)':<12} {'Centralidade':<15}\n")
            f.write("   " + "-" * 70 + "\n")

            for idx, ((no1, no2), centralidade) in enumerate(top_edge_betweenness, 1):
                chave = tuple(sorted([no1, no2]))
                dist = self.distancias.get(chave, 0)
                f.write(f"   {idx:<6} {no1:<10} {no2:<10} {dist:<12.2f} {centralidade:<15.6f}\n")

            # ===== SEÇÃO 6: CORRELAÇÕES ENTRE MÉTRICAS =====
            f.write("\n6. CORRELAÇÕES ENTRE MÉTRICAS\n")
            f.write("-" * 80 + "\n\n")
            f.write(f"   Correlações de Pearson (N={self.grafo.number_of_nodes()}):\n\n")

            corr_deg_bet, p_deg_bet = correlacoes['degree_betweenness']
            corr_deg_clo, p_deg_clo = correlacoes['degree_closeness']
            corr_bet_clo, p_bet_clo = correlacoes['betweenness_closeness']

            f.write(f"   Degree x Betweenness:     r = {corr_deg_bet:.4f}, p = {p_deg_bet:.6f}\n")
            f.write(f"   Degree x Closeness:       r = {corr_deg_clo:.4f}, p = {p_deg_clo:.6f}\n")
            f.write(f"   Betweenness x Closeness:  r = {corr_bet_clo:.4f}, p = {p_bet_clo:.6f}\n\n")

            # ===== SEÇÃO 7: DADOS ADICIONAIS =====
            f.write("7. DADOS ADICIONAIS\n")
            f.write("-" * 80 + "\n\n")

            # Encontrar nó com maior betweenness
            no_max_bet = max(self.betweenness_centrality.items(), key=lambda x: x[1])
            razao_max_media = no_max_bet[1] / media_bet

            f.write("   Concentração de Betweenness:\n")
            f.write(f"   • Nó com maior valor:     {no_max_bet[0]} ({no_max_bet[1]:.4f})\n")
            f.write(f"   • Razão máximo/média:     {razao_max_media:.2f}x\n\n")

            # Calcular concentração no top 10
            top_10_bet = sorted(valores_betweenness, reverse=True)[:10]
            conc_top_10 = (sum(top_10_bet) / sum(valores_betweenness)) * 100

            f.write(f"   Concentração no Top 10:   {conc_top_10:.1f}% do total de betweenness\n\n")

            f.write(f"   Pontes identificadas:     {num_pontes} ({perc_pontes:.1f}% das vias)\n\n")

            f.write("8. REFERÊNCIAS\n")
            f.write("-" * 80 + "\n")
            f.write("   • Crucitti, P., Latora, V., & Porta, S. (2006). Centrality measures in\n")
            f.write("     spatial networks of urban streets. Physical Review E, 73, 036125.\n\n")
            f.write("   • Newman, M. E. J. (2010). Networks: An Introduction. Oxford University Press.\n\n")
            f.write("   • Derrible, S., & Kennedy, C. (2010). The complexity and robustness of\n")
            f.write("     metro networks. Physica A, 389(17), 3678-3691.\n\n")

            f.write("=" * 80 + "\n")

        print(f"\n>> Relatorio salvo em: {arquivo_saida}")


def main():
    """
    Função principal para execução da análise de centralidades.
    """
    # Caminhos dos arquivos
    base_path = Path(__file__).parent.parent
    caminho_net = base_path / 'base_conhecimento_projeto' / 'brasilia.net'
    caminho_edge_info = base_path / 'base_conhecimento_projeto' / 'brasilia_edge_info.txt'

    # Criar analisador
    analisador = AnalisadorCentralidades(caminho_net, caminho_edge_info)

    # Executar análise
    analisador.carregar_dados()
    analisador.calcular_centralidades()
    analisador.criar_rankings(top_n=10)
    analisador.visualizar_centralidades(salvar=True, mostrar=False)
    analisador.exportar_metricas()
    analisador.gerar_relatorio()

    print("\n" + "=" * 70)
    print(">> ANALISE DE CENTRALIDADES CONCLUIDA COM SUCESSO")
    print("=" * 70)
    print("\nArquivos gerados:")
    print("   - resultados/graficos/04_centralidades_heatmaps.png")
    print("   - resultados/03_metricas_nodes_centralidades.csv")
    print("   - resultados/04_metricas_edges_centralidades.csv")
    print("   - resultados/03_relatorio_analise_centralidades.txt")
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
