"""
Página: Resumo Anual
Visão macro fora do mês corrente: comparação de gastos entre meses,
evolução do saldo ao longo do ano e distribuição de gastos por categoria.
"""
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

from data.io import (
    MESES_PT,
    carregar_renda_ano, carregar_gastos_fixos_ano, carregar_gastos_variaveis_ano,
)
from data.calculos import soma_renda, calcular_desconto_percentual, calcular_valor_dia, calcular_saldo_liquido
from utils_sessao import seletor_periodo_sidebar

st.set_page_config(page_title="Resumo Anual", page_icon="📊", layout="wide")

seletor_periodo_sidebar()

st.title("📊 Resumo Anual")

anos_disponiveis = list(range(2023, datetime.today().year + 2))
ano_resumo = st.selectbox(
    "Ano para análise", anos_disponiveis,
    index=anos_disponiveis.index(st.session_state["ano_selecionado"])
    if st.session_state["ano_selecionado"] in anos_disponiveis else 0,
)

df_renda_ano = carregar_renda_ano(ano_resumo)
df_fixos_ano = carregar_gastos_fixos_ano(ano_resumo)
df_variaveis_ano = carregar_gastos_variaveis_ano(ano_resumo)

# ---------------------------------------------------------------------------
# Monta uma tabela mensal consolidada (renda, gastos, saldo) para o ano
# ---------------------------------------------------------------------------
linhas = []
for m in range(1, 13):
    renda_mes = df_renda_ano[df_renda_ano["mes"] == m]
    if not renda_mes.empty:
        r = renda_mes.iloc[0]
        total_renda = soma_renda(r["salario"], r["renda_extra1"], r["renda_extra2"])
        desconto = calcular_desconto_percentual(total_renda, r["percentual_desconto"])
        valor_dia = calcular_valor_dia(total_renda)
        saldo_liquido = calcular_saldo_liquido(total_renda, desconto, r["valor_extra_fixo"], valor_dia)
    else:
        total_renda = 0.0
        saldo_liquido = 0.0

    total_fixos = float(df_fixos_ano[df_fixos_ano["mes"] == m]["valor"].sum())
    total_variaveis = float(df_variaveis_ano[df_variaveis_ano["mes"] == m]["valor"].sum())
    saldo_final = saldo_liquido - total_fixos - total_variaveis

    linhas.append({
        "mes": MESES_PT[m - 1][:3],
        "renda": total_renda,
        "gastos_fixos": total_fixos,
        "gastos_variaveis": total_variaveis,
        "saldo_final": saldo_final,
    })

df_resumo = pd.DataFrame(linhas)

if df_resumo[["renda", "gastos_fixos", "gastos_variaveis"]].sum().sum() == 0:
    st.info(f"Ainda não há dados lançados para o ano de {ano_resumo}.")
else:
    # -----------------------------------------------------------------
    # Gráfico de barras: renda x gastos fixos x gastos variáveis por mês
    # -----------------------------------------------------------------
    st.header("📊 Comparação mensal")
    fig1, ax1 = plt.subplots(figsize=(10, 4))
    largura = 0.25
    posicoes = range(len(df_resumo))
    ax1.bar([p - largura for p in posicoes], df_resumo["renda"], width=largura, label="Renda")
    ax1.bar(posicoes, df_resumo["gastos_fixos"], width=largura, label="Gastos fixos")
    ax1.bar([p + largura for p in posicoes], df_resumo["gastos_variaveis"], width=largura, label="Gastos variáveis")
    ax1.set_xticks(list(posicoes))
    ax1.set_xticklabels(df_resumo["mes"])
    ax1.set_ylabel("R$")
    ax1.legend()
    ax1.set_title(f"Renda x Gastos por mês — {ano_resumo}")
    st.pyplot(fig1)

    # -----------------------------------------------------------------
    # Gráfico de linha: evolução do saldo final ao longo do ano
    # -----------------------------------------------------------------
    st.header("📈 Evolução do saldo")
    fig2, ax2 = plt.subplots(figsize=(10, 4))
    ax2.plot(df_resumo["mes"], df_resumo["saldo_final"], marker="o")
    ax2.axhline(0, color="gray", linewidth=0.8, linestyle="--")
    ax2.set_ylabel("R$")
    ax2.set_title(f"Saldo final por mês — {ano_resumo}")
    st.pyplot(fig2)

    # -----------------------------------------------------------------
    # Gráfico de pizza: distribuição de gastos por categoria no ano
    # -----------------------------------------------------------------
    st.header("🥧 Distribuição de gastos por categoria (ano todo)")
    todos_gastos = pd.concat([
        df_fixos_ano[["categoria", "valor"]],
        df_variaveis_ano[["categoria", "valor"]],
    ], ignore_index=True)

    if not todos_gastos.empty:
        por_categoria = todos_gastos.groupby("categoria")["valor"].sum().sort_values(ascending=False)
        fig3, ax3 = plt.subplots(figsize=(6, 6))
        ax3.pie(por_categoria.values, labels=por_categoria.index, autopct="%1.1f%%", startangle=90)
        ax3.axis("equal")
        st.pyplot(fig3)
    else:
        st.info("Nenhum gasto lançado ainda para gerar o gráfico de categorias.")

    # -----------------------------------------------------------------
    # Tabela resumo
    # -----------------------------------------------------------------
    st.header("📋 Tabela resumo")
    st.dataframe(
        df_resumo,
        use_container_width=True,
        hide_index=True,
        column_config={
            "mes": st.column_config.TextColumn("Mês"),
            "renda": st.column_config.NumberColumn("Renda", format="%.2f"),
            "gastos_fixos": st.column_config.NumberColumn("Gastos fixos", format="%.2f"),
            "gastos_variaveis": st.column_config.NumberColumn("Gastos variáveis", format="%.2f"),
            "saldo_final": st.column_config.NumberColumn("Saldo final", format="%.2f"),
        },
    )
