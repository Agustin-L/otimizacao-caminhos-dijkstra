# Projeto: Caminho Mínimo em uma Rede de Telecomunicações

## 1. Sobre o projeto

Este projeto implementa o algoritmo de Dijkstra para encontrar o menor caminho entre dois nós de uma rede de telecomunicações, utilizando a topologia SNDlib Polska disponibilizada pela plataforma TopoHub.

O algoritmo de Dijkstra foi implementado no próprio código. A biblioteca NetworkX é utilizada somente para desenhar o grafo, e Matplotlib apresenta a visualização.

## 2. Objetivos

- Implementar o algoritmo de Dijkstra.
- Representar uma topologia de telecomunicações como grafo ponderado.
- Permitir a escolha de origem e destino pelo usuário.
- Exibir a menor rota e sua distância total sobre o mapa da Polônia.

## 3. Fontes dos dados

**Topologia da rede:** TopoHub — SNDlib Polska  
https://www.topohub.org/

O arquivo `polska.json` contém os nós, as conexões, as distâncias e as coordenadas utilizadas pelo programa.

**Divisões administrativas:** geometrias GeoJSON das 16 voivodias da Polônia, disponibilizadas no repositório `andilabs/polska-wojewodztwa-geojson`.  
https://github.com/andilabs/polska-wojewodztwa-geojson

A imagem `assets/mapa_polonia.png` mostra somente o território da Polônia e suas divisões administrativas internas. Os contornos regionais foram simplificados para compor a visualização do projeto; países vizinhos, rios e outros elementos externos foram removidos.

## 4. Tecnologias

- Python
- NetworkX: desenho do grafo, sem cálculo da rota
- Matplotlib: visualização do mapa e da rede
- JSON: armazenamento da topologia

## 5. Estrutura do projeto

```text
otimizacao-caminhos-dijkstra/
├── main.py
├── polska.json
├── requirements.txt
├── README.md
├── assets/
│   └── mapa_polonia.png
└── dados/
    └── polska.gml
```

O único mapa utilizado pelo sistema é `assets/mapa_polonia.png`. O arquivo GML é mantido como material complementar e não é carregado pelo programa.

## 6. Instalação e execução

Com Python instalado, abra o terminal na pasta do projeto e execute:

```bash
python -m pip install -r requirements.txt
python main.py
```

O programa lista as cidades disponíveis e solicita origem e destino. É possível informar o nome ou o ID de um nó. Em caso de entrada inválida, o programa pergunta se o usuário deseja tentar novamente.

## 7. Funcionamento do algoritmo

1. Todas as distâncias são inicializadas com infinito, exceto a origem, que recebe zero.
2. O algoritmo seleciona o nó não visitado com menor distância conhecida.
3. Avalia os vizinhos e atualiza as distâncias quando encontra um caminho menor.
4. Armazena o nó anterior para reconstruir a rota.
5. Finaliza ao alcançar o destino ou quando não há caminho disponível.

## 8. Posicionamento dos nós no mapa

Os nós são posicionados usando as coordenadas geográficas presentes em `polska.json`. O contorno do país e as coordenadas dos nós utilizam a mesma transformação cartográfica, mantendo os pontos alinhados ao mapa. As posições não são distribuídas artificialmente: cada nó permanece na localização indicada pela base de dados.

A imagem `mapa_polonia.png` serve como fundo geográfico. As conexões e os pesos utilizados no cálculo vêm dos dados da topologia, e não da imagem.

## 9. Detalhes do mapa

O mapa apresenta as 16 voivodias (regiões administrativas) da Polônia, com preenchimentos discretos e limites internos destacados. Os nós da rede são sobrepostos à imagem usando as coordenadas geográficas presentes em `polska.json` e a mesma transformação de longitude aplicada ao mapa.

O mapa é utilizado somente como referência visual. As divisões administrativas não alteram o grafo nem participam do cálculo: o Dijkstra utiliza exclusivamente os nós, as conexões e as distâncias da topologia SNDlib Polska.

## 10. Modelo da rede

A topologia é representada por um grafo não direcionado e ponderado:

- Nós representam pontos da rede.
- Arestas representam conexões.
- Pesos representam as distâncias em quilômetros.

## 11. Considerações finais

O projeto demonstra a aplicação do algoritmo de Dijkstra em uma topologia pública de telecomunicações, permitindo comparar rotas entre diferentes pares de nós e visualizar o caminho mínimo encontrado.
