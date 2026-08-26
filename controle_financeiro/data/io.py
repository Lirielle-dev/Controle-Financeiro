"""
Módulo de persistência dos dados.

Toda leitura/escrita de CSV fica centralizada aqui. Se um dia você quiser
migrar para SQLite, é só reescrever as funções deste arquivo — o resto do
sistema (telas e cálculos) não precisa mudar.
"""
import os
import json
import pandas as pd
from datetime import datetime

# Pasta onde todos os CSVs ficam guardados
PASTA_DADOS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "csv_data")
os.makedirs(PASTA_DADOS, exist_ok=True)

ARQ_RENDA = os.path.join(PASTA_DADOS, "renda_mensal.csv")
ARQ_GASTOS_FIXOS = os.path.join(PASTA_DADOS, "gastos_fixos.csv")
ARQ_GASTOS_VARIAVEIS = os.path.join(PASTA_DADOS, "gastos_variaveis.csv")
ARQ_METAS = os.path.join(PASTA_DADOS, "metas_categoria.csv")
ARQ_RESERVA = os.path.join(PASTA_DADOS, "reserva_emergencia.csv")
ARQ_CONFIG = os.path.join(PASTA_DADOS, "config.json")

MESES_PT = [
    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro",
]


# ---------------------------------------------------------------------------
# Helpers genéricos
# ---------------------------------------------------------------------------
def _ler_csv(caminho: str, colunas: list) -> pd.DataFrame:
    """Lê um CSV, criando-o vazio (com as colunas certas) se ainda não existir."""
    if not os.path.exists(caminho):
        df_vazio = pd.DataFrame(columns=colunas)
        df_vazio.to_csv(caminho, index=False)
        return df_vazio
    df = pd.read_csv(caminho)
    # Garante que todas as colunas esperadas existam mesmo em arquivos antigos
    for col in colunas:
        if col not in df.columns:
            df[col] = None
    return df[colunas]


def _salvar_csv(df: pd.DataFrame, caminho: str):
    df.to_csv(caminho, index=False)


def _proximo_id(df: pd.DataFrame) -> int:
    if df.empty or "id" not in df.columns or df["id"].isna().all():
        return 1
    return int(df["id"].max()) + 1


# ---------------------------------------------------------------------------
# Renda mensal
# ---------------------------------------------------------------------------
COLUNAS_RENDA = ["ano", "mes", "salario", "renda_extra1", "renda_extra2",
                  "percentual_desconto", "valor_extra_fixo"]


def carregar_renda_mensal(ano: int, mes: int) -> dict:
    df = _ler_csv(ARQ_RENDA, COLUNAS_RENDA)
    linha = df[(df["ano"] == ano) & (df["mes"] == mes)]
    if linha.empty:
        return {
            "salario": 0.0, "renda_extra1": 0.0, "renda_extra2": 0.0,
            "percentual_desconto": 10.0, "valor_extra_fixo": 0.0,
        }
    r = linha.iloc[0]
    return {
        "salario": float(r["salario"] or 0),
        "renda_extra1": float(r["renda_extra1"] or 0),
        "renda_extra2": float(r["renda_extra2"] or 0),
        "percentual_desconto": float(r["percentual_desconto"] or 0),
        "valor_extra_fixo": float(r["valor_extra_fixo"] or 0),
    }


def salvar_renda_mensal(ano: int, mes: int, salario: float, renda_extra1: float,
                         renda_extra2: float, percentual_desconto: float,
                         valor_extra_fixo: float):
    df = _ler_csv(ARQ_RENDA, COLUNAS_RENDA)
    df = df[~((df["ano"] == ano) & (df["mes"] == mes))]
    nova = pd.DataFrame([{
        "ano": ano, "mes": mes, "salario": salario,
        "renda_extra1": renda_extra1, "renda_extra2": renda_extra2,
        "percentual_desconto": percentual_desconto, "valor_extra_fixo": valor_extra_fixo,
    }])
    df = pd.concat([df, nova], ignore_index=True)
    _salvar_csv(df, ARQ_RENDA)


# ---------------------------------------------------------------------------
# Gastos fixos
# ---------------------------------------------------------------------------
COLUNAS_GASTOS_FIXOS = ["id", "ano", "mes", "categoria", "valor"]


