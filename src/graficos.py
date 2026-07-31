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

    # Adiciona a média móvel de 20 períodos.
    fig.add_trace(
        go.Scatter(
            x=base[coluna_data],
            y=base["MM20"],
            mode="lines",
            name="MM20",
            line=dict(width=2)
        )
    )

    # Adiciona a média móvel de 50 períodos.
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
    Cria o gráfico de barras com a quantidade
    de ações negociadas em cada período.
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
        yaxis_title="Quantidade de ações",
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
    com o desempenho do Ibovespa utilizando
    somente datas presentes nas duas séries.
    """

    # Remove o sufixo técnico utilizado pelo Yahoo Finance.
    ticker_exibicao = ticker.replace(".SA", "")

    # Seleciona somente as colunas necessárias.
    dados_acao = base[
        [coluna_data, "Close"]
    ].copy()

    dados_ibov = ibov[
        [coluna_data_ibov, "Close"]
    ].copy()

    # Padroniza os nomes das colunas para permitir
    # o cruzamento entre os dois DataFrames.
    dados_acao = dados_acao.rename(
        columns={
            coluna_data: "Data",
            "Close": "Acao"
        }
    )

    dados_ibov = dados_ibov.rename(
        columns={
            coluna_data_ibov: "Data",
            "Close": "Ibovespa"
        }
    )

    # Converte as colunas para o formato datetime.
    dados_acao["Data"] = pd.to_datetime(
        dados_acao["Data"]
    )

    dados_ibov["Data"] = pd.to_datetime(
        dados_ibov["Data"]
    )

    # Remove possíveis informações de fuso horário.
    # Isso evita incompatibilidade durante o merge.
    if dados_acao["Data"].dt.tz is not None:
        dados_acao["Data"] = (
            dados_acao["Data"]
            .dt.tz_localize(None)
        )

    if dados_ibov["Data"].dt.tz is not None:
        dados_ibov["Data"] = (
            dados_ibov["Data"]
            .dt.tz_localize(None)
        )

    # Mantém somente datas e horários presentes
    # simultaneamente na ação e no Ibovespa.
    comparacao = pd.merge(
        dados_acao,
        dados_ibov,
        on="Data",
        how="inner"
    )

    # Remove registros incompletos e organiza
    # os dados em ordem cronológica.
    comparacao = (
        comparacao
        .dropna()
        .sort_values("Data")
        .reset_index(drop=True)
    )

    # Caso não existam datas em comum, retorna um gráfico
    # com uma mensagem em vez de provocar um erro.
    if comparacao.empty:
        fig = go.Figure()

        fig.add_annotation(
            text=(
                "Não foi possível comparar a ação "
                "com o Ibovespa neste período."
            ),
            x=0.5,
            y=0.5,
            xref="paper",
            yref="paper",
            showarrow=False
        )

        fig.update_layout(
            title=f"{ticker_exibicao} vs. Ibovespa",
            xaxis_title="Data e hora",
            yaxis_title="Desempenho normalizado (base 100)",
            template="plotly_white",
            height=500
        )

        return fig

    # Normaliza as séries somente depois que ação e Ibovespa
    # estão alinhados pelas mesmas datas e horários.
    comparacao["Acao_normalizada"] = normalizar_serie(
        comparacao["Acao"]
    )

    comparacao["Ibovespa_normalizado"] = normalizar_serie(
        comparacao["Ibovespa"]
    )

    # Inicializa o gráfico comparativo.
    fig = go.Figure()

    # Adiciona a linha de desempenho da ação.
    fig.add_trace(
        go.Scatter(
            x=comparacao["Data"],
            y=comparacao["Acao_normalizada"],
            mode="lines",
            name=ticker_exibicao
        )
    )

    # Adiciona a linha de desempenho do Ibovespa.
    fig.add_trace(
        go.Scatter(
            x=comparacao["Data"],
            y=comparacao["Ibovespa_normalizado"],
            mode="lines",
            name="Ibovespa"
        )
    )

    # Adiciona uma linha de referência na base inicial 100.
    fig.add_hline(
        y=100,
        line_dash="dash"
    )

    # Define título, eixos, legenda e interação.
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