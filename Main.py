
import math
import topohub
import networkx as nx
import matplotlib.pyplot as plt


def carregar_rede():
    """Carrega a topologia SNDlib Polska e monta o grafo."""

    print("Carregando topologia SNDlib Polska...")

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
        origem = id_para_nome[aresta["source"]]
        destino = id_para_nome[aresta["target"]]

        distancia = float(aresta["dist"])

        # Rede não direcionada: permite percorrer nos dois sentidos.
        grafo[origem][destino] = distancia
        grafo[destino][origem] = distancia

    print(f"Rede carregada: {len(grafo)} nós.")

    return grafo


def dijkstra(grafo, origem, destino):
    """Implementação própria do algoritmo de Dijkstra."""

    distancias = {}
    anteriores = {}
    nao_visitados = set(grafo)

    for cidade in grafo:
        distancias[cidade] = math.inf
        anteriores[cidade] = None

    distancias[origem] = 0

    while nao_visitados:

        # Seleciona o nó com menor distância conhecida.
        atual = min(
            nao_visitados,
            key=lambda cidade: distancias[cidade]
        )

        # Não existem mais caminhos possíveis.
        if distancias[atual] == math.inf:
            break

        nao_visitados.remove(atual)

        if atual == destino:
            break

        # Atualiza as distâncias dos vizinhos.
        for vizinha, peso in grafo[atual].items():

            if vizinha in nao_visitados:

                nova_distancia = distancias[atual] + peso

                if nova_distancia < distancias[vizinha]:

                    distancias[vizinha] = nova_distancia
                    anteriores[vizinha] = atual

    # Reconstrução do caminho.
    caminho = []
    cidade = destino

    while cidade is not None:
        caminho.append(cidade)
        cidade = anteriores[cidade]

    caminho.reverse()

    if (
        not caminho
        or caminho[0] != origem
        or distancias[destino] == math.inf
    ):
        return math.inf, []

    return distancias[destino], caminho


def mostrar_grafo(grafo, caminho):
    """Exibe o grafo e destaca a rota encontrada."""

    rede_visual = nx.Graph()

    for cidade, vizinhas in grafo.items():

        rede_visual.add_node(cidade)

        for vizinha, distancia in vizinhas.items():

            rede_visual.add_edge(
                cidade,
                vizinha,
                weight=distancia
            )

    posicoes = nx.spring_layout(
        rede_visual,
        seed=7
    )

    plt.figure(figsize=(14, 9))

    # Desenha todos os nós e conexões.
    nx.draw_networkx(
        rede_visual,
        pos=posicoes,
        with_labels=True,
        node_size=850,
        font_size=8
    )

    # Mostra as distâncias das conexões.
    rotulos = {
        (u, v): f"{dados['weight']:.0f}"
        for u, v, dados in rede_visual.edges(data=True)
    }

    nx.draw_networkx_edge_labels(
        rede_visual,
        pos=posicoes,
        edge_labels=rotulos,
        font_size=7
    )

    # Destaca o menor caminho encontrado.
    if caminho:

        arestas_caminho = list(
            zip(caminho, caminho[1:])
        )

        nx.draw_networkx_edges(
            rede_visual,
            pos=posicoes,
            edgelist=arestas_caminho,
            width=4
        )

    plt.title(
        "Rede SNDlib Polska - Algoritmo de Dijkstra"
    )

    plt.axis("off")
    plt.tight_layout()
    plt.show()


def main():

    try:
        grafo = carregar_rede()

    except Exception as erro:
        print("Erro ao carregar a rede:", erro)
        print("Verifique sua conexão com a internet e as bibliotecas.")
        return

    print("\n========== CIDADES DISPONÍVEIS ==========")

    print(", ".join(sorted(grafo.keys())))

    origem = (
        input("\nCidade de origem [Gdansk]: ").strip()
        or "Gdansk"
    )

    destino = (
        input("Cidade de destino [Warsaw]: ").strip()
        or "Warsaw"
    )

    if origem not in grafo:
        print(f"Origem '{origem}' não encontrada.")
        return

    if destino not in grafo:
        print(f"Destino '{destino}' não encontrado.")
        return

    print("\nExecutando Dijkstra...")

    distancia, caminho = dijkstra(
        grafo,
        origem,
        destino
    )

    if not caminho:
        print("Não existe caminho entre essas cidades.")
        return

    print("\n========== RESULTADO ==========")

    print("Origem:", origem)
    print("Destino:", destino)

    print("Menor caminho:")
    print(" -> ".join(caminho))

    print(f"\nQuantidade de conexões: {len(caminho) - 1}")

    print(f"Distância total: {distancia:.2f} km")

    print("\nExibindo representação gráfica...")

    mostrar_grafo(grafo, caminho)


if __name__ == "__main__":
    main()
