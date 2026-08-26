"""
Controle Financeiro Pessoal
Ponto de entrada do app. Aqui vive o seletor global de ano/mês, guardado em
st.session_state para que todas as páginas (pages/) usem o mesmo período.
"""
import streamlit as st
from data.io import MESES_PT
from utils_sessao import seletor_periodo_sidebar

st.set_page_config(
    page_title="Controle Financeiro",
    page_icon="💰",
    layout="wide",
)

ano, mes = seletor_periodo_sidebar()

st.title("💰 Controle Financeiro Pessoal")
st.markdown(f"### Período selecionado: **{MESES_PT[mes - 1]} de {ano}**")

st.markdown(
    """
    Use o menu à esquerda para navegar entre as seções:

    - **📅 Visão Mensal** — lance sua renda, descontos, gastos fixos e variáveis do mês.
    - **💰 Reserva de Emergência** — acompanhe aportes, retiradas e sua meta.
    - **📊 Resumo Anual** — compare meses e veja a evolução do seu saldo ao longo do ano.

    O ano e o mês escolhidos aqui na barra lateral valem para todas as páginas.
    """
)
