# **Análise de Veículos Elétricos - Estado de Washington**

## **Introdução**

Este projeto realiza a limpeza, **transformação**, plotagem e análise dos dados de veículos elétricos (BEVs e PHEVs) registrados no estado de Washington. O objetivo é entender a adoção de tecnologias de transporte limpo e as tendências de mercado dos fabricantes.

## **Origem dos Dados**

Os dados são fornecidos pelo *Washington State Department of Licensing* (DOL) e estão disponíveis no portal de dados abertos do governo de Washington: [data.wa.gov](https://data.wa.gov). 

## **Objetivos Principais da Análise**

* **Crescimento temporal:** Como a adoção de EVs evoluiu ao longo dos anos?
* **Distribuição por Fabricante:** Quais marcas dominam a frota?
* **Autonomia Média:** Qual a evolução da capacidade das baterias por ano do modelo?
* **Localização:** Quais cidades possuem a maior densidade de veículos elétricos?

## **Documentações das Bibliotecas Utilizadas**

* [**Pandas**](https://pandas.pydata.org/docs/)
* [**Numpy**](https://numpy.org/doc/2.4/)
* [**Plotly**](https://plotly.com/python/)

---

## **Convenções Utilizadas**

* *Itálico:* Para palavras estrangeiras ou termos técnicos.
* **Negrito:** Para informações importantes.
* ~~Riscado:~~ Para valores, colunas ou elementos que foram posteriormente removidos ou transformados.

---

## **Explicação das Colunas**

Devido ao *dataset* original estar em inglês, traduzi e expliquei o significado de cada coluna para facilitar a compreensão:
 
* ~~VIN (1-10)~~: Referente aos primeiros dígitos do número do chassi.
* **County:** Condado em que o carro está registrado.
* **City:** Cidade em que o carro está registrado.
* ~~State~~: Estado do registro.
* ~~Postal Code~~: Código postal (similar ao CEP no Brasil).
* **Model Year:** Ano de fabricação do carro.
* **Make:** Fabricante/Montadora do veículo.
* **Model:** Modelo do carro.
* **Electric Vehicle Type:** Tipo do carro (BEV: Totalmente elétrico ou PHEV: Híbrido Plug-in).
* ~~Clean Alternative Fuel Vehicle (CAFV) Eligibility~~ (alterado para **CAFV Status**): Indica se o veículo é apto a receber incentivos fiscais (apenas veículos com autonomia superior ou igual a 30 milhas).
* **Electric Range:** Autonomia do carro (distância que percorre com uma carga completa).
* ~~Legislative District~~: Código referente ao distrito legislativo.
* ~~DOL Vehicle ID~~: Número de registro do veículo no *DOL* (*Department of Licensing*), órgão similar ao DETRAN no Brasil.
* ~~Vehicle Location~~: Localização do veículo por meio de coordenadas geográficas.
* **Electric Utility:** Companhia responsável pelo fornecimento de energia na região.
* ~~2020 Census Tract~~: Identificador numérico utilizado para fins de censo.

---

## **⚠️ Aviso sobre o Plotly!**

O **Plotly** possui uma característica de interatividade (zoom e filtros) quando executado em um ambiente *Jupyter*. Por esse motivo, é provável que, ao visualizar os *notebooks* diretamente pelo GitHub, os gráficos não sejam renderizados. 

Todas as imagens estão presentes na pasta `imagens`, porém recomendo fortemente rodar o projeto localmente ou em plataformas como o [**Google Colab**](https://colab.research.google.com/), para que você possa interagir com os dados (especialmente nos *scatter plots* e *treemap*).

---

## **Considerações Finais**

Este é o meu primeiro projeto publicado no GitHub, fruto de meses de estudo sobre *Python*, *Pandas* e Análise Exploratória de Dados (EDA). O projeto foca em limpeza, transformação e visualização; não inclui modelos de *Machine Learning* no momento, mas pretendo retornar a este *dataset* no futuro para aplicar modelos preditivos conforme meus conhecimentos avançarem.

Embora este *dataset* seja popular na comunidade de dados, este projeto foi desenvolvido de forma autoral, sem a consulta a outros códigos ou conclusões prontas, buscando uma abordagem única.

Espero que goste do conteúdo! Sinta-se livre para abrir ***issues*** sobre qualquer ponto, desde erros de grafia até sugestões técnicas. Como revisei o projeto por conta própria, toda contribuição para melhoria é bem-vinda.

---
