# coding=utf-8
"""Resources test.

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

try:
    from qgis.PyQt.QtGui import QIcon
    QGIS_AVAILABLE = True
except ImportError:
    # Mock QIcon for testing without QGIS
    class QIcon:
        def __init__(self, path=None):
            self.path = path
        def isNull(self):
            return False
    QGIS_AVAILABLE = False


class ISToolsResourcesTest(unittest.TestCase):
    """Test resources work."""

    def setUp(self):
        """Runs before each test."""
        self.plugin_dir = os.path.dirname(os.path.dirname(__file__))

    def test_icon_istools(self):
        """Test icon_istools.png can be loaded."""
        icon_path = os.path.join(self.plugin_dir, 'icon_istools.png')
        self.assertTrue(os.path.exists(icon_path), f"Icon file not found: {icon_path}")
        icon = QIcon(icon_path)
        self.assertIsNotNone(icon)
        if QGIS_AVAILABLE:
            self.assertFalse(icon.isNull())

    def test_icon_extend_lines(self):
        """Test icon_extend_lines.png can be loaded."""
        icon_path = os.path.join(self.plugin_dir, 'icon_extend_lines.png')
        self.assertTrue(os.path.exists(icon_path), f"Icon file not found: {icon_path}")
        icon = QIcon(icon_path)
        self.assertIsNotNone(icon)
        if QGIS_AVAILABLE:
            self.assertFalse(icon.isNull())

    def test_icon_polygon_generator(self):
        """Test icon_polygon_generator.png can be loaded."""
        icon_path = os.path.join(self.plugin_dir, 'icon_polygon_generator.png')
        self.assertTrue(os.path.exists(icon_path), f"Icon file not found: {icon_path}")
        icon = QIcon(icon_path)
        self.assertIsNotNone(icon)
        if QGIS_AVAILABLE:
            self.assertFalse(icon.isNull())

    def test_icon_bounded_polygon_generator(self):
        """Test icon_bounded_polygon_generator.png can be loaded."""
        icon_path = os.path.join(self.plugin_dir, 'icon_bounded_polygon_generator.png')
        self.assertTrue(os.path.exists(icon_path), f"Icon file not found: {icon_path}")
        icon = QIcon(icon_path)
        self.assertIsNotNone(icon)
        if QGIS_AVAILABLE:
            self.assertFalse(icon.isNull())

    def test_icon_point_on_surface_generator(self):
        """Test icon_point_on_surface_generator.png can be loaded."""
        icon_path = os.path.join(self.plugin_dir, 'icon_point_on_surface_generator.png')
        self.assertTrue(os.path.exists(icon_path), f"Icon file not found: {icon_path}")
        icon = QIcon(icon_path)
        self.assertIsNotNone(icon)
        if QGIS_AVAILABLE:
            self.assertFalse(icon.isNull())


if __name__ == "__main__":
    suite = unittest.makeSuite(ISToolsResourcesTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)



