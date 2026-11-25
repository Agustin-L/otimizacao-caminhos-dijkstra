# -*- coding: utf-8 -*-
"""
Main_Krakow.py — Caminho mínimo na rede viária real de Kraków (Dijkstra e A*), com menu interativo.

Pré-requisito (uma vez):  python gerar_grafo.py      -> cria dados/krakow.json a partir do OpenStreetMap
Uso:
  python Main_Krakow.py             # menu interativo
  python Main_Krakow.py --demo      # roda TUDO sozinho e grava os resultados em resultados/ (bom para o vídeo)
Caso real (opcional): coloque pontos_empresa.csv (colunas nome,lat,lon) na pasta; o cenário em lote passa a usá-lo.
"""
import argparse
import math
import re
import sys
import unicodedata
from pathlib import Path

import pandas as pd

import analises
import locais as loc
import nucleo
import visual
from nucleo import Rede

PASTA_RES = Path("resultados")


def slug(txt):
    ascii_ = unicodedata.normalize("NFKD", txt).encode("ascii", "ignore").decode()
    return re.sub(r"[^A-Za-z0-9]+", "_", ascii_).strip("_")[:40]


# ----------------------------------------------------------------------------- entrada
LIMITE_SNAP_M = 500


def snap_avisando(rede, lat, lon, nome):
    """Nó mais próximo; avisa se o ponto cai longe da malha (ex.: fora do limite da cidade)."""
    no, d = rede.snap(lat, lon)
    if d > LIMITE_SNAP_M:
        print(f"  ⚠ '{nome}' está a {d:,.0f} m do cruzamento mais próximo (fora/longe da malha baixada). A rota usará esse cruzamento.")
    return no


def listar_locais(locais, colunas=3, largura=38):
    """Imprime todos os locais numerados, em colunas."""
    rotulos = [f"{i:>3}. " + (n if len(n) <= largura - 7 else n[:largura - 8] + "…") for i, n in enumerate(locais.nome, 1)]
    linhas = math.ceil(len(rotulos) / colunas)
    for r in range(linhas):
        print("  " + "".join(f"{rotulos[r + c * linhas]:<{largura}}" for c in range(colunas) if r + c * linhas < len(rotulos)))


def ler_ponto(rede, locais, prompt):
    """Escolha de ponto: nº da lista · parte do nome (filtra) · 'l' lista tudo · 'lat,lon' · 'id:N'. Enter volta."""
    while True:
        txt = input(prompt).strip()
        if txt == "":
            return None
        if txt.lower() in ("l", "lista", "listar"):
            listar_locais(locais)
            continue
        try:
            if txt.isdigit() and 1 <= int(txt) <= len(locais):
                r = locais.iloc[int(txt) - 1]
                return snap_avisando(rede, r.lat, r.lon, r.nome), str(r.nome)
            if txt.lower().startswith("id:"):
                n = int(txt[3:])
                if n in rede.coords:
                    return n, f"nó {n}"
            elif "," in txt and txt.replace(",", "").replace(".", "").replace("-", "").replace(" ", "").isdigit():
                lat, lon = (float(x) for x in txt.split(","))
                return snap_avisando(rede, lat, lon, f"({lat:.4f}, {lon:.4f})"), f"({lat:.4f}, {lon:.4f})"
            else:
                chave = loc.normalizar(txt)
                ach = locais[locais.nome.map(loc.normalizar).str.contains(chave, regex=False)]
                if len(ach) == 1:
                    r = ach.iloc[0]
                    return snap_avisando(rede, r.lat, r.lon, r.nome), str(r.nome)
                if len(ach) > 1:
                    print(f"  {len(ach)} locais combinam com '{txt}' — digite o número:")
                    for i, r in ach.iterrows():
                        print(f"   {i + 1:>3}. {r.nome}")
                    continue
        except ValueError:
            pass
        print("  Não encontrei. Digite o nº da lista, parte do nome, 'l' para listar tudo, 'lat,lon' ou 'id:N'. (Enter = voltar)")


