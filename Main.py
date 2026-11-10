import json
import math
from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.lines import Line2D

BASE = Path(__file__).resolve().parent
ARQUIVO_DADOS = BASE / "polska.json"
ARQUIVO_MAPA = BASE / "assets" / "mapa_polonia.png"
FATOR_LONGITUDE = math.cos(math.radians(52.0))
LIMITE_MAPA = (
    8.576218338974924,
    14.990071613540623,
    48.886,
    54.956
)


def carregar_rede():
    with ARQUIVO_DADOS.open("r", encoding="utf-8") as arquivo:
        dados = json.load(arquivo)

    grafo = {no["id"]: [] for no in dados["nodes"]}
    nomes = {no["id"]: no["name"] for no in dados["nodes"]}
    posicoes = {
        no["id"]: (no["pos"][0] * FATOR_LONGITUDE, no["pos"][1])
        for no in dados["nodes"]
    }
    arestas = []

    for aresta in dados["edges"]:
        origem = aresta["source"]
        destino = aresta["target"]
        distancia = float(aresta["dist"])
        grafo[origem].append((destino, distancia))
        grafo[destino].append((origem, distancia))
        arestas.append((origem, destino, distancia))

    return grafo, nomes, posicoes, arestas


def dijkstra(grafo, origem, destino):
    distancias = {no: math.inf for no in grafo}
    anteriores = {no: None for no in grafo}
    nao_visitados = set(grafo)
    distancias[origem] = 0

    while nao_visitados:
        atual = min(nao_visitados, key=lambda no: distancias[no])

        if distancias[atual] == math.inf:
            break

        nao_visitados.remove(atual)

        if atual == destino:
            break

        for vizinho, peso in grafo[atual]:
            if vizinho in nao_visitados:
                nova_distancia = distancias[atual] + peso
                if nova_distancia < distancias[vizinho]:
                    distancias[vizinho] = nova_distancia
                    anteriores[vizinho] = atual

    if distancias[destino] == math.inf:
        return None, math.inf

    caminho = []
    atual = destino
    while atual is not None:
        caminho.append(atual)
        atual = anteriores[atual]

    caminho.reverse()
    return caminho, distancias[destino]


def desenhar_grafo(grafo, nomes, posicoes, arestas, caminho=None):
    rede = nx.Graph()
    rede.add_nodes_from(grafo)
    rede.add_weighted_edges_from(arestas)

    fig, ax = plt.subplots(figsize=(15, 11))
    fig.patch.set_facecolor("#f4f7f8")
    ax.set_facecolor("#f4f7f8")

    mapa = plt.imread(ARQUIVO_MAPA)
    ax.imshow(
        mapa,
        extent=LIMITE_MAPA,
        origin="upper",
        aspect="auto",
        interpolation="bilinear",
        zorder=0
    )

    nx.draw_networkx_edges(
        rede, posicoes, ax=ax,
        edge_color="#425f70", width=2.0, alpha=0.9
    )

    arestas_caminho = set()
    if caminho:
        arestas_caminho = {
            frozenset((caminho[i], caminho[i + 1]))
            for i in range(len(caminho) - 1)
        }

    destacadas = [
        (origem, destino)
        for origem, destino, _ in arestas
        if frozenset((origem, destino)) in arestas_caminho
    ]

    if destacadas:
        nx.draw_networkx_edges(
            rede, posicoes, edgelist=destacadas, ax=ax,
            edge_color="#e32636", width=4.2
        )

    cores = []
    for no in rede.nodes:
        if caminho and no == caminho[0]:
            cores.append("#20bf55")
        elif caminho and no == caminho[-1]:
            cores.append("#ff7043")
        elif caminho and no in caminho:
            cores.append("#ffd43b")
        else:
            cores.append("#62b6d9")

    nx.draw_networkx_nodes(
        rede, posicoes, ax=ax, node_color=cores,
        node_size=820, edgecolors="#183247", linewidths=1.5
    )
    nx.draw_networkx_labels(
        rede, posicoes,
        labels={no: nomes[no] for no in rede.nodes},
        ax=ax, font_size=8, font_weight="bold", font_color="#102b3f"
    )

    for indice, (origem, destino, distancia) in enumerate(arestas):
        x1, y1 = posicoes[origem]
        x2, y2 = posicoes[destino]
        deslocamento = 9 if indice % 2 == 0 else -9
        ax.annotate(
            f"{distancia:.2f} km",
            xy=((x1 + x2) / 2, (y1 + y2) / 2),
            xytext=(0, deslocamento),
            textcoords="offset points",
            ha="center", va="center", fontsize=7.2,
            bbox={"boxstyle": "round,pad=0.18", "fc": "white", "ec": "#9eb4c2", "lw": 0.5, "alpha": 0.96}
        )

    legenda = [
        Line2D([0], [0], color="#e32636", linewidth=3.5, label="Caminho encontrado"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor="#20bf55", markeredgecolor="#183247", markersize=9, label="Origem"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor="#ff7043", markeredgecolor="#183247", markersize=9, label="Destino"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor="#62b6d9", markeredgecolor="#183247", markersize=9, label="Demais pontos")
    ]
    ax.legend(handles=legenda, loc="lower center", bbox_to_anchor=(0.5, -0.075), ncol=4, frameon=True)
    ax.set_title("POLSKA | REDE DE TELECOMUNICAÇÕES", fontsize=17, fontweight="bold", color="#17324d", pad=18)
    ax.text(
        0.5, 1.005,
        "Topologia SNDlib Polska • divisões administrativas da Polônia",
        transform=ax.transAxes, ha="center", fontsize=10, color="#31566e"
    )

    ax.set_xlim(LIMITE_MAPA[0], LIMITE_MAPA[1])
    ax.set_ylim(LIMITE_MAPA[2], LIMITE_MAPA[3])
    ax.set_aspect("equal", adjustable="box")
    ax.axis("off")
    fig.subplots_adjust(top=0.91, bottom=0.12, left=0.06, right=0.94)
    plt.show()


