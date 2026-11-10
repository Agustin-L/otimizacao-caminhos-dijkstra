"""
PROJETO: Caminho mínimo em uma rede de telecomunicações
ALGORITMO: Dijkstra
FONTE DOS DADOS: TopoHub - topologia SNDlib Polska

O Dijkstra abaixo foi implementado pelo grupo.
NetworkX é usado somente para desenhar o grafo, não para calcular a rota.
"""

import math
import topohub
import networkx as nx
import matplotlib.pyplot as plt


def carregar_rede():
    """Carrega a topologia pública e monta um dicionário de conexões."""
    topologia = topohub.get("sndlib/polska")

    nos = topologia["nodes"]
    arestas = topologia["edges"]

    id_para_nome = {}
    grafo = {}

    for no in nos:
        identificador = no["id"]
        nome = no.get("name", str(identificador))
        id_para_nome[identificador] = nome
        grafo[nome] = {}

    for aresta in arestas:
        origem = id_para_nome.get(aresta["source"], str(aresta["source"]))
        destino = id_para_nome.get(aresta["target"], str(aresta["target"]))
        distancia = float(aresta["dist"])

        # A rede é tratada como não direcionada:
        # se existe ligação A-B, podemos percorrê-la nos dois sentidos.
        grafo[origem][destino] = distancia
        grafo[destino][origem] = distancia

    return grafo


def dijkstra(grafo, origem, destino):
    """Retorna a menor distância e o caminho entre origem e destino."""
    distancias = {}
    anteriores = {}
    nao_visitados = set(grafo)

    for cidade in grafo:
        distancias[cidade] = math.inf
        anteriores[cidade] = None

    distancias[origem] = 0

    while nao_visitados:
        # Escolhe a cidade ainda não visitada com menor distância conhecida.
        atual = min(nao_visitados, key=lambda cidade: distancias[cidade])

        # Se todos os caminhos restantes forem infinitos, não há rota.
        if distancias[atual] == math.inf:
            break

        nao_visitados.remove(atual)

        if atual == destino:
            break

        # Verifica se passar pela cidade atual melhora cada vizinha.
        for vizinha, distancia_ligacao in grafo[atual].items():
            if vizinha in nao_visitados:
                nova_distancia = distancias[atual] + distancia_ligacao

                if nova_distancia < distancias[vizinha]:
                    distancias[vizinha] = nova_distancia
                    anteriores[vizinha] = atual

    # Reconstrói o caminho voltando do destino até a origem.
    caminho = []
    cidade = destino

    while cidade is not None:
        caminho.append(cidade)
        cidade = anteriores[cidade]

    caminho.reverse()

    if not caminho or caminho[0] != origem or distancias[destino] == math.inf:
        return math.inf, []

    return distancias[destino], caminho


def mostrar_grafo(grafo, caminho):
    """Desenha a rede e destaca o caminho encontrado pelo nosso Dijkstra."""
    rede_visual = nx.Graph()

    for cidade, vizinhas in grafo.items():
        rede_visual.add_node(cidade)
        for vizinha, distancia in vizinhas.items():
            rede_visual.add_edge(cidade, vizinha, weight=distancia)

    posicoes = nx.spring_layout(rede_visual, seed=7)

    plt.figure(figsize=(12, 8))
    nx.draw_networkx(
        rede_visual,
        pos=posicoes,
        with_labels=True,
        node_size=850,
        font_size=8
    )

    rotulos_distancia = {
        (origem, destino): f"{dados['weight']:.0f}"
        for origem, destino, dados in rede_visual.edges(data=True)
    }
    nx.draw_networkx_edge_labels(
        rede_visual,
        pos=posicoes,
        edge_labels=rotulos_distancia,
        font_size=7
    )

    if caminho:
        arestas_caminho = list(zip(caminho, caminho[1:]))
        nx.draw_networkx_edges(
            rede_visual,
            pos=posicoes,
            edgelist=arestas_caminho,
            width=4
        )

    plt.title("Rede SNDlib Polska - menor caminho encontrado pelo Dijkstra")
    plt.axis("off")
    plt.tight_layout()
    plt.show()


def main():
    grafo = carregar_rede()

    print("\nCIDADES DISPONÍVEIS:")
    print(", ".join(sorted(grafo.keys())))

    origem = input("\nCidade de origem [Gdansk]: ").strip() or "Gdansk"
    destino = input("Cidade de destino [Warsaw]: ").strip() or "Warsaw"

    if origem not in grafo or destino not in grafo:
        print("Cidade não encontrada. Confira os nomes exibidos na lista.")
        return

    distancia, caminho = dijkstra(grafo, origem, destino)

    if not caminho:
        print(f"Não existe caminho entre {origem} e {destino}.")
        return

    print("\nRESULTADO")
    print("Menor caminho:", " -> ".join(caminho))
    print(f"Distância total: {distancia:.2f} km")

    mostrar_grafo(grafo, caminho)


if __name__ == "__main__":
    main()
