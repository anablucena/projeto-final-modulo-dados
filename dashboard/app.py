"""
app.py
Dashboard do Grupo 9 - Categorização dos Municípios Turísticos 2019.

Rodar com:
    streamlit run dashboard/app.py
"""
import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

sys.path.append(str(Path(__file__).resolve().parent))
from data import carregar_dados, indicadores_por_cluster, comparar_grupos_ab_de, ORDEM_CLUSTER, CORES_CLUSTER

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
    "População residente (IBGE/SIDRA, **2019** — ver limitação no rodapé)."
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
col3.metric("PIB per capita médio — Categoria A", f"R$ {pib_a:,.0f}".replace(",", "."))
col4.metric("PIB per capita médio — Categoria E", f"R$ {pib_e:,.0f}".replace(",", "."), delta=f"{razao_pib:.1f}x menor que A", delta_color="inverse")

st.markdown("---")

# ----------------------------------------------------------------------------
# Seção 1 — Quais municípios têm melhor desempenho?
# ----------------------------------------------------------------------------
st.header("1. Quais municípios tiveram melhor desempenho no turismo em 2019?")

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
    st.caption(
        "A maioria dos municípios do Mapa do Turismo estão nas categorias D e E"
    )

with col_dir:
    top_n = st.slider("Mostrar municípios com melhor desempenho", 5, 15, 10)
    top_a = (
        df_filtrado[df_filtrado["CLUSTER"] == "A"]
        .sort_values("ARRECADACAO", ascending=False)
        .head(top_n)[["MUNICIPIO", "UF", "ARRECADACAO", "PIB_PER_CAPITA_R$", "TOTAL_VISITAS_ESTIMADAS"]]
    )
    st.markdown(f"Ranking de municípios com melhor desempenho")
    st.dataframe(
        top_a.rename(columns={
            "MUNICIPIO": "Município", "UF": "UF",
            "ARRECADACAO": "Arrecadação (R$)",
            "PIB_PER_CAPITA_R$": "PIB per capita (R$)",
            "TOTAL_VISITAS_ESTIMADAS": "Visitas estimadas",
        }).style.format({
            "Arrecadação (R$)": "R$ {:,.0f}",
            "PIB per capita (R$)": "R$ {:,.0f}",
            "Visitas estimadas": "{:,.0f}",
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
    ("pib_per_capita_medio", "PIB per capita médio (R$)"),
    ("empregos_por_estab_medio", "Empregos por estabelecimento (médio)"),
    ("visitas_media", "Visitas estimadas (médio)"),
    ("arrecadacao_media", "Arrecadação média (R$)"),
]

cols = st.columns(4)
for (campo, titulo), col in zip(indicadores_plot, cols):
    with col:
        fig = px.bar(
            agg, x="CLUSTER", y=campo,
            color="CLUSTER", color_discrete_map=CORES_CLUSTER,
            title=titulo,
        )
        fig.update_layout(showlegend=False, height=320, xaxis_title="", yaxis_title="")
        st.plotly_chart(fig, use_container_width=True)

st.info(
    f"**Leitura dos dados:** municípios de categoria A têm, em média, PIB per capita "
    f"**{(agg.loc[agg.CLUSTER=='A','pib_per_capita_medio'].values[0] / agg.loc[agg.CLUSTER=='E','pib_per_capita_medio'].values[0]):.1f}x maior** "
    f"e recebem **{(agg.loc[agg.CLUSTER=='A','visitas_media'].values[0] / max(agg.loc[agg.CLUSTER=='D','visitas_media'].values[0], 1)):.0f}x mais visitas** "
    f"que a categoria D. Isso é uma **correlação**, não uma prova de causa — municípios "
    f"grandes e ricos podem atrair turismo por outros motivos (infraestrutura, "
    f"acesso, já serem polos regionais), não necessariamente o turismo é o que os "
    f"deixa ricos. Essa é uma hipótese a ser discutida na apresentação, não uma certeza."
)

st.markdown("---")

# ----------------------------------------------------------------------------
# Seção 3 — O que diferencia A/B de D/E?
# ----------------------------------------------------------------------------
st.header("3. O que diferencia um município de categoria A/B de um de categoria D/E?")

comparacao = comparar_grupos_ab_de(df_filtrado)
comparacao["Quantas vezes maior (A+B vs D+E)"] = (comparacao["A+B"] / comparacao["D+E"].replace(0, pd.NA)).round(1)

st.dataframe(
    comparacao.style.format({
        "A+B": "{:,.1f}",
        "D+E": "{:,.1f}",
        "Quantas vezes maior (A+B vs D+E)": "{:.1f}x",
    }),
    use_container_width=True,
)

fig_radar = go.Figure()
indicadores_radar = ["PIB per capita (R$)", "Empregos por estabelecimento", "Visitas estimadas (total)"]
for grupo, cor in [("A+B", CORES_CLUSTER["A"]), ("D+E", CORES_CLUSTER["E"])]:
    valores = comparacao.loc[indicadores_radar, grupo]
    valores_norm = valores / comparacao.loc[indicadores_radar].max(axis=1)  # normaliza 0-1 para caber no radar
    fig_radar.add_trace(go.Scatterpolar(
        r=list(valores_norm) + [valores_norm.iloc[0]],
        theta=indicadores_radar + [indicadores_radar[0]],
        fill="toself", name=grupo, line_color=cor,
    ))
fig_radar.update_layout(
    title="Comparação normalizada (0-1) entre grupos — quanto maior a área, melhor o indicador",
    polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
    showlegend=True, height=420,
)
st.plotly_chart(fig_radar, use_container_width=True)

st.success(
    "**Conclusão do grupo (hipótese apoiada pelos dados):** municípios de categoria A/B "
    "concentram muito mais empregos formais em hospedagem por estabelecimento, PIB per "
    "capita mais alto e recebem ordens de magnitude mais visitantes que municípios D/E. "
    "Isso sugere que **desempenho turístico está ligado a uma base econômica local mais "
    "forte e a uma estrutura de hospedagem mais profissionalizada** — não apenas à "
    "existência de um atrativo turístico."
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
        - **População**: IBGE/SIDRA (Tabela 793) — ano de referência **2019**.
          (base disponível mais antiga que a de 2019; usada aqui apenas como *proxy* de porte
          do município, não em cálculos per capita de 2019).
        - As variáveis usadas na categorização do MTur combinam diferentes anos-base
          (RAIS 2017, pesquisas de demanda doméstica 2012 e internacional 2017) — limitação
          da própria metodologia do Ministério do Turismo.
        - Correlações apresentadas neste dashboard **não implicam causalidade**.
        """
    )