def perguntar_repetir():
    while True:
        resposta = input("Deseja tentar novamente? (s/n): ").strip().casefold()
        if resposta in ("s", "sim"):
            return True
        if resposta in ("n", "nao", "não"):
            return False
        print("Resposta inválida. Digite s para sim ou n para não.")


def selecionar_no(mensagem, mapa_nomes, mapa_ids, grafo):
    while True:
        entrada = input(mensagem).strip()
        no = mapa_nomes.get(entrada.casefold(), mapa_ids.get(entrada))
        if no in grafo:
            return no
        print("Cidade ou ID inválido.")
        if not perguntar_repetir():
            return None


def main():
    try:
        if not ARQUIVO_MAPA.is_file():
            print("Mapa não encontrado. Verifique a pasta assets.")
            return

        grafo, nomes, posicoes, arestas = carregar_rede()
        print("\n===== REDE DE TELECOMUNICAÇÕES - POLSKA =====")
        print(f"Nós: {len(grafo)} | Conexões: {len(arestas)}")

        mapa_nomes = {nome.casefold(): no for no, nome in nomes.items()}
        mapa_ids = {str(no): no for no in grafo}

        while True:
            print("\nCidades disponíveis:")
            for no, nome in sorted(nomes.items(), key=lambda item: item[1]):
                print(f"- {nome} (ID {no})")

            origem = selecionar_no("\nDigite a cidade ou ID de origem: ", mapa_nomes, mapa_ids, grafo)
            if origem is None:
                break

            destino = selecionar_no("Digite a cidade ou ID de destino: ", mapa_nomes, mapa_ids, grafo)
            if destino is None:
                break

            if destino == origem:
                print("Origem e destino não podem ser iguais.")
                if perguntar_repetir():
                    continue
                break

            caminho, distancia = dijkstra(grafo, origem, destino)

            if caminho is None:
                print("\nNão existe caminho entre as cidades informadas.")
            else:
                print("\n===== RESULTADO DO DIJKSTRA =====")
                print(" -> ".join(nomes[no] for no in caminho))
                print(f"Distância total: {distancia:.2f} km")
                print(f"Quantidade de conexões: {len(caminho) - 1}")

            desenhar_grafo(grafo, nomes, posicoes, arestas, caminho)

            if not perguntar_repetir_rota():
                print("Programa encerrado.")
                break

    except FileNotFoundError:
        print("Arquivo polska.json não encontrado. Coloque-o na mesma pasta da main.py.")
    except KeyboardInterrupt:
        print("\nExecução interrompida pelo usuário.")
    except EOFError:
        print("\nEntrada encerrada. Programa finalizado.")
    except Exception as erro:
        print(f"Erro ao executar o projeto: {erro}")


def perguntar_repetir_rota():
    while True:
        resposta = input("\nDeseja calcular outra rota? (s/n): ").strip().casefold()
        if resposta in ("s", "sim"):
            return True
        if resposta in ("n", "nao", "não"):
            return False
        print("Resposta inválida. Digite s para sim ou n para não.")


if __name__ == "__main__":
    main()
