"""
Análise Estrutural - Malha Viária de Brasília
Projeto de Teoria dos Grafos

Este módulo identifica pontos críticos na rede viária usando o algoritmo de Tarjan:
- Pontes (arestas críticas)
- Pontos de articulação (vértices críticos)

Essas estruturas representam vulnerabilidades na malha viária, onde a remoção
pode desconectar a rede ou aumentar significativamente distâncias.
"""

import sys
import io
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# Configurar encoding UTF-8 para saída (compatibilidade Windows)
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


class AnalisadorEstrutural:
    """
    Classe para análise estrutural da rede viária de Brasília.
    Identifica pontos críticos usando algoritmos de Tarjan.
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
        self.pontes = []       # Lista de arestas críticas
        self.pontos_articulacao = []  # Lista de vértices críticos

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

    def identificar_pontes(self):
        """
        Identifica pontes (arestas críticas) no grafo usando algoritmo de Tarjan.

        Pontes são arestas cuja remoção aumenta o número de componentes conexos,
        potencialmente desconectando partes da rede viária.
        """
        print("\n" + "=" * 70)
        print("IDENTIFICANDO PONTES (ARESTAS CRÍTICAS)")
        print("=" * 70)
        print("\nUtilizando: Algoritmo de Tarjan para detecção de pontes")
        print("Definição: Aresta cuja remoção desconecta o grafo\n")

        # Calcular pontes usando NetworkX (implementa Tarjan)
        self.pontes = list(nx.bridges(self.grafo))

        print(f">> Analise concluida")
        print(f"\nRESULTADO: {len(self.pontes)} ponte(s) identificada(s)")

        if len(self.pontes) > 0:
            print("\nPONTES CRITICAS IDENTIFICADAS:")
            print("-" * 70)
            print(f"{'#':<5} {'No 1':<10} {'No 2':<10} {'Distancia (m)':<15}")
            print("-" * 70)

            for idx, (no1, no2) in enumerate(self.pontes, 1):
                chave = tuple(sorted([no1, no2]))
                distancia = self.distancias.get(chave, 0)
                print(f"{idx:<5} {no1:<10} {no2:<10} {distancia:<15.2f}")

            print("-" * 70)

            # Calcular estatísticas das pontes
            distancias_pontes = []
            for no1, no2 in self.pontes:
                chave = tuple(sorted([no1, no2]))
                dist = self.distancias.get(chave, 0)
                distancias_pontes.append(dist)

            if distancias_pontes:
                print(f"\nEstatisticas das Pontes:")
                print(f"   - Distancia media:     {np.mean(distancias_pontes):.2f} m")
                print(f"   - Distancia minima:    {np.min(distancias_pontes):.2f} m")
                print(f"   - Distancia maxima:    {np.max(distancias_pontes):.2f} m")
                print(f"   - Distancia total:     {np.sum(distancias_pontes):.2f} m")
        else:
            print("\n>> Nao ha pontes no grafo (rede altamente conectada)")

        print("=" * 70)

    def identificar_pontos_articulacao(self):
        """
        Identifica pontos de articulação (vértices críticos) usando algoritmo de Tarjan.

        Pontos de articulação são vértices cuja remoção aumenta o número de
        componentes conexos da rede.
        """
        print("\n" + "=" * 70)
        print("IDENTIFICANDO PONTOS DE ARTICULAÇÃO (VÉRTICES CRÍTICOS)")
        print("=" * 70)
        print("\nUtilizando: Algoritmo de Tarjan para detecção de pontos de articulação")
        print("Definição: Vértice cuja remoção desconecta o grafo\n")

        # Calcular pontos de articulação usando NetworkX (implementa Tarjan)
        self.pontos_articulacao = list(nx.articulation_points(self.grafo))

        print(f">> Analise concluida")
        print(f"\nRESULTADO: {len(self.pontos_articulacao)} ponto(s) de articulacao identificado(s)")

        if len(self.pontos_articulacao) > 0:
            print("\nPONTOS DE ARTICULACAO CRITICOS:")
            print("-" * 70)
            print(f"{'#':<5} {'No':<10} {'Grau':<10} {'Coord X':<15} {'Coord Y':<15}")
            print("-" * 70)

            graus = dict(self.grafo.degree())

            for idx, no in enumerate(sorted(self.pontos_articulacao), 1):
                grau = graus[no]
                coord = self.coordenadas.get(no, (0, 0))
                print(f"{idx:<5} {no:<10} {grau:<10} {coord[0]:<15.2f} {coord[1]:<15.2f}")

            print("-" * 70)

            # Estatísticas dos pontos de articulação
            graus_pontos = [graus[no] for no in self.pontos_articulacao]

            print(f"\nEstatisticas dos Pontos de Articulacao:")
            print(f"   - Grau medio:          {np.mean(graus_pontos):.2f}")
            print(f"   - Grau minimo:         {np.min(graus_pontos)}")
            print(f"   - Grau maximo:         {np.max(graus_pontos)}")

            # Percentual de nós críticos
            percentual = (len(self.pontos_articulacao) / self.grafo.number_of_nodes()) * 100
            print(f"   - % de nos criticos:   {percentual:.1f}%")
        else:
            print("\n>> Nao ha pontos de articulacao (rede altamente conectada)")

        print("=" * 70)

    def visualizar_pontos_criticos(self, salvar=True, mostrar=False):
        """
        Cria visualização destacando pontes (arestas críticas).

        Args:
            salvar: Se True, salva a figura em arquivo
            mostrar: Se True, exibe a figura interativamente
        """
        print("\n" + "=" * 70)
        print("GERANDO VISUALIZAÇÃO DAS PONTES (ARESTAS CRÍTICAS)")
        print("=" * 70)

        # Criar figura única
        fig, ax = plt.subplots(1, 1, figsize=(10, 8))

        print("\nVisualizando pontes (arestas críticas)...")

        pos = self.coordenadas

        # Separar arestas normais e pontes
        arestas_normais = [(u, v) for u, v in self.grafo.edges()
                          if (u, v) not in self.pontes and (v, u) not in self.pontes]

        # Desenhar arestas normais (cinza claro)
        nx.draw_networkx_edges(
            self.grafo, pos,
            edgelist=arestas_normais,
            alpha=0.15,
            width=0.5,
            edge_color='gray',
            ax=ax
        )

        # Desenhar pontes (vermelho, destaque)
        if len(self.pontes) > 0:
            nx.draw_networkx_edges(
                self.grafo, pos,
                edgelist=self.pontes,
                alpha=0.9,
                width=2.5,
                edge_color='red',
                ax=ax,
                label=f'{len(self.pontes)} Pontes'
            )

        # Desenhar nós
        nx.draw_networkx_nodes(
            self.grafo, pos,
            node_color='lightblue',
            node_size=40,
            alpha=0.6,
            ax=ax
        )

        # Destacar nós que fazem parte de pontes
        nos_pontes = set()
        for u, v in self.pontes:
            nos_pontes.add(u)
            nos_pontes.add(v)

        if len(nos_pontes) > 0:
            nx.draw_networkx_nodes(
                self.grafo, pos,
                nodelist=list(nos_pontes),
                node_color='darkred',
                node_size=60,
                alpha=0.8,
                ax=ax
            )

        ax.set_title(f'Pontes (Arestas Críticas) - {len(self.pontes)} identificadas',
                     fontsize=14, fontweight='bold', pad=15)
        ax.set_xlabel('Coordenada X (m)', fontsize=11)
        ax.set_ylabel('Coordenada Y (m)', fontsize=11)
        ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
        ax.set_aspect('equal')
        if len(self.pontes) > 0:
            ax.legend(loc='upper right', fontsize=10)

        print("   >> Visualizacao concluida")

        # Adicionar informações no rodapé
        info_text = f"Nos: {self.grafo.number_of_nodes()} | Arestas: {self.grafo.number_of_edges()} | "
        info_text += f"Pontes: {len(self.pontes)} ({len(self.pontes)/self.grafo.number_of_edges()*100:.1f}% das arestas)"
        fig.text(0.5, 0.02, info_text, ha='center', fontsize=10,
                style='italic', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))

        plt.tight_layout(rect=[0, 0.04, 1, 0.98])

        # Salvar figura
        if salvar:
            caminho_saida = Path(__file__).parent.parent / 'resultados' / 'graficos'
            caminho_saida.mkdir(parents=True, exist_ok=True)
            arquivo_saida = caminho_saida / '03_pontes_criticas.png'
            plt.savefig(arquivo_saida, dpi=300, bbox_inches='tight')
            print(f"\n>> Figura salva em: {arquivo_saida}")

        # Mostrar figura
        if mostrar:
            plt.show()
        else:
            plt.close()

        print("=" * 70)

    def gerar_relatorio(self):
        """
        Gera relatório detalhado da análise estrutural em formato texto.
        """
        caminho_saida = Path(__file__).parent.parent / 'resultados'
        caminho_saida.mkdir(parents=True, exist_ok=True)
        arquivo_saida = caminho_saida / '02_relatorio_analise_estrutural.txt'

        with open(arquivo_saida, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("RELATÓRIO DE ANÁLISE ESTRUTURAL\n")
            f.write("Malha Viária de Brasília - Projeto de Teoria dos Grafos\n")
            f.write("=" * 80 + "\n\n")

            f.write("1. METODOLOGIA\n")
            f.write("-" * 80 + "\n")
            f.write("   • Algoritmo: Tarjan (1972)\n")
            f.write("   • Complexidade: O(V + E)\n")
            f.write("   • Implementação: NetworkX\n\n")

            f.write("2. PONTES (ARESTAS CRÍTICAS)\n")
            f.write("-" * 80 + "\n")
            f.write(f"   Total de pontes identificadas: {len(self.pontes)}\n\n")

            if len(self.pontes) > 0:
                f.write("   Listagem detalhada:\n\n")
                f.write(f"   {'#':<5} {'Nó 1':<10} {'Nó 2':<10} {'Distância (m)':<15}\n")
                f.write("   " + "-" * 70 + "\n")

                for idx, (no1, no2) in enumerate(self.pontes, 1):
                    chave = tuple(sorted([no1, no2]))
                    distancia = self.distancias.get(chave, 0)
                    f.write(f"   {idx:<5} {no1:<10} {no2:<10} {distancia:<15.2f}\n")

                # Estatísticas
                distancias_pontes = [self.distancias.get(tuple(sorted([u, v])), 0)
                                    for u, v in self.pontes]
                f.write("\n   Estatísticas:\n")
                f.write(f"   • Distância média das pontes:    {np.mean(distancias_pontes):.2f} m\n")
                f.write(f"   • Distância total das pontes:    {np.sum(distancias_pontes):.2f} m\n")
            else:
                f.write("   Não há pontes no grafo.\n")

            f.write("\n3. PONTOS DE ARTICULAÇÃO (VÉRTICES CRÍTICOS)\n")
            f.write("-" * 80 + "\n")
            f.write(f"   Total de pontos de articulação: {len(self.pontos_articulacao)}\n\n")

            if len(self.pontos_articulacao) > 0:
                f.write("   Listagem detalhada:\n\n")
                f.write(f"   {'#':<5} {'Nó':<10} {'Grau':<10} {'Coord X':<15} {'Coord Y':<15}\n")
                f.write("   " + "-" * 70 + "\n")

                graus = dict(self.grafo.degree())

                for idx, no in enumerate(sorted(self.pontos_articulacao), 1):
                    grau = graus[no]
                    coord = self.coordenadas.get(no, (0, 0))
                    f.write(f"   {idx:<5} {no:<10} {grau:<10} {coord[0]:<15.2f} {coord[1]:<15.2f}\n")

                # Estatísticas
                graus_pontos = [graus[no] for no in self.pontos_articulacao]
                percentual = (len(self.pontos_articulacao) / self.grafo.number_of_nodes()) * 100

                f.write("\n   Estatísticas:\n")
                f.write(f"   • Grau médio dos pontos críticos:   {np.mean(graus_pontos):.2f}\n")
                f.write(f"   • Grau máximo:                      {np.max(graus_pontos)}\n")
                f.write(f"   • % de nós críticos:                {percentual:.1f}%\n")
            else:
                f.write("   Não há pontos de articulação no grafo.\n")

            f.write("\n4. REFERÊNCIAS\n")
            f.write("-" * 80 + "\n")
            f.write("   - Tarjan, R. (1972). Depth-first search and linear graph algorithms.\n")
            f.write("     SIAM Journal on Computing, 1(2), 146-160.\n\n")

            f.write("=" * 80 + "\n")

        print(f"\n>> Relatorio salvo em: {arquivo_saida}")


def main():
    """
    Função principal para execução da análise estrutural.
    """
    # Caminhos dos arquivos
    base_path = Path(__file__).parent.parent
    caminho_net = base_path / 'base_conhecimento_projeto' / 'brasilia.net'
    caminho_edge_info = base_path / 'base_conhecimento_projeto' / 'brasilia_edge_info.txt'

    # Criar analisador
    analisador = AnalisadorEstrutural(caminho_net, caminho_edge_info)

    # Executar análise
    analisador.carregar_dados()
    analisador.identificar_pontes()
    analisador.identificar_pontos_articulacao()
    analisador.visualizar_pontos_criticos(salvar=True, mostrar=False)
    analisador.gerar_relatorio()

    print("\n" + "=" * 70)
    print(">> ANALISE ESTRUTURAL CONCLUIDA COM SUCESSO")
    print("=" * 70)
    print("\nArquivos gerados:")
    print("   - resultados/graficos/03_pontes_criticas.png")
    print("   - resultados/02_relatorio_analise_estrutural.txt")
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
