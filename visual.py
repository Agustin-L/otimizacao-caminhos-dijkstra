# -*- coding: utf-8 -*-
"""visual.py — figuras (malha viária, rotas, painel executivo, escalabilidade)."""
import math
import os

import matplotlib

if not os.environ.get("DISPLAY") and os.name != "nt" and "MPLBACKEND" not in os.environ:
    matplotlib.use("Agg")                      # servidor sem tela: só salva os PNGs
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import LineCollection

COR_ANTES, COR_DEPOIS, COR_FUNDO = "#1f77b4", "#e32636", "#c9d3da"


def _k(rede):
    return math.cos(math.radians(float(np.mean(rede._xy[:, 1]))))


def _fundo(rede):
    k, vistos, segs = _k(rede), set(), []
    for (u, v) in rede.peso:
        par = (u, v) if u < v else (v, u)
        if par in vistos:
            continue
        vistos.add(par)
        segs.append([(rede.coords[u][0] * k, rede.coords[u][1]), (rede.coords[v][0] * k, rede.coords[v][1])])
    return LineCollection(segs, colors=COR_FUNDO, linewidths=0.35)


def _seg(rede, c):
    k = _k(rede)
    return [(rede.coords[n][0] * k, rede.coords[n][1]) for n in c]


def _finalizar(fig, arquivo, mostrar):
    if arquivo:
        fig.savefig(arquivo, dpi=170, bbox_inches="tight")
    if mostrar and matplotlib.get_backend().lower() != "agg":
        plt.show()
    plt.close(fig)


def desenhar_rede(rede, arquivo, mostrar=False):
    fig, ax = plt.subplots(figsize=(10, 9))
    ax.add_collection(_fundo(rede))
    ax.autoscale()
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(f"Rede viária — {rede.nome}: {rede.n_nos:,} nós · {rede.n_arcos:,} arcos", fontsize=12, fontweight="bold")
    _finalizar(fig, arquivo, mostrar)


def desenhar_rotas(rede, rotas, titulo, arquivo=None, pontos=None, mostrar=True):
    """rotas: lista de (caminho, cor, estilo, rótulo). pontos: lista de (nó, rótulo)."""
    fig, ax = plt.subplots(figsize=(11, 9.5))
    ax.add_collection(_fundo(rede))
    for c, cor, estilo, rot in rotas:
        xs, ys = zip(*_seg(rede, c))
        ax.plot(xs, ys, color=cor, lw=3.0 if estilo == "-" else 3.6, ls=estilo, label=rot, zorder=3)
    for n, rot in (pontos or []):
        x, y = _seg(rede, [n])[0]
        ax.scatter([x], [y], s=85, c="#17324d", zorder=5)
        ax.annotate(rot, (x, y), textcoords="offset points", xytext=(7, 7), fontsize=9, fontweight="bold", zorder=6)
    ax.autoscale()
    ax.set_aspect("equal")
    ax.axis("off")
    ax.legend(loc="lower left")
    ax.set_title(titulo, fontsize=12, fontweight="bold")
    _finalizar(fig, arquivo, mostrar)


def desenhar_passos(rede_sub, sub, ordem, rotulos, passos, arquivo=None, mostrar=True):
    import networkx as nx
    n, cols = len(passos), 4
    lin = math.ceil(n / cols)
    fig, axs = plt.subplots(lin, cols, figsize=(4.6 * cols, 3.8 * lin))
    axs = np.atleast_1d(axs).ravel()
    k = math.cos(math.radians(np.mean([rede_sub.coords[x][1] for x in ordem])))
    pos = {x: (rede_sub.coords[x][0] * k, rede_sub.coords[x][1]) for x in ordem}
    R = nx.DiGraph()
    R.add_nodes_from(ordem)
    for u in sub:
        for v, _ in sub[u]:
            R.add_edge(u, v)
    for ax, p, i in zip(axs, passos, range(1, n + 1)):
        cor = ["#e32636" if x == p["atual"] else "#20bf55" if x in p["fechados"] else "#ffd43b" if p["dist"][x] < math.inf else "#d0d7de" for x in R.nodes]
        nx.draw_networkx_edges(R, pos, ax=ax, edge_color="#8aa0ae", width=1.0, arrows=True, arrowsize=9, node_size=380)
        arv = [(a, b) for b, a in p["ant"].items() if a is not None]
        nx.draw_networkx_edges(R, pos, edgelist=arv, ax=ax, edge_color="#17324d", width=2.4, arrows=True, arrowsize=11, node_size=380)
        nx.draw_networkx_nodes(R, pos, ax=ax, node_color=cor, node_size=380, edgecolors="#183247")
        rr = {x: f"{rotulos[x]}\n" + (f"{p['dist'][x]:.0f}" if p["dist"][x] < math.inf else "∞") for x in R.nodes}
        nx.draw_networkx_labels(R, pos, labels=rr, ax=ax, font_size=6, font_weight="bold")
        ax.set_title(f"Iter. {i}: fecha {rotulos[p['atual']]}", fontsize=9)
        ax.axis("off")
    for ax in axs[n:]:
        ax.axis("off")
    fig.suptitle("Dijkstra passo a passo (recorte real) — rótulo = nó e menor distância conhecida (m); setas = sentido da via", fontsize=11)
    plt.tight_layout()
    _finalizar(fig, arquivo, mostrar)


