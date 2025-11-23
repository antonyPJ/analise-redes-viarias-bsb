"""
Análise de Redes Viárias - Brasília
Projeto de Teoria dos Grafos - SMAC03

Pipeline completo de análise da malha viária de Brasília utilizando
teoria dos grafos para identificar pontos críticos e avaliar vulnerabilidades.
"""

import sys
import subprocess
from pathlib import Path


def executar_modulo(modulo_path, nome_etapa):
    """
    Executa um módulo de análise como subprocess.

    Args:
        modulo_path: Caminho do módulo Python a executar
        nome_etapa: Nome da etapa para exibição

    Returns:
        int: Código de retorno do processo
    """
    resultado = subprocess.run(
        [sys.executable, str(modulo_path)],
        capture_output=False,
        text=True
    )
    return resultado.returncode


def main():
    """
    Pipeline completo de análise da rede viária de Brasília.

    Executa sequencialmente:
    1. Análise Exploratória - Estatísticas descritivas e visualização inicial
    2. Análise Estrutural - Pontes e pontos de articulação (Tarjan)
    3. Análise de Centralidades - Degree, Betweenness, Closeness
    4. Análise de Impacto - Caminhos mínimos (Dijkstra) e simulações

    Retorna:
        int: 0 se sucesso, 1 se erro
    """
    print("=" * 70)
    print("PIPELINE DE ANALISE DA MALHA VIARIA DE BRASILIA")
    print("Projeto de Teoria dos Grafos - SMAC03")
    print("=" * 70)
    print("\nDataset: 179 nos (intersecoes), 230 arestas (vias)")
    print("Extensao total: 30.91 km")
    print("\nExecutando pipeline completo em 4 etapas...")
    print("=" * 70)

    # Caminhos dos módulos
    base_path = Path(__file__).parent / "src"
    modulos = [
        (base_path / "analise_exploratoria.py", "ANALISE EXPLORATORIA"),
        (base_path / "analise_estrutural.py", "ANALISE ESTRUTURAL"),
        (base_path / "analise_centralidades.py", "ANALISE DE CENTRALIDADES"),
        (base_path / "analise_impacto.py", "ANALISE DE IMPACTO E CAMINHOS MINIMOS"),
    ]

    try:
        for idx, (modulo_path, nome_etapa) in enumerate(modulos, 1):
            print("\n" + "=" * 70)
            print(f"[ETAPA {idx}/4] {nome_etapa}")
            print("=" * 70)

            if idx == 3:
                print(">> ATENCAO: Esta etapa pode levar alguns minutos...")

            codigo_retorno = executar_modulo(modulo_path, nome_etapa)

            if codigo_retorno != 0:
                print(f"\n>> ERRO: Etapa {idx} falhou com codigo {codigo_retorno}")
                return 1

            print(f"\n>> Etapa {idx} concluida")

        # Resumo final
        print("\n" + "=" * 70)
        print("PIPELINE CONCLUIDO COM SUCESSO")
        print("=" * 70)
        print("\nTodos os resultados foram salvos em: resultados/")
        print("\nArquivos gerados:")
        print("  GRAFICOS (resultados/graficos/):")
        print("    - 01_grafo_brasilia_inicial.png")
        print("    - 02_distribuicao_graus.png")
        print("    - 03_pontes_criticas.png")
        print("    - 04_centralidades_heatmaps.png")
        print("    - 05_impacto_remocao_ponte_*.png")
        print("\n  RELATORIOS (resultados/):")
        print("    - 01_relatorio_analise_exploratoria.txt")
        print("    - 02_relatorio_analise_estrutural.txt")
        print("    - 03_relatorio_analise_centralidades.txt")
        print("    - 04_relatorio_analise_impacto.txt")
        print("\n  METRICAS CSV (resultados/):")
        print("    - 03_metricas_nodes_centralidades.csv")
        print("    - 04_metricas_edges_centralidades.csv")
        print("\n" + "=" * 70)

        return 0

    except KeyboardInterrupt:
        print("\n\n>> Pipeline interrompido pelo usuario")
        return 1

    except Exception as e:
        print("\n" + "=" * 70)
        print("ERRO DURANTE EXECUCAO DO PIPELINE")
        print("=" * 70)
        print(f"\nErro: {e}")
        print("\nPara executar analises individuais:")
        print("  python src/analise_exploratoria.py")
        print("  python src/analise_estrutural.py")
        print("  python src/analise_centralidades.py")
        print("  python src/analise_impacto.py")
        print("=" * 70)
        return 1


if __name__ == "__main__":
    sys.exit(main())
