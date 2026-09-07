import math

import pandas as pd
import plotly.graph_objects as go

from indicadores import normalizar_serie


MAX_PONTOS_GRAFICO = 500


def preparar_dados_grafico(
    base: pd.DataFrame,
    coluna_data: str,
    max_pontos: int = MAX_PONTOS_GRAFICO
) -> pd.DataFrame:
    """
    Prepara uma cópia dos dados exclusivamente para visualização.

    Quando o conjunto já possui uma quantidade confortável de pontos,
    ele é mantido sem alterações. Em séries muito densas, os registros
    são agrupados em blocos consecutivos preservando OHLC e volume.
    Dessa forma, o dashboard continua usando os dados completos nos
    indicadores, tabela e exportação, enquanto o gráfico permanece legível.
    """

    if base.empty:
        return base.copy()

    dados = base.copy()
    dados[coluna_data] = pd.to_datetime(dados[coluna_data])
    dados = dados.sort_values(coluna_data).reset_index(drop=True)

    if len(dados) <= max_pontos:
        return dados

    tamanho_bloco = math.ceil(len(dados) / max_pontos)
    dados["_grupo_grafico"] = dados.index // tamanho_bloco

    agregacoes = {
        coluna_data: "first",
        "Open": "first",
        "High": "max",
        "Low": "min",
        "Close": "last"
    }

    if "Volume" in dados.columns:
        agregacoes["Volume"] = "sum"

    dados = (
        dados
        .groupby("_grupo_grafico", as_index=False)
        .agg(agregacoes)
    )

    # As médias são recalculadas apenas na versão visual agregada.
    # A base original permanece inalterada para os demais indicadores.
    dados["MM20"] = dados["Close"].rolling(
        window=20,
        min_periods=1
    ).mean()

    dados["MM50"] = dados["Close"].rolling(
        window=50,
        min_periods=1
    ).mean()

    return dados