def carregar_gastos_fixos(ano: int, mes: int) -> pd.DataFrame:
    df = _ler_csv(ARQ_GASTOS_FIXOS, COLUNAS_GASTOS_FIXOS)
    return df[(df["ano"] == ano) & (df["mes"] == mes)].reset_index(drop=True)


def mes_anterior(ano: int, mes: int) -> tuple:
    if mes == 1:
        return ano - 1, 12
    return ano, mes - 1


def garantir_gastos_fixos_do_mes(ano: int, mes: int):
    """
    Se o mês ainda não tem nenhum gasto fixo lançado, copia automaticamente
    as categorias e valores do mês anterior (o usuário só ajusta o que mudou).
    """
    df = _ler_csv(ARQ_GASTOS_FIXOS, COLUNAS_GASTOS_FIXOS)
    ja_existe = not df[(df["ano"] == ano) & (df["mes"] == mes)].empty
    if ja_existe:
        return

    ano_ant, mes_ant = mes_anterior(ano, mes)
    anteriores = df[(df["ano"] == ano_ant) & (df["mes"] == mes_ant)]
    if anteriores.empty:
        return

    prox_id = _proximo_id(df)
    novas_linhas = []
    for _, r in anteriores.iterrows():
        novas_linhas.append({
            "id": prox_id, "ano": ano, "mes": mes,
            "categoria": r["categoria"], "valor": r["valor"],
        })
        prox_id += 1
    df = pd.concat([df, pd.DataFrame(novas_linhas)], ignore_index=True)
    _salvar_csv(df, ARQ_GASTOS_FIXOS)


def salvar_gastos_fixos(ano: int, mes: int, df_editado: pd.DataFrame):
    """Substitui todos os gastos fixos do mês pelo conteúdo editado pelo usuário."""
    df = _ler_csv(ARQ_GASTOS_FIXOS, COLUNAS_GASTOS_FIXOS)
    df = df[~((df["ano"] == ano) & (df["mes"] == mes))]

    df_editado = df_editado.copy()
    df_editado["ano"] = ano
    df_editado["mes"] = mes
    # Garante IDs para linhas novas (adicionadas pelo usuário no data_editor)
    prox_id = _proximo_id(df)
    for idx, row in df_editado.iterrows():
        if pd.isna(row.get("id")):
            df_editado.at[idx, "id"] = prox_id
            prox_id += 1

    df = pd.concat([df, df_editado[COLUNAS_GASTOS_FIXOS]], ignore_index=True)
    _salvar_csv(df, ARQ_GASTOS_FIXOS)


# ---------------------------------------------------------------------------
# Gastos variáveis
# ---------------------------------------------------------------------------
COLUNAS_GASTOS_VAR = ["id", "ano", "mes", "data", "categoria", "descricao", "valor"]


def carregar_gastos_variaveis(ano: int, mes: int) -> pd.DataFrame:
    df = _ler_csv(ARQ_GASTOS_VARIAVEIS, COLUNAS_GASTOS_VAR)
    return df[(df["ano"] == ano) & (df["mes"] == mes)].reset_index(drop=True)


def adicionar_gasto_variavel(ano: int, mes: int, data: str, categoria: str,
                              descricao: str, valor: float):
    df = _ler_csv(ARQ_GASTOS_VARIAVEIS, COLUNAS_GASTOS_VAR)
    novo_id = _proximo_id(df)
    nova = pd.DataFrame([{
        "id": novo_id, "ano": ano, "mes": mes, "data": data,
        "categoria": categoria, "descricao": descricao, "valor": valor,
    }])
    df = pd.concat([df, nova], ignore_index=True)
    _salvar_csv(df, ARQ_GASTOS_VARIAVEIS)


def excluir_gasto_variavel(id_lancamento: int):
    df = _ler_csv(ARQ_GASTOS_VARIAVEIS, COLUNAS_GASTOS_VAR)
    df = df[df["id"] != id_lancamento]
    _salvar_csv(df, ARQ_GASTOS_VARIAVEIS)


