# Otimização de Caminhos em Redes de Telecomunicações com Dijkstra

Projeto acadêmico de Pesquisa Operacional que utiliza o **algoritmo de
Dijkstra** para encontrar o caminho de menor custo entre dois pontos de
uma rede de telecomunicações.

A rede é representada por um grafo: - **Vértices (nós):** representam os
pontos da rede. - **Arestas:** representam as conexões entre os
pontos. - **Peso da aresta:** representa a distância da conexão, em
quilômetros.

## 1. Requisitos

Antes de executar o projeto, é necessário ter instalado:

-   Python 3;
-   pip (gerenciador de pacotes do Python).

Para conferir se o Python está instalado, abra o terminal e execute:

``` bash
python --version
```

Para conferir o pip:

``` bash
pip --version
```

> No Windows, caso o comando `python` não funcione, tente
> `py --version`.

## 2. Baixar o projeto

Clone o repositório:

``` bash
git clone https://github.com/SEU-USUARIO/otimizacao-caminhos-dijkstra.git
```

Entre na pasta:

``` bash
cd otimizacao-caminhos-dijkstra
```

Se preferir, também é possível baixar o projeto pelo GitHub usando
**Code \> Download ZIP**. Depois, extraia o arquivo e abra a pasta no
terminal ou no VS Code.

## 3. Instalar as bibliotecas

O projeto utiliza as seguintes bibliotecas externas:

  Biblioteca     Finalidade
  -------------- --------------------------------------------------
  `topohub`      Obter os dados da topologia da rede
  `networkx`     Organizar o grafo utilizado na visualização
  `matplotlib`   Desenhar o grafo e destacar o caminho encontrado

Instale todas de uma vez, dentro da pasta do projeto:

``` bash
pip install -r requirements.txt
```

O arquivo `requirements.txt` deve conter:

``` txt
topohub
networkx
matplotlib
```

Também é possível instalar as bibliotecas diretamente:

``` bash
pip install topohub networkx matplotlib
```

A biblioteca `math`, utilizada em operações matemáticas pelo código, já
faz parte da biblioteca padrão do Python e não precisa ser instalada.

### (Opcional) Criar um ambiente virtual

É recomendado criar um ambiente virtual para manter as dependências do
projeto separadas de outros projetos Python.

No Windows:

``` bash
python -m venv venv
venv\Scripts\activate
```

No Linux ou macOS:

``` bash
python3 -m venv venv
source venv/bin/activate
```

Depois de ativar o ambiente virtual, instale as dependências:

``` bash
pip install -r requirements.txt
```

## 4. Executar o projeto

Com as bibliotecas instaladas, execute:

``` bash
python main.py
```

O programa carrega a topologia, solicita o ponto de origem e o ponto de
destino, calcula o caminho de menor distância usando Dijkstra e
apresenta o resultado. A visualização do grafo destaca o caminho
encontrado.

Caso o programa apresente opções padrão para origem e destino, elas
podem ser utilizadas pressionando Enter. Os nomes informados devem
corresponder aos nós disponíveis na topologia carregada.

## 5. Como o algoritmo funciona

O algoritmo de Dijkstra calcula os menores caminhos a partir de um
vértice de origem em um grafo com pesos não negativos.

De forma resumida, ele:

1.  Define a distância da origem como zero e as demais como infinito.
2.  Seleciona o nó ainda não processado com a menor distância conhecida.
3.  Verifica seus vizinhos e tenta melhorar as distâncias calculadas.
4.  Registra o nó anterior sempre que encontra um caminho melhor.
5.  Repete o processo até concluir a busca.
6.  Reconstrói o caminho entre a origem e o destino.

A atualização de distância é representada por:

``` text
nova_distancia = distancia_atual + peso_da_aresta
```

Se a nova distância for menor que a distância registrada para o vizinho,
o valor é atualizado.

## 6. Estrutura do projeto

``` text
otimizacao-caminhos-dijkstra/
│
├── main.py
├── requirements.txt
├── README.md
├── .gitignore
│
└── docs/
    └── Guia_Dijkstra_Checkpoint_12_11.docx
```

-   `main.py`: código principal, carregamento da rede, algoritmo e
    visualização.
-   `requirements.txt`: bibliotecas necessárias para executar o projeto.
-   `README.md`: documentação e instruções de execução.
-   `.gitignore`: arquivos e pastas que não devem ser enviados ao Git.
-   `docs/`: documentos de apoio do projeto.

## 7. Problemas comuns

**Erro: `python` não é reconhecido**

Verifique se o Python está instalado e adicionado ao PATH. No Windows,
tente utilizar `py` no lugar de `python`.

**Erro: `No module named ...`**

As dependências não foram instaladas no ambiente Python utilizado para
executar o projeto. Ative o ambiente virtual, se estiver usando um, e
execute:

``` bash
pip install -r requirements.txt
```

**Erro ao carregar a topologia**

A obtenção dos dados depende do acesso ao serviço do TopoHub e da
disponibilidade da topologia utilizada. Verifique a conexão com a
internet e se a biblioteca e o formato dos dados continuam compatíveis
com o código.

**Origem ou destino não encontrado**

Confira se o nome digitado corresponde exatamente a um nó existente na
topologia.

## 8. Integrantes

-   Agustin Penelas
-   Agustin Cancino
-   Gabriel Valenga

------------------------------------------------------------------------

**Observação:** este README descreve a execução prevista para o código
do projeto. Antes da apresentação, o grupo deve testar a instalação das
dependências, o carregamento real da topologia e a execução completa em
outro computador ou ambiente, se possível.
