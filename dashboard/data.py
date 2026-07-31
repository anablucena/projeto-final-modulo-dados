"""
data.py
Funções de acesso e agregação de dados para o dashboard.
Tenta ler do banco Postgres (Supabase); se DATABASE_URL não estiver configurada
ou a conexão falhar, cai automaticamente para o CSV tratado local — assim o
dashboard nunca fica fora do ar por causa do banco.
"""
import os
from pathlib import Path

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

CAMINHO_CSV = Path(__file__).resolve().parent.parent / "bases_tratadas" / "base_final_tratada.csv"
NOME_TABELA = "base_final_tratada.csv"

# ordem lógica das categorias, do melhor para o pior desempenho turístico
ORDEM_CLUSTER = ["A", "B", "C", "D", "E"]

# paleta consistente: verde (melhor) -> vermelho (pior), usada em todo o dashboard
CORES_CLUSTER = {
    "A": "#1a7a3c",
    "B": "#78b83f",
    "C": "#e8c547",
    "D": "#e2823a",
    "E": "#c0392b",
}


@st.cache_data(ttl=3600, show_spinner="Carregando dados...")
def carregar_dados() -> pd.DataFrame:
    """Lê a base tratada do banco (Supabase); se falhar, usa o CSV local."""
    url = os.getenv("DATABASE_URL")
    if url:
        try:
            from sqlalchemy import create_engine
            engine = create_engine(url)
            df = pd.read_sql_table(NOME_TABELA, engine)
            return _preparar(df)
        except Exception as e:
            st.warning(f"Não foi possível ler do banco remoto ({e}). Usando o CSV local.")

    df = pd.read_csv(CAMINHO_CSV)
    return _preparar(df)


def _preparar(df: pd.DataFrame) -> pd.DataFrame:
    df["CLUSTER"] = pd.Categorical(df["CLUSTER"], categories=ORDEM_CLUSTER, ordered=True)
    return df


@st.cache_data
def indicadores_por_cluster(df: pd.DataFrame) -> pd.DataFrame:
    """Médias dos principais indicadores, agrupadas por categoria (A-E)."""
    agg = (
        df.groupby("CLUSTER", observed=True)
        .agg(
            n_municipios=("COD_IBGE", "count"),
            pib_per_capita_medio=("PIB_PER_CAPITA_R$", "mean"),
            empregos_por_estab_medio=("EMPREGOS_POR_ESTABELECIMENTO", "mean"),
            arrecadacao_media=("ARRECADACAO", "mean"),
            visitas_media=("TOTAL_VISITAS_ESTIMADAS", "mean"),
            populacao_media=("POPULACAO_2019", "mean"),
        )
        .reindex(ORDEM_CLUSTER)
        .round(1)
        .reset_index()
    )
    return agg


def comparar_grupos_ab_de(df: pd.DataFrame) -> pd.DataFrame:
    """Compara a média dos indicadores entre o grupo A+B (melhor) e D+E (pior)."""
    grupo = df["CLUSTER"].map({"A": "A+B", "B": "A+B", "C": None, "D": "D+E", "E": "D+E"})
    tmp = df.assign(GRUPO=grupo).dropna(subset=["GRUPO"])

    colunas = {
        "PIB_PER_CAPITA_R$": "PIB per capita (R$)",
        "EMPREGOS_POR_ESTABELECIMENTO": "Empregos por estabelecimento",
        "ARRECADACAO": "Arrecadação média (R$)",
        "TOTAL_VISITAS_ESTIMADAS": "Visitas estimadas (total)",
        "POPULACAO_2019": "População (2019)",
    }
    resultado = tmp.groupby("GRUPO", observed=True)[list(colunas.keys())].mean().rename(columns=colunas)
    resultado = resultado.reindex(["A+B", "D+E"]).round(1)
    return resultado.T