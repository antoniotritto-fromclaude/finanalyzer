"""
Utility per formattazione numeri in stile europeo
Formato: 1.000,00 (punto per migliaia, virgola per decimali)
"""


def format_currency_eur(value: float, decimals: int = 2) -> str:
    """
    Formatta valore in euro con formato europeo: 1.000,00€

    Args:
        value: Valore da formattare
        decimals: Numero decimali (default 2)

    Returns:
        Stringa formattata: "1.000,00€"
    """
    # Formatta con separatore migliaia punto e decimali virgola
    if decimals == 0:
        formatted = f"{value:,.0f}".replace(",", ".")
        return f"{formatted}€"
    elif decimals == 2:
        formatted = f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return f"{formatted}€"
    else:
        # Generico per qualsiasi decimale
        formatted = f"{value:,.{decimals}f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return f"{formatted}€"


def format_number_eur(value: float, decimals: int = 2) -> str:
    """
    Formatta numero con formato europeo: 1.000,00 (senza simbolo €)

    Args:
        value: Valore da formattare
        decimals: Numero decimali

    Returns:
        Stringa formattata: "1.000,00"
    """
    if decimals == 0:
        return f"{value:,.0f}".replace(",", ".")
    else:
        return f"{value:,.{decimals}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def format_percentage(value: float, decimals: int = 1) -> str:
    """
    Formatta percentuale: 12,5%

    Args:
        value: Valore percentuale (12.5 per 12.5%)
        decimals: Numero decimali

    Returns:
        Stringa formattata: "12,5%"
    """
    formatted = f"{value:.{decimals}f}".replace(".", ",")
    return f"{formatted}%"
