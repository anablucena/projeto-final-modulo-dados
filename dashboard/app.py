import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

sys.path.append(str(Path(__file__).resolve().parent))
from data import carregar_dados, indicadores_por_cluster, ORDEM_CLUSTER, CORES_CLUSTER

# ----------------------------------------------------------------------------
# Configuração da página
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="Turismo Brasil 2019 — Grupo 9",
    page_icon="🏖️",
    layout="wide",
)

st.title("Desempenho Turístico dos Municípios Brasileiros - 2019")
st.markdown(
    "Categorização de **2.694 municípios** do Mapa do Turismo Brasileiro "
    "(Ministério do Turismo), cruzada com PIB per capita, empregos e "
    "população para investigar o que diferencia os melhores dos piores "
    "desempenhos turísticos do país."
)

df = carregar_dados()

# ----------------------------------------------------------------------------
# Filtros (barra lateral)
# ----------------------------------------------------------------------------
st.sidebar.header("Filtros")

ufs = sorted(df["UF"].dropna().unique())
uf_sel = st.sidebar.multiselect("UF", ufs, default=ufs)

clusters_sel = st.sidebar.multiselect(
    "Categoria (CLUSTER)", ORDEM_CLUSTER, default=ORDEM_CLUSTER
)

df_filtrado = df[df["UF"].isin(uf_sel) & df["CLUSTER"].isin(clusters_sel)]

if df_filtrado.empty:
    st.warning("Nenhum município para os filtros selecionados. Ajuste os filtros na barra lateral.")
    st.stop()

st.sidebar.markdown("---")
st.sidebar.caption(
    "Fontes: Categorização MTur 2019 · PIB dos Municípios (IBGE, 2019) · "
    "População residente (IBGE/SIDRA, **2007** — ver limitação no rodapé)."
)

# ----------------------------------------------------------------------------
# KPIs principais
# ----------------------------------------------------------------------------
total_municipios = len(df_filtrado)
pct_a = (df_filtrado["CLUSTER"] == "A").mean() * 100
pib_a = df_filtrado.loc[df_filtrado["CLUSTER"] == "A", "PIB_PER_CAPITA_R$"].mean()
pib_e = df_filtrado.loc[df_filtrado["CLUSTER"] == "E", "PIB_PER_CAPITA_R$"].mean()
razao_pib = (pib_a / pib_e) if pib_e and pib_e > 0 else float("nan")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Municípios analisados", f"{total_municipios:,}".replace(",", "."))
col2.metric("Em categoria A", f"{(df_filtrado['CLUSTER']=='A').sum()}", f"{pct_a:.1f}% do total")
col3.metric("PIB per capita — Categoria A", f"R$ {pib_a:,.0f}".replace(",", "."))
col4.metric(
    "PIB per capita — Categoria E",
    f"R$ {pib_e:,.0f}".replace(",", "."),
    delta=f"{razao_pib:.1f}x menor que A",
    delta_color="inverse",
)

st.markdown("---")

# ----------------------------------------------------------------------------
# Seção 1 — Quais municípios têm melhor desempenho?
# ----------------------------------------------------------------------------
st.header("1. Quais municípios tiveram melhor desempenho no turismo em 2019?")

# --- Destaque: São Paulo, o município de maior desempenho ---------------
sp = df_filtrado[(df_filtrado["MUNICIPIO"] == "São Paulo") & (df_filtrado["UF"] == "SP")]

if not sp.empty:
    sp = sp.iloc[0]
    media_geral = df_filtrado[["ARRECADACAO", "PIB_PER_CAPITA_R$", "TOTAL_VISITAS_ESTIMADAS"]].mean()
    rank_arrecadacao = df_filtrado.sort_values("ARRECADACAO", ascending=False).reset_index(drop=True)
    posicao_sp = rank_arrecadacao.index[rank_arrecadacao["MUNICIPIO"] == "São Paulo"][0] + 1

    with st.container(border=True):
        col_titulo, col_badge = st.columns([3, 1])
        with col_titulo:
            st.markdown("### 🏆 São Paulo (SP)")
            st.caption("Município de maior desempenho turístico do país em 2019 — Categoria A")
        with col_badge:
            st.markdown(
                f"<div style='text-align:right; font-size:1.3rem; font-weight:700; color:#1a7a3c;'>"
                f"#{posicao_sp} do Brasil</div>",
                unsafe_allow_html=True,
            )

        c1, c2, c3, c4 = st.columns(4)
        c1.metric(
            "Arrecadação",
            f"R$ {sp['ARRECADACAO']/1e6:,.1f} mi",
            f"{sp['ARRECADACAO']/media_geral['ARRECADACAO']:.0f}x a média nacional",
        )
        c2.metric(
            "Visitas estimadas (total)",
            f"{sp['TOTAL_VISITAS_ESTIMADAS']:,.0f}".replace(",", "."),
            f"{sp['TOTAL_VISITAS_ESTIMADAS']/media_geral['TOTAL_VISITAS_ESTIMADAS']:.0f}x a média nacional",
        )
        c3.metric(
            "PIB per capita",
            f"R$ {sp['PIB_PER_CAPITA_R$']:,.0f}".replace(",", "."),
            f"{sp['PIB_PER_CAPITA_R$']/media_geral['PIB_PER_CAPITA_R$']:.1f}x a média nacional",
        )
        c4.metric(
            "Empregos por estabelecimento",
            f"{sp['EMPREGOS_POR_ESTABELECIMENTO']:.1f}",
            "estrutura de hospedagem mais profissionalizada",
            delta_color="off",
        )
    st.markdown("")

