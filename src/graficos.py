import pandas as pd
import plotly.graph_objects as go

from indicadores import normalizar_serie


def preparar_dados_grafico(
    base: pd.DataFrame,
    coluna_data: str,
    max_pontos: int = 250
) -> pd.DataFrame:
    """
    Reduz a quantidade de pontos exibidos em períodos longos,
    preservando a estrutura OHLC do candlestick.

    A base original não é alterada.
    """

    dados = base.copy()

    # Garante que a coluna de data esteja no formato datetime.
    dados[coluna_data] = pd.to_datetime(
        dados[coluna_data]
    )

    # Organiza os dados em ordem cronológica.
    dados = (
        dados
        .sort_values(coluna_data)
        .reset_index(drop=True)
    )

    # Para períodos menores, mantém todos os registros.
    if len(dados) <= max_pontos:
        return dados

    # Calcula quantos registros serão agrupados
    # para formar cada vela visual.
    tamanho_grupo = (
        len(dados) + max_pontos - 1
    ) // max_pontos

    dados["_grupo"] = (
        dados.index // tamanho_grupo
    )

    # Regras de agregação para preservar
    # corretamente as informações de cada candle.
    agregacoes = {
        coluna_data: "last",
        "Open": "first",
        "High": "max",
        "Low": "min",
        "Close": "last"
    }

    # Soma o volume negociado dentro de cada grupo.
    if "Volume" in dados.columns:
        agregacoes["Volume"] = "sum"

    # Mantém o último valor disponível
    # das médias móveis em cada grupo.
    if "MM20" in dados.columns:
        agregacoes["MM20"] = "last"

    if "MM50" in dados.columns:
        agregacoes["MM50"] = "last"

    dados_reduzidos = (
        dados
        .groupby("_grupo", as_index=False)
        .agg(agregacoes)
        .dropna(
            subset=[
                "Open",
                "High",
                "Low",
                "Close"
            ]
        )
    )

    return dados_reduzidos


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

    # Remove o sufixo técnico utilizado pelo Yahoo Finance.
    ticker_exibicao = ticker.replace(".SA", "")

    # Prepara uma base otimizada somente para visualização.
    # A base original continua intacta.
    base_grafico = preparar_dados_grafico(
        base=base,
        coluna_data=coluna_data
    )

    # Inicializa o gráfico.
    fig = go.Figure()

    # Adiciona as velas.
    fig.add_trace(
        go.Candlestick(
            x=base_grafico[coluna_data],
            open=base_grafico["Open"],
            high=base_grafico["High"],
            low=base_grafico["Low"],
            close=base_grafico["Close"],
            name=ticker_exibicao
        )
    )

    # Adiciona a média móvel de 20 períodos.
    if "MM20" in base_grafico.columns:
        fig.add_trace(
            go.Scatter(
                x=base_grafico[coluna_data],
                y=base_grafico["MM20"],
                mode="lines",
                name="MM20",
                line=dict(width=2)
            )
        )

    # Adiciona a média móvel de 50 períodos.
    if "MM50" in base_grafico.columns:
        fig.add_trace(
            go.Scatter(
                x=base_grafico[coluna_data],
                y=base_grafico["MM50"],
                mode="lines",
                name="MM50",
                line=dict(width=2)
            )
        )

    # Define aparência geral do gráfico.
    fig.update_layout(
        title=f"{ticker_exibicao} — Candlestick ({periodo})",
        xaxis_title="Data",
        yaxis_title="Preço (R$)",
        template="plotly_white",
        height=650,
        margin=dict(
            l=20,
            r=20,
            t=60,
            b=40
        ),
        legend=dict(
            orientation="h",
            y=1.02,
            x=0
        )
    )

    # Melhora a visualização do eixo X.
    fig.update_xaxes(
        rangeslider_visible=False,
        nticks=10,
        showgrid=True,
        rangebreaks=[
            dict(bounds=["sat", "mon"])
        ]
    )

    # Mantém a grade horizontal.
    fig.update_yaxes(
        showgrid=True
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

    # Define título, eixos e aparência geral.
    fig.update_layout(
        title=f"Volume negociado — {ticker_exibicao}",
        xaxis_title="Data e hora",
        yaxis_title="Quantidade de ações",
        template="plotly_white",
        height=300,
        showlegend=False
    )

    # Remove o seletor inferior.
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

    # Padroniza os nomes das colunas.
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

    # Converte as colunas para datetime.
    dados_acao["Data"] = pd.to_datetime(
        dados_acao["Data"]
    )

    dados_ibov["Data"] = pd.to_datetime(
        dados_ibov["Data"]
    )

    # Remove possíveis informações de fuso horário.
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

    # Mantém somente datas presentes
    # simultaneamente nas duas séries.
    comparacao = pd.merge(
        dados_acao,
        dados_ibov,
        on="Data",
        how="inner"
    )

    # Remove dados incompletos e organiza cronologicamente.
    comparacao = (
        comparacao
        .dropna()
        .sort_values("Data")
        .reset_index(drop=True)
    )

    # Caso não existam datas em comum.
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

    # Normaliza as séries.
    comparacao["Acao_normalizada"] = normalizar_serie(
        comparacao["Acao"]
    )

    comparacao["Ibovespa_normalizado"] = normalizar_serie(
        comparacao["Ibovespa"]
    )

    # Inicializa o gráfico comparativo.
    fig = go.Figure()

    # Linha da ação.
    fig.add_trace(
        go.Scatter(
            x=comparacao["Data"],
            y=comparacao["Acao_normalizada"],
            mode="lines",
            name=ticker_exibicao
        )
    )

    # Linha do Ibovespa.
    fig.add_trace(
        go.Scatter(
            x=comparacao["Data"],
            y=comparacao["Ibovespa_normalizado"],
            mode="lines",
            name="Ibovespa"
        )
    )

    # Linha de referência da base 100.
    fig.add_hline(
        y=100,
        line_dash="dash"
    )

    # Configuração visual.
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

    # Remove o seletor inferior.
    fig.update_xaxes(
        rangeslider_visible=False
    )

    return fig
