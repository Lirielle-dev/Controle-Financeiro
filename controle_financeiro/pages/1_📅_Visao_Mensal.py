"""
Página: Visão Mensal
Renda do mês, descontos, gastos fixos e variáveis, metas por categoria
e saldo corrente — tudo referente ao ano/mês selecionado na barra lateral.
"""
import streamlit as st
import pandas as pd
from datetime import datetime

from data.io import (
    MESES_PT,
    carregar_renda_mensal, salvar_renda_mensal,
    garantir_gastos_fixos_do_mes, carregar_gastos_fixos, salvar_gastos_fixos,
    carregar_gastos_variaveis, adicionar_gasto_variavel,
    excluir_gasto_variavel, atualizar_gastos_variaveis,
    carregar_metas, salvar_metas,
)
from data.calculos import (
    soma_renda, calcular_desconto_percentual, calcular_valor_dia,
    calcular_saldo_liquido, calcular_saldo_corrente,
)
from utils_sessao import seletor_periodo_sidebar

st.set_page_config(page_title="Visão Mensal", page_icon="📅", layout="wide")

ano, mes = seletor_periodo_sidebar()
st.title(f"📅 Visão Mensal — {MESES_PT[mes - 1]}/{ano}")

# ---------------------------------------------------------------------------
# 1. Renda do mês
# ---------------------------------------------------------------------------
st.header("💵 Renda do mês")

dados_renda = carregar_renda_mensal(ano, mes)

with st.form("form_renda"):
    col1, col2, col3 = st.columns(3)
    salario = col1.number_input("Salário (R$)", min_value=0.0, step=50.0,
                                 value=dados_renda["salario"], format="%.2f")
    renda_extra1 = col2.number_input("Renda extra 1 (R$)", min_value=0.0, step=50.0,
                                      value=dados_renda["renda_extra1"], format="%.2f")
    renda_extra2 = col3.number_input("Renda extra 2 (R$)", min_value=0.0, step=50.0,
                                      value=dados_renda["renda_extra2"], format="%.2f")

    col4, col5 = st.columns(2)
    percentual_desconto = col4.number_input(
        "Percentual de desconto sobre a renda (%)", min_value=0.0, max_value=100.0,
        step=1.0, value=dados_renda["percentual_desconto"], format="%.1f",
        help="Percentual configurável mês a mês, aplicado sobre a soma da renda.",
    )
    valor_extra_fixo = col5.number_input(
        "Valor adicional a preencher manualmente (R$)", min_value=0.0, step=10.0,
        value=dados_renda["valor_extra_fixo"], format="%.2f",
        help="Valor livre, definido manualmente por você todo mês.",
    )

    salvar = st.form_submit_button("💾 Salvar renda do mês", use_container_width=True)
    if salvar:
        salvar_renda_mensal(ano, mes, salario, renda_extra1, renda_extra2,
                             percentual_desconto, valor_extra_fixo)
        st.success("Renda do mês salva com sucesso!")
        st.rerun()

# Cálculos com os dados mais recentes salvos
dados_renda = carregar_renda_mensal(ano, mes)
total_renda = soma_renda(dados_renda["salario"], dados_renda["renda_extra1"], dados_renda["renda_extra2"])
desconto = calcular_desconto_percentual(total_renda, dados_renda["percentual_desconto"])
valor_dia = calcular_valor_dia(total_renda)
saldo_liquido = calcular_saldo_liquido(total_renda, desconto, dados_renda["valor_extra_fixo"], valor_dia)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total de renda", f"R$ {total_renda:,.2f}")
c2.metric(f"Desconto ({dados_renda['percentual_desconto']:.1f}%)", f"R$ {desconto:,.2f}")
c3.metric("Valor de 1 dia (÷30)", f"R$ {valor_dia:,.2f}")
c4.metric("💰 Saldo líquido disponível", f"R$ {saldo_liquido:,.2f}")

st.divider()

# ---------------------------------------------------------------------------
# 2. Gastos fixos
# ---------------------------------------------------------------------------
st.header("🏠 Gastos fixos")
st.caption("As categorias e valores repetem automaticamente o mês anterior — edite o que mudou, "
           "adicione novas linhas ou apague o que não se aplica mais.")

garantir_gastos_fixos_do_mes(ano, mes)
df_fixos = carregar_gastos_fixos(ano, mes)
df_fixos_editavel = df_fixos[["id", "categoria", "valor"]] if not df_fixos.empty else \
    pd.DataFrame(columns=["id", "categoria", "valor"])

df_fixos_editado = st.data_editor(
    df_fixos_editavel,
    num_rows="dynamic",
    use_container_width=True,
    key="editor_gastos_fixos",
    column_config={
        "id": st.column_config.NumberColumn("ID", disabled=True),
        "categoria": st.column_config.TextColumn("Categoria", required=True),
        "valor": st.column_config.NumberColumn("Valor (R$)", format="%.2f", required=True),
    },
)

if st.button("💾 Salvar gastos fixos"):
    df_para_salvar = df_fixos_editado.dropna(subset=["categoria"])
    salvar_gastos_fixos(ano, mes, df_para_salvar)
    st.success("Gastos fixos salvos!")
    st.rerun()

