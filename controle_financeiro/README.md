# Controle Financeiro Pessoal

Sistema de controle financeiro mensal feito em Streamlit + Pandas, com dados salvos em CSV.

## Como rodar

1. Abra a pasta `controle_financeiro/` no PyCharm.
2. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```
3. Rode o app a partir da raiz da pasta:
   ```
   streamlit run app.py
   ```
4. O navegador vai abrir automaticamente. Use o menu lateral para navegar entre
   **Visão Mensal**, **Reserva de Emergência** e **Resumo Anual**.

## Estrutura do projeto

```
controle_financeiro/
├── app.py                      # Página inicial + seletor global de ano/mês
├── utils_sessao.py              # Funções compartilhadas de sessão (seletor de período)
├── requirements.txt
├── data/
│   ├── io.py                    # Toda leitura/escrita de CSV (persistência)
│   └── calculos.py              # Regras de negócio puras (sem Streamlit)
├── pages/
│   ├── 1_📅_Visao_Mensal.py     # Renda, descontos, gastos fixos/variáveis, metas, saldo corrente
│   ├── 2_💰_Reserva_Emergencia.py  # Meta, aportes, retiradas, progresso
│   └── 3_📊_Resumo_Anual.py     # Comparação mensal, evolução do saldo, pizza por categoria
└── csv_data/                    # Criada automaticamente na primeira execução
```

## O que cada tela faz

### Visão Mensal
- Preenche salário, renda extra 1 e renda extra 2.
- Define um percentual de desconto configurável sobre a renda total (editável todo mês).
- Preenche um valor adicional manual.
- O sistema calcula automaticamente: total de renda, valor de 1 dia (renda ÷ 30) e o saldo líquido disponível.
- Gastos fixos: categorias livres, repetem automaticamente o valor do mês anterior (editável em tabela estilo Excel via `st.data_editor`).
- Gastos variáveis: lançamento por formulário + tabela editável + exclusão com confirmação.
- Metas por categoria: definidas livremente, comparadas com o gasto real do mês (sem alertas especiais).
- Saldo corrente: mostra quanto ainda resta conforme os gastos vão sendo lançados.

### Reserva de Emergência
- Defina uma meta total e acompanhe o progresso com barra visual.
- Registre aportes e retiradas manualmente, com data e motivo.
- Histórico completo com opção de exclusão.
- Totalmente separada do saldo mensal de gastos.

### Resumo Anual
- Gráfico de barras comparando renda x gastos fixos x gastos variáveis por mês.
- Gráfico de linha com a evolução do saldo final ao longo do ano.
- Gráfico de pizza com a distribuição de gastos por categoria no ano.
- Tabela resumo com todos os meses.

## Próximos passos sugeridos (quando quiser evoluir)

- Migrar a camada `data/io.py` para SQLite (a estrutura já foi pensada para isso).
- Hospedar no Streamlit Community Cloud para acessar de outros dispositivos.
- Adicionar autenticação simples, caso vá hospedar publicamente.