# ----------------------------------------------------------------------------- ações
def acao_rota(rede, s, t, ns, nt, vel, mostrar, prefixo="rota"):
    d, a = rede.resolver(s, t, "dijkstra"), rede.resolver(s, t, "astar")
    base = rede.menos_trechos(s, t)
    assert abs(d.metros - a.metros) < 1e-6, "A* e Dijkstra devem coincidir"
    print(f"\n=== {ns}  →  {nt} ===")
    print(f"Rota ótima (Dijkstra): {d.metros/1000:.3f} km · {len(d.caminho)-1} trechos · ~{60*d.metros/1000/vel:.1f} min a {vel:.0f} km/h (hipótese)")
    print(f"  Dijkstra: {d.ms:.1f} ms, {d.expandidos:,} nós expandidos")
    print(f"  A*      : {a.ms:.1f} ms, {a.expandidos:,} nós expandidos ({100*(1-a.expandidos/d.expandidos):.0f}% menos), mesma distância ✔")
    print(f"  Antes (menos trechos): {base.metros/1000:.3f} km · {len(base.caminho)-1} trechos → economia {(base.metros-d.metros)/1000:.3f} km ({100*(base.metros-d.metros)/base.metros:.1f}%)")
    PASTA_RES.mkdir(exist_ok=True)
    nome = f"{prefixo}_{slug(ns)}__{slug(nt)}"
    rotas = [(d.caminho, visual.COR_DEPOIS, "-", f"Dijkstra: {d.metros/1000:.2f} km")]
    if base.metros - d.metros > 1e-6:
        rotas.insert(0, (base.caminho, visual.COR_ANTES, "--", f"Antes (menos trechos): {base.metros/1000:.2f} km"))
    visual.desenhar_rotas(rede, rotas, f"{ns} → {nt}", PASTA_RES / f"{nome}.png", [(s, ns), (t, nt)], mostrar)
    analises.exportar_geojson(rede, d.caminho, PASTA_RES / f"{nome}.geojson", {"origem": ns, "destino": nt, "metros": round(d.metros, 1)})
    print(f"  Mapa: resultados/{nome}.png · rota: resultados/{nome}.geojson")
    return dict(s=s, t=t, ns=ns, nt=nt, d=d, a=a, base=base)


def acao_bloqueio(rede, ult, mostrar, escolha=None, interativo=True):
    if not ult:
        print("Calcule uma rota primeiro (opção 1).")
        return
    base, df_b = analises.sensibilidade_bloqueio(rede, ult["s"], ult["t"])
    trechos = list(zip(base.caminho, base.caminho[1:]))
    fin = df_b[~df_b.ponte]
    print(f"\nA rota tem {len(trechos)} trechos. {int(df_b.ponte.sum())} trecho(s) sem alternativa (ruas de acesso/pontes). "
          f"Nos demais, o desvio por UM bloqueio tem mediana {fin.desvio_m.median():,.0f} m e máximo {fin.desvio_m.max():,.0f} m.")
    if escolha is None and interativo:
        txt = input(f"Qual trecho bloquear (1-{len(trechos)})? Enter = o mais crítico com alternativa: ").strip()
        escolha = int(txt) if txt.isdigit() and 1 <= int(txt) <= len(trechos) else None
    u, v = trechos[escolha - 1] if escolha else tuple(int(x) for x in fin.iloc[0].trecho.split("→"))
    r = rede.resolver(ult["s"], ult["t"], "dijkstra", Rede.ruas_bloqueadas(u, v))
    if r is None:
        print("Sem rota alternativa: o trecho bloqueado é o único acesso (ponte).")
        return base, df_b
    print(f"Bloqueando o trecho {u}→{v} ({rede.peso[(u, v)]:.0f} m): nova rota {r.metros/1000:.3f} km (+{(r.metros-base.metros):,.0f} m, +{100*(r.metros-base.metros)/base.metros:.1f}%)")
    PASTA_RES.mkdir(exist_ok=True)
    visual.desenhar_rotas(rede, [(base.caminho, visual.COR_ANTES, "--", f"Original: {base.metros/1000:.2f} km"),
                                 (r.caminho, visual.COR_DEPOIS, "-", f"Com bloqueio: {r.metros/1000:.2f} km")],
                          "Simulação de bloqueio de via", PASTA_RES / "bloqueio.png", [(u, "✕ bloqueio")], mostrar)
    visual.grafico_bloqueios(df_b, PASTA_RES / "bloqueios_criticos.png", False)
    print("  Mapa: resultados/bloqueio.png · criticidade: resultados/bloqueios_criticos.png")
    return base, df_b


