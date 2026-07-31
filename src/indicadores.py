import pandas as pd


def calcular_medias_moveis(
    base: pd.DataFrame
) -> pd.DataFrame:
    """
    Calcula as médias móveis de 20 e 50 períodos
    a partir do preço de fechamento.
    """

    # Cria uma cópia para preservar o DataFrame original.
    base = base.copy()

    # A MM20 representa a média dos últimos 20
    # preços de fechamento disponíveis.
    base["MM20"] = (
        base["Close"]
        .rolling(window=20)
        .mean()
    )

    # A MM50 representa a média dos últimos 50
    # preços de fechamento disponíveis.
    base["MM50"] = (
        base["Close"]
        .rolling(window=50)
        .mean()
    )

    return base


def calcular_indicadores(
    base: pd.DataFrame
) -> dict:
    """
    Calcula os principais indicadores utilizados
    no resumo da ação.
    """

    # Utiliza o primeiro e o último fechamento para
    # calcular o desempenho da ação no período.
    primeira_cotacao = float(
        base["Close"].iloc[0]
    )

    ultima_cotacao = float(
        base["Close"].iloc[-1]
    )

    # Calcula a variação percentual entre o início
    # e o fim do período selecionado.
    variacao = (
        (ultima_cotacao - primeira_cotacao)
        / primeira_cotacao
    ) * 100

    # Obtém o maior e o menor preço registrados.
    maxima = float(
        base["High"].max()
    )

    minima = float(
        base["Low"].min()
    )

    # Soma o volume negociado no período.
    # Caso a coluna não exista, utiliza zero.
    if "Volume" in base.columns:
        volume_total = float(
            base["Volume"]
            .fillna(0)
            .sum()
        )
    else:
        volume_total = 0.0

    # Reúne os resultados para facilitar o uso no app.py.
    return {
        "primeira_cotacao": primeira_cotacao,
        "ultima_cotacao": ultima_cotacao,
        "variacao": variacao,
        "maxima": maxima,
        "minima": minima,
        "volume_total": volume_total
    }


def normalizar_serie(
    serie: pd.Series
) -> pd.Series:
    """
    Normaliza uma série para que o primeiro valor
    válido seja igual a 100.
    """

    # Remove valores ausentes antes da normalização.
    serie = serie.dropna()

    if serie.empty:
        return serie

    primeiro_valor = serie.iloc[0]

    # Evita divisão por zero durante o cálculo.
    if primeiro_valor == 0:
        return serie

    # Converte a série para uma base comum iniciada em 100.
    # Isso permite comparar ativos com preços diferentes.
    return (
        serie / primeiro_valor
    ) * 100


def formatar_valor_mercado(
    valor_mercado
) -> str:
    """
    Formata o valor de mercado para exibição
    em milhões ou bilhões de reais.
    """

    if valor_mercado is None:
        return "Não informado"

    try:
        valor_mercado = float(
            valor_mercado
        )

        # Exibe valores acima de um bilhão de forma resumida.
        if valor_mercado >= 1_000_000_000:
            return (
                f"R$ "
                f"{valor_mercado / 1_000_000_000:.2f} "
                f"bilhões"
            )

        # Exibe valores acima de um milhão de forma resumida.
        if valor_mercado >= 1_000_000:
            return (
                f"R$ "
                f"{valor_mercado / 1_000_000:.2f} "
                f"milhões"
            )

        # Mantém o valor completo quando ele é inferior a um milhão.
        return f"R$ {valor_mercado:,.0f}"

    except (TypeError, ValueError):
        return "Não informado"


def formatar_numero(valor) -> str:
    """
    Formata um valor numérico com duas casas decimais.
    """

    if valor is None:
        return "Não informado"

    try:
        return f"{float(valor):.2f}"

    except (TypeError, ValueError):
        return "Não informado"


def formatar_percentual(valor) -> str:
    """
    Converte um valor decimal para percentual.
    """

    if valor is None:
        return "Não informado"

    try:
        # O Yahoo Finance normalmente retorna percentuais
        # em formato decimal. Exemplo: 0.05 representa 5%.
        return f"{float(valor) * 100:.2f}%"

    except (TypeError, ValueError):
        return "Não informado"