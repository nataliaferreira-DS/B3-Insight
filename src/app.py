import streamlit as st

from config import (
    DESCRICAO_APP,
    PERIODOS,
    TICKER_PADRAO,
    TITULO_APP
)

from dados import (
    baixar_dados_acao,
    baixar_dados_ibovespa,
    buscar_informacoes_empresa,
    identificar_coluna_data,
    limpar_dados_acao,
    limpar_dados_ibovespa,
    padronizar_ticker
)

from graficos import (
    criar_grafico_candlestick,
    criar_grafico_comparacao,
    criar_grafico_volume
)

from indicadores import (
    calcular_indicadores,
    calcular_medias_moveis,
    formatar_numero,
    formatar_valor_mercado
)


def aplicar_estilo() -> None:
    """Aplica uma identidade visual mais limpa e profissional."""

    st.markdown(
        """
        <style>
        :root {
            --primary: #16324f;
            --primary-soft: #edf3f8;
            --surface: #ffffff;
            --surface-muted: #f6f8fa;
            --border: #dfe5eb;
            --text: #17212b;
            --text-muted: #667481;
        }

        .stApp {
            background: #f7f9fb;
        }

        .block-container {
            max-width: 1380px;
            padding-top: 2rem;
            padding-bottom: 3rem;
        }

        h1, h2, h3 {
            color: var(--text);
            letter-spacing: -0.02em;
        }

        h1 {
            font-size: 2.1rem !important;
            font-weight: 700 !important;
            margin-bottom: 0.25rem !important;
        }

        h2, h3 {
            font-weight: 650 !important;
        }

        [data-testid="stSidebar"] {
            background: #111f2d;
            border-right: 1px solid #1e3347;
        }

        [data-testid="stSidebar"] * {
            color: #eef4f8;
        }

        [data-testid="stSidebar"] input,
        [data-testid="stSidebar"] div[data-baseweb="select"] > div {
            background: #ffffff;
            color: #17212b;
        }

        [data-testid="stSidebar"] label p {
            font-weight: 600;
        }

        [data-testid="stMetric"] {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 1rem 1.1rem;
            min-height: 118px;
            box-shadow: 0 1px 2px rgba(16, 24, 40, 0.03);
        }

        [data-testid="stMetricLabel"] {
            color: var(--text-muted);
        }

        [data-testid="stMetricValue"] {
            color: var(--text);
            font-weight: 700;
        }

        div[data-testid="stVerticalBlockBorderWrapper"] {
            background: var(--surface);
            border-color: var(--border) !important;
            border-radius: 10px;
        }

        div[data-testid="stPlotlyChart"] {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 0.35rem;
            box-shadow: 0 1px 2px rgba(16, 24, 40, 0.03);
        }

        [data-testid="stDataFrame"] {
            border: 1px solid var(--border);
            border-radius: 10px;
            overflow: hidden;
        }

        .app-kicker {
            color: #486174;
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            margin-bottom: 0.35rem;
        }

        .app-description {
            color: var(--text-muted);
            font-size: 1rem;
            margin-top: 0;
            margin-bottom: 1.5rem;
        }

        .analysis-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 1rem;
            background: var(--surface);
            border: 1px solid var(--border);
            border-left: 4px solid var(--primary);
            border-radius: 10px;
            padding: 1rem 1.2rem;
            margin: 0.4rem 0 1.5rem 0;
        }

        .analysis-symbol {
            color: var(--text);
            font-size: 1.35rem;
            font-weight: 750;
        }

        .analysis-meta {
            color: var(--text-muted);
            font-size: 0.9rem;
        }

        .section-heading {
            margin-top: 1.7rem;
            margin-bottom: 0.2rem;
            color: var(--text);
            font-size: 1.2rem;
            font-weight: 700;
        }

        .section-caption {
            color: var(--text-muted);
            font-size: 0.9rem;
            margin-bottom: 0.8rem;
        }

        .company-label {
            color: var(--text-muted);
            font-size: 0.78rem;
            font-weight: 650;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            margin-bottom: 0.2rem;
        }

        .company-value {
            color: var(--text);
            font-size: 0.98rem;
            margin-bottom: 1rem;
        }

        hr {
            border-color: var(--border) !important;
        }

        .stButton > button,
        .stDownloadButton > button {
            border-radius: 8px;
            font-weight: 650;
        }

        [data-testid="stSidebar"] .stButton > button {
            background: #eef4f8;
            color: #13283b;
            border: none;
        }

        [data-testid="stSidebar"] .stButton > button:hover {
            background: #dfeaf2;
            color: #13283b;
        }

        @media (max-width: 900px) {
            .block-container {
                padding-top: 1.2rem;
            }

            .analysis-header {
                display: block;
            }
        }
        </style>
        """,
        unsafe_allow_html=True
    )


def titulo_secao(titulo: str, descricao: str) -> None:
    """Renderiza cabeçalhos de seção com hierarquia visual consistente."""

    st.markdown(
        f"""
        <div class="section-heading">{titulo}</div>
        <div class="section-caption">{descricao}</div>
        """,
        unsafe_allow_html=True
    )