def atualizar_gastos_variaveis(ano: int, mes: int, df_editado: pd.DataFrame):
    """Sobrescreve os lançamentos do mês com o conteúdo editado na tabela."""
    df = _ler_csv(ARQ_GASTOS_VARIAVEIS, COLUNAS_GASTOS_VAR)
    df = df[~((df["ano"] == ano) & (df["mes"] == mes))]

    df_editado = df_editado.copy()
    df_editado["ano"] = ano
    df_editado["mes"] = mes
    prox_id = _proximo_id(df)
    for idx, row in df_editado.iterrows():
        if pd.isna(row.get("id")):
            df_editado.at[idx, "id"] = prox_id
            prox_id += 1

    df = pd.concat([df, df_editado[COLUNAS_GASTOS_VAR]], ignore_index=True)
    _salvar_csv(df, ARQ_GASTOS_VARIAVEIS)


# ---------------------------------------------------------------------------
# Metas por categoria
# ---------------------------------------------------------------------------
COLUNAS_METAS = ["ano", "mes", "categoria", "limite"]


def carregar_metas(ano: int, mes: int) -> pd.DataFrame:
    df = _ler_csv(ARQ_METAS, COLUNAS_METAS)
    return df[(df["ano"] == ano) & (df["mes"] == mes)].reset_index(drop=True)


def salvar_metas(ano: int, mes: int, df_editado: pd.DataFrame):
    df = _ler_csv(ARQ_METAS, COLUNAS_METAS)
    df = df[~((df["ano"] == ano) & (df["mes"] == mes))]
    df_editado = df_editado.copy()
    df_editado["ano"] = ano
    df_editado["mes"] = mes
    df = pd.concat([df, df_editado[COLUNAS_METAS]], ignore_index=True)
    _salvar_csv(df, ARQ_METAS)


# ---------------------------------------------------------------------------
# Reserva de emergência
# ---------------------------------------------------------------------------
COLUNAS_RESERVA = ["id", "data", "tipo", "valor", "motivo"]


def carregar_reserva() -> pd.DataFrame:
    return _ler_csv(ARQ_RESERVA, COLUNAS_RESERVA)


def adicionar_movimentacao_reserva(data: str, tipo: str, valor: float, motivo: str):
    """tipo deve ser 'Aporte' ou 'Retirada'."""
    df = _ler_csv(ARQ_RESERVA, COLUNAS_RESERVA)
    novo_id = _proximo_id(df)
    nova = pd.DataFrame([{
        "id": novo_id, "data": data, "tipo": tipo, "valor": valor, "motivo": motivo,
    }])
    df = pd.concat([df, nova], ignore_index=True)
    _salvar_csv(df, ARQ_RESERVA)


def excluir_movimentacao_reserva(id_mov: int):
    df = _ler_csv(ARQ_RESERVA, COLUNAS_RESERVA)
    df = df[df["id"] != id_mov]
    _salvar_csv(df, ARQ_RESERVA)


def calcular_saldo_reserva() -> float:
    df = carregar_reserva()
    if df.empty:
        return 0.0
    aportes = df[df["tipo"] == "Aporte"]["valor"].sum()
    retiradas = df[df["tipo"] == "Retirada"]["valor"].sum()
    return round(float(aportes - retiradas), 2)


# ---------------------------------------------------------------------------
# Configuração geral (meta da reserva, etc.)
# ---------------------------------------------------------------------------
def carregar_config() -> dict:
    if not os.path.exists(ARQ_CONFIG):
        config_padrao = {"meta_reserva_emergencia": 0.0}
        salvar_config(config_padrao)
        return config_padrao
    with open(ARQ_CONFIG, "r", encoding="utf-8") as f:
        return json.load(f)


def salvar_config(config: dict):
    with open(ARQ_CONFIG, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# Consultas auxiliares para o Resumo Anual
# ---------------------------------------------------------------------------
def carregar_renda_ano(ano: int) -> pd.DataFrame:
    df = _ler_csv(ARQ_RENDA, COLUNAS_RENDA)
    return df[df["ano"] == ano].reset_index(drop=True)


def carregar_gastos_fixos_ano(ano: int) -> pd.DataFrame:
    df = _ler_csv(ARQ_GASTOS_FIXOS, COLUNAS_GASTOS_FIXOS)
    return df[df["ano"] == ano].reset_index(drop=True)


def carregar_gastos_variaveis_ano(ano: int) -> pd.DataFrame:
    df = _ler_csv(ARQ_GASTOS_VARIAVEIS, COLUNAS_GASTOS_VAR)
    return df[df["ano"] == ano].reset_index(drop=True)
