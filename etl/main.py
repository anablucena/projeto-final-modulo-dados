"""
main.py
Roda o pipeline de ETL completo, do início ao fim, com um único comando:

    python etl/main.py

Lê as 3 bases originais (bases_originais/), limpa, padroniza a chave de
junção (código IBGE) e gera a base tratada final em bases_tratadas/.
"""
import sys
from pathlib import Path
from importlib import import_module

sys.path.append(str(Path(__file__).resolve().parent))


def main():
    print("=" * 60)
    print("ETL - Projeto Final Módulo de Dados | Grupo 9 (Turismo 2019)")
    print("=" * 60)

    print("\n>> Etapa 1/4: lendo as bases originais...")
    leitura = import_module("01_leitura_bases")
    leitura.ler_base_principal()
    leitura.ler_pib_municipios()
    leitura.ler_populacao_residente()
    print("   OK.")

    print("\n>> Etapa 2/4: limpando e padronizando cada base...")
    limpeza = import_module("02_limpeza")
    limpeza.limpar_base_principal()
    limpeza.limpar_pib()
    limpeza.limpar_populacao()
    print("   OK.")

    print("\n>> Etapa 3/4: construindo o crosswalk...")
    padronizacao = import_module("03_padronizacao_chave")
    padronizacao.anexar_cod_ibge_na_populacao()
    print("   OK.")

    print("\n>> Etapa 4/4: juntando as bases e salvando a base tratada...")
    join_final = import_module("04_join_final")
    base_final = join_final.montar_base_final()
    join_final.salvar_base_tratada(base_final)

    print("\n" + "=" * 60)
    print("Pipeline concluído com sucesso.")
    print("=" * 60)


if __name__ == "__main__":
    main()