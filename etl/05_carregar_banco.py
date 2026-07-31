"""
05_carregar_banco.py
Carrega a base tratada final para um banco Postgres remoto (ex.: Supabase).
A string de conexão é lida do arquivo .env (nunca deve ser commitada no Git).

Uso:
    python etl/05_carregar_banco.py
"""
import os
from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()  # lê o arquivo .env da raiz do projeto

PASTA_TRATADAS = Path(__file__).resolve().parent.parent / "bases_tratadas"
CAMINHO_CSV = PASTA_TRATADAS / "base_final_tratada.csv"
NOME_TABELA = "base_final_tratada.csv"


def montar_engine():
    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError(
            "DATABASE_URL não encontrada.\n"
            "Crie um arquivo .env na raiz do projeto com uma linha assim:\n"
            "DATABASE_URL=postgresql+psycopg2://usuario:senha@host:porta/postgres\n"
            "(pegue essa string em Supabase > Project Settings > Database > Connection string)"
        )
    return create_engine(url)


def carregar_base_no_banco():
    if not CAMINHO_CSV.exists():
        raise FileNotFoundError(
            f"Base tratada não encontrada em {CAMINHO_CSV}. Rode 'python etl/main.py' primeiro."
        )

    df = pd.read_csv(CAMINHO_CSV)
    engine = montar_engine()

    # if_exists="replace": recria a tabela toda vez -> pipeline continua reprodutível
    df.to_sql(NOME_TABELA, engine, if_exists="replace", index=False)
    print(f"[OK] {len(df)} linhas carregadas na tabela '{NOME_TABELA}'.")

    with engine.connect() as conn:
        total = conn.execute(text(f"SELECT COUNT(*) FROM {NOME_TABELA}")).scalar()
        print(f"[checagem] {total} linhas confirmadas no banco remoto.")


if __name__ == "__main__":
    carregar_base_no_banco()