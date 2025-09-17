# -*- coding: utf-8 -*-
"""
ISTools Plugin for QGIS

A collection of vectorization tools for QGIS including line extension,
polygon generation, bounded polygon creation, and point on surface generation.

Author: Irlan Souza
Email: irlan.souza@example.com
Version: 1.2
License: GPL v2
"""

import os
from qgis.PyQt.QtCore import QTranslator, QCoreApplication, qVersion
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QMenu
from qgis.core import QgsApplication
from .extend_lines import ExtendLines
from .polygon_generator import QgisPolygonGenerator
from .bounded_polygon_generator import BoundedPolygonGenerator
from .point_on_surface_generator import PointOnSurfaceGenerator


def tr(message):
    """Get the translation for a string using Qt translation API.
    
    Args:
        message (str): String to be translated
        
    Returns:
        str: Translated string
    """
    return QCoreApplication.translate('ISTools', message)


class ISTools:
    """Main plugin class for ISTools.
    
    This class manages the initialization and cleanup of all ISTools
    functionalities within QGIS interface.
    """
    def __init__(self, iface):
        """Initialize the ISTools plugin.
        
        Args:
            iface: QGIS interface instance
        """
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        self.menu = QMenu(tr("ISTools"), self.iface.mainWindow().menuBar())
        self.actions = []
        
        # Initialize internationalization
        self.translator = None
        self._init_translator()
        
        # Initialize tool instances
        self.extend_lines = None
        self.polygon_generator = None
        self.bounded_polygon_generator = None
        self.point_on_surface_generator = None

    def _init_translator(self):
        """Initialize the translation system"""
        try:
            # Get the locale from QGIS settings
            locale = QgsSettings().value('locale/userLocale', 'en')[0:2]
            
            # Define translation file path
            locale_path = os.path.join(
                os.path.dirname(__file__),
                'i18n',
                f'istools_{locale}.qm'
            )
            
            # Check if translation file exists
            if os.path.exists(locale_path):
                self.translator = QTranslator()
                if self.translator.load(locale_path):
                    QCoreApplication.installTranslator(self.translator)
                    print(f"ISTools: Loaded translation for {locale}")
                else:
                    print(f"ISTools: Failed to load translation file: {locale_path}")
                    self.translator = None
            else:
                print(f"ISTools: Translation file not found: {locale_path}")
                print("ISTools: Using default English strings")
                self.translator = None
                
        except Exception as e:
            print(f"ISTools: Error initializing translator: {e}")
            self.translator = None

    def initGui(self):
        """Initialize the plugin GUI components.
        
        Creates all toolbar actions and menu items for the plugin tools.
        """
        self._init_extend_lines_tool()
        self._init_polygon_generator_tool()
        self._init_bounded_polygon_generator_tool()
        self._init_point_on_surface_generator_tool()
        
        # Add ISTools menu to QGIS Plugins menu
        plugin_menu = self.iface.pluginMenu()
        plugin_menu.addMenu(self.menu)
    
    def _init_extend_lines_tool(self):
        """Initialize the Extend Lines tool."""
        self.extend_lines = ExtendLines(self.iface)
        extend_icon_path = os.path.join(self.plugin_dir, "icon_extend_lines.png")
        extend_action = QAction(
            QIcon(extend_icon_path),
            tr("Extend Lines"),
            self.iface.mainWindow()
        )
        extend_action.setToolTip(tr("Extends loose lines until they touch other lines"))
        extend_action.triggered.connect(self.extend_lines.run)
        self.actions.append(extend_action)
        self.menu.addAction(extend_action)
        self.iface.addToolBarIcon(extend_action)
    
    def _init_polygon_generator_tool(self):
        """Initialize the Polygon Generator tool."""
        self.polygon_generator = QgisPolygonGenerator(self.iface)
        polygon_icon_path = os.path.join(self.plugin_dir, "icon_polygon_generator.png")
        polygon_action = QAction(
            QIcon(polygon_icon_path),
            tr("Polygon Generator"),
            self.iface.mainWindow()
        )
        polygon_action.setToolTip(tr("Generates polygons from lines or areas around a point"))
        polygon_action.triggered.connect(self.polygon_generator.activate_tool)
        self.actions.append(polygon_action)
        self.menu.addAction(polygon_action)
        self.iface.addToolBarIcon(polygon_action)
    
    def _init_bounded_polygon_generator_tool(self):
        """Initialize the Bounded Polygon Generator tool."""
        self.bounded_polygon_generator = BoundedPolygonGenerator(self.iface)
        bounded_polygon_icon_path = os.path.join(self.plugin_dir, "icon_bounded_polygon_generator.png")
        bounded_polygon_action = QAction(
            QIcon(bounded_polygon_icon_path),
            tr("Bounded Polygon Generator"),
            self.iface.mainWindow()
        )
        bounded_polygon_action.setToolTip(tr("Generates bounded polygons from a frame and line or polygon layers"))
        bounded_polygon_action.triggered.connect(self.bounded_polygon_generator.activate_tool)
        self.actions.append(bounded_polygon_action)
        self.menu.addAction(bounded_polygon_action)
        self.iface.addToolBarIcon(bounded_polygon_action)
    
    def _init_point_on_surface_generator_tool(self):
        """Initialize the Point on Surface Generator tool."""
        self.point_on_surface_generator = PointOnSurfaceGenerator(self.iface)
        point_icon_path = os.path.join(self.plugin_dir, "icon_point_on_surface_generator.png")
        point_action = QAction(
            QIcon(point_icon_path),
            tr("Point on Surface Generator"),
            self.iface.mainWindow()
        )
        point_action.setToolTip(tr("Generates points inside selected polygons"))
        point_action.triggered.connect(self.point_on_surface_generator.run)
        self.actions.append(point_action)
        self.menu.addAction(point_action)
        self.iface.addToolBarIcon(point_action)

    def unload(self):
        """Clean up plugin resources when unloading.
        
        Removes all actions from toolbar and menu, unloads tools,
        and cleans up references.
        """
        # Remove translator
        if self.translator:
            QCoreApplication.removeTranslator(self.translator)
            self.translator = None
        
        # Remove actions from toolbar and menu
        for action in self.actions:
            self.iface.removeToolBarIcon(action)
            self.menu.removeAction(action)
        
        # Remove ISTools menu from Plugins menu
        plugin_menu = self.iface.pluginMenu()
        if self.menu.menuAction() in plugin_menu.actions():
            plugin_menu.removeAction(self.menu.menuAction())
        
        # Unload tools
        if self.extend_lines:
            self.extend_lines.unload()
        if self.polygon_generator:
            self.polygon_generator.unload()
        if self.bounded_polygon_generator:
            self.bounded_polygon_generator.unload()
        if self.point_on_surface_generator:
            self.point_on_surface_generator.unload()
        
        # Clear references
        self.actions = []
        self.extend_lines = None
        self.polygon_generator = None
        self.bounded_polygon_generator = None
        self.point_on_surface_generator = None