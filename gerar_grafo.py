# -*- coding: utf-8 -*-
"""
gerar_grafo.py — GERAÇÃO DO GRAFO a partir do OpenStreetMap.

Baixa a rede viária (carro) de uma cidade com OSMnx, limpa e valida (maior componente fortemente conexa,
sem laços, sem pesos <= 0, arcos paralelos -> o menor) e grava:
  * dados/krakow.json        — grafo no formato do projeto (lido pelo Main_Krakow.py, sem precisar do OSMnx)
  * assets/rede_krakow.png   — imagem da malha viária
  * dados/krakow_osm.graphml — cache do download (reaproveitado nas próximas execuções)

Uso:
  python gerar_grafo.py                               # baixa Kraków do OSM
  python gerar_grafo.py --cidade "Wrocław, Poland"    # outra cidade
  python gerar_grafo.py --graphml arquivo.graphml     # usa um .graphml já salvo (offline)
"""
import argparse
import sys
from pathlib import Path

import networkx as nx

import locais
import nucleo
import visual


def grafo_de_osm(G):
    """MultiDiGraph do OSMnx -> (grafo dict, coords) com IDs compactos 0..n-1."""
    comp = max(nx.strongly_connected_components(G), key=len)       # toda origem alcança todo destino
    H = G.subgraph(comp)
    ids = {n: i for i, n in enumerate(H.nodes)}
    melhor = {}
    for u, v, d in H.edges(data=True):
        w = float(d.get("length", 0.0))
        if u == v or w <= 0:
            continue
        k = (ids[u], ids[v])
        if k not in melhor or w < melhor[k]:                       # arcos paralelos: fica o menor
            melhor[k] = w
    grafo = {i: [] for i in ids.values()}
    for (a, b), w in melhor.items():
        grafo[a].append((b, w))
    coords = {ids[n]: (float(H.nodes[n]["x"]), float(H.nodes[n]["y"])) for n in H.nodes}
    return grafo, coords


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cidade", default="Kraków, Poland")
    ap.add_argument("--graphml", help="usar este .graphml em vez de baixar")
    ap.add_argument("--saida", default="dados/krakow.json")
    ap.add_argument("--cache", default="dados/krakow_osm.graphml")
    ap.add_argument("--png", default="assets/rede_krakow.png")
    ap.add_argument("--locais", type=int, default=90, help="quantos locais (bairros/pontos de interesse) listar no menu")
    ap.add_argument("--sem-locais", action="store_true", help="não baixar a lista de locais")
    a = ap.parse_args()

    import osmnx as ox
    origem_dados = a.graphml or a.cache
    if Path(origem_dados).is_file():
        print(f"Lendo {origem_dados} ...")
        G = ox.load_graphml(origem_dados)
        fonte = f"arquivo {origem_dados}"
    else:
        print(f"Baixando a rede viária de '{a.cidade}' do OpenStreetMap (1 a 3 min) ...")
        G = ox.graph_from_place(a.cidade, network_type="drive")
        Path(a.cache).parent.mkdir(parents=True, exist_ok=True)
        ox.save_graphml(G, a.cache)
        fonte = f"OpenStreetMap via OSMnx ({a.cidade})"
    print(f"Bruto: {G.number_of_nodes():,} nós · {G.number_of_edges():,} arcos")

    grafo, coords = grafo_de_osm(G)
    for desc, ok in nucleo.validar(grafo, coords, levantar=False):
        print(("  [OK] " if ok else "  [FALHA] ") + desc)
    nucleo.validar(grafo, coords)                                   # levanta erro se algo falhou

    meta = {"cidade": a.cidade, "fonte": fonte, "pesos": "metros (atributo 'length' do OSM)", "dirigido": True}
    nucleo.salvar_json(grafo, coords, a.saida, meta)
    rede = nucleo.Rede(grafo, coords, a.cidade)
    visual.desenhar_rede(rede, a.png)
    if not a.sem_locais:
        print("\nBaixando bairros e pontos de interesse do OSM para a lista de origem/destino ...")
        df_loc = locais.selecionar_locais(locais.baixar_locais(ox, a.cidade), rede, n=a.locais)
        if len(df_loc):
            df_loc.to_csv("dados/locais.csv", index=False, encoding="utf-8")
            print(f"  {len(df_loc)} locais gravados em dados/locais.csv "
                  f"({(df_loc.tipo == 'bairro/distrito').sum()} bairros/distritos, {(df_loc.tipo == 'ponto de interesse').sum()} pontos de interesse)")
        else:
            print("  nenhum local obtido; o menu usará só a lista curta pontos_krakow.csv")
    print(f"\nGrafo final: {rede.n_nos:,} nós · {rede.n_arcos:,} arcos · {rede.pct_mao_unica():.1f}% de arcos em mão única")
    print(f"Gravado em {a.saida} e {a.png}")


if __name__ == "__main__":
    sys.exit(main())
