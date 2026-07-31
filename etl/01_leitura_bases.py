import pandas as pd
from pathlib import Path

PASTA_ORIGINAIS = Path(__file__).resolve().parent.parent / "bases_originais"


def ler_base_principal() -> pd.DataFrame:
   
    caminho = PASTA_ORIGINAIS / "base_principal.csv"
  
    df = pd.read_csv(
        caminho, sep=None, engine="python", encoding="utf-8",
        dtype={"QUANTIDADE_EMPREGOS": str},
    )
    df.columns = [c.strip() for c in df.columns]  
    return df


def ler_pib_municipios() -> pd.DataFrame:

    caminho = PASTA_ORIGINAIS / "base_complementar_01_pib.xlsx"
    df = pd.read_excel(caminho, sheet_name="PIB_dos_Municípios")
    return df


def ler_populacao_residente() -> pd.DataFrame:

    caminho = PASTA_ORIGINAIS / "base_complementar_02_populacao.csv"
    df = pd.read_csv(
        caminho,
        sep=";",
        engine="python",
        encoding="utf-8-sig",
        header=None,
        names=["localidade", "valor"],
        skiprows=4,  
        quotechar='"',
    )
    return df


if __name__ == "__main__":
    bp = ler_base_principal()
    print(f"[base_principal] {bp.shape[0]} linhas, {bp.shape[1]} colunas")
    print(bp.columns.tolist())

    pib = ler_pib_municipios()
    print(f"\n[PIB municípios] {pib.shape[0]} linhas, {pib.shape[1]} colunas")
    print(f"Anos disponíveis: {sorted(pib['Ano'].unique())}")

    pop = ler_populacao_residente()
    print(f"\n[população] {pop.shape[0]} linhas (brutas, antes de filtrar notas de rodapé)")
    print(pop.head())