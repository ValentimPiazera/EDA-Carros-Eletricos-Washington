# Análise de Veículos Elétricos — Washington State

Este projeto realiza a limpeza, transformação, plotagem e análise exploratória (*EDA*) dos dados de veículos elétricos (BEVs e PHEVs) registrados no estado de Washington. O objetivo é entender a adoção de tecnologias de transporte limpo, a evolução da autonomia das baterias e as tendências de *marketshare* dos fabricantes.

---

## Origem dos Dados

Os dados são fornecidos pelo *Washington State Department of Licensing* (DOL) e estão disponíveis no portal de dados abertos do governo de Washington: [data.wa.gov](https://data.wa.gov).

O arquivo utilizado é o `Electric_Vehicle_Population_Data_20260122.csv`, com aproximadamente **271 mil registros** de veículos elétricos registrados no estado.

---

## Estrutura do Projeto

O projeto está dividido em dois *notebooks*:

| Notebook | Descrição |
| --- | --- |
| `01_limpeza.ipynb` | Exploração inicial, limpeza e transformação dos dados |
| `02_analise_eda.ipynb` | Visualizações, análises e *insights* |

---

## Objetivos da Análise

- **Crescimento temporal:** Como a adoção de EVs evoluiu ao longo dos anos?
- **Distribuição por fabricante:** Quais marcas dominam a frota?
- **Autonomia média:** Qual a evolução da capacidade das baterias por ano do modelo?
- **Localização:** Quais cidades possuem a maior densidade de veículos elétricos?
- ***Marketshare*:** Qual a fatia real de cada fabricante no mercado, em porcentagem?

---

## Etapas da Limpeza (`01_limpeza.ipynb`)

O *notebook* de limpeza cobre as seguintes etapas:

1. **Remoção de linhas inconsistentes** — 10 linhas com valores *NaN* em campos como cidade e condado foram removidas. Em um *dataframe* com ~271 mil linhas, essa perda é insignificante.
2. **Filtro geográfico** — Linhas fora do estado de Washington foram removidas (~1.000 registros), mantendo o foco da análise.
3. **Tratamento de autonomia zerada** — Valores `0` na coluna `Electric Range` foram substituídos por *NaN*, pois representam veículos recentes sem dados oficiais de autonomia registrados, e não valores reais.
4. **Remoção de colunas irrelevantes** — Foram descartadas: `VIN (1-10)`, `State`, `Postal Code`, `Legislative District`, `DOL Vehicle ID`, `Vehicle Location` e `2020 Census Tract`, por não contribuírem para os objetivos da análise.
5. **Criação da coluna `Vehicle Age`** — Calculada como `2026 - Model Year`, representando a idade do veículo em anos.
6. **Padronização de nomes** — A coluna `Clean Alternative Fuel Vehicle (CAFV) Eligibility` foi renomeada para `CAFV Status` e seus valores foram simplificados. Os tipos de veículo também foram abreviados para `BEV` e `PHEV`.
7. **Limpeza da coluna `Electric Utility`** — Remoção de sufixos como `INC`, `WA` e barras, além da padronização do nome da *Bonneville Power Administration*.
8. **Verificação de *outliers*** — Aplicado o método de quartis (IQR). *Outliers* identificados, como um Ford Ranger de 1999, foram mantidos por representarem dados verdadeiros dentro de um *dataset* abrangente.

---

## Análises e Visualizações (`02_analise_eda.ipynb`)

### Parte II — Visão Geral da Frota

| Figura | Gráfico | Descrição |
| --- | --- | --- |
| Fig. 1 | Barras horizontais | Top 10 marcas com mais veículos registrados |
| Fig. 2 | Pizza | Proporção entre BEVs e PHEVs na frota |
| Fig. 3 | Área | Curva de crescimento anual dos registros |
| Fig. 4 | Barras empilhadas | Correlação entre tipo de veículo e elegibilidade *CAFV* |
| Fig. 5 | Funil | Top 15 cidades com mais veículos registrados |

### Parte III — Autonomia e Evolução Tecnológica

| Figura | Gráfico | Período |
| --- | --- | --- |
| Fig. 6 | *Scatter plot* | 2015 – 2019 |
| Fig. 7 | *Scatter plot* | 2020 – 2026 |

Os *scatter plots* relacionam quantidade de registros com autonomia média por modelo, permitindo comparar a diversidade de tecnologias entre os dois períodos e identificar marcas dominantes.

### Parte IV — *Marketshare*

| Figura | Gráfico | Descrição |
| --- | --- | --- |
| Fig. 8 | *Treemap* | *Marketshare* geral por fabricante (em %) |

---

## Explicação das Colunas

Abaixo estão as colunas do *dataset* original. As ~~riscadas~~ foram removidas durante a limpeza; as **em negrito** foram utilizadas na análise.

| Coluna Original | Status | Descrição |
| --- | --- | --- |
| ~~VIN (1-10)~~ | Removida | Número do chassi do veículo |
| **County** | Mantida | Condado onde o veículo está registrado |
| **City** | Mantida | Cidade onde o veículo está registrado |
| ~~State~~ | Removida | Estado (todos são Washington) |
| ~~Postal Code~~ | Removida | Código postal, similar ao CEP no Brasil |
| **Model Year** | Mantida | Ano de fabricação do veículo |
| **Make** | Mantida | Montadora/fabricante |
| **Model** | Mantida | Modelo do veículo |
| **Electric Vehicle Type** | Mantida | Tipo: BEV (totalmente elétrico) ou PHEV (híbrido) |
| ~~Clean Alternative Fuel Vehicle (CAFV) Eligibility~~ → **CAFV Status** | Renomeada | Aptidão ao incentivo fiscal (exige autonomia ≥ 30 milhas / ~48 km) |
| **Electric Range** | Mantida | Autonomia em milhas com a bateria carregada |
| ~~Legislative District~~ | Removida | Código do distrito legislativo |
| ~~DOL Vehicle ID~~ | Removida | ID de registro no *Department of Licensing* (similar ao DETRAN) |
| ~~Vehicle Location~~ | Removida | Coordenadas geográficas do veículo |
| **Electric Utility** | Mantida | Fornecedor de energia elétrica associado ao veículo |
| ~~2020 Census Tract~~ | Removida | Código identificador da pesquisa censitária |
| **Vehicle Age** *(criada)* | Nova | Idade do veículo em anos (`2026 - Model Year`) |

---

## Convenções Utilizadas

- *Itálico:* palavras estrangeiras ou termos técnicos.
- **Negrito:** informações importantes.
- ~~Riscado:~~ colunas, valores ou elementos removidos durante o processo.

---

## Bibliotecas Utilizadas

| Biblioteca | Uso | Documentação |
| --- | --- | --- |
| Pandas | Manipulação e análise de dados | [pandas.pydata.org](https://pandas.pydata.org/docs/) |
| NumPy | Operações numéricas e tratamento de tipos | [numpy.org](https://numpy.org/doc/2.4/) |
| Plotly Express | Visualizações interativas | [plotly.com/python](https://plotly.com/python/) |
| Matplotlib | Suporte a visualizações auxiliares | [matplotlib.org](https://matplotlib.org/stable/index.html) |

---

## ⚠️ Aviso sobre os Gráficos (Plotly)

O *Plotly* gera gráficos **interativos** no *Jupyter Notebook* — é possível dar zoom, filtrar e explorar os dados diretamente no gráfico. Por esse motivo, ao visualizar os *notebooks* pelo GitHub, as figuras podem **não ser renderizadas**.

Todas as imagens estáticas estão salvas na pasta `/imagens`.

**Para a melhor experiência, recomenda-se rodar localmente, no Google Colab ou no Kaggle.**

> ⚠️ Para os *scatter plots* (Figs. 6 e 7) e o *treemap* (Fig. 8), **não é recomendado usar PNG** como exportação, pois esses gráficos perdem informação relevante no formato estático.

## ⚠️ Aviso base de dados

**Baixe a base de dados! Como novos dados são adcionados frequentemente, isso poderia "quebrar" certos comandos. Então decidi por baixar a versão isolado do dia que baixei, disponível na pasta `base_de_dados`**