def acao_benchmark(rede, pois, mostrar, n_pares=40):
    pares = analises.amostrar_pares(rede, n_pares)
    b = analises.benchmark_pares(rede, pares)
    print(f"\n1 origem → TODOS os {rede.n_nos:,} nós: {b['t_todos_ms']:.0f} ms")
    print(f"Par origem–destino (média de {len(pares)}): Dijkstra {b['t_dij_ms']:.1f} ms · A* {b['t_ast_ms']:.1f} ms · NetworkX {b['t_nx_ms']:.1f} ms")
    print(f"Nós expandidos: Dijkstra {b['exp_dij']:,.0f} · A* {b['exp_ast']:,.0f} → A* expande {b['reducao_pct']:.0f}% menos")
    r0 = pois.iloc[0]
    df_t = analises.benchmark_escala(rede, rede.mais_proximo(r0.lat, r0.lon))
    print("\nEscalabilidade (recortes reais crescentes):\n" + df_t.to_string(index=False))
    PASTA_RES.mkdir(exist_ok=True)
    visual.grafico_escalabilidade(df_t, PASTA_RES / "escalabilidade.png", mostrar)
    return b, df_t


def acao_lote(rede, pontos_empresa, vel, custo_km, mostrar, n_pares=150):
    real = pontos_empresa is not None
    pares = analises.pares_de_pontos(rede, pontos_empresa, n_pares) if real else analises.amostrar_pares(rede, n_pares)
    print("\n" + ("CASO REAL (pontos da empresa)" if real else "SIMULAÇÃO com pares amostrados (NÃO é caso real)") + f" — {len(pares)} viagens")
    df = analises.cenario_antes_depois(rede, pares)
    r = analises.resumo_cenario(df, vel, custo_km)
    print(f"Distância total: {r['km_antes']:,.1f} → {r['km_depois']:,.1f} km (−{r['ganho_pct']:.1f}%) · {r['mudaram']}/{len(df)} rotas mudaram · maior ganho {r['maior_pct']:.1f}%")
    print(f"Tempo a {vel:.0f} km/h (hipótese): {r['min_antes']:,.0f} → {r['min_depois']:,.0f} min")
    if custo_km:
        print(f"Custo a R$ {custo_km:.2f}/km: R$ {r['custo_antes']:,.2f} → R$ {r['custo_depois']:,.2f}")
    PASTA_RES.mkdir(exist_ok=True)
    visual.painel_executivo(rede, df, r, f"PAINEL EXECUTIVO — {rede.nome}: menos trechos × menor distância (Dijkstra) · {'CASO REAL' if real else 'simulação com pares amostrados'}",
                            PASTA_RES / "painel_executivo.png", mostrar)
    df.drop(columns=["c_antes", "c_depois"]).round(2).to_csv(PASTA_RES / "antes_depois.csv", index=False)
    print("  Painel: resultados/painel_executivo.png · tabela: resultados/antes_depois.csv")
    return df, r, real


def acao_ruido(rede, pares_amostra):
    df_r = analises.sensibilidade_ruido(rede, pares_amostra[:25])
    print("\nErro nos pesos (cada comprimento × U(1−σ, 1+σ)); custo REAL medido com os pesos originais:\n" + df_r.to_string(index=False))
    return df_r


def acao_validar(rede):
    print("\nRestrições do modelo:")
    for desc, ok in nucleo.validar(rede.grafo, rede.coords, levantar=False):
        print(("  [OK] " if ok else "  [FALHA] ") + desc)
    n = analises.verificar_contra_networkx(rede, 200)
    print(f"Verificação cruzada: {n} pares — Dijkstra = A* = NetworkX (0 divergências); caminhos simples e contínuos ✔")
    print(f"Rede: {rede.n_nos:,} nós · {rede.n_arcos:,} arcos · {rede.pct_mao_unica():.1f}% em mão única · fator da heurística A* = {rede.fator_h:.3f}")