col_esq, col_dir = st.columns([1, 1.3])

with col_esq:
    contagem = df_filtrado["CLUSTER"].value_counts().reindex(ORDEM_CLUSTER).fillna(0).reset_index()
    contagem.columns = ["CLUSTER", "n_municipios"]
    fig_contagem = px.bar(
        contagem, x="CLUSTER", y="n_municipios",
        color="CLUSTER", color_discrete_map=CORES_CLUSTER,
        text="n_municipios",
        title="Número de municípios por categoria",
        labels={"n_municipios": "Nº de municípios", "CLUSTER": "Categoria (CLUSTER)"},
    )
    fig_contagem.update_traces(textposition="outside")
    fig_contagem.update_layout(showlegend=False, yaxis_title="Nº de municípios")
    st.plotly_chart(fig_contagem, use_container_width=True)
    st.caption("A maioria dos municípios do Mapa do Turismo estão nas categorias D e E.")

with col_dir:
    top_n = st.slider("Mostrar top N municípios", 5, 30, 10)
    top_a = (
        df_filtrado[df_filtrado["CLUSTER"] == "A"]
        .sort_values("ARRECADACAO", ascending=False)
        .head(top_n)[["MUNICIPIO", "UF", "ARRECADACAO", "PIB_PER_CAPITA_R$", "TOTAL_VISITAS_ESTIMADAS", "POPULACAO_2007"]]
    )
    st.markdown("**Ranking de municípios com melhor desempenho**")
    st.dataframe(
        top_a.rename(columns={
            "MUNICIPIO": "Município", "UF": "UF",
            "ARRECADACAO": "Arrecadação (R$)",
            "PIB_PER_CAPITA_R$": "PIB per capita (R$)",
            "TOTAL_VISITAS_ESTIMADAS": "Visitas estimadas",
            "POPULACAO_2007": "População (2007)",
        }).style.format({
            "Arrecadação (R$)": "R$ {:,.0f}",
            "PIB per capita (R$)": "R$ {:,.0f}",
            "Visitas estimadas": "{:,.0f}",
            "População (2007)": "{:,.0f}",
        }),
        use_container_width=True,
        hide_index=True,
    )

st.markdown("---")

# ----------------------------------------------------------------------------
# Seção 2 — O que explica esse resultado?
# ----------------------------------------------------------------------------
st.header("2. O que pode explicar esse resultado?")
st.markdown(
    "Comparando a **média de cada indicador por categoria**, dá para ver quais fatores "
    "acompanham o desempenho turístico e quais não."
)

agg = indicadores_por_cluster(df_filtrado)

indicadores_plot = [
    ("pib_per_capita_medio", "PIB per capita (R$)"),
    ("populacao_media", "População (2007)"),
    ("visitas_media", "Visitas estimadas"),
    ("arrecadacao_media", "Arrecadação (R$)"),
]

cols = st.columns(4)
for (campo, titulo), col in zip(indicadores_plot, cols):
    with col:
        fig = px.bar(
            agg, x="CLUSTER", y=campo,
            color="CLUSTER", color_discrete_map=CORES_CLUSTER,
            title=titulo,
        )
        # eixo e hover com o MESMO formato (número cheio, sem abreviação
        # ambígua tipo "M"/"k" que não bate entre si) -> evita confusão de escala
        fig.update_yaxes(tickformat=",.0f")
        fig.update_traces(hovertemplate="Categoria %{x}<br>%{y:,.0f}<extra></extra>")
        fig.update_layout(showlegend=False, height=320, xaxis_title="", yaxis_title="")
        st.plotly_chart(fig, use_container_width=True)

st.info(
    f"Municípios de categoria A têm, em média, PIB per capita "
    f"**{(agg.loc[agg.CLUSTER=='A','pib_per_capita_medio'].values[0] / agg.loc[agg.CLUSTER=='E','pib_per_capita_medio'].values[0]):.1f}x maior** "
    f"e recebem **{(agg.loc[agg.CLUSTER=='A','visitas_media'].values[0] / max(agg.loc[agg.CLUSTER=='D','visitas_media'].values[0], 1)):.0f}x mais visitas** "
    f"que a categoria D. Isso é uma **correlação**, não uma prova de causa — municípios "
    f"grandes e ricos podem atrair turismo por outros motivos (infraestrutura, acesso, já "
    f"serem polos regionais), não necessariamente é o turismo que os deixa ricos. Essa é uma "
    f"hipótese a ser discutida na apresentação, não uma certeza."
)

# ----------------------------------------------------------------------------
# Rodapé — fontes, período e limitações
# ----------------------------------------------------------------------------
st.markdown("---")
with st.expander("📋 Fontes, período e limitações dos dados"):
    st.markdown(
        """
        - **Base principal**: Categorização dos Municípios Turísticos 2019 — Ministério do Turismo.
        - **PIB per capita**: PIB dos Municípios — IBGE, ano de referência **2019**.
        - **População**: IBGE/SIDRA (Tabela 793) — ano de referência **2007**
          (base disponível mais antiga que a de 2019; usada aqui apenas como *proxy* de porte
          do município, não em cálculos per capita de 2019).
        - As variáveis usadas na categorização do MTur combinam diferentes anos-base
          (RAIS 2017, pesquisas de demanda doméstica 2012 e internacional 2017) — limitação
          da própria metodologia do Ministério do Turismo.
        - Correlações apresentadas neste dashboard **não implicam causalidade**.
        """
    )