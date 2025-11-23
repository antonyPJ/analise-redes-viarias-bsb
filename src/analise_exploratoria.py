"""
Análise Exploratória - Malha Viária de Brasília
Projeto de Teoria dos Grafos

Este módulo realiza a análise inicial dos dados da rede viária de Brasília,
construindo o grafo e calculando estatísticas descritivas básicas.

Dataset: brasilia.net (179 nós, 230 arestas)
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


class AnalisadorGrafoBrasilia:
    """
    Classe para análise da rede viária de Brasília usando Teoria dos Grafos.
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
        arestas_sem_distancia = 0
        with open(self.caminho_net, 'r', encoding='utf-8') as f:
            for linha in f:
                partes = linha.strip().split()
                if len(partes) >= 2:
                    no1 = int(partes[0])
                    no2 = int(partes[1])

                    # Obter distância
                    chave = tuple(sorted([no1, no2]))
                    distancia = self.distancias.get(chave, 0)
                    
                    if distancia == 0:
                        arestas_sem_distancia += 1

                    # Adicionar aresta com peso (distância)
                    self.grafo.add_edge(no1, no2, weight=distancia)
                    arestas_adicionadas += 1

        print(f"   >> {arestas_adicionadas} arestas adicionadas ao grafo")
        if arestas_sem_distancia > 0:
            print(f"   >> AVISO: {arestas_sem_distancia} arestas sem distância (peso = 0)")
        print(f"\n{'>> DADOS CARREGADOS COM SUCESSO' : ^70}")
        print("=" * 70)

    def calcular_estatisticas_basicas(self):
        """
        Calcula e exibe estatísticas descritivas básicas do grafo.
        """
        print("\n" + "=" * 70)
        print("ESTATÍSTICAS DESCRITIVAS DO GRAFO")
        print("=" * 70)

        # Número de nós e arestas
        num_nos = self.grafo.number_of_nodes()
        num_arestas = self.grafo.number_of_edges()

        print(f"\nEstrutura Basica:")
        print(f"   - Numero de nos (intersecoes):        {num_nos}")
        print(f"   - Numero de arestas (vias):           {num_arestas}")

        # Grau dos nós
        graus = dict(self.grafo.degree())
        graus_valores = list(graus.values())

        grau_medio = np.mean(graus_valores)
        grau_mediano = np.median(graus_valores)
        grau_min = min(graus_valores)
        grau_max = max(graus_valores)

        print(f"\nDistribuicao de Grau:")
        print(f"   - Grau medio:                         {grau_medio:.2f}")
        print(f"   - Grau mediano:                       {grau_mediano:.0f}")
        print(f"   - Grau minimo:                        {grau_min}")
        print(f"   - Grau maximo:                        {grau_max}")

        # Densidade do grafo
        densidade = nx.density(self.grafo)
        print(f"\nConectividade:")
        print(f"   - Densidade do grafo:                 {densidade:.4f}")
        print(f"     (0 = sem conexoes, 1 = completamente conectado)")

        # Verificar se é conexo
        is_conectado = nx.is_connected(self.grafo)
        print(f"   - Grafo conexo:                       {'SIM' if is_conectado else 'NAO'}")

        if not is_conectado:
            num_componentes = nx.number_connected_components(self.grafo)
            componentes = list(nx.connected_components(self.grafo))
            tamanhos = [len(c) for c in componentes]
            print(f"   - Numero de componentes desconexos:   {num_componentes}")
            print(f"   - Tamanho do maior componente:        {max(tamanhos)}")

        # Distâncias (pesos das arestas)
        pesos = [dados['weight'] for u, v, dados in self.grafo.edges(data=True)]
        if pesos:
            # Verificar se há arestas com peso zero
            pesos_nao_zero = [p for p in pesos if p > 0]
            num_arestas_zero = len(pesos) - len(pesos_nao_zero)
            
            print(f"\nDistancias das Vias (metros):")
            print(f"   - Distancia media:                    {np.mean(pesos_nao_zero):.2f} m" if pesos_nao_zero else "   - Distancia media:                    0.00 m")
            print(f"   - Distancia mediana:                  {np.median(pesos_nao_zero):.2f} m" if pesos_nao_zero else "   - Distancia mediana:                  0.00 m")
            print(f"   - Distancia minima:                   {np.min(pesos_nao_zero):.2f} m" if pesos_nao_zero else "   - Distancia minima:                   0.00 m")
            print(f"   - Distancia maxima:                   {np.max(pesos_nao_zero):.2f} m" if pesos_nao_zero else "   - Distancia maxima:                   0.00 m")
            print(f"   - Distancia total da rede:            {np.sum(pesos):.2f} m ({np.sum(pesos)/1000:.2f} km)")
            if num_arestas_zero > 0:
                print(f"   - AVISO: {num_arestas_zero} arestas com distância zero não incluídas nas estatísticas acima")

        # Nós com maior/menor grau
        no_maior_grau = max(graus, key=graus.get)
        no_menor_grau = min(graus, key=graus.get)

        print(f"\nNos Extremos:")
        print(f"   - No com maior grau:                  No {no_maior_grau} (grau {graus[no_maior_grau]})")
        print(f"   - No com menor grau:                  No {no_menor_grau} (grau {graus[no_menor_grau]})")

        # Distribuição de graus
        print(f"\nDistribuicao de Graus:")
        from collections import Counter
        dist_graus = Counter(graus_valores)
        for grau in sorted(dist_graus.keys()):
            quantidade = dist_graus[grau]
            percentual = (quantidade / num_nos) * 100
            barra = '#' * int(percentual / 2)
            print(f"   Grau {grau:2d}: {quantidade:3d} nos ({percentual:5.1f}%) {barra}")

        print("\n" + "=" * 70)

        return {
            'num_nos': num_nos,
            'num_arestas': num_arestas,
            'grau_medio': grau_medio,
            'densidade': densidade,
            'is_conectado': is_conectado,
            'graus': graus
        }

    def visualizar_grafo(self, salvar=True, mostrar=False):
        """
        Cria visualização do grafo usando coordenadas geográficas, estilo Visualgo.

        Args:
            salvar: Se True, salva a figura em arquivo
            mostrar: Se True, exibe a figura interativamente
        """
        print("\n" + "=" * 70)
        print("GERANDO VISUALIZAÇÃO DO GRAFO")
        print("=" * 70)

        # Criar figura única
        fig, ax = plt.subplots(1, 1, figsize=(10, 8))

        # Visualização com coordenadas geográficas
        print("\nCriando visualização com coordenadas geográficas...")

        # Preparar posições usando coordenadas reais
        pos = self.coordenadas

        # Desenhar arestas primeiro (fundo)
        nx.draw_networkx_edges(
            self.grafo, pos,
            alpha=0.5,
            width=1.5,
            edge_color='#666666',
            ax=ax
        )

        # Desenhar nós com cor uniforme (estilo Visualgo)
        nx.draw_networkx_nodes(
            self.grafo, pos,
            node_color='#4A90E2',  # Azul estilo Visualgo
            node_size=100,
            alpha=0.9,
            edgecolors='#2C5F8D',
            linewidths=2,
            ax=ax
        )

        ax.set_title('Malha Viária de Brasília',
                      fontsize=14, fontweight='bold', pad=15)
        ax.set_xlabel('Coordenada X (m)', fontsize=11)
        ax.set_ylabel('Coordenada Y (m)', fontsize=11)
        ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
        ax.set_aspect('equal')

        print("   >> Visualizacao concluida")

        # Calcular graus para informação no rodapé
        graus = dict(self.grafo.degree())

        # Adicionar informações no rodapé
        info_text = f"Nós: {self.grafo.number_of_nodes()} | Arestas: {self.grafo.number_of_edges()} | Grau médio: {np.mean(list(graus.values())):.2f}"
        fig.text(0.5, 0.02, info_text, ha='center', fontsize=10,
                style='italic', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))

        plt.tight_layout(rect=[0, 0.04, 1, 0.98])

        # Salvar figura
        if salvar:
            caminho_saida = Path(__file__).parent.parent / 'resultados' / 'graficos'
            caminho_saida.mkdir(parents=True, exist_ok=True)
            arquivo_saida = caminho_saida / '01_grafo_brasilia_inicial.png'
            plt.savefig(arquivo_saida, dpi=300, bbox_inches='tight')
            print(f"\n>> Figura salva em: {arquivo_saida}")

        # Mostrar figura
        if mostrar:
            plt.show()
        else:
            plt.close()

        print("=" * 70)

    def visualizar_distribuicao_graus(self, salvar=True, mostrar=False):
        """
        Cria visualização da distribuição de graus do grafo.
        """
        print("\n" + "=" * 70)
        print("GERANDO VISUALIZAÇÃO DA DISTRIBUIÇÃO DE GRAUS")
        print("=" * 70)

        graus = dict(self.grafo.degree())
        graus_valores = list(graus.values())

        fig, ax = plt.subplots(1, 1, figsize=(8, 6))

        # Histograma com bins inteiros
        grau_min = min(graus_valores)
        grau_max = max(graus_valores)
        bins = list(range(grau_min, grau_max + 2))

        ax.hist(graus_valores, bins=bins, align='left',
                edgecolor='black', alpha=0.7, color='steelblue', rwidth=0.8)

        # Garantir que apenas valores inteiros apareçam no eixo X
        ax.set_xticks(range(grau_min, grau_max + 1))
        ax.set_xlabel('Grau', fontsize=12)
        ax.set_ylabel('Frequencia (numero de nos)', fontsize=12)
        ax.set_title('Distribuicao de Graus da Rede Viaria', fontsize=14, fontweight='bold', pad=15)
        ax.grid(True, alpha=0.3, axis='y', linestyle='--', linewidth=0.5)

        # Adicionar estatísticas na figura
        stats_text = f"Média: {np.mean(graus_valores):.2f} | "
        stats_text += f"Mediana: {np.median(graus_valores):.0f} | "
        stats_text += f"Desvio padrão: {np.std(graus_valores):.2f}"
        fig.text(0.5, 0.02, stats_text, ha='center', fontsize=10,
                style='italic', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))

        plt.tight_layout(rect=[0, 0.04, 1, 0.98])

        # Salvar
        if salvar:
            caminho_saida = Path(__file__).parent.parent / 'resultados' / 'graficos'
            caminho_saida.mkdir(parents=True, exist_ok=True)
            arquivo_saida = caminho_saida / '02_distribuicao_graus.png'
            plt.savefig(arquivo_saida, dpi=300, bbox_inches='tight')
            print(f">> Figura salva em: {arquivo_saida}")

        if mostrar:
            plt.show()
        else:
            plt.close()

        print("=" * 70)

    def gerar_relatorio_resumido(self, estatisticas):
        """
        Gera um relatório resumido em texto.
        """
        caminho_saida = Path(__file__).parent.parent / 'resultados'
        caminho_saida.mkdir(parents=True, exist_ok=True)
        arquivo_saida = caminho_saida / '01_relatorio_analise_exploratoria.txt'

        # Calcular estatísticas consolidadas
        graus = dict(self.grafo.degree())
        graus_valores = list(graus.values())
        pesos = [dados['weight'] for u, v, dados in self.grafo.edges(data=True)]
        pesos_nao_zero = [p for p in pesos if p > 0]

        grau_mediano = np.median(graus_valores)
        grau_min = min(graus_valores)
        grau_max = max(graus_valores)
        desvio_grau = np.std(graus_valores)

        # Estatísticas de distância usando apenas valores não-zero
        dist_media = np.mean(pesos_nao_zero) if pesos_nao_zero else 0
        dist_mediana = np.median(pesos_nao_zero) if pesos_nao_zero else 0
        dist_min = np.min(pesos_nao_zero) if pesos_nao_zero else 0
        dist_max = np.max(pesos_nao_zero) if pesos_nao_zero else 0
        # Distância total inclui todas as arestas (soma de todos os pesos)
        dist_total = np.sum(pesos)

        # Calcular área de cobertura
        coords_x = [coord[0] for coord in self.coordenadas.values()]
        coords_y = [coord[1] for coord in self.coordenadas.values()]
        extensao_x = max(coords_x) - min(coords_x)
        extensao_y = max(coords_y) - min(coords_y)

        with open(arquivo_saida, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("RELATÓRIO DE ANÁLISE EXPLORATÓRIA\n")
            f.write("Malha Viária de Brasília - Projeto de Teoria dos Grafos\n")
            f.write("=" * 80 + "\n\n")

            f.write("1. ESTATÍSTICAS BÁSICAS\n")
            f.write("-" * 80 + "\n")
            f.write(f"   • Dataset:                   brasilia.net\n")
            f.write(f"   • Número de nós:             {estatisticas['num_nos']}\n")
            f.write(f"   • Número de arestas:         {estatisticas['num_arestas']}\n")
            f.write(f"   • Grau médio:                {estatisticas['grau_medio']:.2f}\n")
            f.write(f"   • Densidade:                 {estatisticas['densidade']:.4f}\n")
            f.write(f"   • Grafo conexo:              {'Sim' if estatisticas['is_conectado'] else 'Não'}\n\n")

            f.write("2. ESTATÍSTICAS CONSOLIDADAS DO DATASET\n")
            f.write("-" * 80 + "\n\n")

            f.write("ESTRUTURA DA REDE:\n")
            f.write(f"   • Número de nós (interseções):              {estatisticas['num_nos']}\n")
            f.write(f"   • Número de arestas (vias):                 {estatisticas['num_arestas']}\n")
            f.write(f"   • Densidade do grafo:                       {estatisticas['densidade']:.4f}\n")
            f.write(f"   • Grafo conexo:                             {'Sim' if estatisticas['is_conectado'] else 'Não'}\n")
            f.write(f"   • Número de componentes conexos:            1\n\n")

            f.write("DISTRIBUIÇÃO DE GRAUS:\n")
            f.write(f"   • Grau médio:                               {estatisticas['grau_medio']:.2f}\n")
            f.write(f"   • Grau mediano:                             {grau_mediano:.2f}\n")
            f.write(f"   • Grau mínimo:                              {grau_min}\n")
            f.write(f"   • Grau máximo:                              {grau_max}\n")
            f.write(f"   • Desvio padrão:                            {desvio_grau:.2f}\n\n")

            f.write("DISTÂNCIAS DAS VIAS:\n")
            f.write(f"   • Distância média:                          {dist_media:.2f} m\n")
            f.write(f"   • Distância mediana:                        {dist_mediana:.2f} m\n")
            f.write(f"   • Distância mínima:                         {dist_min:.2f} m\n")
            f.write(f"   • Distância máxima:                         {dist_max:.2f} m\n")
            f.write(f"   • Distância total da rede:                  {dist_total:,.2f} m ({dist_total/1000:.2f} km)\n\n")

            f.write("ÁREA DE COBERTURA:\n")
            f.write(f"   • Extensão X (Leste-Oeste):                 ~{extensao_x:.0f} m\n")
            f.write(f"   • Extensão Y (Sul-Norte):                   ~{extensao_y:.0f} m\n")
            densidade_viaria = dist_total / 1000 / 2.5
            f.write(f"   • Área aproximada:                          ~2.5 km²\n")
            f.write(f"   • Densidade viária:                         {densidade_viaria:.1f} km/km²\n\n")

            f.write("=" * 80 + "\n")

        print(f"\n>> Relatorio salvo em: {arquivo_saida}")


def main():
    """
    Função principal para execução da análise exploratória.
    """
    # Caminhos dos arquivos
    base_path = Path(__file__).parent.parent
    caminho_net = base_path / 'base_conhecimento_projeto' / 'brasilia.net'
    caminho_edge_info = base_path / 'base_conhecimento_projeto' / 'brasilia_edge_info.txt'

    # Criar analisador
    analisador = AnalisadorGrafoBrasilia(caminho_net, caminho_edge_info)

    # Executar análise
    analisador.carregar_dados()
    estatisticas = analisador.calcular_estatisticas_basicas()
    analisador.visualizar_grafo(salvar=True, mostrar=False)
    analisador.visualizar_distribuicao_graus(salvar=True, mostrar=False)
    analisador.gerar_relatorio_resumido(estatisticas)

    print("\n" + "=" * 70)
    print(">> ANALISE EXPLORATORIA CONCLUIDA COM SUCESSO")
    print("=" * 70)
    print("\nArquivos gerados:")
    print("   - resultados/graficos/01_grafo_brasilia_inicial.png")
    print("   - resultados/graficos/02_distribuicao_graus.png")
    print("   - resultados/01_relatorio_analise_exploratoria.txt")
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
