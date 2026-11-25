# Roteiro do vídeo (meta: 13 a 14 min, todos em câmera, sem leitura)

Regra da ficha: **10 a 15 min**, Meet/Teams, **todos os integrantes em câmera e explicando**. Ensaiem com cronômetro e rodem `python Main_Krakow.py --demo` antes de gravar para ter os números reais.

| Tempo | Quem | Conteúdo | Tela |
|---|---|---|---|
| 0:00–1:30 | Integrante 1 | Problema, evolução da A1 (Polska, 12 nós) para Kraków; por que o OSM; origem dos dados e colunas | `assets/rede_krakow.png` |
| 1:30–4:00 | Integrante 2 | Modelagem (V, A, w, F.O., restrições); por que Dijkstra e A\*; alternativas descartadas (Bellman-Ford, Floyd-Warshall) | README seção 1 |
| 4:00–7:00 | Integrante 3 | **Passo a passo manual** do Dijkstra (menu 3): mostrar uma iteração com a conta e apontar a linha no `nucleo.py` (escolha gulosa, relaxamento, predecessor) | terminal + `passo_a_passo.png` + código |
| 7:00–9:30 | Integrante 4 | Engenharia: módulos, validação automática, testes (`pytest`), verificação contra NetworkX, tempo e escalabilidade (menu 4 e 7) | terminal + `escalabilidade.png` |
| 9:30–12:30 | Integrante 1 ou 2 | Resultados: rota ao vivo (menu 1), bloqueio de via (menu 2), painel Antes × Depois (menu 5), sensibilidade (menu 6). **Traduzir o número em decisão** | painel + mapas |
| 12:30–14:00 | Todos | Conclusão em uma frase cada: ganho, limite (o "antes" é uma referência; velocidade é hipótese), próximos passos | `resumo.md` |

Dicas: cada um deve responder uma pergunta técnica de improviso; dividam as falas por tema, não por leitura de slide; deixem a câmera ligada o tempo todo; confiram no fim que o link do vídeo está **acessível**.
