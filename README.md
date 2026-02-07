# Introdução

 Este projeto realiza uma limpeza, transformação, plotagem e análise dos dados de veículos elétricos (BEVs e PHEVs) registrados no estado de Washington. O objetivo é entender a adoção de tecnologias de transporte limpo e as tendências de mercado dos fabricantes.

---
## Origem dos Dados

 Os dados são fornecidos pelo Washington State Department of Licensing (DOL) e estão disponíveis no portal de dados abertos do governo de Washington: [Site do governo de Washington](data.wa.gov). 

---
## Objetivos Principais da Análise

 **Crescimento temporal:** Como a adoção de EVs evoluiu ao longo dos anos?

 **Distribuição por Fabricante:** Quais marcas dominam a frota?

 **Autonomia Média:** Qual a evolução da capacidade das baterias por ano do modelo?

 **Localização:** Quais cidades possuem a maior densidade de veículos elétricos?

 ---

## Documentações das Bibliotecas Utilizadas

 * [Pandas](https://pandas.pydata.org/docs/)
 * [Numpy](https://numpy.org/doc/2.4/)
 * [Plotly](https://plotly.com/python/)

---

## Convenções Utilizadas

*Itálico:* Para palavras estrangeiras ou termos técnicos.

**Negrito:** Para informações importantes.

~~Riscado:~~ Para valores, colunas ou qualquer coisa que posteriormente removido.

---
## Explicação das Colunas:
 Devido ao *dataset* original ser em inglês achei de nescessário traduzir e apontar o significado de cada coluna.
 
~~VIN (1-10)~~: Referente ao número do chassi.

**County:** Referente ao condado em que o carro está registrado.

**City:** Referente a cidade em que o carro está registrado.

~~State~~: Referente ao estado em que o carro está registrado.

~~Postal Code~~: Referente ao código postal registrado ao veículo, similar ao CEP no Brasil.

**Model Year:** Ano de fabricação do carro.

**Make:** Referente a montadora do veículo.

**Model:** Modelo do carro.

**Electric Vehicle Type:** Tipo do carro (BEV: Totalmente elétrico ou PHEV: Híbrido).

~~Clean Alternative Fuel Vehicle (CAFV) Eligibility~~(depois trocado para o nome: **CAFV Status**): O veículo é apto a receber o incentivo fiscal? apenas veículos com autonomia superior ou igual a 30 milhas se encaixam.

**Electric Range:** Autonomia do carro, o quanto ele percorre até a bateria acabar.

~~Legislative District~~: Número/código referente ao distrito legislativo.

~~DOL Vehicle ID~~: Número de registro do veículos no *DOL*(*Departament of Licensing*, **Departamento de Licenciamento em 
portugês**), muito similar ao DETRAN no Brasil.
~~Vehicle Location~~: Localização do veículo por meio de cordenadas

**Electric Utility:** Companhia ou local responsável pelo fornecimento de energia aos carros.

~~2020 Census Tract~~: Um número da própria pesquisa para identificar as linhas, como um código de barras.

---

## Aviso Plotly!

 O Plotly possui uma característica única quando rodado no terminal do *jupyter*, ele permite dar zoom e interagir com os gráficos, por esse motivo é bem provável que ao visualizar os *notebooks* pelo github as imagens não aparecerem, mas todas estão presentes na pasta imagens, porém recomendo rodar localmente em sua máquina ou em uma plataforma como o [**Google Colab**](https://colab.research.google.com/), pois as imagens são estáticas (recomendo fortemente não usar o *png* para os *scatter plots* e *treemaps*).

---
## Fim

Bem esses foram todos os avisos, espero que goste do conteúdo a seguir, se trata do meu primeiro projeto feito com intenção de postar no *Github* após meses de estudo sobre *python*, *pandas*, *plotagem* e assuntos nescessários para uma *EDA*. O projeto possui "apenas" limpeza, transformação, plotagem e análises dos dados, não possui um modelo de *Machine learning*, pois embora muito goste e admire a área, pouco sei sobre; talvez no futuro com os conhecimentos nescessários posso retornar a esse projeto e fazer um modelo de predição.

Sei que esse *dataset* é muito popular entre a comunidade de dados, porém não consultei ou peguei emprestado nenhum trecho de código, conclusão ou ideia de nenhum outro projeto, nem sequer verifiquei outros projetos com o mesmo *dataset*, pois queria que fosse algo único (embora devem existir projetos muito melhores do que esse).

É isso, aproveite o projeto a seguir, também sinta-se livre para subir *issues* sobre o projeto, qualquer coisa mesmo, seja um simples erro de grafia ou até um erro mais grave (Visto que fiz tudo por conta própria, e por mais que revise muitas vezes, algo irá passar despercebido).

---