def acao_passos(rede, pois, mostrar, centro=None):
    if centro is None:
        r0 = pois.iloc[0]
        centro = rede.mais_proximo(r0.lat, r0.lon)
    sub, ordem = nucleo.recorte_bola(rede.grafo, centro, 12)
    rot = {n: f"N{i+1}" for i, n in enumerate(ordem)}
    passos = nucleo.dijkstra_trace(sub, ordem[0], ordem[-1])
    print(f"\nRecorte real de {len(sub)} cruzamentos · origem {rot[ordem[0]]} → destino {rot[ordem[-1]]} (distâncias em metros)")
    for i, p in enumerate(passos, 1):
        print(f"Iteração {i}: fecha {rot[p['atual']]} (menor custo conhecido = {p['dist'][p['atual']]:.1f} m)")
        for viz, base, w, nova, antiga, ok in p["relax"]:
            a = "∞" if antiga == float("inf") else f"{antiga:.1f}"
            print(f"     {rot[viz]:<4}: {base:8.1f} + {w:7.1f} = {nova:8.1f}  vs {a:>8}  → {'ATUALIZA ✔' if ok else 'mantém'}")
    PASTA_RES.mkdir(exist_ok=True)
    visual.desenhar_passos(rede, sub, ordem, rot, passos, PASTA_RES / "passo_a_passo.png", mostrar)
    print("  Imagens: resultados/passo_a_passo.png")


# ----------------------------------------------------------------------------- demo / resumo
def escrever_resumo(rede, rotas, df_b, bench, df_t, df, r, real, df_r, n_verif):
    L = ["# Resultados desta execução (gerado automaticamente por `Main_Krakow.py --demo`)\n"]
    L.append(f"* Rede: **{rede.n_nos:,} nós**, **{rede.n_arcos:,} arcos** (dirigidos; {rede.pct_mao_unica():.1f}% em mão única), pesos em metros.")
    L.append(f"* Verificação: Dijkstra e A* conferidos contra o NetworkX em {n_verif} pares — 0 divergências.")
    L.append(f"* Tempo por par: Dijkstra {bench['t_dij_ms']:.1f} ms · A* {bench['t_ast_ms']:.1f} ms · NetworkX {bench['t_nx_ms']:.1f} ms; A* expande {bench['reducao_pct']:.0f}% menos nós.")
    L.append(f"* Cenário em lote: **{'CASO REAL' if real else 'SIMULAÇÃO (pares amostrados — não é caso real)'}**, {len(df)} viagens; "
             f"distância {r['km_antes']:,.1f} → {r['km_depois']:,.1f} km (**−{r['ganho_pct']:.1f}%**), {r['mudaram']} rotas mudaram, maior ganho individual {r['maior_pct']:.1f}%.")
    L.append(f"* Tempo (HIPÓTESE {r['vel_kmh']:.0f} km/h): {r['min_antes']:,.0f} → {r['min_depois']:,.0f} min.")
    L.append("\n## Rotas de exemplo\n")
    for x in rotas:
        L.append(f"* {x['ns']} → {x['nt']}: {x['d'].metros/1000:.2f} km ótimos vs {x['base'].metros/1000:.2f} km (menos trechos).")
    L.append("\n## Escalabilidade\n```\n" + df_t.to_string(index=False) + "\n```")
    L.append("\n## Bloqueio de via (rota-exemplo) — trechos mais críticos\n```\n" + df_b.drop(columns=["ponte"]).head(6).round(1).to_string(index=False) + "\n```")
    L.append("\n## Erro nos pesos\n```\n" + df_r.to_string(index=False) + "\n```")
    L.append("\nFiguras: `painel_executivo.png`, `passo_a_passo.png`, `escalabilidade.png`, `bloqueio.png`, `bloqueios_criticos.png`, `rota_*.png`.")
    PASTA_RES.mkdir(exist_ok=True)
    (PASTA_RES / "resumo.md").write_text("\n".join(L), encoding="utf-8")
    print("\nResumo gravado em resultados/resumo.md")


def demo(rede, pois, pontos_empresa, vel, custo_km):
    acao_validar(rede)
    n_verif = 200
    nomes = list(pois.nome)
    pick = lambda frag: next(i for i, n in enumerate(nomes) if frag in n)
    exemplos = [("Estação", "Nowa Huta"), ("Kopiec", "Rynek Główny"), ("Bonarka", "Tauron")]
    rotas = []
    for a, b in exemplos:
        ia, ib = pick(a), pick(b)
        s, t = (snap_avisando(rede, pois.lat.iloc[ia], pois.lon.iloc[ia], nomes[ia]), snap_avisando(rede, pois.lat.iloc[ib], pois.lon.iloc[ib], nomes[ib]))
        if s != t:
            rotas.append(acao_rota(rede, s, t, nomes[ia], nomes[ib], vel, False))
    ult = rotas[0]
    base, df_b = acao_bloqueio(rede, ult, False, interativo=False)
    bench, df_t = acao_benchmark(rede, pois, False)
    df, r, real = acao_lote(rede, pontos_empresa, vel, custo_km, False)
    df_r = acao_ruido(rede, analises.amostrar_pares(rede, 25))
    acao_passos(rede, pois, False)
    escrever_resumo(rede, rotas, df_b, bench, df_t, df, r, real, df_r, n_verif)


