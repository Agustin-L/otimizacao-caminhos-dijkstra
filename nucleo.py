# -*- coding: utf-8 -*-
"""
nucleo.py — núcleo do projeto (sem dependência de OSMnx).

Contém, implementados do zero:
  * Dijkstra com fila de prioridade (heap), Dijkstra O(V²) didático, A* (heurística haversine) e BFS por nº de trechos;
  * validação automática das restrições do modelo;
  * classe Rede (grafo + coordenadas + utilidades) e leitura/gravação do grafo em JSON.

O NetworkX NÃO é usado aqui para calcular rotas (só nos testes, como oráculo de conferência).
"""
from __future__ import annotations

import heapq
import json
import math
import time
from collections import deque
from dataclasses import dataclass
from pathlib import Path

import numpy as np

R_TERRA_M = 6371008.8


def haversine_m(lon1, lat1, lon2, lat2):
    """Distância em linha reta (metros) entre dois pontos (lon, lat em graus)."""
    p1, p2 = math.radians(lat1), math.radians(lat2)
    a = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(math.radians(lon2 - lon1) / 2) ** 2
    return 2 * R_TERRA_M * math.asin(min(1.0, math.sqrt(a)))


class ValidacaoErro(Exception):
    """A base de dados viola alguma restrição do modelo."""


# ----------------------------------------------------------------------------------------------
# Algoritmos (operam sobre grafo = {nó: [(vizinho, peso), ...]})
# ----------------------------------------------------------------------------------------------
def dijkstra(grafo, origem, destino=None, proibidos=frozenset()):
    """Dijkstra com heap: O((V+A) log V). Para ao fechar o destino. Retorna (dist, ant, nós_expandidos)."""
    dist = {origem: 0.0}
    ant = {origem: None}
    fila = [(0.0, origem)]
    fechados = set()
    exp = 0
    while fila:
        d, u = heapq.heappop(fila)                      # escolha gulosa: menor custo conhecido
        if u in fechados:
            continue
        fechados.add(u)
        exp += 1
        if u == destino:                                # parada antecipada
            break
        for v, w in grafo[u]:                           # relaxamento
            if proibidos and (u, v) in proibidos:
                continue
            nd = d + w
            if nd < dist.get(v, math.inf):
                dist[v] = nd
                ant[v] = u
                heapq.heappush(fila, (nd, v))
    return dist, ant, exp


def dijkstra_n2(grafo, origem, destino=None):
    """Versão didática (a do Main.py da Polska): seleção linear do menor custo, O(V²)."""
    dist = {n: math.inf for n in grafo}
    ant = {n: None for n in grafo}
    abertos = set(grafo)
    dist[origem] = 0.0
    while abertos:
        atual = min(abertos, key=lambda n: dist[n])
        if dist[atual] == math.inf:
            break
        abertos.remove(atual)
        if atual == destino:
            break
        for viz, w in grafo[atual]:
            if viz in abertos and dist[atual] + w < dist[viz]:
                dist[viz] = dist[atual] + w
                ant[viz] = atual
    return dist, ant


def astar(grafo, coords, origem, destino, fator=1.0, proibidos=frozenset()):
    """A* com heurística h(n) = fator · haversine(n, destino). Retorna (custo, ant, nós_expandidos)."""
    tx, ty = coords[destino]

    def h(n):
        x, y = coords[n]
        return fator * haversine_m(x, y, tx, ty)

    g = {origem: 0.0}
    ant = {origem: None}
    fila = [(h(origem), origem)]
    fechados = set()
    exp = 0
    while fila:
        _, u = heapq.heappop(fila)
        if u in fechados:
            continue
        fechados.add(u)
        exp += 1
        if u == destino:
            break
        for v, w in grafo[u]:
            if proibidos and (u, v) in proibidos:
                continue
            ng = g[u] + w
            if ng < g.get(v, math.inf):
                g[v] = ng
                ant[v] = u
                heapq.heappush(fila, (ng + h(v), v))
    return g.get(destino, math.inf), ant, exp


def reconstruir(ant, origem, destino):
    """Segue os predecessores do destino até a origem. None se o destino não foi alcançado."""
    caminho, x = [], destino
    while x is not None:
        if x not in ant:
            return None
        caminho.append(x)
        x = ant[x]
    caminho.reverse()
    return caminho if caminho and caminho[0] == origem else None


