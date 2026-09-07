# ==========================
# CONFIGURAÇÕES DO PROJETO
# ==========================

# Nome que aparecerá no título da página
TITULO_APP = "B3 Insight"

# Texto explicativo mostrado logo abaixo do título
DESCRICAO_APP = (
    "Digite o ticker de uma ação negociada na B3 "
    "para analisar seu desempenho."
)

# Ação que aparecerá preenchida automaticamente
TICKER_PADRAO = "PETR4"

# Código utilizado pelo Yahoo Finance para representar o Ibovespa
TICKER_IBOVESPA = "^BVSP"

# Períodos que o usuário poderá escolher no dashboard
PERIODOS = [
    "1d",
    "5d",
    "1mo",
    "3mo",
    "6mo",
    "1y"
]

# Define o intervalo dos dados para cada período
#
# 5m significa dados a cada 5 minutos.
# 30m significa dados a cada 30 minutos.
# 1h significa dados a cada 1 hora.
# 1d significa dados diários.
INTERVALOS_POR_PERIODO = {
    "1d": "5m",
    "5d": "5m",
    "1mo": "30m",
    "3mo": "1h",
    "6mo": "1d",
    "1y": "1d"
}