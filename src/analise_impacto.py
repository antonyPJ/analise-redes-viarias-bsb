"""
Análise de Caminhos Mínimos e Simulação de Impacto
Projeto de Teoria dos Grafos

Este módulo implementa:
- Algoritmo de Dijkstra para caminhos mínimos
- Identificação de rotas estratégicas
- Simulação de impacto da remoção de pontes e pontos críticos
- Análise comparativa antes/depois de bloqueios

O objetivo é quantificar a vulnerabilidade da malha viária.
"""

import sys
import io
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from collections import defaultdict

# Configurar encoding UTF-8 para saída (compatibilidade Windows)
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


class AnalisadorImpacto:
    """
    Classe para análise de caminhos mínimos e simulação de impacto de bloqueios.
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

    def analisar_caminhos_minimos(self, pares_estrategicos=None):
        """
        Analisa caminhos mínimos entre pares de nós usando algoritmo de Dijkstra.

        Args:
            pares_estrategicos: Lista de tuplas (origem, destino). Se None, escolhe automaticamente.
        """
        print("\n" + "=" * 70)
        print("ANÁLISE DE CAMINHOS MÍNIMOS (ALGORITMO DE DIJKSTRA)")
        print("=" * 70)

        if pares_estrategicos is None:
            # Escolher pares estratégicos baseados em centralidade
            print("\nIdentificando pares estratégicos baseados em posição geográfica...")

            # Pegar nós em diferentes quadrantes
            nos = list(self.grafo.nodes())
            coords_x = [self.coordenadas[n][0] for n in nos]
            coords_y = [self.coordenadas[n][1] for n in nos]

            # Encontrar extremos
            idx_min_x = nos[np.argmin(coords_x)]
            idx_max_x = nos[np.argmax(coords_x)]
            idx_min_y = nos[np.argmin(coords_y)]
            idx_max_y = nos[np.argmax(coords_y)]

            # Encontrar nó central
            centro_x = np.median(coords_x)
            centro_y = np.median(coords_y)
            distancias_centro = [(n, np.sqrt((self.coordenadas[n][0] - centro_x)**2 +
                                            (self.coordenadas[n][1] - centro_y)**2))
                               for n in nos]
            no_central = min(distancias_centro, key=lambda x: x[1])[0]

            pares_estrategicos = [
                (idx_min_x, idx_max_x, "Oeste-Leste"),
                (idx_min_y, idx_max_y, "Sul-Norte"),
                (idx_min_x, no_central, "Oeste-Centro"),
                (idx_max_x, no_central, "Leste-Centro"),
                (idx_min_y, no_central, "Sul-Centro"),
            ]

            print(f"   >> {len(pares_estrategicos)} pares estrategicos identificados")

        print("\nCalculando caminhos minimos usando Dijkstra...\n")
        print("-" * 70)
        print(f"{'#':<4} {'Origem':<10} {'Destino':<10} {'Descricao':<15} {'Distancia (m)':<15} {'Nos no Caminho':<10}")
        print("-" * 70)

        resultados = []

        for idx, par in enumerate(pares_estrategicos, 1):
            if len(par) == 3:
                origem, destino, descricao = par
            else:
                origem, destino = par
                descricao = f"{origem}-{destino}"

            try:
                # Calcular caminho mínimo usando Dijkstra
                caminho = nx.shortest_path(self.grafo, origem, destino, weight='weight')
                distancia = nx.shortest_path_length(self.grafo, origem, destino, weight='weight')

                resultados.append({
                    'origem': origem,
                    'destino': destino,
                    'descricao': descricao,
                    'caminho': caminho,
                    'distancia': distancia,
                    'num_nos': len(caminho)
                })

                print(f"{idx:<4} {origem:<10} {destino:<10} {descricao:<15} {distancia:<15.2f} {len(caminho):<10}")

            except nx.NetworkXNoPath:
                print(f"{idx:<4} {origem:<10} {destino:<10} {descricao:<15} {'SEM CAMINHO':<15} {'-':<10}")

        print("-" * 70)

        # Estatísticas
        if resultados:
            distancias = [r['distancia'] for r in resultados]
            print(f"\nEstatisticas dos Caminhos:")
            print(f"   - Distancia media:     {np.mean(distancias):.2f} m ({np.mean(distancias)/1000:.2f} km)")
            print(f"   - Distancia minima:    {np.min(distancias):.2f} m ({np.min(distancias)/1000:.2f} km)")
            print(f"   - Distancia maxima:    {np.max(distancias):.2f} m ({np.max(distancias)/1000:.2f} km)")

        print("=" * 70)

        return resultados

    def simular_remocao_ponte(self, aresta=None, top_n=1):
        """
        Simula o impacto da remoção de pontes (arestas críticas).

        Args:
            aresta: Tupla (u, v) da aresta a remover. Se None, usa a ponte mais crítica.
            top_n: Número de pontes a simular (se aresta=None)

        Returns:
            list: Lista de dicionários com resultados das simulações
        """
        resultados_simulacoes = []
        print("\n" + "=" * 70)
        print("SIMULAÇÃO DE IMPACTO - REMOÇÃO DE PONTES")
        print("=" * 70)

        # Identificar pontes
        pontes = list(nx.bridges(self.grafo))

        if len(pontes) == 0:
            print("\n>> Nao ha pontes no grafo. Simulacao nao aplicavel.")
            print("=" * 70)
            return []

        print(f"\nTotal de pontes identificadas: {len(pontes)}")

        # Se aresta não especificada, usar ponte(s) com maior Edge Betweenness
        if aresta is None:
            print(f"Identificando as {top_n} ponte(s) mais crítica(s) por Edge Betweenness...")

            edge_betweenness = nx.edge_betweenness_centrality(self.grafo, weight='weight')

            # Filtrar apenas pontes e ordenar por betweenness
            pontes_betweenness = [(p, edge_betweenness.get(p, 0)) for p in pontes]
            pontes_betweenness.sort(key=lambda x: x[1], reverse=True)

            arestas_simular = [p[0] for p in pontes_betweenness[:top_n]]
        else:
            arestas_simular = [aresta]

        # Calcular edge betweenness para todas as pontes
        edge_betweenness = nx.edge_betweenness_centrality(self.grafo, weight='weight')

        # Simular remoção de cada ponte
        for idx, aresta_remover in enumerate(arestas_simular, 1):
            print(f"\n{'='*70}")
            print(f"SIMULAÇÃO {idx}/{len(arestas_simular)}: Remoção da ponte {aresta_remover}")
            print(f"{'='*70}")

            u, v = aresta_remover
            chave = tuple(sorted([u, v]))
            dist = self.distancias.get(chave, 0)
            edge_bet = edge_betweenness.get(aresta_remover, 0)

            print(f"\nRemovendo aresta: {u} - {v}")
            print(f"   Distancia da via: {dist:.2f} m")

            # Criar cópia do grafo e remover aresta
            grafo_modificado = self.grafo.copy()
            grafo_modificado.remove_edge(u, v)

            # Análise ANTES da remoção
            num_componentes_antes = nx.number_connected_components(self.grafo)
            num_nos_antes = self.grafo.number_of_nodes()
            is_conexo_antes = nx.is_connected(self.grafo)

            print("\nANTES DA REMOCAO:")
            print(f"   - Componentes conexos:      {num_componentes_antes}")
            print(f"   - Nos alcancaveis:          {num_nos_antes}")
            print(f"   - Grafo conexo:             {'SIM' if is_conexo_antes else 'NAO'}")

            # Análise DEPOIS da remoção
            num_componentes_depois = nx.number_connected_components(grafo_modificado)
            is_conexo_depois = nx.is_connected(grafo_modificado)

            print("\nDEPOIS DA REMOCAO:")
            print(f"   - Componentes conexos:      {num_componentes_depois}")
            print(f"   - Grafo conexo:             {'SIM' if is_conexo_depois else 'NAO'}")

            componentes = []
            tamanhos = []
            menor_componente = []

            if num_componentes_depois > 1:
                print(f"\nIMPACTO CRITICO: A rede foi FRAGMENTADA!")

                componentes = list(nx.connected_components(grafo_modificado))
                tamanhos = [len(c) for c in componentes]

                print(f"\n   Componentes gerados:")
                for i, tamanho in enumerate(sorted(tamanhos, reverse=True), 1):
                    percentual = (tamanho / self.grafo.number_of_nodes()) * 100
                    print(f"   - Componente {i}: {tamanho} nos ({percentual:.1f}%)")

                # Identificar nós isolados
                menor_componente = sorted(min(componentes, key=len))
                print(f"\n   Nos isolados: {menor_componente}")

            # Análise de aumento de distâncias
            print(f"\nIMPACTO NAS DISTANCIAS:")

            # Amostra de pares de nós para testar
            nos_amostra = list(self.grafo.nodes())[:20]  # Usar subset para performance

            aumentos = []
            sem_caminho = 0

            for origem in nos_amostra:
                for destino in nos_amostra:
                    if origem >= destino:
                        continue

                    try:
                        # Distância original
                        dist_original = nx.shortest_path_length(
                            self.grafo, origem, destino, weight='weight')

                        # Distância após remoção
                        try:
                            dist_nova = nx.shortest_path_length(
                                grafo_modificado, origem, destino, weight='weight')

                            if dist_nova > dist_original:
                                aumento_pct = ((dist_nova - dist_original) / dist_original) * 100
                                aumentos.append(aumento_pct)

                        except nx.NetworkXNoPath:
                            sem_caminho += 1

                    except nx.NetworkXNoPath:
                        pass

            if aumentos:
                print(f"   - Pares com aumento de distancia:  {len(aumentos)}")
                print(f"   - Aumento medio:                   {np.mean(aumentos):.1f}%")
                print(f"   - Aumento maximo:                  {np.max(aumentos):.1f}%")

            if sem_caminho > 0:
                print(f"   - Pares sem caminho (isolados):    {sem_caminho}")

            # Armazenar resultados
            resultado = {
                'aresta': (u, v),
                'distancia': dist,
                'edge_betweenness': edge_bet,
                'componentes_antes': num_componentes_antes,
                'componentes_depois': num_componentes_depois,
                'is_conexo_antes': is_conexo_antes,
                'is_conexo_depois': is_conexo_depois,
                'tamanhos_componentes': sorted(tamanhos, reverse=True),
                'nos_isolados': menor_componente,
                'aumentos_distancia': aumentos,
                'pares_desconectados': sem_caminho
            }
            resultados_simulacoes.append(resultado)

        print("\n" + "=" * 70)
        return resultados_simulacoes

    def visualizar_impacto(self, aresta, salvar=True, mostrar=False):
        """
        Cria visualização comparativa antes/depois da remoção de uma aresta.

        Args:
            aresta: Tupla (u, v) da aresta a remover
            salvar: Se True, salva a figura
            mostrar: Se True, exibe a figura
        """
        print("\n" + "=" * 70)
        print("GERANDO VISUALIZAÇÃO DE IMPACTO")
        print("=" * 70)

        # Criar cópia do grafo e remover aresta
        grafo_modificado = self.grafo.copy()
        u, v = aresta
        grafo_modificado.remove_edge(u, v)

        # Criar figura com 2 subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 8))

        pos = self.coordenadas

        # ===== VISUALIZAÇÃO 1: ANTES DA REMOÇÃO =====
        print("\n[1/2] Visualizando grafo original...")

        # Desenhar arestas normais
        arestas_normais = [(a, b) for a, b in self.grafo.edges()
                          if (a, b) != aresta and (b, a) != aresta]

        nx.draw_networkx_edges(
            self.grafo, pos,
            edgelist=arestas_normais,
            alpha=0.3,
            width=0.5,
            edge_color='gray',
            ax=ax1
        )

        # Destacar aresta a ser removida
        nx.draw_networkx_edges(
            self.grafo, pos,
            edgelist=[aresta],
            alpha=1.0,
            width=4.0,
            edge_color='red',
            ax=ax1,
            label='Ponte a ser removida'
        )

        # Desenhar nós
        nx.draw_networkx_nodes(
            self.grafo, pos,
            node_color='lightblue',
            node_size=50,
            alpha=0.6,
            ax=ax1
        )

        # Destacar nós da ponte
        nx.draw_networkx_nodes(
            self.grafo, pos,
            nodelist=[u, v],
            node_color='red',
            node_size=150,
            alpha=1.0,
            ax=ax1
        )

        ax1.set_title(f'ANTES da Remoção\nPonte: {u}-{v}',
                     fontsize=14, fontweight='bold')
        ax1.set_xlabel('Coordenada X', fontsize=11)
        ax1.set_ylabel('Coordenada Y', fontsize=11)
        ax1.grid(True, alpha=0.3)
        ax1.set_aspect('equal')
        ax1.legend(loc='upper right')

        print("      ✓ Concluído")

        # ===== VISUALIZAÇÃO 2: DEPOIS DA REMOÇÃO =====
        print("[2/2] Visualizando grafo modificado...")

        # Identificar componentes
        componentes = list(nx.connected_components(grafo_modificado))
        cores_componentes = plt.cm.Set3(np.linspace(0, 1, len(componentes)))

        # Colorir nós por componente
        node_colors = []
        for node in grafo_modificado.nodes():
            for idx, comp in enumerate(componentes):
                if node in comp:
                    node_colors.append(cores_componentes[idx])
                    break

        # Desenhar arestas
        nx.draw_networkx_edges(
            grafo_modificado, pos,
            alpha=0.3,
            width=0.5,
            edge_color='gray',
            ax=ax2
        )

        # Desenhar nós coloridos por componente
        nx.draw_networkx_nodes(
            grafo_modificado, pos,
            node_color=node_colors,
            node_size=50,
            alpha=0.8,
            ax=ax2
        )

        # Destacar nós que estavam conectados pela ponte
        nx.draw_networkx_nodes(
            grafo_modificado, pos,
            nodelist=[u, v],
            node_color='red',
            node_size=150,
            alpha=1.0,
            ax=ax2,
            edgecolors='black',
            linewidths=2
        )

        num_comp = nx.number_connected_components(grafo_modificado)
        ax2.set_title(f'DEPOIS da Remoção\n{num_comp} componente(s) conexo(s)',
                     fontsize=14, fontweight='bold')
        ax2.set_xlabel('Coordenada X', fontsize=11)
        ax2.set_ylabel('Coordenada Y', fontsize=11)
        ax2.grid(True, alpha=0.3)
        ax2.set_aspect('equal')

        print("      >> Concluido")

        # Informações
        info_text = f"Ponte removida: {u}-{v} | "
        info_text += f"Componentes: {nx.number_connected_components(self.grafo)} -> {num_comp}"
        fig.text(0.5, 0.02, info_text, ha='center', fontsize=10,
                style='italic', bbox=dict(boxstyle='round', facecolor='orange', alpha=0.5))

        plt.tight_layout(rect=[0, 0.03, 1, 0.97])

        # Salvar figura
        if salvar:
            caminho_saida = Path(__file__).parent.parent / 'resultados' / 'graficos'
            caminho_saida.mkdir(parents=True, exist_ok=True)
            arquivo_saida = caminho_saida / f'05_impacto_remocao_ponte_{u}_{v}.png'
            plt.savefig(arquivo_saida, dpi=300, bbox_inches='tight')
            print(f"\n>> Figura salva em: {arquivo_saida}")

        if mostrar:
            plt.show()
        else:
            plt.close()

        print("=" * 70)

    def gerar_relatorio(self, resultados_caminhos, resultados_simulacoes):
        """
        Gera relatório da análise de impacto.

        Args:
            resultados_caminhos: Lista de dicionários com resultados de caminhos mínimos
            resultados_simulacoes: Lista de dicionários com resultados das simulações
        """
        caminho_saida = Path(__file__).parent.parent / 'resultados'
        caminho_saida.mkdir(parents=True, exist_ok=True)
        arquivo_saida = caminho_saida / '04_relatorio_analise_impacto.txt'

        # Calcular betweenness centrality dos nós para seção 2.5
        betweenness_centrality = nx.betweenness_centrality(self.grafo, weight='weight')

        with open(arquivo_saida, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("RELATÓRIO DE ANÁLISE DE CAMINHOS MÍNIMOS E SIMULAÇÃO DE IMPACTO\n")
            f.write("Malha Viária de Brasília - Projeto de Teoria dos Grafos\n")
            f.write("=" * 80 + "\n\n")

            f.write("1. ANÁLISE DE CAMINHOS MÍNIMOS (DIJKSTRA)\n")
            f.write("-" * 80 + "\n\n")

            f.write("   Algoritmo: Dijkstra (1959) - Caminhos mínimos ponderados\n")
            f.write("   Ponderação: Distâncias reais em metros\n\n")

            f.write("   Rotas Estratégicas Analisadas:\n\n")
            f.write(f"   {'#':<4} {'Origem':<10} {'Destino':<10} {'Descrição':<15} {'Dist (m)':<12} {'Dist (km)':<12} {'Nós':<8}\n")
            f.write("   " + "-" * 75 + "\n")

            for idx, r in enumerate(resultados_caminhos, 1):
                f.write(f"   {idx:<4} {r['origem']:<10} {r['destino']:<10} {r['descricao']:<15} "
                       f"{r['distancia']:<12.2f} {r['distancia']/1000:<12.2f} {r['num_nos']:<8}\n")

            if resultados_caminhos:
                distancias = [r['distancia'] for r in resultados_caminhos]
                f.write("\n   Estatísticas:\n")
                f.write(f"   • Distância média:     {np.mean(distancias):.2f} m ({np.mean(distancias)/1000:.2f} km)\n")
                f.write(f"   • Distância mínima:    {np.min(distancias):.2f} m ({np.min(distancias)/1000:.2f} km)\n")
                f.write(f"   • Distância máxima:    {np.max(distancias):.2f} m ({np.max(distancias)/1000:.2f} km)\n")

            f.write("\n2. ELEMENTOS CRÍTICOS DA REDE\n")
            f.write("-" * 80 + "\n\n")

            pontes = list(nx.bridges(self.grafo))
            pontos_art = list(nx.articulation_points(self.grafo))

            f.write(f"   Total de pontes (arestas críticas):           {len(pontes)}\n")
            f.write(f"   Percentual de pontes:                         {(len(pontes)/self.grafo.number_of_edges())*100:.1f}%\n")
            f.write(f"   Total de pontos de articulação (nós críticos): {len(pontos_art)}\n")
            f.write(f"   Percentual de pontos de articulação:          {(len(pontos_art)/self.grafo.number_of_nodes())*100:.1f}%\n")

            # ===== SEÇÃO 2.5: PONTE SELECIONADA PARA SIMULAÇÃO =====
            if resultados_simulacoes:
                ponte_principal = resultados_simulacoes[0]
                u, v = ponte_principal['aresta']
                edge_bet = ponte_principal['edge_betweenness']

                f.write("\n2.5 PONTE SELECIONADA PARA SIMULAÇÃO\n")
                f.write("-" * 80 + "\n\n")
                f.write(f"   Ponte selecionada:        {u}-{v}\n")
                f.write(f"   Critério de seleção:      Maior Edge Betweenness entre pontes\n\n")

                coord_u = self.coordenadas.get(u, (0, 0))
                coord_v = self.coordenadas.get(v, (0, 0))
                dist_ponte = ponte_principal['distancia']
                bet_u = betweenness_centrality.get(u, 0)
                bet_v = betweenness_centrality.get(v, 0)

                f.write(f"   Características:\n")
                f.write(f"   • Nó 1:                   {u} ({coord_u[0]:.2f}, {coord_u[1]:.2f})\n")
                f.write(f"   • Nó 2:                   {v} ({coord_v[0]:.2f}, {coord_v[1]:.2f})\n")
                f.write(f"   • Distância:              {dist_ponte:.2f} m\n")
                f.write(f"   • Edge Betweenness:       {edge_bet:.4f} (ranking: 1º de {len(pontes)})\n")
                f.write(f"   • Betweenness nó {u}:      {bet_u:.4f}\n")
                f.write(f"   • Betweenness nó {v}:      {bet_v:.4f}\n\n")

            f.write("3. SIMULAÇÃO DE IMPACTO\n")
            f.write("-" * 80 + "\n\n")

            # ===== SEÇÃO 3.1: RESULTADOS QUANTITATIVOS =====
            if resultados_simulacoes:
                ponte_principal = resultados_simulacoes[0]
                u, v = ponte_principal['aresta']

                f.write(f"   Cenário simulado: Remoção da ponte {u}-{v} (maior Edge Betweenness)\n\n")

                f.write("3.1 RESULTADOS QUANTITATIVOS DA SIMULAÇÃO\n\n")
                f.write("   ANTES DA REMOÇÃO:\n")
                f.write(f"   • Número de componentes conexos:      {ponte_principal['componentes_antes']}\n")
                f.write(f"   • Número de nós alcançáveis:          {self.grafo.number_of_nodes()}\n")
                f.write(f"   • Grafo conexo:                       {'SIM' if ponte_principal['is_conexo_antes'] else 'NÃO'}\n\n")

                f.write(f"   DEPOIS DA REMOÇÃO DA PONTE {u}-{v}:\n")
                f.write(f"   • Número de componentes conexos:      {ponte_principal['componentes_depois']}\n")
                f.write(f"   • Grafo conexo:                       {'SIM' if ponte_principal['is_conexo_depois'] else 'NÃO'}\n\n")

                if ponte_principal['componentes_depois'] > 1:
                    f.write("   TAMANHO DOS COMPONENTES:\n")
                    for i, tamanho in enumerate(ponte_principal['tamanhos_componentes'], 1):
                        percentual = (tamanho / self.grafo.number_of_nodes()) * 100
                        f.write(f"   • Componente {i}: {tamanho} nós ({percentual:.1f}%)\n")

                    f.write(f"\n   NÓS NO COMPONENTE MENOR:\n")
                    f.write(f"   {ponte_principal['nos_isolados']}\n\n")

                f.write("   IMPACTO NAS DISTÂNCIAS:\n")
                if ponte_principal['aumentos_distancia']:
                    f.write(f"   • Número de pares de nós testados:    Amostra estratégica\n")
                    f.write(f"   • Pares com aumento de distância:     {len(ponte_principal['aumentos_distancia'])}\n")
                    f.write(f"   • Aumento médio de distância:         {np.mean(ponte_principal['aumentos_distancia']):.1f}%\n")
                    f.write(f"   • Aumento máximo de distância:        {np.max(ponte_principal['aumentos_distancia']):.1f}%\n")

                if ponte_principal['pares_desconectados'] > 0:
                    f.write(f"   • Pares completamente desconectados:  {ponte_principal['pares_desconectados']}\n")

                if not ponte_principal['aumentos_distancia'] and ponte_principal['pares_desconectados'] > 0:
                    f.write(f"   • Aumento médio de distância:         N/A (pares desconectados)\n")
                    f.write(f"   • Aumento máximo de distância:        ∞ (sem caminho alternativo)\n\n")

                # ===== SEÇÃO 3.2: COMPARAÇÃO COM OUTRAS PONTES =====
                if len(resultados_simulacoes) > 1:
                    f.write("3.2 COMPARAÇÃO COM OUTRAS PONTES SIMULADAS\n\n")

                    for i in range(1, min(3, len(resultados_simulacoes))):
                        sim = resultados_simulacoes[i]
                        u2, v2 = sim['aresta']
                        f.write(f"   Ponte {u2}-{v2} (ranking Edge Betweenness: {i+1}º):\n")
                        f.write(f"   • Edge Betweenness:       {sim['edge_betweenness']:.4f}\n")
                        f.write(f"   • Componentes após remoção: {sim['componentes_depois']}\n")
                        if sim['componentes_depois'] > 1:
                            for j, tamanho in enumerate(sim['tamanhos_componentes'], 1):
                                perc = (tamanho / self.grafo.number_of_nodes()) * 100
                                f.write(f"   • Componente {j}:          {tamanho} nós ({perc:.1f}%)\n")
                        f.write("\n")
            else:
                f.write("   Sem resultados de simulação disponíveis.\n\n")

            f.write("4. REFERÊNCIAS\n")
            f.write("-" * 80 + "\n")
            f.write("   • Dijkstra, E. W. (1959). A note on two problems in connexion with graphs.\n")
            f.write("     Numerische Mathematik, 1, 269-271.\n")
            f.write("   • Derrible, S., & Kennedy, C. (2010). The complexity and robustness of\n")
            f.write("     metro networks. Physica A, 389(17), 3678-3691.\n\n")

            f.write("=" * 80 + "\n")

        print(f"\n>> Relatorio salvo em: {arquivo_saida}")


def main():
    """
    Função principal para execução da análise de impacto.
    """
    # Caminhos dos arquivos
    base_path = Path(__file__).parent.parent
    caminho_net = base_path / 'base_conhecimento_projeto' / 'brasilia.net'
    caminho_edge_info = base_path / 'base_conhecimento_projeto' / 'brasilia_edge_info.txt'

    # Criar analisador
    analisador = AnalisadorImpacto(caminho_net, caminho_edge_info)

    # Executar análise
    analisador.carregar_dados()

    # Análise de caminhos mínimos
    resultados_caminhos = analisador.analisar_caminhos_minimos()

    # Simulação de impacto
    resultados_simulacoes = analisador.simular_remocao_ponte(top_n=3)

    # Visualizar impacto da ponte mais crítica
    if resultados_simulacoes:
        ponte_critica = resultados_simulacoes[0]['aresta']
        analisador.visualizar_impacto(ponte_critica, salvar=True, mostrar=False)

    # Gerar relatório
    analisador.gerar_relatorio(resultados_caminhos, resultados_simulacoes)

    print("\n" + "=" * 70)
    print(">> ANALISE DE IMPACTO CONCLUIDA COM SUCESSO")
    print("=" * 70)
    print("\nArquivos gerados:")
    print("   - resultados/graficos/05_impacto_remocao_ponte_*.png")
    print("   - resultados/04_relatorio_analise_impacto.txt")
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
