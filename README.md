# **Introdução**

 Este projeto realiza uma limpeza, modelagem e análise dos dados de veículos elétricos (BEVs e PHEVs) registrados no estado de Washington. O objetivo é entender a adoção de tecnologias de transporte limpo e as tendências de mercado dos fabricantes.

## **Origem dos Dados**

 Os dados são fornecidos pelo Washington State Department of Licensing (DOL) e estão disponíveis no portal de dados abertos do governo de Washington: [Site do governo de Washington](data.wa.gov). 
O dataset contém informações sobre:

 **Localização geográfica:** Cidade,
condado e código postal (Equivalente ao CEP no Brasil).

 **Detalhes do veículo:** Marca, modelo e ano.

 **Especificações técnicas:** Autonomia elétrica, elegibilidade de incentivos combustíveis alternativos e fornecedor de energia.

## **Objetivos da Principais da Análise**

 **Crescimento temporal:** Como a adoção de EVs evoluiu ao longo dos anos?

 **Distribuição por Fabricante:** Quais marcas dominam a frota?

 **Autonomia Média:** Qual a evolução da capacidade das baterias por ano do modelo?

 **Localização:** Quais cidades possuem a maior densidade de veículos elétricos?

## **Documentações das Bibliotecas Utilizadas**

 ### [**Pandas**](https://pandas.pydata.org/docs/)


### [**Numpy**](https://numpy.org/doc/2.4/)


### [**Plotly**](https://plotly.com/python/)

## Convenções Utilizadas

*Itálico:* Para palavras estrangeiras ou termos técnicos.
*Negrito:** Para informações importantes.
~~Riscado:~~ Para valores, colunas ou qualquer coisa que posteriormente removido.

## Banco de Palavras e Colunas:
 Devido ao *dataset* original ser em inglês achei de bom grado traduzir e apontar o significado de cada coluna; Além de um banco de palavras para as que estão em *Itálico* ao longo dos *notebooks*:

 ### Colunas
 
    ~~VIN (1-10)~~: Referente ao número do chassi.
    **County:** Referente ao condado em que o carro está registrado.
    **City:** Referente a cidade em que o carro está registrado.
    ~~State~~: Referente ao estado em que o carro está registrado.
    ~~Postal Code~~: Referente ao código postal registrado ao veículo, similar ao CEP no Brasil.
    **Model Year:** Ano de fabricação do carro.
    **Make:** Referente a montadora do veículo.
    **Model:** Modelo do carro.
    **Electric Vehicle Type:** Tipo do carro (BEV ou PHEV)
    ~~Clean Alternative Fuel Vehicle (CAFV) Eligibility~~(depois trocado para o nome: **CAFV Status**): Qual tipo de combustível alternativo o automóvel é compatível.
    **Electric Range:** Autonomia do carro, o quanto ele percorre até a bateria acabar.
    ~~Legislative District~~: Número/código referente ao distrito legislativo.
    ~~DOL Vehicle ID~~: Número de registro do veículos no *DOL*(*Departament of Licensing*, **Departamento de Licenciamento em portugês**), muito similar ao DETRAN no Brasil.
    ~~Vehicle Location~~: Localização do veículo por meio de cordenadas
    **Electric Utility:** Companhia ou local responsável pelo fornecimento de energia aos carros.
    ~~2020 Census Tract~~: Um número da própria pesquisa para identificar as linhas, como um código de barras.

