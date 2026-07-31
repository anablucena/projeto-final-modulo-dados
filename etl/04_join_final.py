"""
04_join_final.py
Junta base_principal + PIB (2019) + população (2007, com ressalva) em uma
única base tratada, pronta para análise, e salva em bases_tratadas/.
"""
import sys
from pathlib import Path
import pandas as pd

sys.path.append(str(Path(__file__).resolve().parent))
from importlib import import_module

limpeza = import_module("02_limpeza")
padronizacao = import_module("03_padronizacao_chave")

PASTA_SAIDA = Path(__file__).resolve().parent.parent / "bases_tratadas"


def montar_base_final() -> pd.DataFrame:
    base_principal = limpeza.limpar_base_principal()
    pib = limpeza.limpar_pib()
    populacao = padronizacao.anexar_cod_ibge_na_populacao()

    populacao_final = populacao[["COD_IBGE", "POPULACAO_2007"]].dropna(subset=["COD_IBGE"])

    # 1) base_principal + PIB (ambas já usam código IBGE nativo -> junção direta)
    df = base_principal.merge(pib, on="COD_IBGE", how="left", indicator="_match_pib")
    sem_pib = (df["_match_pib"] == "left_only").sum()
    print(f"[join] {len(df) - sem_pib}/{len(df)} municípios da base principal casaram com o PIB "
          f"({sem_pib} sem PIB 2019 correspondente)")
    df = df.drop(columns="_match_pib")

    # 2) + população (via crosswalk nome+UF -> código IBGE construído no passo 3)
    df = df.merge(populacao_final, on="COD_IBGE", how="left", indicator="_match_pop")
    sem_pop = (df["_match_pop"] == "left_only").sum()
    print(f"[join] {len(df) - sem_pop}/{len(df)} municípios casaram com a população "
          f"({sem_pop} sem população correspondente)")
    df = df.drop(columns="_match_pop")

    # indicadores derivados úteis para a análise
    import numpy as np
    estabelecimentos = df["QUANTIDADE_ESTABELECIMENTOS"].replace(0, np.nan)
    df["EMPREGOS_POR_ESTABELECIMENTO"] = (df["QUANTIDADE_EMPREGOS"] / estabelecimentos).round(2)
    df["TOTAL_VISITAS_ESTIMADAS"] = df["VISITAS_INTERNACIONAIS_EST"] + df["VISITAS_NACIONAIS_EST"]

    # reordena colunas para facilitar leitura
    colunas_ordem = [
        "COD_IBGE", "MUNICIPIO", "UF", "REGIAO_TURISTICA", "CLUSTER",
        "QUANTIDADE_EMPREGOS", "QUANTIDADE_ESTABELECIMENTOS", "EMPREGOS_POR_ESTABELECIMENTO",
        "VISITAS_INTERNACIONAIS_EST", "VISITAS_NACIONAIS_EST", "TOTAL_VISITAS_ESTIMADAS",
        "ARRECADACAO",
        "PIB_PER_CAPITA_R$",
        "POPULACAO_2019",
    ]
    df = df[colunas_ordem]

    return df


def salvar_base_tratada(df: pd.DataFrame):
    PASTA_SAIDA.mkdir(exist_ok=True)
    caminho = PASTA_SAIDA / "base_final_tratada.csv"
    df.to_csv(caminho, index=False, encoding="utf-8-sig")
    print(f"\n[OK] Base tratada salva em: {caminho}")
    print(f"     {df.shape[0]} linhas x {df.shape[1]} colunas")


if __name__ == "__main__":
    base_final = montar_base_final()
    print("\nAmostra da base final:")
    print(base_final.head())
    print("\nValores ausentes por coluna:")
    print(base_final.isna().sum())
    salvar_base_tratada(base_final)