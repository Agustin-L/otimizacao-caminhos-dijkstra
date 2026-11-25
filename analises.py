# -*- coding: utf-8 -*-
"""analises.py — verificação, desempenho, cenário Antes × Depois e sensibilidade."""
import json
import math
import random
import statistics
import time

import networkx as nx
import numpy as np
import pandas as pd

import nucleo
from nucleo import Rede, dijkstra, dijkstra_n2, haversine_m, recorte_bola, reconstruir


# ------------------------------------------------------------------ pares origem–destino
def amostrar_pares(rede, n, semente=2026, min_reta_m=2000):
    rng = random.Random(semente)
    nos = list(rede.grafo)
    pares = []
    while len(pares) < n:
        s, t = rng.sample(nos, 2)
        if haversine_m(*rede.coords[s], *rede.coords[t]) >= min_reta_m:
            pares.append((s, t, f"{s} → {t}"))
    return pares


def pares_de_pontos(rede, pontos, n_max, semente=2026):
    """Pontos reais (DataFrame com nome, lat, lon) -> pares origem–destino (todos contra todos, amostrados)."""
    snaps = [rede.snap(la, lo) for la, lo in zip(pontos.lat, pontos.lon)]
    nos = [s[0] for s in snaps]
    for nome, (_, d) in zip(pontos.nome, snaps):
        if d > 500:
            print(f"  ⚠ ponto '{nome}' está a {d:,.0f} m da malha viária baixada — confira se está dentro da cidade.")
    todos = [(a, b) for a in range(len(pontos)) for b in range(len(pontos)) if a != b and nos[a] != nos[b]]
    random.Random(semente).shuffle(todos)
    return [(nos[a], nos[b], f"{pontos.nome.iloc[a]} → {pontos.nome.iloc[b]}") for a, b in todos[:n_max]]


# ------------------------------------------------------------------ verificação (oráculo: NetworkX)
def verificar_contra_networkx(rede, n=200, semente=7):
    """Compara Dijkstra e A* (nossos) com o NetworkX em n pares; confere também a validade do caminho."""
    G = nx.DiGraph()
    G.add_weighted_edges_from([(u, v, w) for (u, v), w in rede.peso.items()])
    rng = random.Random(semente)
    nos = list(rede.grafo)
    for _ in range(n):
        s, t = rng.sample(nos, 2)
        ref = nx.dijkstra_path_length(G, s, t, weight="weight")
        for met in ("dijkstra", "astar"):
            r = rede.resolver(s, t, met)
            assert math.isclose(r.metros, ref, rel_tol=1e-9, abs_tol=1e-6), (met, s, t, r.metros, ref)
            assert r.caminho[0] == s and r.caminho[-1] == t and len(set(r.caminho)) == len(r.caminho)
    return n


# ------------------------------------------------------------------ desempenho
def _med(f, rep=1):
    ts = []
    for _ in range(rep):
        t0 = time.perf_counter()
        f()
        ts.append(time.perf_counter() - t0)
    return statistics.median(ts)


def benchmark_pares(rede, pares):
    dij = [rede.resolver(s, t, "dijkstra") for s, t, _ in pares]
    ast = [rede.resolver(s, t, "astar") for s, t, _ in pares]
    G = nx.DiGraph()
    G.add_weighted_edges_from([(u, v, w) for (u, v), w in rede.peso.items()])
    t_nx = statistics.mean(_med(lambda s=s, t=t: nx.dijkstra_path_length(G, s, t)) for s, t, _ in pares[:20])
    s0 = pares[0][0]
    return dict(
        t_todos_ms=_med(lambda: dijkstra(rede.grafo, s0), 3) * 1e3,
        t_dij_ms=statistics.mean(r.ms for r in dij), t_ast_ms=statistics.mean(r.ms for r in ast), t_nx_ms=t_nx * 1e3,
        exp_dij=statistics.mean(r.expandidos for r in dij), exp_ast=statistics.mean(r.expandidos for r in ast),
        reducao_pct=100 * (1 - statistics.mean(r.expandidos for r in ast) / statistics.mean(r.expandidos for r in dij)),
    )


def benchmark_escala(rede, centro, tamanhos=(250, 500, 1000, 2000)):
    linhas = []
    for n in tamanhos:
        sg, _ = recorte_bola(rede.grafo, centro, n)
        o = next(iter(sg))
        tn, th = _med(lambda: dijkstra_n2(sg, o), 3), _med(lambda: dijkstra(sg, o), 3)
        linhas.append((len(sg), sum(len(x) for x in sg.values()), tn * 1e3, th * 1e3))
    s0 = next(iter(rede.grafo))
    linhas.append((rede.n_nos, rede.n_arcos, float("nan"), _med(lambda: dijkstra(rede.grafo, s0), 3) * 1e3))
    return pd.DataFrame(linhas, columns=["V", "A", "O(V²) ms", "heap ms"]).round(2)