def bfs_trechos(grafo, origem):
    """Predecessores da rota com MENOR NÚMERO DE TRECHOS (baseline 'antes', sem usar a distância)."""
    ant = {origem: None}
    fila = deque([origem])
    while fila:
        u = fila.popleft()
        for v, _ in grafo[u]:
            if v not in ant:
                ant[v] = u
                fila.append(v)
    return ant


def custo_caminho(grafo, caminho):
    """Soma dos pesos de um caminho (usa o menor arco u→v caso haja mais de um)."""
    total = 0.0
    for a, b in zip(caminho, caminho[1:]):
        total += min(w for v, w in grafo[a] if v == b)
    return total


# ----------------------------------------------------------------------------------------------
# Passo a passo didático
# ----------------------------------------------------------------------------------------------
def dijkstra_trace(grafo, origem, destino):
    """Mesmo algoritmo do dijkstra_n2, registrando cada iteração (para mostrar a conta 'à mão')."""
    dist = {n: math.inf for n in grafo}
    ant = {n: None for n in grafo}
    abertos = set(grafo)
    fechados, passos = [], []
    dist[origem] = 0.0
    while abertos:
        atual = min(abertos, key=lambda n: dist[n])
        if dist[atual] == math.inf:
            break
        abertos.remove(atual)
        fechados.append(atual)
        relax = []
        if atual != destino:
            for viz, w in grafo[atual]:
                if viz in abertos:
                    nova = dist[atual] + w
                    ok = nova < dist[viz]
                    relax.append((viz, dist[atual], w, nova, dist[viz], ok))
                    if ok:
                        dist[viz] = nova
                        ant[viz] = atual
        passos.append(dict(atual=atual, dist=dict(dist), fechados=list(fechados), relax=relax, ant=dict(ant)))
        if atual == destino:
            break
    return passos


def recorte_bola(grafo, centro, n):
    """Sub-grafo real com os n primeiros nós alcançados (BFS) a partir de 'centro'."""
    ordem, vistos, fila = [centro], {centro}, deque([centro])
    while fila and len(ordem) < n:
        u = fila.popleft()
        for v, _ in grafo[u]:
            if v not in vistos and len(ordem) < n:
                vistos.add(v)
                ordem.append(v)
                fila.append(v)
    sub = {u: [(v, w) for v, w in grafo[u] if v in vistos] for u in ordem}
    return sub, ordem


# ----------------------------------------------------------------------------------------------
# Validação das restrições do modelo
# ----------------------------------------------------------------------------------------------
def _alcanca_todos(grafo, inicio, reverso=False):
    adj = grafo
    if reverso:
        adj = {n: [] for n in grafo}
        for u in grafo:
            for v, w in grafo[u]:
                adj[v].append((u, w))
    vistos, fila = {inicio}, deque([inicio])
    while fila:
        u = fila.popleft()
        for v, _ in adj[u]:
            if v not in vistos:
                vistos.add(v)
                fila.append(v)
    return len(vistos) == len(grafo)


def validar(grafo, coords, levantar=True):
    """Confere as restrições do modelo. Retorna [(descrição, ok)]; levanta ValidacaoErro se algo falhar."""
    arcos = [(u, v, w) for u in grafo for v, w in grafo[u]]
    conj = {(u, v) for u, v, _ in arcos}
    n0 = next(iter(grafo))
    viol = sum(1 for u, v, w in arcos if w < 0.99 * haversine_m(*coords[u], *coords[v]))
    testes = [
        ("Pesos finitos e estritamente positivos (requisito do Dijkstra)", all(math.isfinite(w) and w > 0 for *_, w in arcos)),
        ("Sem laços (u != v)", all(u != v for u, v, _ in arcos)),
        ("Sem arcos duplicados", len(conj) == len(arcos)),
        ("Extremos de todo arco existem", all(v in grafo for _, v, _ in arcos)),
        ("Todo nó tem coordenadas", set(coords) == set(grafo)),
        ("Fortemente conexo — ida (todos alcançáveis a partir do nó inicial)", _alcanca_todos(grafo, n0)),
        ("Fortemente conexo — volta (todos alcançam o nó inicial)", _alcanca_todos(grafo, n0, reverso=True)),
        ("Comprimento do trecho ≥ linha reta (±1%) em ≥ 99% dos arcos (A* admissível)", viol / max(len(arcos), 1) < 0.01),
    ]
    if levantar and not all(ok for _, ok in testes):
        falhas = "; ".join(d for d, ok in testes if not ok)
        raise ValidacaoErro(f"A base viola o modelo: {falhas}")
    return testes


