"""
Funções de sessão compartilhadas entre app.py e todas as páginas em pages/.
Centralizar aqui evita duplicar a lógica do seletor de ano/mês em cada arquivo.
"""
import streamlit as st
from datetime import datetime
from data.io import MESES_PT


def inicializar_periodo():
    """Garante que ano/mês selecionados existam no session_state (padrão: hoje)."""
    hoje = datetime.today()
    if "ano_selecionado" not in st.session_state:
        st.session_state["ano_selecionado"] = hoje.year
    if "mes_selecionado" not in st.session_state:
        st.session_state["mes_selecionado"] = hoje.month


def seletor_periodo_sidebar():
    """
    Renderiza o seletor de Ano/Mês na barra lateral e devolve (ano, mes).
    Chame esta função no topo de CADA página para manter o período sincronizado.
    """
    inicializar_periodo()
    st.sidebar.subheader("📅 Período")

    anos_disponiveis = list(range(2023, datetime.today().year + 2))
    ano_atual = st.session_state["ano_selecionado"]
    ano = st.sidebar.selectbox(
        "Ano", anos_disponiveis,
        index=anos_disponiveis.index(ano_atual) if ano_atual in anos_disponiveis else 0,
        key="_seletor_ano",
    )
    mes = st.sidebar.selectbox(
        "Mês", list(range(1, 13)),
        format_func=lambda m: MESES_PT[m - 1],
        index=st.session_state["mes_selecionado"] - 1,
        key="_seletor_mes",
    )
    st.session_state["ano_selecionado"] = ano
    st.session_state["mes_selecionado"] = mes
    return ano, mes
