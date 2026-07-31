import pandas as pd
import yfinance as yf

from config import (
    INTERVALOS_POR_PERIODO,
    TICKER_IBOVESPA
)


def padronizar_ticker(ticker_digitado: str) -> str:
    """
    Padroniza o código da ação para o formato utilizado
    pelo Yahoo Finance.
    """

    # Remove espaços, converte o texto para maiúsculas
    # e adiciona o sufixo das ações brasileiras.
    ticker = ticker_digitado.strip().upper()

    if not ticker.endswith(".SA"):
        ticker = f"{ticker}.SA"

    return ticker


def preparar_dataframe(base: pd.DataFrame) -> pd.DataFrame:
    """
    Organiza o DataFrame retornado pelo Yahoo Finance.
    """

    # Interrompe o tratamento quando nenhum dado foi retornado.
    if base.empty:
        return base

    # Cria uma cópia para preservar o DataFrame original.
    base = base.copy()

    # O yfinance pode retornar colunas em múltiplos níveis.
    # Mantemos apenas o primeiro nível para simplificar o uso.
    if isinstance(base.columns, pd.MultiIndex):
        base.columns = base.columns.get_level_values(0)

    # Transforma o índice de data em uma coluna comum,
    # permitindo utilizá-lo diretamente nos gráficos e tabelas.
    base = base.reset_index()

    return base


def baixar_dados_acao(
    ticker: str,
    periodo: str
) -> pd.DataFrame:
    """
    Baixa os dados históricos da ação selecionada.
    """

    # Define o intervalo de coleta correspondente ao período escolhido.
    intervalo = INTERVALOS_POR_PERIODO.get(
        periodo,
        "1d"
    )

    try:
        # Realiza a consulta dos preços históricos da ação.
        base = yf.download(
            ticker,
            period=periodo,
            interval=intervalo,
            progress=False,
            auto_adjust=False
        )

        # Organiza o resultado antes de enviá-lo ao dashboard.
        return preparar_dataframe(base)

    except Exception:
        # Retorna um DataFrame vazio para que o app possa
        # tratar a falha sem interromper a execução.
        return pd.DataFrame()


def baixar_dados_ibovespa(
    periodo: str
) -> pd.DataFrame:
    """
    Baixa os dados históricos do Ibovespa.
    """

    # Utiliza o mesmo intervalo da ação para permitir
    # a comparação entre as duas séries.
    intervalo = INTERVALOS_POR_PERIODO.get(
        periodo,
        "1d"
    )

    try:
        # Realiza a consulta dos preços históricos do Ibovespa.
        ibov = yf.download(
            TICKER_IBOVESPA,
            period=periodo,
            interval=intervalo,
            progress=False,
            auto_adjust=False
        )

        # Organiza o resultado antes da comparação.
        return preparar_dataframe(ibov)

    except Exception:
        return pd.DataFrame()


def buscar_informacoes_empresa(ticker: str) -> dict:
    """
    Busca informações gerais e fundamentalistas da empresa.
    """

    try:
        # Cria o objeto utilizado pelo yfinance para consultar
        # dados como nome, setor, segmento e valor de mercado.
        empresa = yf.Ticker(ticker)
        informacoes = empresa.info

        # Garante que o retorno esteja no formato esperado pelo app.
        if isinstance(informacoes, dict):
            return informacoes

        return {}

    except Exception:
        # Um dicionário vazio permite que o dashboard exiba
        # valores padrão quando a consulta não estiver disponível.
        return {}


def identificar_coluna_data(
    base: pd.DataFrame
) -> str | None:
    """
    Identifica a coluna que contém a data dos registros.
    """

    # Dados intradiários normalmente utilizam data e horário.
    if "Datetime" in base.columns:
        return "Datetime"

    # Dados diários normalmente utilizam apenas a data.
    if "Date" in base.columns:
        return "Date"

    return None


def limpar_dados_acao(
    base: pd.DataFrame
) -> pd.DataFrame:
    """
    Valida e remove registros sem informações essenciais de preço.
    """

    # Essas colunas são necessárias para calcular os indicadores
    # e construir o gráfico de candlestick.
    colunas_obrigatorias = [
        "Open",
        "High",
        "Low",
        "Close"
    ]

    if base.empty:
        return base

    # Interrompe o processamento quando a estrutura recebida
    # não contém todas as colunas necessárias.
    if not all(
        coluna in base.columns
        for coluna in colunas_obrigatorias
    ):
        return pd.DataFrame()

    base = base.copy()

    # Remove registros com preços ausentes, pois eles não podem
    # ser utilizados nos cálculos ou nos gráficos.
    base = base.dropna(
        subset=colunas_obrigatorias
    )

    return base


def limpar_dados_ibovespa(
    ibov: pd.DataFrame
) -> pd.DataFrame:
    """
    Valida e remove registros sem preço de fechamento.
    """

    # O fechamento é a coluna utilizada na comparação
    # entre o desempenho da ação e o Ibovespa.
    if ibov.empty or "Close" not in ibov.columns:
        return pd.DataFrame()

    ibov = ibov.copy()

    # Remove os registros que não possuem preço de fechamento.
    return ibov.dropna(
        subset=["Close"]
    )