def formatar_volume(volume_total: float) -> str:
    """Formata o volume para leitura rápida no painel."""

    if volume_total >= 1_000_000_000:
        return (
            f"{volume_total / 1_000_000_000:.1f} bi"
            .replace(".", ",")
        )

    if volume_total >= 1_000_000:
        return (
            f"{volume_total / 1_000_000:.1f} mi"
            .replace(".", ",")
        )

    if volume_total >= 1_000:
        return (
            f"{volume_total / 1_000:.1f} mil"
            .replace(".", ",")
        )

    return (
        f"{volume_total:,.0f}"
        .replace(",", ".")
    )


def executar():
    """Executa a interface principal do dashboard."""

    st.set_page_config(
        page_title=TITULO_APP,
        layout="wide",
        initial_sidebar_state="expanded"
    )

    aplicar_estilo()

    st.markdown(
        '<div class="app-kicker">Mercado de ações brasileiro</div>',
        unsafe_allow_html=True
    )
    st.title(TITULO_APP)
    st.markdown(
        f'<p class="app-description">{DESCRICAO_APP}</p>',
        unsafe_allow_html=True
    )

    st.sidebar.header("Consulta")
    st.sidebar.caption(
        "Selecione uma ação negociada na B3 e o período de análise."
    )

    ticker_digitado = st.sidebar.text_input(
        "Ticker",
        value=TICKER_PADRAO,
        placeholder="Exemplo: PETR4"
    )

    periodo = st.sidebar.selectbox(
        "Período",
        options=PERIODOS,
        index=1
    )

    analisar = st.sidebar.button(
        "Analisar ação",
        type="primary",
        use_container_width=True
    )

    st.sidebar.divider()
    st.sidebar.caption(
        "Tickers de exemplo: PETR4, VALE3, ITUB4, BBAS3 e BBDC4."
    )
    st.sidebar.caption(
        "Fonte de dados: Yahoo Finance."
    )

    if not analisar:
        with st.container(border=True):
            st.subheader("Inicie uma análise")
            st.write(
                "Use os controles na barra lateral para escolher um ticker "
                "e um período. Os indicadores e gráficos serão exibidos aqui."
            )
        return

    if not ticker_digitado.strip():
        st.warning("Digite o código de uma ação.")
        return

    ticker = padronizar_ticker(ticker_digitado)

    with st.spinner(f"Buscando dados de {ticker}..."):
        base = baixar_dados_acao(
            ticker=ticker,
            periodo=periodo
        )
        ibov = baixar_dados_ibovespa(
            periodo=periodo
        )
        info = buscar_informacoes_empresa(ticker)

    if base.empty:
        st.error(
            "Não encontrei dados para esse ticker. "
            "Confira se o código foi digitado corretamente."
        )
        return

    base = limpar_dados_acao(base)
    ibov = limpar_dados_ibovespa(ibov)

    if base.empty:
        st.error(
            "Os dados encontrados não possuem informações suficientes "
            "para a análise."
        )
        return

    coluna_data = identificar_coluna_data(base)
    coluna_data_ibov = identificar_coluna_data(ibov)

    if coluna_data is None:
        st.error("Não foi possível identificar a coluna de data da ação.")
        return

    base = calcular_medias_moveis(base)
    indicadores = calcular_indicadores(base)

    ultima_cotacao = indicadores["ultima_cotacao"]
    variacao = indicadores["variacao"]
    maxima = indicadores["maxima"]
    minima = indicadores["minima"]
    volume_total = indicadores["volume_total"]

    nome_empresa = info.get("longName", "Não informado")
    setor = info.get("sector", "Não informado")
    segmento = info.get("industry", "Não informado")

    traducoes_setores = {
        "Energy": "Energia",
        "Financial Services": "Serviços financeiros",
        "Basic Materials": "Materiais básicos",
        "Industrials": "Bens industriais",
        "Technology": "Tecnologia",
        "Utilities": "Serviços públicos"
    }

    traducoes_segmentos = {
        "Oil & Gas Integrated": "Petróleo e gás integrado",
        "Banks - Regional": "Bancos regionais",
        "Steel": "Siderurgia",
        "Electric Utilities": "Energia elétrica"
    }

    setor = traducoes_setores.get(setor, setor)
    segmento = traducoes_segmentos.get(segmento, segmento)

    valor_mercado_formatado = formatar_valor_mercado(
        info.get("marketCap")
    ).replace(".", ",")

    pl_formatado = formatar_numero(
        info.get("trailingPE")
    ).replace(".", ",")

    dividend_yield = info.get("dividendYield")

    if dividend_yield is None:
        dividend_yield_formatado = "Não informado"
    else:
        dividend_yield = float(dividend_yield)
        if abs(dividend_yield) <= 1:
            dividend_yield *= 100
        dividend_yield_formatado = (
            f"{dividend_yield:.2f}%"
            .replace(".", ",")
        )

    ultima_atualizacao = base[coluna_data].max()

    if hasattr(ultima_atualizacao, "strftime"):
        ultima_atualizacao = ultima_atualizacao.strftime(
            "%d/%m/%Y às %H:%M"
        )
    else:
        ultima_atualizacao = str(ultima_atualizacao)

    ticker_exibicao = ticker.replace(".SA", "")

    st.markdown(
        f"""
        <div class="analysis-header">
            <div>
                <div class="analysis-symbol">{ticker_exibicao}</div>
                <div class="analysis-meta">{nome_empresa}</div>
            </div>
            <div class="analysis-meta">
                Período: <strong>{periodo}</strong><br>
                Atualizado em {ultima_atualizacao}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    titulo_secao(
        "Visão geral",
        "Principais indicadores calculados para o período selecionado."
    )

    coluna1, coluna2, coluna3, coluna4, coluna5 = st.columns(5)

    coluna1.metric(
        "Última cotação",
        f"R$ {ultima_cotacao:.2f}".replace(".", ",")
    )
    coluna2.metric(
        "Variação",
        f"{variacao:.2f}%".replace(".", ",")
    )
    coluna3.metric(
        "Máxima",
        f"R$ {maxima:.2f}".replace(".", ",")
    )
    coluna4.metric(
        "Mínima",
        f"R$ {minima:.2f}".replace(".", ",")
    )
    coluna5.metric(
        "Volume total",
        formatar_volume(volume_total)
    )

    titulo_secao(
        "Empresa",
        "Informações cadastrais e indicadores fundamentalistas disponíveis."
    )

    with st.container(border=True):
        coluna_empresa1, coluna_empresa2, coluna_empresa3 = st.columns(3)

        with coluna_empresa1:
            st.markdown(
                f"""
                <div class="company-label">Empresa</div>
                <div class="company-value">{nome_empresa}</div>
                <div class="company-label">Setor</div>
                <div class="company-value">{setor}</div>
                """,
                unsafe_allow_html=True
            )

        with coluna_empresa2:
            st.markdown(
                f"""
                <div class="company-label">Segmento</div>
                <div class="company-value">{segmento}</div>
                <div class="company-label">Valor de mercado</div>
                <div class="company-value">{valor_mercado_formatado}</div>
                """,
                unsafe_allow_html=True
            )

        with coluna_empresa3:
            st.markdown(
                f"""
                <div class="company-label">P/L</div>
                <div class="company-value">{pl_formatado}</div>
                <div class="company-label">Dividend Yield</div>
                <div class="company-value">{dividend_yield_formatado}</div>
                """,
                unsafe_allow_html=True
            )

    titulo_secao(
        "Preço e tendência",
        "Candlestick com médias móveis de 20 e 50 períodos."
    )

    fig_candlestick = criar_grafico_candlestick(
        base=base,
        ticker=ticker,
        periodo=periodo,
        coluna_data=coluna_data
    )

    st.plotly_chart(
        fig_candlestick,
        use_container_width=True
    )

    titulo_secao(
        "Volume negociado",
        "Quantidade de ações negociadas ao longo do período selecionado."
    )

    fig_volume = criar_grafico_volume(
        base=base,
        ticker=ticker,
        coluna_data=coluna_data
    )

    st.plotly_chart(
        fig_volume,
        use_container_width=True
    )

    titulo_secao(
        "Desempenho relativo",
        "Comparação normalizada entre a ação e o Ibovespa, ambos com base 100."
    )

    if ibov.empty or coluna_data_ibov is None:
        st.warning(
            "Não foi possível obter os dados do Ibovespa "
            "para o período selecionado."
        )
    else:
        fig_comparacao = criar_grafico_comparacao(
            base=base,
            ibov=ibov,
            ticker=ticker,
            coluna_data=coluna_data,
            coluna_data_ibov=coluna_data_ibov
        )

        st.plotly_chart(
            fig_comparacao,
            use_container_width=True
        )

    titulo_secao(
        "Dados históricos",
        "Registros utilizados nos cálculos e na construção dos gráficos."
    )

    tabela = base.drop(
        columns=["MM20", "MM50"],
        errors="ignore"
    ).copy()

    st.dataframe(
        tabela,
        use_container_width=True,
        hide_index=True
    )

    titulo_secao(
        "Exportação",
        "Baixe os dados históricos utilizados nesta análise."
    )

    arquivo_csv = tabela.to_csv(
        index=False
    ).encode("utf-8-sig")

    st.download_button(
        label="Baixar dados em CSV",
        data=arquivo_csv,
        file_name=f"{ticker_exibicao}_{periodo}.csv",
        mime="text/csv"
    )

    st.divider()
    st.caption(
        "Dados obtidos por meio do Yahoo Finance. "
        "Projeto de finalidade educacional; não constitui recomendação de investimento."
    )
    st.caption(
        "Desenvolvido por Natália Ferreira do Nascimento."
    )


if __name__ == "__main__":
    executar()