# ----------------------------------------------------------------------------------------------
# Rede (grafo + coordenadas + utilidades)
# ----------------------------------------------------------------------------------------------
@dataclass
class Resultado:
    caminho: list
    metros: float
    expandidos: int
    ms: float
    metodo: str


class Rede:
    def __init__(self, grafo, coords, nome="rede"):
        self.grafo, self.coords, self.nome = grafo, coords, nome
        self.ids = np.fromiter(coords.keys(), dtype=np.int64)
        self._xy = np.array([coords[i] for i in self.ids], dtype=float)
        self.peso = {(u, v): w for u in grafo for v, w in grafo[u]}
        self._cache_bfs = {}
        razoes = []
        for (u, v), w in self.peso.items():
            d = haversine_m(*coords[u], *coords[v])
            if d > 1.0:
                razoes.append(w / d)
        # fator de segurança: garante h(u) <= w(u,v) + h(v) em todos os arcos (heurística consistente)
        self.fator_h = min(1.0, min(razoes)) if razoes else 1.0

    # --- propriedades -------------------------------------------------------------------------
    @property
    def n_nos(self):
        return len(self.grafo)

    @property
    def n_arcos(self):
        return len(self.peso)

    def pct_mao_unica(self):
        return 100.0 * sum(1 for (u, v) in self.peso if (v, u) not in self.peso) / max(self.n_arcos, 1)

    # --- consultas ----------------------------------------------------------------------------
    def mais_proximo(self, lat, lon):
        k = math.cos(math.radians(lat))
        d = (self._xy[:, 0] - lon) ** 2 * k * k + (self._xy[:, 1] - lat) ** 2
        return int(self.ids[int(np.argmin(d))])

    def snap(self, lat, lon):
        """Nó mais próximo e a distância (m) até ele — avisa quando o ponto está longe da malha."""
        no = self.mais_proximo(lat, lon)
        return no, haversine_m(lon, lat, *self.coords[no])

    def comprimento(self, caminho):
        return sum(self.peso[(a, b)] for a, b in zip(caminho, caminho[1:]))

    def resolver(self, origem, destino, metodo="dijkstra", proibidos=frozenset()):
        """Menor caminho. metodo: 'dijkstra' | 'astar'. Retorna Resultado ou None (destino inalcançável)."""
        t0 = time.perf_counter()
        if metodo == "astar":
            _, ant, exp = astar(self.grafo, self.coords, origem, destino, self.fator_h, proibidos)
        else:
            _, ant, exp = dijkstra(self.grafo, origem, destino, proibidos)
        ms = (time.perf_counter() - t0) * 1e3
        c = reconstruir(ant, origem, destino)
        if c is None:
            return None
        return Resultado(c, self.comprimento(c), exp, ms, metodo)

    def menos_trechos(self, origem, destino):
        """Baseline 'antes': rota com menor número de trechos (cache por origem)."""
        if origem not in self._cache_bfs:
            self._cache_bfs[origem] = bfs_trechos(self.grafo, origem)
        c = reconstruir(self._cache_bfs[origem], origem, destino)
        return None if c is None else Resultado(c, self.comprimento(c), 0, 0.0, "menos_trechos")

    @staticmethod
    def ruas_bloqueadas(u, v):
        """Fechar uma rua fecha os dois sentidos (se existirem)."""
        return frozenset({(u, v), (v, u)})


# ----------------------------------------------------------------------------------------------
# Leitura / gravação do grafo em JSON (formato próprio, compacto)
# ----------------------------------------------------------------------------------------------
def salvar_json(grafo, coords, arquivo, meta=None):
    ids = sorted(grafo)
    assert ids == list(range(len(ids))), "IDs devem ser 0..n-1"
    dados = {
        "meta": meta or {},
        "nodes": [[round(coords[i][0], 6), round(coords[i][1], 6)] for i in ids],      # [lon, lat]; índice = id
        "edges": [[u, v, max(round(w, 2), 0.01)] for u in ids for v, w in grafo[u]],     # [origem, destino, metros]
    }
    Path(arquivo).parent.mkdir(parents=True, exist_ok=True)
    Path(arquivo).write_text(json.dumps(dados, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")


def carregar_json(arquivo):
    dados = json.loads(Path(arquivo).read_text(encoding="utf-8"))
    coords = {i: (lon, lat) for i, (lon, lat) in enumerate(dados["nodes"])}
    grafo = {i: [] for i in coords}
    for u, v, w in dados["edges"]:
        grafo[u].append((v, float(w)))
    return grafo, coords, dados.get("meta", {})
