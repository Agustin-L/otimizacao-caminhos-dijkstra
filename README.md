# Projeto: Caminho Mínimo em uma Rede de Telecomunicações

## 1. Sobre o projeto

Este projeto tem como objetivo implementar e demonstrar o funcionamento do algoritmo de **Dijkstra** para encontrar o menor caminho entre dois nós de uma rede de telecomunicações.

Para a realização dos testes, é utilizada uma topologia real de rede, disponibilizada publicamente pela plataforma **TopoHub**, baseada no conjunto de dados SNDlib Polska.

O algoritmo de Dijkstra foi desenvolvido manualmente pelo grupo, enquanto a biblioteca NetworkX é utilizada exclusivamente para a representação visual da rede, sem participar do cálculo das rotas.

## 2. Objetivos

- Implementar o algoritmo de Dijkstra para encontrar caminhos mínimos.
- Trabalhar com uma topologia real de telecomunicações.
- Representar uma rede por meio de um grafo ponderado.
- Calcular a menor distância entre dois nós escolhidos pelo usuário.
- Exibir graficamente a rede e destacar o caminho encontrado.

## 3. Fonte dos dados

Os dados utilizados são provenientes da plataforma:

**TopoHub – SNDlib Polska**

https://www.topohub.org/

Identificador da topologia utilizada:

```python
topohub.get("sndlib/polska")
```

A topologia contém nós e conexões com pesos associados, utilizados como distâncias entre os pontos da rede.

## 4. Tecnologias e bibliotecas

| Tecnologia | Finalidade |
|---|---|
| Python | Linguagem de programação |
| TopoHub | Carregamento da topologia |
| NetworkX | Visualização e representação do grafo |
| Matplotlib | Exibição gráfica da rede |
| Math | Utilização de valores infinitos no algoritmo |

**Observação:** NetworkX não é utilizado para executar o algoritmo de Dijkstra. Toda a lógica de busca pelo menor caminho foi implementada pelo grupo.

## 5. Estrutura do projeto

```text
projeto_dijkstra/
│
├── main.py
├── README.md
└── requirements.txt
```

## 6. Instalação

É necessário ter Python instalado na máquina.

### 6.1. Clonar o repositório

```bash
git clone URL_DO_REPOSITORIO
```

Entre na pasta do projeto:

```bash
cd projeto_dijkstra
```

### 6.2. Instalar as dependências

Execute:

```bash
pip install -r requirements.txt
```

Caso prefira instalar individualmente:

```bash
pip install topohub networkx matplotlib
```

## 7. Execução

Após instalar as dependências, execute:

```bash
python main.py
```

No Windows, também é possível utilizar:

```bash
py main.py
```

O programa carregará a topologia e apresentará os nós disponíveis para seleção.

O usuário poderá informar a cidade de origem e a cidade de destino.

Exemplo:

```text
Cidade de origem [Gdansk]: Gdansk
Cidade de destino [Warsaw]: Warsaw
```

O programa executará o algoritmo e apresentará:

- Origem e destino selecionados;
- Menor caminho encontrado;
- Quantidade de conexões utilizadas;
- Distância total da rota;
- Representação gráfica da rede.

## 8. Funcionamento do algoritmo de Dijkstra

O algoritmo de Dijkstra é utilizado para encontrar o caminho de menor custo entre um nó de origem e os demais nós de um grafo com pesos não negativos.

A implementação desenvolvida pelo grupo funciona nas seguintes etapas:

1. Inicialização: todas as distâncias recebem infinito, exceto a origem, que recebe zero.
2. Seleção: é escolhido o nó não visitado com a menor distância conhecida.
3. Relaxamento: são verificadas as conexões com os vizinhos para identificar possíveis caminhos menores.
4. Atualização: caso seja encontrado um caminho menor, a distância e o nó anterior são atualizados.
5. Finalização: o processo continua até alcançar o destino ou não existirem mais caminhos possíveis.
6. Reconstrução: o caminho é recuperado utilizando os nós anteriores armazenados durante a execução.

## 9. Representação da rede

A rede é representada como um grafo não direcionado e ponderado.

- **Nós:** representam os pontos da rede de telecomunicações.
- **Arestas:** representam as conexões entre os pontos.
- **Pesos:** representam as distâncias associadas às conexões.

A visualização gráfica apresenta todas as conexões e destaca o menor caminho encontrado pelo algoritmo.

## 10. Considerações finais

O projeto demonstra a aplicação prática do algoritmo de Dijkstra em uma topologia real de telecomunicações.

A implementação própria permite compreender as etapas de inicialização, seleção, atualização de distâncias e reconstrução do caminho mínimo.

A utilização de dados públicos aproxima o exercício de um cenário real, permitindo testar diferentes origens e destinos dentro da rede.

---
**Algoritmo:** Dijkstra  
**Base de dados:** SNDlib Polska  
**Linguagem:** Python
