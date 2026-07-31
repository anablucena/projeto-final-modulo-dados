"""
utils.py
Funções utilitárias de limpeza e padronização usadas em todo o pipeline de ETL.
Grupo 9 - Turismo 2019
"""
import re
import unicodedata
import pandas as pd


def normalizar_texto(texto: str) -> str:
    """
    Remove acentos, espaços extras e coloca em maiúsculas.
    Usado para criar chaves de junção confiáveis entre bases que não
    compartilham um código IBGE (ex.: a base de população).
    Ex.: 'São João da Boa Vista' -> 'SAO JOAO DA BOA VISTA'
    """
    if pd.isna(texto):
        return ""
    texto = str(texto).strip()
    texto = unicodedata.normalize("NFKD", texto).encode("ASCII", "ignore").decode("ASCII")
    texto = re.sub(r"\s+", " ", texto)
    return texto.upper().strip()


def limpar_valor_monetario_brl(valor) -> float:
    """
    Converte string monetária no padrão brasileiro para float.
    Ex.: 'R$  708.887,00' -> 708887.00
         'R$  -'          -> 0.0
    """
    if pd.isna(valor):
        return 0.0
    valor = str(valor).strip()
    valor = valor.replace("R$", "").strip()
    if valor in ("-", "", "..", "...", "X"):
        return 0.0
    valor = valor.replace(".", "").replace(",", ".")
    try:
        return float(valor)
    except ValueError:
        return 0.0


def limpar_numero_brl(valor) -> float:
    """
    Converte número no padrão brasileiro (ponto como separador de milhar,
    sem casas decimais nos dados de visitantes) para float.
    Ex.: '15.309' -> 15309.0 ; '0' -> 0.0
    """
    if pd.isna(valor):
        return 0.0
    valor = str(valor).strip()
    if valor in ("-", "", "..", "...", "X"):
        return 0.0
    valor = valor.replace(".", "")
    valor = valor.replace(",", ".")
    try:
        return float(valor)
    except ValueError:
        return 0.0


def cod_ibge_para_str(codigo) -> str:
    """Padroniza o código IBGE como string de 7 dígitos (sem perder zeros à esquerda)."""
    if pd.isna(codigo):
        return ""
    return str(int(float(codigo))).zfill(7)


# Pequenas divergências de grafia entre a base de população (IBGE/SIDRA)
# e a base de PIB (IBGE) para o mesmo município. Mapeamento manual descoberto
# durante a checagem do resultado do crosswalk (ver 03_padronizacao_chave.py).
CORRECOES_NOME_MUNICIPIO = {
    "ASSU_RN": "ACU_RN",
    "AREZ_RN": "ARES_RN",
    "AMPARO DO SAO FRANCISCO_SE": "AMPARO DE SAO FRANCISCO_SE",
    "BARAO DO MONTE ALTO_MG": "BARAO DE MONTE ALTO_MG",
    "GRAO-PARA_SC": "GRAO PARA_SC",
    "SANTO ANTONIO DE LEVERGER_MT": "SANTO ANTONIO DO LEVERGER_MT",
    "SAO LUIZ DO ANAUA_RR": "SAO LUIZ_RR",
}


def extrair_municipio_uf(texto: str):
    """
    Extrai nome do município e UF do formato usado na base do IBGE (SIDRA):
    'Cacoal (RO)' -> ('Cacoal', 'RO')
    Retorna (None, None) se o texto não seguir esse padrão
    (ex.: linhas de Região/UF/notas de rodapé, que não têm o sufixo '(UF)').
    """
    if pd.isna(texto):
        return None, None
    m = re.match(r"^(.*)\s\(([A-Z]{2})\)$", str(texto).strip())
    if not m:
        return None, None
    return m.group(1).strip(), m.group(2).strip()