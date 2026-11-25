# -*- coding: utf-8 -*-
"""Testes da seleção de locais (usa um GeoDataFrame falso no lugar do download do OSM)."""
import random
import sys
from pathlib import Path

import pytest

gpd = pytest.importorskip("geopandas")
shapely_geometry = pytest.importorskip("shapely.geometry")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import locais
from nucleo import Rede
from test_nucleo import grafo_aleatorio


def gdf_falso(rede, n_dentro=150, n_fora=20):
    rng = random.Random(4)
    nos = list(rede.coords.values())
    linhas = []
    for i in range(n_dentro):
        lon, lat = rng.choice(nos)
        eh_lugar = i % 3 != 0
        linhas.append({"name": f"Local Ąćę {i:03d}", "place": "suburb" if eh_lugar else None,
                       "tourism": None if eh_lugar else "museum", "wikidata": "Q1" if i % 7 == 0 else None,
                       "geometry": shapely_geometry.Point(lon, lat)})
    for i in range(n_fora):                                   # muito longe da malha: devem ser descartados
        linhas.append({"name": f"Longe {i}", "place": "suburb", "tourism": None, "wikidata": None,
                       "geometry": shapely_geometry.Point(25.0 + i * 0.01, 55.0)})
    linhas.append({"name": "local 003", "place": "suburb", "tourism": None, "wikidata": None,   # nome repetido (sem acento/caixa)
                   "geometry": shapely_geometry.Point(*nos[0])})
    linhas.append({"name": None, "place": "suburb", "tourism": None, "wikidata": None, "geometry": shapely_geometry.Point(*nos[1])})
    return gpd.GeoDataFrame(linhas, geometry="geometry", crs="EPSG:4326")


def rede_teste():
    g, pts = grafo_aleatorio()
    return Rede(g, pts)


def test_selecao_limite_sem_repeticao_e_dentro_da_malha():
    rede = rede_teste()
    df = locais.selecionar_locais(gdf_falso(rede), rede, n=90, max_snap_m=400)
    assert 0 < len(df) <= 90
    assert df.nome.map(locais.normalizar).is_unique
    assert not df.nome.str.startswith("Longe").any()
    assert set(df.tipo) <= {"bairro/distrito", "ponto de interesse"}
    assert (df.tipo == "ponto de interesse").sum() <= 30 or len(df) == 90


def test_normalizar_e_unir_listas():
    import pandas as pd
    assert locais.normalizar("Kraków") == "krakow"
    a = pd.DataFrame({"nome": ["Rynek"], "lat": [50.0], "lon": [19.9]})
    b = pd.DataFrame({"nome": ["rynek", "Wawel"], "lat": [50.0, 50.05], "lon": [19.9, 19.93], "tipo": ["x", "y"]})
    u = locais.unir_listas(a, b)
    assert list(u.nome) == ["Rynek", "Wawel"]


def test_sem_dados_retorna_vazio():
    rede = rede_teste()
    assert len(locais.selecionar_locais(None, rede)) == 0
