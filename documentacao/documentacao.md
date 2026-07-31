# DOCUMENTAÇÃO DO PROJETO

**Arquivo:** `bases_tratadas/base_final_tratada.csv`
**Tabela no Supabase:** `turismo_2019_indicadores_municipais`
**Nível:** município (2.694 municípios do Mapa do Turismo Brasileiro)
**Chave primária:** `COD_IBGE`
**Linhas × colunas:** 2.694 × 17

## Colunas

| Coluna | Origem | Descrição | Período |
|---|---|---|---|
| `COD_IBGE` | base_principal | Código IBGE do município (7 dígitos) | — |
| `MUNICIPIO` | base_principal | Nome do município | — |
| `UF` | base_principal | Sigla da unidade da federação | — |
| `MACRO` | base_principal | Macrorregião do Brasil | — |
| `REGIAO_TURISTICA` | base_principal | Região turística do Mapa do Turismo | — |
| `CLUSTER` | base_principal | Categoria de desempenho turístico (A = melhor, E = pior) | 2019 |
| `QUANTIDADE_EMPREGOS` | base_principal | Empregos formais em hospedagem | RAIS 2017 |
| `QUANTIDADE_ESTABELECIMENTOS` | base_principal | Estabelecimentos de hospedagem | RAIS 2017 |
| `EMPREGOS_POR_ESTABELECIMENTO` | calculado | Empregos ÷ estabelecimentos (porte médio da estrutura de hospedagem) | — |
| `VISITAS_INTERNACIONAIS_EST` | base_principal | Visitantes internacionais estimados | Pesquisa FIPE/MTur 2017 |
| `VISITAS_NACIONAIS_EST` | base_principal | Visitantes domésticos estimados | Pesquisa FIPE/MTur 2012 |
| `TOTAL_VISITAS_ESTIMADAS` | calculado | Soma de visitas nacionais + internacionais | — |
| `ARRECADACAO` | base_principal | Arrecadação de impostos federais sobre hospedagem (R$) | — |
| `PIB_PER_CAPITA_R$` | PIB dos Municípios (IBGE) | PIB per capita a preços correntes (R$) | 2019 |
| `VAB_SERVICOS_MIL_R$` | PIB dos Municípios (IBGE) | Valor adicionado bruto dos serviços privados (R$ mil) — exclui administração pública, defesa, educação e saúde públicas | 2019 |
| `ATIVIDADE_PRINCIPAL_PIB` | PIB dos Municípios (IBGE) | Setor com maior VAB no município | 2019 |
| `POPULACAO_2019` | populacao_residente.csv (IBGE/SIDRA) | População residente 

## Fontes originais

| Base | Arquivo | Fonte | Link |
|---|---|---|---|
| Principal | `base_principal.csv` | Categorização dos Municípios Turísticos 2019 — Ministério do Turismo | dados.turismo.gov.br |
| Complementar 1 | `PIB_dos_Municípios_-_base_de_dados_2010-2019.xls` | PIB dos Municípios 2019 — IBGE | sidra.ibge.gov.br |
| Complementar 2 | `populacao_residente.csv` | População residente 2019 (Tabela 793) — IBGE/SIDRA | sidra.ibge.gov.br |

## Chave de junção

- `base_principal` e `PIB dos Municípios` já compartilham o código IBGE de 7 dígitos —
  junção direta, **100% de correspondência** (2.694/2.694).

- `populacao_residente.csv` **não tem** código IBGE, só o texto `"Município (UF)"`. Para
  juntar com segurança, foi criado um *crosswalk* (nome normalizado + UF → código IBGE)
  usando a base de PIB como referência, já que ela cobre todos os 5.570 municípios do
  Brasil. Resultado: ~99,9% de correspondência nesse crosswalk (7 divergências de grafia
  corrigidas manualmente, ex.: "Assú" → "Açu", "Barão do Monte Alto" → "Barão de Monte
  Alto"). Ao final, **2.691/2.694 (99,9%)** dos municípios da base principal ficaram com
  população preenchida; 2 municípios ficam com `POPULACAO_2007` em branco.

## Limitações conhecidas

1. `EMPREGOS_POR_ESTABELECIMENTO` fica em branco quando o município tem 0
   estabelecimentos de hospedagem (807 casos) — divisão por zero é indefinida, tratada
   como ausente (`NaN`), não como erro.

2. 2 municípios ficaram sem população por divergência não
   mapeada manualmente (Graccho Cardoso/SE, Pingo-d'Água/MG).


