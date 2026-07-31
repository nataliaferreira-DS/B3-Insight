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


def executar():
    """Executa a interface principal do dashboard."""

    # ==================================================
    # CONFIGURAÇÃO DA PÁGINA
    # ==================================================

    st.set_page_config(
        page_title=TITULO_APP,
        layout="wide"
    )

    st.title(TITULO_APP)
    st.caption(DESCRICAO_APP)

    # ==================================================
    # ENTRADA DO USUÁRIO
    # ==================================================

    st.sidebar.header("Configurações")

    st.sidebar.caption(
        "Informe uma ação da B3 e escolha "
        "o período que deseja analisar."
    )

    ticker_digitado = st.sidebar.text_input(
        "Ticker da ação",
        value=TICKER_PADRAO,
        placeholder="Exemplo: PETR4"
    )

    periodo = st.sidebar.selectbox(
        "Período de análise",
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
        "Exemplos de tickers: PETR4, VALE3, "
        "ITUB4, BBAS3 e BBDC4."
    )

    # ==================================================
    # VALIDAÇÃO DA ENTRADA
    # ==================================================

    # Interrompe a execução até que o usuário solicite a análise.
    if not analisar:
        st.info(
            "Utilize a barra lateral para selecionar "
            "uma ação e iniciar a análise."
        )
        return

    # Verifica se um ticker foi informado.
    if not ticker_digitado.strip():
        st.warning(
            "Digite o código de uma ação."
        )
        return

    # Padroniza o ticker para o formato aceito pelo Yahoo Finance.
    ticker = padronizar_ticker(
        ticker_digitado
    )

    # ==================================================
    # BUSCA DOS DADOS
    # ==================================================

    # Carrega os dados históricos da ação, do Ibovespa
    # e as informações gerais da empresa.
    with st.spinner(
        f"Buscando dados de {ticker}..."
    ):
        base = baixar_dados_acao(
            ticker=ticker,
            periodo=periodo
        )

        ibov = baixar_dados_ibovespa(
            periodo=periodo
        )

        info = buscar_informacoes_empresa(
            ticker
        )

    # ==================================================
    # VALIDAÇÃO E LIMPEZA DOS DADOS
    # ==================================================

    # Confirma se a consulta retornou dados da ação.
    if base.empty:
        st.error(
            "Não encontrei dados para esse ticker. "
            "Confira se o código foi digitado corretamente."
        )
        return

    # Padroniza as colunas e remove registros inválidos.
    base = limpar_dados_acao(
        base
    )

    ibov = limpar_dados_ibovespa(
        ibov
    )

    # Confirma se ainda existem dados válidos após a limpeza.
    if base.empty:
        st.error(
            "Os dados encontrados não possuem "
            "informações suficientes para a análise."
        )
        return

    # Identifica as colunas de data utilizadas nos gráficos.
    coluna_data = identificar_coluna_data(
        base
    )

    coluna_data_ibov = identificar_coluna_data(
        ibov
    )

    if coluna_data is None:
        st.error(
            "Não foi possível identificar "
            "a coluna de data da ação."
        )
        return

    # ==================================================
    # CÁLCULO DOS INDICADORES
    # ==================================================

    # Adiciona médias móveis ao DataFrame e calcula
    # os indicadores apresentados no dashboard.
    base = calcular_medias_moveis(
        base
    )

    indicadores = calcular_indicadores(
        base
    )

    ultima_cotacao = indicadores[
        "ultima_cotacao"
    ]

    variacao = indicadores[
        "variacao"
    ]

    maxima = indicadores[
        "maxima"
    ]

    minima = indicadores[
        "minima"
    ]

    volume_total = indicadores[
        "volume_total"
    ]

    # ==================================================
    # INFORMAÇÕES DA EMPRESA
    # ==================================================

    # Obtém as principais informações da empresa.
    # Quando um dado não está disponível, exibe "Não informado".
    nome_empresa = info.get(
        "longName",
        "Não informado"
    )

    setor = info.get(
        "sector",
        "Não informado"
    )

    segmento = info.get(
        "industry",
        "Não informado"
    )

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

    setor = traducoes_setores.get(
        setor,
        setor
    )

    segmento = traducoes_segmentos.get(
        segmento,
        segmento
    )

    valor_mercado_formatado = formatar_valor_mercado(
        info.get("marketCap")
    ).replace(".", ",")

    pl_formatado = formatar_numero(
        info.get("trailingPE")
    ).replace(".", ",")

    dividend_yield = info.get(
        "dividendYield"
    )

    if dividend_yield is None:
        dividend_yield_formatado = "Não informado"
    else:
        dividend_yield = float(
            dividend_yield
        )

        if abs(dividend_yield) <= 1:
            dividend_yield *= 100

        dividend_yield_formatado = (
            f"{dividend_yield:.2f}%"
            .replace(".", ",")
        )

    ultima_atualizacao = base[
        coluna_data
    ].max()

    if hasattr(
        ultima_atualizacao,
        "strftime"
    ):
        ultima_atualizacao = ultima_atualizacao.strftime(
            "%d/%m/%Y às %H:%M"
        )
    else:
        ultima_atualizacao = str(
            ultima_atualizacao
        )

    # ==================================================
    # CABEÇALHO DA ANÁLISE
    # ==================================================

    st.success(
    f"Dados carregados para {ticker.replace('.SA', '')}"
    )
 

    st.caption(
        f"Período selecionado: {periodo}"
    )

    st.divider()

    # ==================================================
    # INDICADORES PRINCIPAIS
    # ==================================================

    st.subheader(
        "Indicadores do período"
    )

    # Organiza os indicadores em cinco colunas.
    (
        coluna1,
        coluna2,
        coluna3,
        coluna4,
        coluna5
    ) = st.columns(5)

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
    if volume_total >= 1_000_000_000:
      volume_formatado = (
        f"{volume_total / 1_000_000_000:.1f} bi"
        .replace(".", ",")
    )

    elif volume_total >= 1_000_000:
      volume_formatado = (
        f"{volume_total / 1_000_000:.1f} mi"
        .replace(".", ",")
    )

    elif volume_total >= 1_000:
      volume_formatado = (
        f"{volume_total / 1_000:.1f} mil"
        .replace(".", ",")
    )

    else:
      volume_formatado = (
        f"{volume_total:,.0f}"
        .replace(",", ".")
    )

    coluna5.metric(
        "Volume total de ações",
         volume_formatado
    )

    st.divider()

    # ==================================================
    # INFORMAÇÕES DA EMPRESA
    # ==================================================

    st.subheader(
        "Informações da empresa"
    )

    # Exibe as informações dentro de um bloco visual.
    with st.container(border=True):

        coluna_empresa1, coluna_empresa2 = st.columns(2)

        with coluna_empresa1:
            st.markdown(
                f"**Empresa:** {nome_empresa}"
            )

            st.markdown(
                f"**Setor:** {setor}"
            )

            st.markdown(
                f"**Segmento:** {segmento}"
            )

        with coluna_empresa2:
            st.markdown(
                f"**Valor de mercado:** "
                f"{valor_mercado_formatado}"
            )

            st.markdown(
                f"**P/L:** {pl_formatado}"
            )

            st.markdown(
                f"**Dividend Yield:** "
                f"{dividend_yield_formatado}"
            )

    st.divider()

    # ==================================================
    # GRÁFICO DE CANDLESTICK
    # ==================================================

    st.subheader(
        "Análise gráfica"
    )

    st.caption(
        "Evolução do preço da ação com as médias "
        "móveis de 20 e 50 períodos."
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

    # ==================================================
    # GRÁFICO DE VOLUME
    # ==================================================

    st.subheader(
        "Volume negociado"
    )

    st.caption(
        "Quantidade de ações negociadas "
        "ao longo do período selecionado."
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

    st.divider()

    # ==================================================
    # COMPARAÇÃO COM O IBOVESPA
    # ==================================================

    st.subheader(
        "Desempenho comparativo"
    )

    # O gráfico comparativo só é exibido quando
    # os dados do Ibovespa estão disponíveis.
    if ibov.empty or coluna_data_ibov is None:
        st.warning(
            "Não foi possível obter os dados "
            "do Ibovespa para o período selecionado."
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

        st.caption(
            "As duas séries começam em 100, "
            "permitindo comparar o desempenho "
            "percentual da ação com o Ibovespa."
        )

    st.divider()

    # ==================================================
    # TABELA DE DADOS HISTÓRICOS
    # ==================================================

    st.subheader(
        "Dados históricos"
    )

    st.caption(
        "Registros utilizados na construção "
        "dos indicadores e gráficos."
    )

    # Remove as médias móveis da tabela exportada,
    # pois elas são utilizadas apenas na análise gráfica.
    tabela = base.drop(
        columns=["MM20", "MM50"],
        errors="ignore"
    ).copy()

    # Exibe os dados históricos na própria aplicação.
    st.dataframe(
        tabela,
        use_container_width=True
    )

    # ==================================================
    # EXPORTAÇÃO DOS DADOS
    # ==================================================

    st.subheader(
        "Exportação"
    )

    st.caption(
        "Baixe os dados históricos utilizados na análise."
    )

    # Converte o DataFrame para CSV.
    arquivo_csv = tabela.to_csv(
        index=False
    ).encode(
        "utf-8-sig"
    )

    # Permite baixar os dados analisados.
    st.download_button(
        label="Baixar dados em CSV",
        data=arquivo_csv,
        file_name=(
            f"{ticker.replace('.SA', '')}_"
            f"{periodo}.csv"
        ),
        mime="text/csv",
        use_container_width=True
    )

    # ==================================================
    # RODAPÉ
    # ==================================================

    st.divider()

    st.caption(
        "Dados obtidos por meio do Yahoo Finance. "
        "Este projeto possui finalidade educacional "
        "e não constitui recomendação de investimento."
    )

    st.caption(
        f"Última atualização dos dados: {ultima_atualizacao}."
    )

    st.caption(
        "Desenvolvido por Natália Ferreira do Nascimento."
    )

# Inicia o dashboard quando este arquivo é executado.
if __name__ == "__main__":
    executar()