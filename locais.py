# -*- coding: utf-8 -*-
"""
locais.py — lista de ~100 locais selecionáveis (origem/destino), extraídos do OpenStreetMap.

Bairros/distritos (place=suburb|neighbourhood|quarter) + pontos de interesse (atrações, museus, universidades,
hospitais, estações ...) da cidade. Só entram locais que estão dentro/perto da malha viária baixada.
"""
import unicodedata

import pandas as pd


def normalizar(txt):
    """Minúsculas e sem acento: 'Kraków' ~ 'krakow'."""
    return unicodedata.normalize("NFKD", str(txt)).encode("ascii", "ignore").decode().lower().strip()


TAGS_LUGARES = {"place": ["suburb", "neighbourhood", "quarter"]}
TAGS_POIS = {
    "tourism": ["attraction", "museum", "gallery", "viewpoint"],
    "amenity": ["university", "hospital", "theatre", "marketplace"],
    "railway": ["station"],
    "historic": ["castle", "monument"],
}


def baixar_locais(ox, cidade):
    """Baixa do OSM (precisa de internet). Retorna um GeoDataFrame ou None se tudo falhar."""
    partes = []
    for tags in (TAGS_LUGARES, TAGS_POIS):
        try:
            partes.append(ox.features_from_place(cidade, tags=tags))
        except Exception as e:                                  # sem internet, tag sem resultado etc.
            print(f"  aviso: não consegui baixar {list(tags)[0]}: {e}")
    return pd.concat(partes) if partes else None


def selecionar_locais(gdf, rede, n=90, max_snap_m=400, quota_poi=30):
    """GeoDataFrame do OSM -> DataFrame(nome, lat, lon, tipo) com até n locais, sem repetir nomes."""
    colunas = ["nome", "lat", "lon", "tipo"]
    if gdf is None or len(gdf) == 0 or "name" not in gdf.columns:
        return pd.DataFrame(columns=colunas)
    gdf = gdf[gdf["name"].notna()]
    pts = gdf.geometry.representative_point()                  # polígono -> ponto dentro dele
    df = pd.DataFrame({
        "nome": gdf["name"].astype(str).values, "lat": pts.y.values, "lon": pts.x.values,
        "lugar": (gdf["place"].notna().values if "place" in gdf.columns else False),
        "notavel": (gdf["wikidata"].notna().values if "wikidata" in gdf.columns else False),
    })
    df["chave"] = df.nome.map(normalizar)
    df = df.sort_values(["notavel", "nome"], ascending=[False, True]).drop_duplicates("chave")
    d = [rede.snap(la, lo)[1] for la, lo in zip(df.lat, df.lon)]
    df = df[[x <= max_snap_m for x in d]]                      # descarta o que está fora da malha
    lugares, pois = df[df.lugar].sort_values("nome"), df[~df.lugar]
    pois = pois.sort_values(["notavel", "nome"], ascending=[False, True])
    p_poi = pois.head(quota_poi)
    p_lug = lugares.head(max(n - len(p_poi), 0))
    sel = pd.concat([p_lug.assign(tipo="bairro/distrito"), p_poi.assign(tipo="ponto de interesse")])
    if len(sel) < n:                                           # completa com o que sobrou
        sobra = pd.concat([lugares.iloc[len(p_lug):].assign(tipo="bairro/distrito"), pois.iloc[len(p_poi):].assign(tipo="ponto de interesse")])
        sel = pd.concat([sel, sobra.head(n - len(sel))])
    return sel[colunas].sort_values("nome").reset_index(drop=True)


def unir_listas(*listas):
    """Junta listas (nome, lat, lon[, tipo]) sem repetir nomes (a 1ª lista tem prioridade)."""
    todos = pd.concat([l.assign(tipo=l["tipo"] if "tipo" in l.columns else "ponto de referência") for l in listas], ignore_index=True)
    todos["chave"] = todos.nome.map(normalizar)
    return todos.drop_duplicates("chave").drop(columns="chave").reset_index(drop=True)
