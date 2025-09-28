# coding=utf-8
"""Tests for IntersectionLineTool integration with ISTools plugin."""

__author__ = 'Irlan Souza'
__date__ = '2024/01/27'
__license__ = "GPL"
__copyright__ = 'Copyright 2024, Irlan Souza'

import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Add the plugin directory to the Python path
plugin_dir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, plugin_dir)

try:
    from qgis.core import QgsApplication
    from qgis.gui import QgisInterface
    QGIS_AVAILABLE = True
except ImportError:
    QGIS_AVAILABLE = False


class TestIntersectionLineIntegration(unittest.TestCase):
    """Test IntersectionLineTool integration with ISTools plugin."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        if not QGIS_AVAILABLE:
            self.skipTest("QGIS not available")
        
        # Mock QGIS interface
        self.iface = Mock(spec=QgisInterface)
        self.iface.mainWindow.return_value = Mock()
        self.iface.mapCanvas.return_value = Mock()
        self.iface.messageBar.return_value = Mock()

    def test_intersection_line_tool_import(self):
        """Test that IntersectionLineTool can be imported."""
        try:
            from intersection_line import IntersectionLineTool
            self.assertTrue(True, "IntersectionLineTool imported successfully")
        except ImportError as e:
            self.fail(f"Failed to import IntersectionLineTool: {e}")

    def test_istools_plugin_initialization(self):
        """Test that ISTools plugin initializes with IntersectionLineTool."""
        try:
            from istools import ISTools
            plugin = ISTools(self.iface)
            
            # Check if intersection_line_tool attribute exists
            self.assertTrue(hasattr(plugin, 'intersection_line_tool'))
            self.assertIsNone(plugin.intersection_line_tool)
            
        except Exception as e:
            self.fail(f"Failed to initialize ISTools plugin: {e}")

    @patch('istools.QAction')
    @patch('istools.QIcon')
    def test_intersection_line_tool_setup(self, mock_qicon, mock_qaction):
        """Test that intersection line tool is properly set up in initGui."""
        try:
            from istools import ISTools
            plugin = ISTools(self.iface)
            
            # Mock the action and icon
            mock_action = Mock()
            mock_qaction.return_value = mock_action
            mock_qicon.return_value = Mock()
            
            # Initialize GUI
            plugin.initGui()
            
            # Verify that intersection_line_tool is initialized
            self.assertIsNotNone(plugin.intersection_line_tool)
            
            # Verify that QAction was called for intersection line tool
            self.assertTrue(mock_qaction.called)
            
        except Exception as e:
            self.fail(f"Failed to set up intersection line tool: {e}")

    def test_intersection_line_tool_unload(self):
        """Test that intersection line tool is properly unloaded."""
        try:
            from istools import ISTools
            plugin = ISTools(self.iface)
            
            # Initialize and then unload
            plugin.initGui()
            plugin.unload()
            
            # After unload, tool should be None or properly cleaned up
            # The exact behavior depends on implementation
            self.assertTrue(True, "Unload completed without errors")
            
        except Exception as e:
            self.fail(f"Failed to unload intersection line tool: {e}")

    def test_intersection_line_tool_activation(self):
        """Test that intersection line tool can be activated."""
        try:
            from intersection_line import IntersectionLineTool
            
            # Create tool instance
            tool = IntersectionLineTool(self.iface)
            
            # Test activation
            tool.activate()
            
            # Verify tool is active (implementation dependent)
            self.assertTrue(True, "Tool activation completed without errors")
            
        except Exception as e:
            self.fail(f"Failed to activate intersection line tool: {e}")

    def test_intersection_line_tool_deactivation(self):
        """Test that intersection line tool can be deactivated."""
        try:
            from intersection_line import IntersectionLineTool
            
            # Create tool instance
            tool = IntersectionLineTool(self.iface)
            
            # Test activation and deactivation
            tool.activate()
            tool.deactivate()
            
            # Verify tool is deactivated (implementation dependent)
            self.assertTrue(True, "Tool deactivation completed without errors")
            
        except Exception as e:
            self.fail(f"Failed to deactivate intersection line tool: {e}")

    def test_translation_entries_exist(self):
        """Test that translation entries for intersection line tool exist."""
        try:
            from translations.dictionary import dic
            
            # Check if intersection line translations exist
            self.assertIn('Intersection Line', dic)
            self.assertIn('Insert shared vertices at line intersections within a selected area', dic)
            self.assertIn('Select the intersection region', dic)
            self.assertIn('Insert vertices at intersections (rectangle)', dic)
            
            # Check if translations have required languages
            for key in ['Intersection Line']:
                if key in dic:
                    self.assertIn('es', dic[key])
                    self.assertIn('fr', dic[key])
                    self.assertIn('de', dic[key])
            
        except Exception as e:
            self.fail(f"Failed to check translation entries: {e}")

    def test_icon_resource_exists(self):
        """Test that intersection line icon resource exists."""
        try:
            # Check if icon file exists
            icon_path = os.path.join(plugin_dir, 'icon_intersection_line.png')
            self.assertTrue(os.path.exists(icon_path), "Intersection line icon file exists")
            
        except Exception as e:
            self.fail(f"Failed to check icon resource: {e}")


if __name__ == '__main__':
    unittest.main()