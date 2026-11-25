# Matriz de evidências — critérios da ficha A2

O nível final é decisão do professor; esta tabela mostra onde está a evidência de cada item "Excelente" e o que ainda depende do grupo.

| Critério (nível Excelente) | Evidência neste projeto | Depende de vocês |
|---|---|---|
| 1.1 Dataset: base limpa/tratada, parâmetros reais, justificativa | `gerar_grafo.py` (limpeza e 8 validações), README §1B | Explicar a origem (OSM) e as colunas no vídeo |
| 1.2 Algoritmo: comparou alternativas e detalhou como os dados alimentam o método | README §1C; notebook seção 7; `Main_Krakow.py` opções 4 e 7 | Defender por que não Bellman-Ford/Floyd-Warshall |
| 1.3 Modelagem: formulação impecável, restrições de domínio, protótipo | README §1D; `nucleo.validar` | — |
| 2.1 Algoritmo: passo manual/visual completo com dados reais e onde está no código | Menu 3 e notebook seção 3 (recorte real de 12 cruzamentos) | Mostrar no código as linhas citadas |
| 2.2 Implementação: pipeline automatizado, modular, validação de restrições e análise de tempo | Módulos, `gerar_grafo.py`, `pytest`, verificação contra NetworkX, benchmark | Rodar uma vez e mostrar os testes passando |
| 2.3 Visual: painel "Antes × Depois" | `resultados/painel_executivo.png` (menu 5) | — |
| 2.4 Vídeo 10–15 min, todos em câmera, domínio técnico | `docs/ROTEIRO_VIDEO.md` | Gravar e conferir tempo e acesso ao link |
| 2.5 Análise: compara com a operação real sem otimização, % ganho, sensibilidade | Cenário em lote, bloqueio de via, erro nos pesos | **Operação real exige dados de uma empresa** (`pontos_empresa.csv`); sem eles, é simulação |