total_gastos_fixos = float(df_fixos_editado["valor"].fillna(0).sum()) if not df_fixos_editado.empty else 0.0
st.markdown(f"**Total em gastos fixos: R$ {total_gastos_fixos:,.2f}**")

st.divider()

# ---------------------------------------------------------------------------
# 3. Gastos variáveis
# ---------------------------------------------------------------------------
st.header("🛒 Gastos variáveis")

with st.form("form_gasto_variavel", clear_on_submit=True):
    col1, col2, col3, col4 = st.columns([1, 1, 2, 1])
    data_gasto = col1.date_input("Data", value=datetime.today())
    categoria_var = col2.text_input("Categoria")
    descricao_var = col3.text_input("Descrição")
    valor_var = col4.number_input("Valor (R$)", min_value=0.0, step=10.0, format="%.2f")

    adicionar = st.form_submit_button("➕ Adicionar gasto", use_container_width=True)
    if adicionar:
        if categoria_var.strip() == "" or valor_var <= 0:
            st.warning("Preencha ao menos a categoria e um valor maior que zero.")
        else:
            adicionar_gasto_variavel(ano, mes, data_gasto.strftime("%Y-%m-%d"),
                                      categoria_var, descricao_var, valor_var)
            st.success("Gasto adicionado!")
            st.rerun()

df_variaveis = carregar_gastos_variaveis(ano, mes)

if df_variaveis.empty:
    st.info("Nenhum gasto variável lançado neste mês ainda.")
else:
    st.markdown("**Lançamentos do mês** — edite diretamente na tabela se precisar.")
    df_var_editado = st.data_editor(
        df_variaveis,
        use_container_width=True,
        key="editor_gastos_variaveis",
        column_config={
            "id": st.column_config.NumberColumn("ID", disabled=True),
            "ano": None,
            "mes": None,
            "data": st.column_config.TextColumn("Data"),
            "categoria": st.column_config.TextColumn("Categoria"),
            "descricao": st.column_config.TextColumn("Descrição"),
            "valor": st.column_config.NumberColumn("Valor (R$)", format="%.2f"),
        },
        hide_index=True,
    )
    if st.button("💾 Salvar edições nos gastos variáveis"):
        atualizar_gastos_variaveis(ano, mes, df_var_editado)
        st.success("Alterações salvas!")
        st.rerun()

    st.markdown("**Excluir um lançamento**")
    col_del1, col_del2 = st.columns([3, 1])
    id_para_excluir = col_del1.selectbox(
        "Selecione o lançamento",
        options=df_variaveis["id"].tolist(),
        format_func=lambda i: (
            f"#{i} — {df_variaveis.loc[df_variaveis['id'] == i, 'categoria'].values[0]} "
            f"— R$ {df_variaveis.loc[df_variaveis['id'] == i, 'valor'].values[0]:.2f}"
        ),
    )
    confirmar = col_del2.checkbox("Confirmo")
    if st.button("🗑️ Excluir lançamento selecionado", disabled=not confirmar):
        excluir_gasto_variavel(id_para_excluir)
        st.success("Lançamento excluído.")
        st.rerun()

total_gastos_variaveis = float(df_variaveis["valor"].sum()) if not df_variaveis.empty else 0.0
st.markdown(f"**Total em gastos variáveis: R$ {total_gastos_variaveis:,.2f}**")

st.divider()

# ---------------------------------------------------------------------------
# 4. Metas por categoria
# ---------------------------------------------------------------------------
st.header("🎯 Metas por categoria")

df_metas = carregar_metas(ano, mes)
df_metas_editavel = df_metas[["categoria", "limite"]] if not df_metas.empty else \
    pd.DataFrame(columns=["categoria", "limite"])

df_metas_editado = st.data_editor(
    df_metas_editavel,
    num_rows="dynamic",
    use_container_width=True,
    key="editor_metas",
    column_config={
        "categoria": st.column_config.TextColumn("Categoria", required=True),
        "limite": st.column_config.NumberColumn("Limite (R$)", format="%.2f", required=True),
    },
)

if st.button("💾 Salvar metas"):
    df_para_salvar = df_metas_editado.dropna(subset=["categoria"])
    salvar_metas(ano, mes, df_para_salvar)
    st.success("Metas salvas!")
    st.rerun()

if not df_metas_editado.empty and not df_variaveis.empty:
    gastos_por_categoria = df_variaveis.groupby("categoria")["valor"].sum()
    st.markdown("**Gasto atual x meta:**")
    for _, linha in df_metas_editado.dropna(subset=["categoria"]).iterrows():
        gasto_atual = float(gastos_por_categoria.get(linha["categoria"], 0.0))
        st.write(f"- {linha['categoria']}: R$ {gasto_atual:,.2f} / R$ {linha['limite']:,.2f}")

st.divider()

# ---------------------------------------------------------------------------
# 5. Saldo corrente
# ---------------------------------------------------------------------------
saldo_corrente = calcular_saldo_corrente(saldo_liquido, total_gastos_fixos, total_gastos_variaveis)
st.header("📊 Saldo corrente do mês")
st.metric("Saldo restante após todos os gastos lançados", f"R$ {saldo_corrente:,.2f}",
           delta=f"R$ {saldo_corrente - saldo_liquido:,.2f} em relação ao saldo líquido inicial")