# ----------------------------------------------------------------------------- menu
MENU = """
================  Kraków — Caminho Mínimo (Dijkstra / A*)  ================
 1) Calcular rota entre dois pontos
 2) Simular bloqueio de uma via na última rota
 3) Passo a passo do Dijkstra (recorte real de 12 cruzamentos)
 4) Desempenho e escalabilidade (Dijkstra × A* × NetworkX)
 5) Cenário Antes × Depois em lote (painel executivo)
 6) Sensibilidade a erros nos pesos
 7) Validar a base e conferir contra o NetworkX
 0) Sair
"""


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json", default="dados/krakow.json")
    ap.add_argument("--pois", default="pontos_krakow.csv")
    ap.add_argument("--locais", default="dados/locais.csv", help="lista de ~100 locais gerada pelo gerar_grafo.py")
    ap.add_argument("--empresa", default="pontos_empresa.csv", help="CASO REAL (opcional): nome,lat,lon")
    ap.add_argument("--vel", type=float, default=30.0, help="velocidade média (km/h) — HIPÓTESE")
    ap.add_argument("--custo-km", type=float, default=None, help="custo por km, se a empresa informar")
    ap.add_argument("--demo", action="store_true", help="executa tudo e grava resultados/")
    ap.add_argument("--sem-tela", action="store_true", help="não abre janelas (só salva PNGs)")
    a = ap.parse_args()

    if not Path(a.json).is_file():
        sys.exit(f"Não encontrei {a.json}. Rode antes:  python gerar_grafo.py")
    grafo, coords, meta = nucleo.carregar_json(a.json)
    nucleo.validar(grafo, coords)
    rede = Rede(grafo, coords, meta.get("cidade", "Kraków"))
    pois = pd.read_csv(a.pois)
    locais = loc.unir_listas(pois, pd.read_csv(a.locais)) if Path(a.locais).is_file() else pois.assign(tipo="ponto de referência")
    pontos_empresa = pd.read_csv(a.empresa) if Path(a.empresa).is_file() else None
    mostrar = not a.sem_tela
    print(f"Rede carregada: {rede.n_nos:,} nós · {rede.n_arcos:,} arcos · {rede.pct_mao_unica():.1f}% em mão única · fonte: {meta.get('fonte', '?')} · {len(locais)} locais para escolher")

    if a.demo:
        return demo(rede, pois, pontos_empresa, a.vel, a.custo_km)

    ult = None
    while True:
        try:
            print(MENU)
            op = input("Escolha uma opção: ").strip()
            if op == "0":
                break
            elif op == "1":
                print(f"\n{len(locais)} locais disponíveis (coordenadas do OpenStreetMap):")
                listar_locais(locais)
                print("\nDica: digite parte do nome para FILTRAR (ex.: 'nowa'), 'l' para listar de novo, ou 'lat,lon'.")
                o = ler_ponto(rede, locais, "\nORIGEM (nº / nome / l / lat,lon / id:N; Enter = voltar): ")
                if o is None:
                    continue
                d = ler_ponto(rede, locais, "DESTINO: ")
                if d is None:
                    continue
                if o[0] == d[0]:
                    print("Origem e destino caem no mesmo cruzamento.")
                    continue
                ult = acao_rota(rede, o[0], d[0], o[1], d[1], a.vel, mostrar)
            elif op == "2":
                acao_bloqueio(rede, ult, mostrar)
            elif op == "3":
                acao_passos(rede, pois, mostrar)
            elif op == "4":
                acao_benchmark(rede, pois, mostrar)
            elif op == "5":
                acao_lote(rede, pontos_empresa, a.vel, a.custo_km, mostrar)
            elif op == "6":
                acao_ruido(rede, analises.amostrar_pares(rede, 25))
            elif op == "7":
                acao_validar(rede)
            else:
                print("Opção inválida.")
        except (EOFError, KeyboardInterrupt):
            print()
            break
    print("Até logo!")


if __name__ == "__main__":
    main()
