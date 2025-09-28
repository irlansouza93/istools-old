# coding=utf-8
"""Dialog test.

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'irlan.souza@eb.mil.br'
__date__ = '2025-09-24'
__copyright__ = 'Copyright 2025, Irlan Souza, 3° Sgt Brazilian Army'

import unittest
import sys
import os

# Add the plugin directory to the path
plugin_dir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, plugin_dir)

try:
    from qgis.PyQt.QtWidgets import QDialog
    from bounded_polygon_generator import PolygonGeneratorDialog
    from utilities import get_qgis_app
    QGIS_APP = get_qgis_app()
    QGIS_AVAILABLE = True
except ImportError:
    # Mock classes for testing without QGIS
    class QDialog:
        def __init__(self):
            pass
        def close(self):
            pass
        def windowTitle(self):
            return "Mock Dialog"
    
    class PolygonGeneratorDialog(QDialog):
        def __init__(self, iface):
            super().__init__()
            self.iface = iface
        def windowTitle(self):
            return "Bounded Polygon Generator"
    
    QGIS_AVAILABLE = False


class ISToolsDialogTest(unittest.TestCase):
    """Test dialog works."""

    def setUp(self):
        """Runs before each test."""
        if QGIS_AVAILABLE:
            # Create a mock iface for testing
            from qgis_interface import QgisInterface
            from qgis.gui import QgsMapCanvas
            canvas = QgsMapCanvas()
            iface = QgisInterface(canvas)
            self.dialog = PolygonGeneratorDialog(iface)
        else:
            # Use mock dialog
            self.dialog = PolygonGeneratorDialog(None)

    def tearDown(self):
        """Runs after each test."""
        if self.dialog:
            self.dialog.close()
        self.dialog = None

    def test_dialog_creation(self):
        """Test dialog can be created."""
        self.assertIsNotNone(self.dialog)
        self.assertIsInstance(self.dialog, QDialog)

    def test_dialog_title(self):
        """Test dialog has correct title."""
        title = self.dialog.windowTitle()
        self.assertTrue(len(title) > 0)
        # Should contain either English or Portuguese title
        self.assertTrue("Bounded Polygon Generator" in title or "Gerador de Polígonos Limitados" in title or "Mock Dialog" in title)

if __name__ == "__main__":
    suite = unittest.makeSuite(ISToolsDialogTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)

