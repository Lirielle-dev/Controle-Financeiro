"""
Módulo de cálculos financeiros.

Contém apenas regras de negócio puras (sem nenhuma dependência do Streamlit),
o que facilita testes e manutenção.
"""


def soma_renda(salario: float, renda_extra1: float, renda_extra2: float) -> float:
    """Soma todas as fontes de renda do mês."""
    return round((salario or 0) + (renda_extra1 or 0) + (renda_extra2 or 0), 2)


def calcular_desconto_percentual(soma_total: float, percentual: float) -> float:
    """
    Calcula um desconto percentual sobre a soma da renda.
    Ex: soma_total=1000, percentual=10 -> retorna 100.0
    """
    if percentual is None:
        percentual = 0
    return round(soma_total * (percentual / 100), 2)


def calcular_valor_dia(soma_total: float) -> float:
    """Calcula o valor equivalente a 1 dia de trabalho (soma / 30)."""
    return round(soma_total / 30, 2)


def calcular_saldo_liquido(soma_total: float, desconto_percentual: float,
                            valor_extra_fixo: float, valor_dia: float) -> float:
    """
    Saldo líquido = soma da renda - desconto percentual - valor extra fixo - valor do dia.
    Esse é o valor disponível para gastos fixos e variáveis do mês.
    """
    return round(soma_total - (desconto_percentual or 0) - (valor_extra_fixo or 0) - (valor_dia or 0), 2)


def calcular_saldo_corrente(saldo_liquido: float, total_gastos_fixos: float,
                             total_gastos_variaveis: float) -> float:
    """Saldo que ainda resta depois de descontar gastos fixos e variáveis já lançados."""
    return round((saldo_liquido or 0) - (total_gastos_fixos or 0) - (total_gastos_variaveis or 0), 2)


def calcular_progresso_percentual(valor_atual: float, meta: float) -> float:
    """Progresso (%) de um valor atual em relação a uma meta. Limitado a 100%."""
    if not meta or meta <= 0:
        return 0.0
    progresso = (valor_atual / meta) * 100
    return round(min(progresso, 100.0), 2)
