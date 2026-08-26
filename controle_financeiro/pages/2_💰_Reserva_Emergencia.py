"""
Página: Reserva de Emergência
Meta total, aportes e retiradas manuais, histórico e progresso —
totalmente separada do saldo mensal de gastos.
"""
import streamlit as st
from datetime import datetime

from data.io import (
    carregar_reserva, adicionar_movimentacao_reserva, excluir_movimentacao_reserva,
    calcular_saldo_reserva, carregar_config, salvar_config,
)
from data.calculos import calcular_progresso_percentual
from utils_sessao import seletor_periodo_sidebar

st.set_page_config(page_title="Reserva de Emergência", page_icon="💰", layout="wide")

# O período (ano/mês) não é usado diretamente nesta página, mas mantemos o
# seletor na barra lateral para consistência de navegação entre as páginas.
seletor_periodo_sidebar()

st.title("💰 Reserva de Emergência")

# ---------------------------------------------------------------------------
# Meta e progresso
# ---------------------------------------------------------------------------
config = carregar_config()
saldo_atual = calcular_saldo_reserva()

with st.expander("⚙️ Definir/editar meta total", expanded=(config["meta_reserva_emergencia"] == 0)):
    nova_meta = st.number_input(
        "Meta total da reserva (R$)", min_value=0.0, step=100.0,
        value=float(config["meta_reserva_emergencia"]), format="%.2f",
    )
    if st.button("Salvar meta"):
        config["meta_reserva_emergencia"] = nova_meta
        salvar_config(config)
        st.success("Meta atualizada!")
        st.rerun()

meta = config["meta_reserva_emergencia"]
progresso = calcular_progresso_percentual(saldo_atual, meta)

col1, col2, col3 = st.columns(3)
col1.metric("💰 Reserva atual", f"R$ {saldo_atual:,.2f}")
col2.metric("🎯 Meta", f"R$ {meta:,.2f}")
col3.metric("📈 Progresso", f"{progresso:.1f}%")
st.progress(min(progresso / 100, 1.0))

st.divider()

# ---------------------------------------------------------------------------
# Nova movimentação (aporte ou retirada)
# ---------------------------------------------------------------------------
st.header("➕ Registrar movimentação")

with st.form("form_movimentacao", clear_on_submit=True):
    col1, col2, col3 = st.columns(3)
    data_mov = col1.date_input("Data", value=datetime.today())
    tipo_mov = col2.selectbox("Tipo", ["Aporte", "Retirada"])
    valor_mov = col3.number_input("Valor (R$)", min_value=0.0, step=50.0, format="%.2f")
    motivo_mov = st.text_input("Motivo (opcional para aporte, recomendado para retirada)")

    registrar = st.form_submit_button("💾 Registrar", use_container_width=True)
    if registrar:
        if valor_mov <= 0:
            st.warning("Informe um valor maior que zero.")
        elif tipo_mov == "Retirada" and valor_mov > saldo_atual:
            st.error(f"Você está tentando retirar mais do que o saldo atual (R$ {saldo_atual:,.2f}).")
        else:
            adicionar_movimentacao_reserva(data_mov.strftime("%Y-%m-%d"), tipo_mov, valor_mov, motivo_mov)
            st.success(f"{tipo_mov} de R$ {valor_mov:,.2f} registrado(a)!")
            st.rerun()

st.divider()

# ---------------------------------------------------------------------------
# Histórico
# ---------------------------------------------------------------------------
st.header("📜 Histórico de movimentações")

df_reserva = carregar_reserva()
if df_reserva.empty:
    st.info("Nenhuma movimentação registrada ainda.")
else:
    df_ordenado = df_reserva.sort_values("data", ascending=False).reset_index(drop=True)
    st.dataframe(
        df_ordenado,
        use_container_width=True,
        hide_index=True,
        column_config={
            "id": st.column_config.NumberColumn("ID"),
            "data": st.column_config.TextColumn("Data"),
            "tipo": st.column_config.TextColumn("Tipo"),
            "valor": st.column_config.NumberColumn("Valor (R$)", format="%.2f"),
            "motivo": st.column_config.TextColumn("Motivo"),
        },
    )

    st.markdown("**Excluir uma movimentação**")
    col_del1, col_del2 = st.columns([3, 1])
    id_para_excluir = col_del1.selectbox(
        "Selecione a movimentação",
        options=df_ordenado["id"].tolist(),
        format_func=lambda i: (
            f"#{i} — {df_ordenado.loc[df_ordenado['id'] == i, 'tipo'].values[0]} "
            f"— R$ {df_ordenado.loc[df_ordenado['id'] == i, 'valor'].values[0]:.2f} "
            f"em {df_ordenado.loc[df_ordenado['id'] == i, 'data'].values[0]}"
        ),
    )
    confirmar = col_del2.checkbox("Confirmo")
    if st.button("🗑️ Excluir movimentação selecionada", disabled=not confirmar):
        excluir_movimentacao_reserva(id_para_excluir)
        st.success("Movimentação excluída.")
        st.rerun()
