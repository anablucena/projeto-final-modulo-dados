# Projeto Final — Módulo de Dados | Grupo 9

## Objetivo do projeto

Investigar **quais municípios brasileiros apresentaram o melhor desempenho no turismo em
2019 e o que pode explicar esse resultado**.

## Pergunta investigada

> Quais municípios apresentavam melhor desempenho no turismo em 2019 e o que pode
> explicar esse resultado?

## Integrantes do grupo

- Ana Beatriz Vital 
- André Tiago Closs 
- Murilo Rodrigues Santos

## Ferramentas usadas

| Etapa | Ferramenta |
|---|---|
| ETL / tratamento de dados | Python 3.12, pandas, openpyxl/xlrd |
| Dashboard | Streamlit, Plotly |
| Ambiente de desenvolvimento | VSCode |
| Controle de versão | Git / GitHub |

## Fontes de dados

| Base | Fonte | Período |
|---|---|---|
| Categorização dos Municípios Turísticos 2019 (principal) | Ministério do Turismo | 2019 |
| PIB dos Municípios | IBGE | 2019 |
| População Residente (Tabela 793) | IBGE/SIDRA | 2019 |

## Como executar o projeto

### 1. Pré-requisitos

- Python 3.12

### 2. Configurar o ambiente
```bash
cd projeto_final_modulo_dados

python -m venv venv

source venv/Scripts/activate


pip install -r requirements.txt
```

### 3. Rodar o ETL (gera a base tratada)
```bash
python etl/main.py
```

### 5. Rodar o dashboard
```bash
streamlit run dashboard/app.py
```