def painel_executivo(rede, df, resumo, titulo, arquivo=None, mostrar=True):
    mel = df.loc[df.ganho_m.idxmax()]
    fig = plt.figure(figsize=(17, 9.5), facecolor="#f4f7f8")
    gs = fig.add_gridspec(2, 3, width_ratios=[1.55, 1, 1], height_ratios=[1, 1.15], hspace=0.34, wspace=0.3)
    ax_m, ax_k, ax_h, ax_r = (fig.add_subplot(gs[:, 0]), fig.add_subplot(gs[0, 1]), fig.add_subplot(gs[0, 2]), fig.add_subplot(gs[1, 1:]))

    ax_m.add_collection(_fundo(rede))
    ax_m.plot(*zip(*_seg(rede, mel.c_antes)), color=COR_ANTES, lw=3.2, ls="--", label=f"ANTES (menos trechos): {mel.m_antes/1000:.2f} km")
    ax_m.plot(*zip(*_seg(rede, mel.c_depois)), color=COR_DEPOIS, lw=2.6, label=f"DEPOIS (Dijkstra): {mel.m_depois/1000:.2f} km")
    ax_m.scatter(*zip(*[_seg(rede, [mel.s])[0], _seg(rede, [mel.t])[0]]), s=90, c="#17324d", zorder=5)
    ax_m.autoscale()
    ax_m.set_aspect("equal")
    ax_m.axis("off")
    ax_m.legend(loc="lower left")
    ax_m.set_title(f"Viagem de maior impacto: −{mel.ganho_m/1000:.2f} km ({mel.ganho_pct:.0f}%)", fontsize=12, fontweight="bold")

    KA, KD = resumo["km_antes"], resumo["km_depois"]
    ax_k.bar(["Antes", "Depois"], [KA, KD], color=[COR_ANTES, COR_DEPOIS])
    for i, v in enumerate([KA, KD]):
        ax_k.text(i, v, f"{v:,.0f} km", ha="center", va="bottom", fontweight="bold")
    ax_k.set_ylim(0, max(KA, KD) * 1.12)
    ax_k.spines[["top", "right"]].set_visible(False)
    ax_k.set_title(f"Distância total ({len(df)} viagens)\n−{resumo['ganho_pct']:.1f}%  ({KA-KD:,.0f} km)", fontsize=11, fontweight="bold")

    ax_h.hist(df.ganho_pct, bins=20, color=COR_DEPOIS, alpha=0.85)
    ax_h.axvline(df.ganho_pct.median(), color="#17324d", ls="--")
    ax_h.spines[["top", "right"]].set_visible(False)
    ax_h.set_title(f"Economia por viagem (%)\nmediana {df.ganho_pct.median():.1f}% · {resumo['mudaram']}/{len(df)} rotas mudaram", fontsize=11, fontweight="bold")
    ax_h.set_xlabel("% de distância evitada")
    ax_h.set_ylabel("nº de viagens")

    top = df.sort_values("ganho_m", ascending=False).head(8).iloc[::-1]
    nomes = top.par.str.slice(0, 28)
    ax_r.barh(nomes, top.m_antes / 1000, color=COR_ANTES, alpha=0.35, label="Antes (km)")
    ax_r.barh(nomes, top.m_depois / 1000, color=COR_DEPOIS, label="Depois (km)")
    for y, (a, b) in enumerate(zip(top.m_antes, top.m_depois)):
        ax_r.text(a / 1000 + 0.1, y, f"−{(a-b)/1000:.2f} km", va="center", fontsize=9, fontweight="bold")
    ax_r.set_title("8 viagens com maior economia", fontsize=11, fontweight="bold")
    ax_r.legend(loc="lower right")
    ax_r.spines[["top", "right"]].set_visible(False)
    ax_r.set_xlim(0, (top.m_antes.max() / 1000) * 1.2)
    fig.suptitle(titulo, fontsize=15, fontweight="bold", color="#17324d")
    _finalizar(fig, arquivo, mostrar)


def grafico_escalabilidade(df_t, arquivo=None, mostrar=True):
    fig, ax = plt.subplots(figsize=(7.5, 4.3))
    ax.loglog(df_t["V"], df_t["O(V²) ms"], "o-", label="Dijkstra O(V²) (versão do Main.py)")
    ax.loglog(df_t["V"], df_t["heap ms"], "s-", label="Dijkstra com heap")
    ax.set_xlabel("Nós (V)")
    ax.set_ylabel("Tempo, 1 origem → todos (ms)")
    ax.grid(True, which="both", alpha=0.3)
    ax.set_title("Escalabilidade em recortes reais da cidade (log-log)")
    ax.legend()
    plt.tight_layout()
    _finalizar(fig, arquivo, mostrar)


def grafico_bloqueios(df_b, arquivo=None, mostrar=True):
    d = df_b.sort_index()
    fin = d[~d.ponte]
    teto = (fin.desvio_m.max() if len(fin) else 1.0) * 1.15
    alt = np.where(d.ponte, teto, d.desvio_m)
    cores = np.where(d.ponte, "#9aa5ad", COR_DEPOIS)
    fig, ax = plt.subplots(figsize=(8, 3.6))
    ax.bar(range(len(d)), alt, color=cores)
    ax.set_xlabel("Trechos da rota (na ordem do percurso)")
    ax.set_ylabel("Desvio se a rua for bloqueada (m)")
    ax.set_title("Quais trechos da rota são mais críticos? (cinza = sem alternativa)")
    ax.spines[["top", "right"]].set_visible(False)
    plt.tight_layout()
    _finalizar(fig, arquivo, mostrar)
