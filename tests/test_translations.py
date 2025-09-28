# coding=utf-8
"""ISTools Translations Test.

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'irlan.souza@eb.mil.br'
__date__ = '2025-09-24'
__copyright__ = 'Copyright 2025, Irlan Souza, 3° Sgt Brazilian Army'

import unittest
import os
import sys

# Add the plugin directory to the path
plugin_dir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, plugin_dir)

try:
    from utilities import get_qgis_app
    QGIS_APP = get_qgis_app()
except ImportError:
    QGIS_APP = None

from translations.translate import translate


class ISToolsTranslationsTest(unittest.TestCase):
    """Test ISTools custom translation system."""

    def setUp(self):
        """Runs before each test."""
        pass

    def tearDown(self):
        """Runs after each test."""
        pass

    def test_english_translation(self):
        """Test English translation (default)."""
        # Test single string
        result = translate("Hello", "en")
        self.assertEqual(result, "Hello")
        
        # Test tuple (English, Portuguese)
        result = translate(("Hello", "Olá"), "en")
        self.assertEqual(result, "Hello")

    def test_portuguese_translation(self):
        """Test Portuguese translation."""
        # Test single string (should return as-is)
        result = translate("Hello", "pt")
        self.assertEqual(result, "Hello")
        
        # Test tuple (English, Portuguese)
        result = translate(("Hello", "Olá"), "pt")
        self.assertEqual(result, "Olá")

    def test_fallback_language(self):
        """Test fallback to English for unsupported languages."""
        # Test with unsupported language code - should fallback to Portuguese if tuple has 2 elements
        result = translate(("Hello", "Olá"), "fr")
        self.assertEqual(result, "Olá")  # Fallback para português conforme implementação

    def test_empty_string(self):
        """Test handling of empty strings."""
        result = translate("", "en")
        self.assertEqual(result, "")
        
        result = translate(("", ""), "pt")
        self.assertEqual(result, "")

    def test_none_input(self):
        """Test handling of None input."""
        result = translate(None, "en")
        self.assertEqual(result, None)  # A função retorna None para entrada None


if __name__ == "__main__":
    suite = unittest.makeSuite(ISToolsTranslationsTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
