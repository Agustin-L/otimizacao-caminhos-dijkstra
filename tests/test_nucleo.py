# -*- coding: utf-8 -*-
"""Testes automáticos (pytest):  python -m pytest -q"""
import math
import random
import sys
from pathlib import Path

import networkx as nx
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import nucleo
from nucleo import Rede, dijkstra, dijkstra_n2, reconstruir


def grafo_pequeno():
    # 0→1 (4), 0→2 (1), 2→1 (2), 1→3 (1), 2→3 (5), 3→0 (10): rota ótima 0→3 = 0,2,1,3 com custo 4
    g = {0: [(1, 4.0), (2, 1.0)], 1: [(3, 1.0)], 2: [(1, 2.0), (3, 5.0)], 3: [(0, 10.0)]}
    c = {0: (19.9, 50.0), 1: (19.900005, 50.0), 2: (19.9, 50.000005), 3: (19.900008, 50.0)}   # ~0,3 a 0,6 m: pesos >= linha reta
    return g, c


def grafo_aleatorio(n=300, semente=3):
    rng = random.Random(semente)
    pts = {i: (19.8 + rng.random() * 0.3, 49.98 + rng.random() * 0.15) for i in range(n)}
    g = {i: [] for i in range(n)}
    for i in range(n):
        viz = sorted(range(n), key=lambda j: nucleo.haversine_m(*pts[i], *pts[j]))[1:5]
        for j in viz:
            w = nucleo.haversine_m(*pts[i], *pts[j]) * rng.uniform(1.0, 1.3)
            if all(v != j for v, _ in g[i]):
                g[i].append((j, w))
            if all(v != i for v, _ in g[j]):
                g[j].append((i, w))
    return g, pts


def test_dijkstra_exemplo_conhecido():
    g, _ = grafo_pequeno()
    dist, ant, _ = dijkstra(g, 0, 3)
    assert dist[3] == 4.0 and reconstruir(ant, 0, 3) == [0, 2, 1, 3]


def test_grafo_dirigido_respeita_sentido():
    g, _ = grafo_pequeno()
    dist, _, _ = dijkstra(g, 1)
    assert math.isclose(dist[2], 1.0 + 10.0 + 1.0)         # 1 só chega ao 2 por 1→3→0→2


def test_n2_igual_heap():
    g, _ = grafo_aleatorio()
    for s in (0, 17, 250):
        d1, _, _ = dijkstra(g, s)
        d2, _ = dijkstra_n2(g, s)
        assert all(math.isclose(d1[n], d2[n], rel_tol=1e-9) for n in g if d2[n] < math.inf)


def test_contra_networkx():
    g, _ = grafo_aleatorio()
    G = nx.DiGraph()
    G.add_weighted_edges_from([(u, v, w) for u in g for v, w in g[u]])
    rng = random.Random(1)
    for _ in range(60):
        s, t = rng.sample(list(g), 2)
        try:
            ref = nx.dijkstra_path_length(G, s, t)
        except nx.NetworkXNoPath:
            continue
        assert math.isclose(dijkstra(g, s, t)[0][t], ref, rel_tol=1e-9)


def test_astar_otimo_e_expande_menos():
    g, pts = grafo_aleatorio()
    rede = Rede(g, pts)
    rng = random.Random(5)
    exp_d = exp_a = 0
    for _ in range(40):
        s, t = rng.sample(list(g), 2)
        d, a = rede.resolver(s, t, "dijkstra"), rede.resolver(s, t, "astar")
        if d is None:
            continue
        assert math.isclose(d.metros, a.metros, rel_tol=1e-9)
        exp_d += d.expandidos
        exp_a += a.expandidos
    assert exp_a <= exp_d


def test_baseline_nunca_melhor_que_dijkstra():
    g, pts = grafo_aleatorio()
    rede = Rede(g, pts)
    rng = random.Random(9)
    for _ in range(40):
        s, t = rng.sample(list(g), 2)
        d, b = rede.resolver(s, t), rede.menos_trechos(s, t)
        if d and b:
            assert b.metros >= d.metros - 1e-9
            assert len(b.caminho) <= len(d.caminho)        # BFS minimiza o nº de trechos


def test_bloqueio_nao_melhora_rota():
    g, pts = grafo_aleatorio()
    rede = Rede(g, pts)
    base = rede.resolver(0, 150)
    u, v = base.caminho[0], base.caminho[1]
    r = rede.resolver(0, 150, "dijkstra", Rede.ruas_bloqueadas(u, v))
    assert r is None or r.metros >= base.metros - 1e-9


def test_validacao_detecta_peso_negativo_e_nao_conexo():
    g, c = grafo_pequeno()
    assert all(ok for _, ok in nucleo.validar(g, c, levantar=False))
    ruim = {k: list(v) for k, v in g.items()}
    ruim[0][0] = (1, -4.0)
    with pytest.raises(nucleo.ValidacaoErro):
        nucleo.validar(ruim, c)
    with pytest.raises(nucleo.ValidacaoErro):
        nucleo.validar({0: [(1, 5.0)], 1: []}, {0: (19.9, 50.0), 1: (19.900005, 50.0)})


def test_json_ida_e_volta(tmp_path):
    g, c = grafo_pequeno()
    nucleo.salvar_json(g, c, tmp_path / "g.json", {"cidade": "teste"})
    g2, c2, meta = nucleo.carregar_json(tmp_path / "g.json")
    assert meta["cidade"] == "teste" and sorted(g2) == sorted(g)
    assert sorted((u, v) for u in g for v, _ in g[u]) == sorted((u, v) for u in g2 for v, _ in g2[u])


def test_passo_a_passo_coincide_com_dijkstra():
    g, _ = grafo_pequeno()
    passos = nucleo.dijkstra_trace(g, 0, 3)
    assert passos[-1]["dist"][3] == dijkstra(g, 0, 3)[0][3]
