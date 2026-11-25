# Caminho Mínimo na rede viária de Kraków (Dijkstra e A\*)

Projeto da **A2 de Pesquisa Operacional I** — Trilha 3: *Caminho Mínimo em Grafo (Dijkstra/A\*)*.
Evolução do trabalho da A1 (rede de telecomunicações **SNDlib Polska**, 12 nós) para uma **rede viária real com dezenas de milhares de cruzamentos**.
O projeto da Polska (`Main.py`) continua válido no repositório original e serve de validação de corretude.

## 1. Declaração de escopo, dados e algoritmo (Etapa 1)

**A) Trilha:** 3 — Caminho Mínimo em Grafo (Dijkstra/A\*).

**B) Problema e dados.** Encontrar a rota de menor distância entre dois pontos da cidade de Kraków, considerando o sentido das ruas.
Dados: **OpenStreetMap** (rede `drive` de Kraków, obtida com OSMnx). Colunas usadas: nós `x` (longitude) e `y` (latitude); arcos `length` (metros) e o sentido de circulação.
*Por que esta base:* é pública e real, tem a escala de uma operação logística urbana (dezenas de milhares de nós), os pesos têm significado físico (metros) — o que permite validar a solução e usar A\* — e amplia a rede de 12 nós da A1, conforme sugestão do professor.
O `gerar_grafo.py` limpa e valida a base (maior componente fortemente conexa, sem laços, sem pesos ≤ 0, arcos paralelos → o menor).

**C) Por que Dijkstra (e A\*).** Todos os pesos são estritamente positivos (verificado automaticamente), então a escolha gulosa do Dijkstra é ótima, com custo O((V+A) log V) usando fila de prioridade.
O A\* resolve o mesmo problema usando a distância em linha reta (haversine) como heurística admissível, expandindo menos nós. Bellman-Ford (pesos negativos) e Floyd-Warshall (todos contra todos, O(V³)) foram comparados e descartados — ver `docs/` e o notebook.

**D) Modelagem formal.** Grafo dirigido e ponderado G = (V, A, w).
* **V:** cruzamentos/pontas de rua. **A:** trechos dirigíveis (u→v). **w(u,v) > 0:** comprimento em metros.
* **Variável de decisão:** x(u,v) ∈ {0,1} — 1 se o trecho faz parte da rota.
* **Função objetivo:** minimizar Σ w(u,v)·x(u,v).
* **Restrições:** conservação de fluxo (saída líquida = 1 na origem, −1 no destino, 0 nos demais) e x binário.

## 2. Estrutura

| Arquivo | Função |
|---|---|
| `gerar_grafo.py` | **Geração do grafo**: baixa o OSM, limpa, valida e grava `dados/krakow.json`, `dados/locais.csv` (lista de locais) e `assets/rede_krakow.png` |
| `nucleo.py` | Dijkstra (heap), Dijkstra O(V²), A\*, BFS, validação, passo a passo, leitura/gravação do grafo |
| `locais.py` | Seleciona ~100 locais (bairros/distritos e pontos de interesse do OSM) para escolher origem e destino |
| `analises.py` | Verificação contra NetworkX, desempenho, cenário Antes × Depois, sensibilidade |
| `visual.py` | Mapas, painel executivo, escalabilidade |
| `Main_Krakow.py` | **Programa interativo** (menu) e modo `--demo` |
| `tests/test_nucleo.py` | 10 testes automáticos (`python -m pytest -q`) |
| `A2_Dijkstra_Krakow.ipynb` | Versão em notebook (Colab) com todas as análises e gráficos |
| `pontos_krakow.csv` | Pontos de referência da cidade (coordenadas aproximadas) |
| `docs/` | Roteiro do vídeo e matriz de evidências da avaliação |

## 3. Como executar
```bash
python -m pip install -r requirements.txt
python gerar_grafo.py            # uma vez (1 a 3 min; precisa de internet)
python Main_Krakow.py            # menu interativo
python Main_Krakow.py --demo     # executa tudo e grava resultados/ (figuras, CSV e resumo.md)
python -m pytest -q              # testes automáticos
```
No menu (opção 1) aparece a lista de ~100 locais de Kraków: escolha origem e destino pelo **nº da lista**, **digitando parte do nome para filtrar** (aceita sem acento: `nowa`, `krakow`), `l` para listar de novo, `lat,lon` ou `id:N`; simule o bloqueio de uma rua; veja o passo a passo do Dijkstra; compare o desempenho; gere o painel Antes × Depois.

## 4. Cenário Antes × Depois e caso real
* **Depois:** rota de menor distância (Dijkstra). **Antes (referência):** rota de menor número de trechos. *O tamanho do ganho depende dessa definição.*
* **Caso real:** se existir `pontos_empresa.csv` (colunas `nome,lat,lon`) com pontos reais de uma empresa, o cenário em lote usa esses pontos; sem o arquivo, usa pares amostrados e **avisa que é simulação**.
* Hipóteses explícitas: velocidade média (`--vel`, padrão 30 km/h) e custo por km (`--custo-km`, só se a empresa informar).

## 5. Resultados
Rodando `python Main_Krakow.py --demo`, os números reais desta máquina são gravados em `resultados/resumo.md` e as figuras em `resultados/`.