def configurar_eixo_tempo(
    fig: go.Figure,
    coluna_data: pd.Series,
    mostrar_rangeslider: bool = False
) -> None:
    """
    Padroniza o eixo temporal de acordo com a duração real da série.

    Regras visuais do projeto:
    - até 2 dias: hora (HH:MM)
    - até 10 dias: dia/mês
    - até 120 dias: dia/mês
    - acima de 120 dias: mês/ano

    Assim, todos os gráficos seguem a mesma lógica sem depender
    das escolhas automáticas de formatação do Plotly.
    """

    rangebreaks = []
    tickformat = "%d/%m"
    nticks = 8

    if not coluna_data.empty:
        datas = pd.to_datetime(coluna_data).sort_values()
        duracao = datas.max() - datas.min()

        # Define explicitamente o formato do eixo X.
        if duracao <= pd.Timedelta(days=2):
            tickformat = "%H:%M"
            nticks = 8
        elif duracao <= pd.Timedelta(days=10):
            tickformat = "%d/%m"
            nticks = 6
        elif duracao <= pd.Timedelta(days=120):
            tickformat = "%d/%m"
            nticks = 8
        else:
            tickformat = "%b/%Y"
            nticks = 7

        # Remove fins de semana em séries que cobrem vários dias.
        if duracao >= pd.Timedelta(days=3):
            rangebreaks.append(
                dict(bounds=["sat", "mon"])
            )

        # Detecta séries intradiárias pela presença de vários registros
        # no mesmo dia e comprime somente as horas sem pregão.
        serie_datas = pd.Series(datas)

        registros_por_dia = (
            serie_datas
            .dt.normalize()
            .value_counts()
        )

        serie_intradiaria = (
            not registros_por_dia.empty
            and registros_por_dia.max() > 1
        )

        if serie_intradiaria:
            minutos_do_dia = (
                serie_datas.dt.hour * 60
                + serie_datas.dt.minute
            )

            primeiro_minuto = int(minutos_do_dia.min())
            ultimo_minuto = int(minutos_do_dia.max())

            # Pequena folga para não cortar o primeiro ou o último candle.
            abertura = max(0, primeiro_minuto - 5) / 60
            fechamento = min(24 * 60, ultimo_minuto + 5) / 60

            rangebreaks.append(
                dict(
                    bounds=[fechamento, abertura],
                    pattern="hour"
                )
            )

    fig.update_xaxes(
        rangeslider_visible=mostrar_rangeslider,
        showgrid=True,
        gridcolor="rgba(0, 0, 0, 0.08)",
        nticks=nticks,
        tickformat=tickformat,
        tickangle=0,
        rangebreaks=rangebreaks
    )


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

    ticker_exibicao = ticker.replace(".SA", "")
    base_grafico = preparar_dados_grafico(
        base,
        coluna_data
    )

    fig = go.Figure()

    fig.add_trace(
        go.Candlestick(
            x=base_grafico[coluna_data],
            open=base_grafico["Open"],
            high=base_grafico["High"],
            low=base_grafico["Low"],
            close=base_grafico["Close"],
            name=ticker_exibicao,
            increasing_line_color="#16a34a",
            decreasing_line_color="#dc2626",
            increasing_fillcolor="#22c55e",
            decreasing_fillcolor="#ef4444"
        )
    )

    fig.add_trace(
        go.Scatter(
            x=base_grafico[coluna_data],
            y=base_grafico["MM20"],
            mode="lines",
            name="MM20",
            line=dict(width=1.8),
            connectgaps=False
        )
    )

    fig.add_trace(
        go.Scatter(
            x=base_grafico[coluna_data],
            y=base_grafico["MM50"],
            mode="lines",
            name="MM50",
            line=dict(width=1.8),
            connectgaps=False
        )
    )

    fig.update_layout(
        title=dict(
            text=f"{ticker_exibicao} — Candlestick ({periodo})",
            x=0.01,
            y=0.98,
            xanchor="left",
            yanchor="top"
        ),
        xaxis_title=None,
        yaxis_title="Preço (R$)",
        template="plotly_white",
        height=620,
        hovermode="x unified",
        margin=dict(l=20, r=20, t=85, b=20),
        legend=dict(
            orientation="h",
            y=1.02,
            yanchor="bottom",
            x=0.01,
            xanchor="left"
        ),
        hoverlabel=dict(
            bgcolor="white",
            font_size=12
        )
    )

    configurar_eixo_tempo(
        fig,
        base_grafico[coluna_data],
        mostrar_rangeslider=False
    )

    fig.update_yaxes(
        showgrid=True,
        gridcolor="rgba(0, 0, 0, 0.08)",
        zeroline=False,
        tickprefix="R$ ",
        tickformat=".2f",
        fixedrange=False
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

    ticker_exibicao = ticker.replace(".SA", "")
    base_grafico = preparar_dados_grafico(
        base,
        coluna_data
    )

    fig = go.Figure()

    if "Volume" in base_grafico.columns:
        fig.add_trace(
            go.Bar(
                x=base_grafico[coluna_data],
                y=base_grafico["Volume"],
                name="Volume",
                marker_line_width=0,
                hovertemplate=(
                    "%{x}<br>Volume: %{y:,.0f}"
                    "<extra></extra>"
                )
            )
        )

    fig.update_layout(
        title=dict(
            text=f"Volume negociado — {ticker_exibicao}",
            x=0.01,
            xanchor="left"
        ),
        xaxis_title=None,
        yaxis_title="Quantidade de ações",
        template="plotly_white",
        height=320,
        showlegend=False,
        bargap=0.08,
        margin=dict(l=20, r=20, t=55, b=20),
        hovermode="x"
    )

    configurar_eixo_tempo(
        fig,
        base_grafico[coluna_data],
        mostrar_rangeslider=False
    )

    fig.update_yaxes(
        showgrid=True,
        gridcolor="rgba(0, 0, 0, 0.08)",
        zeroline=False,
        tickformat="~s"
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

    ticker_exibicao = ticker.replace(".SA", "")

    dados_acao = base[
        [coluna_data, "Close"]
    ].copy()

    dados_ibov = ibov[
        [coluna_data_ibov, "Close"]
    ].copy()

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

    dados_acao["Data"] = pd.to_datetime(
        dados_acao["Data"]
    )

    dados_ibov["Data"] = pd.to_datetime(
        dados_ibov["Data"]
    )

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

    comparacao = pd.merge(
        dados_acao,
        dados_ibov,
        on="Data",
        how="inner"
    )

    comparacao = (
        comparacao
        .dropna()
        .sort_values("Data")
        .reset_index(drop=True)
    )

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

    comparacao["Acao_normalizada"] = normalizar_serie(
        comparacao["Acao"]
    )

    comparacao["Ibovespa_normalizado"] = normalizar_serie(
        comparacao["Ibovespa"]
    )

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=comparacao["Data"],
            y=comparacao["Acao_normalizada"],
            mode="lines",
            name=ticker_exibicao,
            line=dict(width=2)
        )
    )

    fig.add_trace(
        go.Scatter(
            x=comparacao["Data"],
            y=comparacao["Ibovespa_normalizado"],
            mode="lines",
            name="Ibovespa",
            line=dict(width=2)
        )
    )

    fig.add_hline(
        y=100,
        line_dash="dash",
        opacity=0.5
    )

    fig.update_layout(
        title=dict(
            text=f"{ticker_exibicao} vs. Ibovespa",
            x=0.01,
            y=0.98,
            xanchor="left",
            yanchor="top"
        ),
        xaxis_title=None,
        yaxis_title="Desempenho normalizado (base 100)",
        template="plotly_white",
        height=500,
        hovermode="x unified",
        margin=dict(l=20, r=20, t=80, b=20),
        legend=dict(
            orientation="h",
            y=1.02,
            yanchor="bottom",
            x=0.01,
            xanchor="left"
        )
    )

    configurar_eixo_tempo(
        fig,
        comparacao["Data"],
        mostrar_rangeslider=False
    )

    fig.update_yaxes(
        showgrid=True,
        gridcolor="rgba(0, 0, 0, 0.08)",
        zeroline=False
    )

    return fig