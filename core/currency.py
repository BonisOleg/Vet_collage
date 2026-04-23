"""
Centralized currency management for pricing models.
Single source of truth for currency choices, symbols, and formatting.
"""
from typing import Optional, Tuple

# ISO 4217 currency codes and common naming
DEFAULT_CURRENCY = 'EUR'

CURRENCY_CHOICES: list[Tuple[str, str]] = [
    ('EUR', 'EUR (€) - Euro'),
    ('UAH', 'UAH (₴) - Ukrainian Hryvnia'),
    ('USD', 'USD ($) - US Dollar'),
    ('GBP', 'GBP (£) - British Pound'),
    ('CHF', 'CHF (Fr) - Swiss Franc'),
    ('PLN', 'PLN (zł) - Polish Zloty'),
]

# ISO currency symbols mapping
CURRENCY_SYMBOLS: dict[str, str] = {
    'EUR': '€',
    'UAH': '₴',
    'USD': '$',
    'GBP': '£',
    'CHF': 'Fr',
    'PLN': 'zł',
}


def get_currency_symbol(currency_code: str) -> str:
    """
    Get currency symbol for a given ISO currency code.
    
    Args:
        currency_code: ISO 4217 currency code (e.g., 'EUR', 'USD')
    
    Returns:
        Currency symbol (e.g., '€', '$')
        Falls back to the code itself if not found in the mapping.
    """
    return CURRENCY_SYMBOLS.get(currency_code, currency_code)


def validate_currency(currency_code: str) -> bool:
    """
    Validate if a currency code is in the supported list.
    
    Args:
        currency_code: ISO currency code to validate
    
    Returns:
        True if currency is supported, False otherwise
    """
    valid_codes = [code for code, _ in CURRENCY_CHOICES]
    return currency_code in valid_codes


def format_price(price: str | int | float, currency_code: str) -> str:
    """
    Format a price with currency symbol for display.
    
    Args:
        price: Numeric price value
        currency_code: ISO currency code
    
    Returns:
        Formatted price string (e.g., "100.50 €")
    """
    symbol = get_currency_symbol(currency_code)
    return f"{price} {symbol}"
