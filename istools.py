# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ISTools - Main Plugin Class
                                 A QGIS plugin
 Professional vectorization toolkit for QGIS
                              -------------------
        begin                : 2025-01-15
        git sha              : $Format:%H$
        copyright            : (C) 2025 by Irlan Souza, 3° Sgt Brazilian Army
        email                : irlansouza193@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os
from qgis.PyQt.QtCore import QCoreApplication, QSettings, QTranslator
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QMenu
from qgis.core import QgsApplication
from .extend_lines import ExtendLines
from .polygon_generator import QgisPolygonGenerator
from .bounded_polygon_generator import BoundedPolygonGenerator
from .point_on_surface_generator import PointOnSurfaceGenerator
from .intersection_line import IntersectionLineTool
from .translations.translate import translate


class ISTools:
    """
    Main plugin class for ISTools - Professional vectorization toolkit for QGIS.
    
    This class manages the initialization, GUI setup, and cleanup of all ISTools
    components including extend lines, polygon generators, and point generators.
    """
    
    def tr(self, *string):
        """
        Traduz strings usando o novo sistema de tradução bilíngue.
        
        Args:
            *string: (inglês, português) ou string única
            
        Returns:
            str: String traduzida conforme o locale do QGIS
        """
        return translate(string, QgsApplication.locale()[:2])
    
    def __init__(self, iface):
        """
        Initialize the ISTools plugin.
        
        Args:
            iface: QGIS interface object
        """
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        self.translator = None  # Initialize translator attribute
        
        # Create ISTools submenu for Vector menu
        self.menu = QMenu(self.tr("ISTools", "ISTools"))
        
        # Create ISTools toolbar
        self.toolbar = self.iface.addToolBar("ISTools")
        self.toolbar.setObjectName("ISToolsToolbar")
        
        self.actions = []
        
        # Initialize tool instances
        self.extend_lines = None
        self.polygon_generator = None
        self.bounded_polygon_generator = None
        self.point_on_surface_generator = None
        self.intersection_line_tool = None

    def _initialize_translation(self):
        """
        Inicializa sistema de tradução com pt_BR como idioma padrão.
        Prioriza português brasileiro para melhor experiência do usuário.
        """
        # Detecção inteligente de locale com prioridade para pt_BR
        system_locale = QSettings().value('locale/userLocale', '')
        
        # Se o sistema estiver em qualquer variante de português, força pt_BR
        if system_locale.startswith('pt'):
            locale = 'pt_BR'
        else:
            # Para outros idiomas, usa detecção normal mas com pt_BR como fallback
            locale = system_locale[:2] if system_locale and len(system_locale) >= 2 else 'pt_BR'
        
        # Lista de prioridade de idiomas para tentar
        locales_to_try = [locale, 'pt_BR', 'pt', 'en']
        # Remove duplicatas mantendo ordem
        locales_to_try = list(dict.fromkeys(locales_to_try))
        
        for try_locale in locales_to_try:
            locale_path = os.path.join(self.plugin_dir, 'i18n', f'istools_{try_locale}.qm')
            
            if os.path.exists(locale_path):
                self.translator = QTranslator()
                if self.translator.load(locale_path):
                    if QCoreApplication.installTranslator(self.translator):
                        print(f"Tradução {try_locale} carregada com sucesso!")
                        return
                    else:
                        print(f"Falha ao instalar tradutor para {try_locale}")
                else:
                    print(f"Falha ao carregar: {locale_path}")
        
        print("Nenhuma tradução pôde ser carregada")
        self.translator = None

    def initGui(self):
        """
        Initialize the plugin GUI by creating menu items and toolbar actions.
        
        This method sets up all the tools and their corresponding actions,
        icons, tooltips, and connects them to their respective functions.
        """
        # Initialize translation system when QGIS is fully loaded
        self._initialize_translation()
        
        # Initialize and setup Extend Lines tool
        self._setup_extend_lines_tool()
        
        # Initialize and setup Polygon Generator tool
        self._setup_polygon_generator_tool()
        
        # Initialize and setup Bounded Polygon Generator tool
        self._setup_bounded_polygon_generator_tool()
        
        # Initialize and setup Point on Surface Generator tool
        self._setup_point_on_surface_generator_tool()
        
        # Initialize and setup Intersection Line tool
        self._setup_intersection_line_tool()

        # Add ISTools submenu to Vector menu
        vector_menu = self.iface.vectorMenu()
        vector_menu.addMenu(self.menu)

    def _setup_extend_lines_tool(self):
        """
        Setup the Extend Lines tool with its action, icon, and menu entry.
        """
        self.extend_lines = ExtendLines(self.iface)
        extend_icon_path = os.path.join(self.plugin_dir, "icon_extend_lines.png")
        
        extend_action = QAction(
            QIcon(extend_icon_path),
            self.tr("Extend Lines", "Estender Linhas"),
            self.iface.mainWindow()
        )
        extend_action.setToolTip(self.tr("Extends loose lines until they touch other lines", "Estende linhas soltas até tocarem outras linhas"))
        extend_action.triggered.connect(self.extend_lines.run)
        
        self._add_action_to_interface(extend_action)

    def _setup_polygon_generator_tool(self):
        """
        Setup the Polygon Generator tool with its action, icon, and menu entry.
        """
        self.polygon_generator = QgisPolygonGenerator(self.iface)
        polygon_icon_path = os.path.join(self.plugin_dir, "icon_polygon_generator.png")
        
        polygon_action = QAction(
            QIcon(polygon_icon_path),
            self.tr("Polygon Generator", "Gerador de Polígonos"),
            self.iface.mainWindow()
        )
        polygon_action.setToolTip(self.tr("Generates polygons from lines or areas around a point", "Gera polígonos a partir de linhas ou áreas ao redor de um ponto"))
        polygon_action.triggered.connect(self.polygon_generator.activate_tool)
        
        self._add_action_to_interface(polygon_action)

    def _setup_bounded_polygon_generator_tool(self):
        """
        Setup the Bounded Polygon Generator tool with its action, icon, and menu entry.
        """
        self.bounded_polygon_generator = BoundedPolygonGenerator(self.iface)
        bounded_polygon_icon_path = os.path.join(
            self.plugin_dir, 
            "icon_bounded_polygon_generator.png"
        )
        
        bounded_polygon_action = QAction(
            QIcon(bounded_polygon_icon_path),
            self.tr("Bounded Polygon Generator", "Gerador de Polígonos Limitados"),
            self.iface.mainWindow()
        )
        bounded_polygon_action.setToolTip(
            self.tr("Generates bounded polygons from a frame and line or polygon layers", "Gera polígonos limitados a partir de um quadro e camadas de linhas ou polígonos")
        )
        bounded_polygon_action.triggered.connect(
            self.bounded_polygon_generator.activate_tool
        )
        
        self._add_action_to_interface(bounded_polygon_action)

    def _setup_point_on_surface_generator_tool(self):
        """
        Setup the Point on Surface Generator tool with its action, icon, and menu entry.
        """
        self.point_on_surface_generator = PointOnSurfaceGenerator(self.iface)
        point_icon_path = os.path.join(
            self.plugin_dir, 
            "icon_point_on_surface_generator.png"
        )
        
        point_action = QAction(
            QIcon(point_icon_path),
            self.tr("Point on Surface Generator", "Gerador de Pontos na Superfície"),
            self.iface.mainWindow()
        )
        point_action.setToolTip(self.tr("Generates points inside selected polygons", "Gera pontos dentro de polígonos selecionados"))
        point_action.triggered.connect(self.point_on_surface_generator.run)
        
        self._add_action_to_interface(point_action)

    def _setup_intersection_line_tool(self):
        """
        Setup the Intersection Line tool with its action, icon, and menu entry.
        """
        self.intersection_line_tool = IntersectionLineTool(self.iface)
        intersection_icon_path = os.path.join(
            self.plugin_dir, 
            "icon_intersection_line.png"
        )
        
        intersection_action = QAction(
            QIcon(intersection_icon_path),
            self.tr("Intersection Line", "Interseção de Linhas"),
            self.iface.mainWindow()
        )
        intersection_action.setToolTip(self.tr("Insert shared vertices at line intersections within a selected area", "Insere vértices compartilhados nas interseções de linhas dentro de uma área selecionada"))
        intersection_action.triggered.connect(self.intersection_line_tool.activate)
        
        self._add_action_to_interface(intersection_action)

    def _add_action_to_interface(self, action):
        """
        Add an action to the plugin menu and toolbar.
        
        Args:
            action: QAction object to be added to the interface
        """
        self.actions.append(action)
        self.menu.addAction(action)
        self.toolbar.addAction(action)

    def unload(self):
        """
        Clean up the plugin by removing all actions and unloading tools.
        
        This method is called when the plugin is unloaded and ensures
        proper cleanup of all GUI elements and tool instances.
        """
        # Remove actions from toolbar and menu
        for action in self.actions:
            self.iface.removeToolBarIcon(action)
            self.toolbar.removeAction(action)
            self.menu.removeAction(action)
            
        # Remove ISTools submenu from Vector menu
        vector_menu = self.iface.vectorMenu()
        vector_menu.removeAction(self.menu.menuAction())
        
        # Remove ISTools toolbar
        if self.toolbar:
            del self.toolbar
            self.toolbar = None
            
        # Unload all tools
        self._unload_tools()
        
        # Remove translator if it exists
        if hasattr(self, 'translator'):
            QCoreApplication.removeTranslator(self.translator)
        
        # Clear actions list
        self.actions = []

    def _unload_tools(self):
        """
        Unload all individual tools and clean up their resources.
        """
        if self.extend_lines:
            self.extend_lines.unload()
            self.extend_lines = None
            
        if self.polygon_generator:
            self.polygon_generator.unload()
            self.polygon_generator = None
            
        if self.bounded_polygon_generator:
            self.bounded_polygon_generator.unload()
            self.bounded_polygon_generator = None
            
        if self.point_on_surface_generator:
            self.point_on_surface_generator.unload()
            self.point_on_surface_generator = None
            
        if self.intersection_line_tool:
            self.intersection_line_tool.deactivate()
            self.intersection_line_tool = None