"""
03_padronizacao_chave.py
A base de população não traz código IBGE, só "Município (UF)".
Para juntar com segurança, usamos a base de PIB (que cobre os 5.570
municípios do Brasil e tem código IBGE) como "crosswalk": nome+UF
normalizados -> código IBGE. Isso evita duplicidade de nomes de município
entre estados diferentes.
"""
import sys
from pathlib import Path
import pandas as pd

sys.path.append(str(Path(__file__).resolve().parent))
from utils import normalizar_texto, CORRECOES_NOME_MUNICIPIO
from importlib import import_module
limpeza = import_module("02_limpeza")


def montar_crosswalk_nome_uf_para_ibge() -> pd.DataFrame:
    pib = limpeza.limpar_pib()
    crosswalk = pib[["COD_IBGE", "MUNICIPIO_PIB", "UF_PIB"]].copy()
    crosswalk["CHAVE_NOME_UF"] = (
        crosswalk["MUNICIPIO_PIB"].apply(normalizar_texto) + "_" + crosswalk["UF_PIB"]
    )
    return crosswalk[["CHAVE_NOME_UF", "COD_IBGE"]].drop_duplicates(subset=["CHAVE_NOME_UF"])


def anexar_cod_ibge_na_populacao() -> pd.DataFrame:
    pop = limpeza.limpar_populacao()
    crosswalk = montar_crosswalk_nome_uf_para_ibge()

    # aplica correções manuais de grafia conhecidas antes de casar as chaves
    pop["CHAVE_NOME_UF"] = pop["CHAVE_NOME_UF"].replace(CORRECOES_NOME_MUNICIPIO)

    pop_com_codigo = pop.merge(crosswalk, on="CHAVE_NOME_UF", how="left")

    total = len(pop_com_codigo)
    sem_match = pop_com_codigo["COD_IBGE"].isna().sum()
    print(f"[crosswalk população->IBGE] {total - sem_match}/{total} municípios casados "
          f"({sem_match} sem correspondência)")

    if sem_match > 0:
        exemplos = pop_com_codigo[pop_com_codigo["COD_IBGE"].isna()][["MUNICIPIO_POP", "UF_POP"]].head(10)
        print("Exemplos sem correspondência (nome pode divergir entre as bases):")
        print(exemplos.to_string(index=False))

    return pop_com_codigo


if __name__ == "__main__":
    resultado = anexar_cod_ibge_na_populacao()
    print(resultado.head())