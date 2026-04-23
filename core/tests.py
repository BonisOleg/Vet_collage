from django.test import TestCase

from core.currency import (
    CURRENCY_CHOICES,
    CURRENCY_SYMBOLS,
    DEFAULT_CURRENCY,
    format_price,
    get_currency_symbol,
    validate_currency,
)


class CurrencyUtilsTestCase(TestCase):
    """Test currency utilities and constants."""

    def test_default_currency_is_eur(self):
        """Ensure DEFAULT_CURRENCY is set to EUR."""
        self.assertEqual(DEFAULT_CURRENCY, 'EUR')

    def test_currency_choices_not_empty(self):
        """Ensure CURRENCY_CHOICES contains values."""
        self.assertGreater(len(CURRENCY_CHOICES), 0)

    def test_currency_choices_structure(self):
        """Ensure CURRENCY_CHOICES has correct structure (code, label)."""
        for code, label in CURRENCY_CHOICES:
            self.assertIsInstance(code, str)
            self.assertIsInstance(label, str)
            self.assertEqual(len(code), 3)  # ISO codes are 3 letters

    def test_currency_symbols_contains_common_codes(self):
        """Ensure CURRENCY_SYMBOLS has common currency codes."""
        required_codes = ['EUR', 'UAH', 'USD', 'GBP', 'CHF', 'PLN']
        for code in required_codes:
            self.assertIn(code, CURRENCY_SYMBOLS)

    def test_get_currency_symbol_for_known_code(self):
        """Test get_currency_symbol returns correct symbol for known code."""
        self.assertEqual(get_currency_symbol('EUR'), '€')
        self.assertEqual(get_currency_symbol('UAH'), '₴')
        self.assertEqual(get_currency_symbol('USD'), '$')
        self.assertEqual(get_currency_symbol('GBP'), '£')
        self.assertEqual(get_currency_symbol('CHF'), 'Fr')
        self.assertEqual(get_currency_symbol('PLN'), 'zł')

    def test_get_currency_symbol_for_unknown_code(self):
        """Test get_currency_symbol returns code itself for unknown currency."""
        self.assertEqual(get_currency_symbol('XYZ'), 'XYZ')
        self.assertEqual(get_currency_symbol('UNKNOWN'), 'UNKNOWN')

    def test_validate_currency_for_valid_codes(self):
        """Test validate_currency returns True for valid currency codes."""
        self.assertTrue(validate_currency('EUR'))
        self.assertTrue(validate_currency('UAH'))
        self.assertTrue(validate_currency('USD'))
        self.assertTrue(validate_currency('GBP'))

    def test_validate_currency_for_invalid_codes(self):
        """Test validate_currency returns False for invalid currency codes."""
        self.assertFalse(validate_currency('XYZ'))
        self.assertFalse(validate_currency('INVALID'))
        self.assertFalse(validate_currency(''))

    def test_format_price_with_valid_currency(self):
        """Test format_price returns formatted string with symbol."""
        self.assertEqual(format_price(100, 'EUR'), '100 €')
        self.assertEqual(format_price(50.99, 'USD'), '50.99 $')
        self.assertEqual(format_price(1000, 'UAH'), '1000 ₴')

    def test_format_price_with_integer(self):
        """Test format_price works with integer prices."""
        self.assertEqual(format_price(100, 'EUR'), '100 €')

    def test_format_price_with_float(self):
        """Test format_price works with float prices."""
        self.assertEqual(format_price(99.99, 'EUR'), '99.99 €')

    def test_format_price_with_unknown_currency(self):
        """Test format_price uses code itself when currency is unknown."""
        self.assertEqual(format_price(100, 'XYZ'), '100 XYZ')
