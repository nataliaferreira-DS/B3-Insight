import pandas as pd
import plotly.graph_objects as go

from indicadores import normalizar_serie


def criar_grafico_candlestick(
    base: pd.DataFrame,
    ticker: str,
    periodo: str,
    coluna_data: str
) -> go.Figure:
    """
    Cria o gráfico de candlestick da ação
    com as médias móveis de 20 e 50 períodos.
    """

    # Remove o sufixo técnico utilizado pelo Yahoo Finance
    # para apresentar o ticker de forma mais limpa.
    ticker_exibicao = ticker.replace(".SA", "")

    # Inicializa o gráfico que receberá as velas
    # e as linhas das médias móveis.
    fig = go.Figure()

    # Adiciona as velas com os preços de abertura,
    # máxima, mínima e fechamento.
    fig.add_trace(
        go.Candlestick(
            x=base[coluna_data],
            open=base["Open"],
            high=base["High"],
            low=base["Low"],
            close=base["Close"],
            name=ticker_exibicao
        )
    )

    # Adiciona a média móvel de 20 períodos,
    # utilizada para observar movimentos mais recentes.
    fig.add_trace(
        go.Scatter(
            x=base[coluna_data],
            y=base["MM20"],
            mode="lines",
            name="MM20",
            line=dict(width=2)
        )
    )

    # Adiciona a média móvel de 50 períodos,
    # utilizada para observar uma tendência mais ampla.
    fig.add_trace(
        go.Scatter(
            x=base[coluna_data],
            y=base["MM50"],
            mode="lines",
            name="MM50",
            line=dict(width=2)
        )
    )

    # Define título, eixos, legenda e aparência geral.
    fig.update_layout(
        title=f"{ticker_exibicao} — Candlestick ({periodo})",
        xaxis_title="Data e hora",
        yaxis_title="Preço (R$)",
        template="plotly_white",
        height=600,
        legend=dict(
            orientation="h",
            y=-0.22,
            x=0
        )
    )

    # Mantém o seletor inferior para facilitar
    # a navegação pelo período analisado.
    fig.update_xaxes(
        rangeslider_visible=True
    )

    return fig


def criar_grafico_volume(
    base: pd.DataFrame,
    ticker: str,
    coluna_data: str
) -> go.Figure:
    """
    Cria o gráfico de barras do volume negociado.
    """

    # Remove o sufixo técnico utilizado pelo Yahoo Finance.
    ticker_exibicao = ticker.replace(".SA", "")

    # Inicializa o gráfico de volume.
    fig = go.Figure()

    # Adiciona as barras somente quando a coluna
    # de volume está disponível no DataFrame.
    if "Volume" in base.columns:
        fig.add_trace(
            go.Bar(
                x=base[coluna_data],
                y=base["Volume"],
                name="Volume"
            )
        )

    # Define título, eixos e aparência geral do gráfico.
    fig.update_layout(
        title=f"Volume negociado — {ticker_exibicao}",
        xaxis_title="Data e hora",
        yaxis_title="Volume",
        template="plotly_white",
        height=300,
        showlegend=False
    )

    # Remove o seletor inferior, pois ele não é necessário
    # no gráfico de volume.
    fig.update_xaxes(
        rangeslider_visible=False
    )

    return fig


def criar_grafico_comparacao(
    base: pd.DataFrame,
    ibov: pd.DataFrame,
    ticker: str,
    coluna_data: str,
    coluna_data_ibov: str
) -> go.Figure:
    """
    Compara o desempenho normalizado da ação
    com o desempenho do Ibovespa.
    """

    # Remove o sufixo técnico utilizado pelo Yahoo Finance.
    ticker_exibicao = ticker.replace(".SA", "")

    # Normaliza as duas séries para que ambas comecem em 100.
    # Isso permite comparar desempenhos mesmo com preços diferentes.
    desempenho_acao = normalizar_serie(
        base["Close"]
    )

    desempenho_ibov = normalizar_serie(
        ibov["Close"]
    )

    # Inicializa o gráfico comparativo.
    fig = go.Figure()

    # Adiciona a linha de desempenho da ação.
    fig.add_trace(
        go.Scatter(
            x=base.loc[
                desempenho_acao.index,
                coluna_data
            ],
            y=desempenho_acao,
            mode="lines",
            name=ticker_exibicao
        )
    )

    # Adiciona a linha de desempenho do Ibovespa.
    fig.add_trace(
        go.Scatter(
            x=ibov.loc[
                desempenho_ibov.index,
                coluna_data_ibov
            ],
            y=desempenho_ibov,
            mode="lines",
            name="Ibovespa"
        )
    )

    # Adiciona uma linha de referência no nível inicial 100.
    fig.add_hline(
        y=100,
        line_dash="dash"
    )

    # Define título, eixos, legenda e comportamento de interação.
    fig.update_layout(
        title=f"{ticker_exibicao} vs. Ibovespa",
        xaxis_title="Data e hora",
        yaxis_title="Desempenho normalizado (base 100)",
        template="plotly_white",
        height=500,
        hovermode="x unified",
        legend=dict(
            orientation="h",
            y=-0.22,
            x=0
        )
    )

    # Remove o seletor inferior para manter
    # o gráfico comparativo mais limpo.
    fig.update_xaxes(
        rangeslider_visible=False
    )

    return fig