# ------------------------------------------------------------------ cenário Antes × Depois
def cenario_antes_depois(rede, pares):
    linhas = []
    for s, t, nome in pares:
        a, d = rede.menos_trechos(s, t), rede.resolver(s, t, "dijkstra")
        if a is None or d is None:
            continue
        linhas.append(dict(par=nome, s=s, t=t, m_antes=a.metros, m_depois=d.metros,
                           trechos_antes=len(a.caminho) - 1, trechos_depois=len(d.caminho) - 1,
                           c_antes=a.caminho, c_depois=d.caminho))
    df = pd.DataFrame(linhas)
    df["ganho_m"] = df.m_antes - df.m_depois
    df["ganho_pct"] = 100 * df.ganho_m / df.m_antes
    assert (df.ganho_m > -1e-6).all(), "Dijkstra não pode ser pior que outra rota válida"
    return df


def resumo_cenario(df, vel_kmh=30.0, custo_km=None):
    ka, kd = df.m_antes.sum() / 1000, df.m_depois.sum() / 1000
    r = dict(km_antes=ka, km_depois=kd, ganho_pct=100 * (ka - kd) / ka, mudaram=int((df.ganho_m > 1e-6).sum()),
             maior_pct=float(df.ganho_pct.max()), maior_m=float(df.ganho_m.max()),
             min_antes=60 * ka / vel_kmh, min_depois=60 * kd / vel_kmh, vel_kmh=vel_kmh)
    if custo_km:
        r.update(custo_antes=ka * custo_km, custo_depois=kd * custo_km, custo_km=custo_km)
    return r


# ------------------------------------------------------------------ sensibilidade
def sensibilidade_bloqueio(rede, s, t):
    """Bloqueia (os dois sentidos de) cada trecho da rota ótima e mede o desvio."""
    base = rede.resolver(s, t, "dijkstra")
    linhas = []
    for u, v in zip(base.caminho, base.caminho[1:]):
        r = rede.resolver(s, t, "dijkstra", Rede.ruas_bloqueadas(u, v))
        d = math.inf if r is None else r.metros
        linhas.append(dict(trecho=f"{u}→{v}", comprimento_m=rede.peso[(u, v)], desvio_m=d - base.metros,
                           desvio_pct=100 * (d - base.metros) / base.metros))
    df = pd.DataFrame(linhas)
    df["ponte"] = ~np.isfinite(df.desvio_m)              # sem alternativa (ex.: rua de acesso sem saída)
    ordenado = pd.concat([df[~df.ponte].sort_values("desvio_m", ascending=False), df[df.ponte]])
    return base, ordenado


def sensibilidade_ruido(rede, pares, sigmas=(0.10, 0.20, 0.30), runs=15, semente=2026):
    rng = random.Random(semente)
    amostra = [(s, t) for s, t, _ in pares]
    base = {(s, t): rede.resolver(s, t, "dijkstra") for s, t in amostra}
    linhas = []
    for sig in sigmas:
        mudou, perda = [], []
        for _ in range(runs):
            ruidoso = {u: [(v, w * rng.uniform(1 - sig, 1 + sig)) for v, w in rede.grafo[u]] for u in rede.grafo}
            for s, t in amostra:
                _, ant, _ = dijkstra(ruidoso, s, t)
                c = reconstruir(ant, s, t)
                mudou.append(tuple(c) != tuple(base[(s, t)].caminho))
                perda.append(100 * (rede.comprimento(c) - base[(s, t)].metros) / base[(s, t)].metros)
        linhas.append((f"±{int(sig*100)}%", 100 * np.mean(mudou), np.mean(perda), np.max(perda)))
    return pd.DataFrame(linhas, columns=["Erro nos pesos", "% de viagens com rota diferente", "Distância extra média (%)", "Pior caso (%)"]).round(2)


# ------------------------------------------------------------------ exportação
def exportar_geojson(rede, caminho, arquivo, propriedades=None):
    feat = {"type": "Feature", "properties": propriedades or {},
            "geometry": {"type": "LineString", "coordinates": [list(rede.coords[n]) for n in caminho]}}
    with open(arquivo, "w", encoding="utf-8") as f:
        json.dump({"type": "FeatureCollection", "features": [feat]}, f, ensure_ascii=False)
