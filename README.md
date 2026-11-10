# Projeto: Caminho Mínimo em uma Rede de Telecomunicações

## 1. Sobre o projeto

Este projeto implementa o algoritmo de Dijkstra para encontrar o menor caminho entre dois nós de uma rede de telecomunicações, utilizando a topologia SNDlib Polska disponibilizada pela plataforma TopoHub.

O algoritmo de Dijkstra é implementado manualmente no arquivo `Main.py`. A biblioteca NetworkX é utilizada exclusivamente para construir e desenhar a representação visual do grafo, enquanto Matplotlib apresenta o mapa, os nós, as conexões e a rota calculada.

## 2. Objetivos

- Implementar o algoritmo de Dijkstra sem utilizar funções prontas de cálculo de menor caminho.
- Representar uma topologia de telecomunicações como um grafo não direcionado e ponderado.
- Permitir que o usuário escolha os nós de origem e destino pelo nome da cidade ou pelo ID.
- Calcular e exibir a menor rota e sua distância total.
- Destacar a rota encontrada sobre o mapa da Polônia.

## 3. Fontes dos dados

**Topologia da rede:** TopoHub — SNDlib Polska  
https://www.topohub.org/

O arquivo `polska.json` armazena os nós, suas identificações, nomes, coordenadas geográficas e as conexões da topologia com suas respectivas distâncias.

**Divisões administrativas:** geometrias GeoJSON das 16 voivodias da Polônia, disponibilizadas no repositório `andilabs/polska-wojewodztwa-geojson`.  
https://github.com/andilabs/polska-wojewodztwa-geojson

A imagem `assets/mapa_polonia.png` é utilizada como fundo geográfico da visualização. Ela apresenta o território da Polônia e suas divisões administrativas internas. O mapa é apenas uma referência visual: não fornece os pesos nem as conexões utilizados pelo algoritmo.

## 4. Tecnologias

- **Python:** implementação do algoritmo e lógica da aplicação.
- **NetworkX:** construção e desenho do grafo; não calcula a menor rota.
- **Matplotlib:** exibição do mapa e da visualização da rede.
- **JSON:** armazenamento local dos dados da topologia.

## 5. Estrutura do projeto

A estrutura efetiva da versão publicada na branch `main` é:

```text
otimizacao-caminhos-dijkstra/
├── Main.py
├── polska.json
├── requirements.txt
├── README.md
└── assets/
    └── mapa_polonia.png
```

O programa carrega `polska.json` e `assets/mapa_polonia.png` a partir de caminhos relativos à localização do próprio arquivo `Main.py`. Não é necessária uma pasta `dados/` nem um arquivo GML para executar a versão atual.

## 6. Instalação e execução

É necessário ter Python instalado. Abra o terminal na pasta do projeto e execute:

```bash
python -m pip install -r requirements.txt
python Main.py
```

O arquivo de dependências `requirements.txt` contém:

```text
networkx
matplotlib
```

O programa lista as cidades disponíveis e solicita os nós de origem e destino. É possível informar o nome da cidade ou o ID correspondente. Caso a entrada seja inválida, o sistema permite tentar novamente. Depois de apresentar o resultado e a visualização, também é possível calcular outra rota.

## 7. Funcionamento do algoritmo de Dijkstra

A função `dijkstra(grafo, origem, destino)`, implementada em `Main.py`, executa as seguintes etapas:

1. Inicializa a distância de todos os nós como infinito e define a distância da origem como zero.
2. Seleciona, entre os nós ainda não visitados, aquele que possui a menor distância conhecida.
3. Avalia os vizinhos do nó selecionado e atualiza suas distâncias quando encontra um caminho de menor custo.
4. Registra o nó anterior de cada atualização para permitir a reconstrução do caminho.
5. Encerra quando alcança o destino ou quando não há mais nós alcançáveis.
6. Reconstrói e retorna a rota encontrada e a distância total. Caso não exista caminho, informa que a rota não está disponível.

O cálculo é realizado pelo código do projeto. NetworkX é utilizado posteriormente para a representação visual da rede.

## 8. Modelo da rede

A topologia é representada como um grafo não direcionado e ponderado:

- **Nós:** representam os pontos da rede e estão identificados por IDs e nomes de cidades.
- **Arestas:** representam as conexões entre os pontos.
- **Pesos:** representam as distâncias das conexões, expressas em quilômetros.

Como o grafo é não direcionado, cada conexão é considerada nos dois sentidos durante a construção das listas de adjacência.

## 9. Posicionamento dos nós no mapa

Os nós são posicionados com base nas coordenadas geográficas registradas em `polska.json`. O código aplica um fator de correção à longitude (`cos(52°)`) para a representação visual e utiliza essas posições para desenhar os pontos e as conexões.

A imagem do mapa é exibida como fundo por meio de uma extensão geográfica definida no código. Assim, o mapa serve como referência para a visualização; os dados que determinam o cálculo continuam sendo os nós, as arestas e as distâncias armazenados no JSON.

## 10. Visualização do resultado

A visualização apresenta a topologia sobre o mapa da Polônia. As conexões da rede são desenhadas entre os nós, e os pesos das arestas são indicados em quilômetros.

Quando uma rota é calculada, suas conexões são destacadas em vermelho. A origem é identificada em verde, o destino em laranja e os demais nós pertencentes ao caminho em amarelo. Os outros pontos da rede permanecem em azul.

As 16 divisões administrativas aparecem somente no mapa de fundo e não interferem na estrutura do grafo nem no cálculo do menor caminho.

## 11. Considerações finais

O projeto demonstra a aplicação do algoritmo de Dijkstra em uma topologia pública de telecomunicações. A aplicação permite selecionar diferentes pares de cidades, calcular a rota de menor distância e visualizar o resultado sobre uma representação geográfica da Polônia.

A separação entre o cálculo do caminho e a visualização também evidencia que o algoritmo utiliza os dados da topologia, enquanto as bibliotecas gráficas são responsáveis apenas por apresentar a rede e o resultado.
