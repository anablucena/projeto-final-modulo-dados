import pandas as pd
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))
from utils import limpar_valor_monetario_brl, limpar_numero_brl, extrair_municipio_uf, normalizar_texto

from importlib import import_module
leitura = import_module("01_leitura_bases")


def limpar_base_principal() -> pd.DataFrame:
    df = leitura.ler_base_principal()

    df = df.rename(columns={
        "QUANTIDADE_ ESTABELECIMENTOS": "QUANTIDADE_ESTABELECIMENTOS",
        "QUANTIDADE_VISITAS_ESTIMADAS_ INTERNACIONAL": "VISITAS_INTERNACIONAIS_EST",
        "QUANTIDADE_VISITAS_ESTIMADAS_ NACIONAL": "VISITAS_NACIONAIS_EST",
    })

    df["VISITAS_INTERNACIONAIS_EST"] = df["VISITAS_INTERNACIONAIS_EST"].apply(limpar_numero_brl)
    df["VISITAS_NACIONAIS_EST"] = df["VISITAS_NACIONAIS_EST"].apply(limpar_numero_brl)
    df["ARRECADACAO"] = df["ARRECADACAO"].apply(limpar_valor_monetario_brl)

    df["COD_IBGE"] = df["COD_IBGE"].astype(str).str.zfill(7)
    df["MUNICIPIO"] = df["MUNICIPIO"].astype(str).str.strip()
    df["UF"] = df["UF"].astype(str).str.strip()
    df["CLUSTER"] = df["CLUSTER"].astype(str).str.strip()

    # linhas totalmente duplicadas (se houver) são removidas
    antes = len(df)
    df = df.drop_duplicates()
    if len(df) < antes:
        print(f"[base_principal] removidas {antes - len(df)} linhas duplicadas")

    return df


def limpar_pib(ano: int = 2019) -> pd.DataFrame:
    df = leitura.ler_pib_municipios()
    df = df[df["Ano"] == ano].copy()

    colunas_uteis = {
        "Código do Município": "COD_IBGE",
        "Nome do Município": "MUNICIPIO_PIB",
        "Sigla da Unidade da Federação": "UF_PIB",
        "PIB_PER_CAPITA_R$": "PIB_PER_CAPITA_R$",
    }
    df = df[list(colunas_uteis.keys())].rename(columns=colunas_uteis)
    df["COD_IBGE"] = df["COD_IBGE"].astype(str).str.zfill(7)

    antes = len(df)
    df = df.drop_duplicates(subset=["COD_IBGE"])
    if len(df) < antes:
        print(f"[PIB] removidas {antes - len(df)} linhas duplicadas de COD_IBGE")

    return df


def limpar_populacao() -> pd.DataFrame:
    """
    Filtra apenas as linhas em formato 'Município (UF)' (descarta regiões,
    estados e notas de rodapé, que não seguem esse padrão) e extrai
    nome do município, UF e a população.
    """
    df = leitura.ler_populacao_residente()

    registros = []
    for _, row in df.iterrows():
        municipio, uf = extrair_municipio_uf(row["localidade"])
        if municipio is None:
            continue  # não é linha de município (é região/UF/nota de rodapé)
        try:
            populacao = int(str(row["valor"]).strip())
        except (ValueError, TypeError):
            continue
        registros.append({
            "MUNICIPIO_POP": municipio,
            "UF_POP": uf,
            "POPULACAO_2019": populacao,
            "CHAVE_NOME_UF": normalizar_texto(municipio) + "_" + uf,
        })

    df_limpo = pd.DataFrame(registros)
    antes = len(df_limpo)
    df_limpo = df_limpo.drop_duplicates(subset=["CHAVE_NOME_UF"])
    if len(df_limpo) < antes:
        print(f"[população] removidas {antes - len(df_limpo)} linhas duplicadas de município+UF")

    return df_limpo


if __name__ == "__main__":
    bp = limpar_base_principal()
    print(f"[base_principal] limpa: {bp.shape}")
    print(bp.dtypes)

    pib = limpar_pib()
    print(f"\n[PIB 2019] limpo: {pib.shape}")
    print(pib.head())

    pop = limpar_populacao()
    print(f"\n[população] limpa: {pop.shape}")
    print(pop.head())