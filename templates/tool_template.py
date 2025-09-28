# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ISTools - Tool Template
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

"""
TOOL TEMPLATE FOR ISTOOLS PLUGIN

This template provides a complete structure for creating new tools compatible
with the ISTools plugin. Follow the patterns and conventions established here
to ensure consistency and proper integration.

INSTRUCTIONS FOR USE:
1. Replace "ToolTemplate" with your tool's class name (PascalCase)
2. Replace "Tool Template" with your tool's display name
3. Replace "TOOL_TEMPLATE" with your tool's constant name (UPPER_CASE)
4. Implement the specific logic in the marked methods
5. Update the docstrings with your tool's specific information
6. Add your tool to the main plugin (istools.py)
7. Create corresponding unit tests

CUSTOMIZATION POINTS:
- Tool constants (lines 60-65)
- Initialization logic (lines 75-85)
- Map tool setup (lines 120-130)
- Event handling (lines 140-180)
- Processing logic (lines 200-250)
- Output creation (lines 270-300)
"""

import os
import uuid
from datetime import datetime
from qgis.PyQt.QtCore import QVariant, QCoreApplication, Qt
from qgis.PyQt.QtGui import QColor, QIcon, QCursor
from qgis.PyQt.QtWidgets import QMessageBox, QAction, QApplication
from qgis.core import (
    QgsProject, QgsVectorLayer, QgsFeature, QgsGeometry,
    QgsField, QgsMessageLog, Qgis, QgsApplication,
    QgsWkbTypes, QgsPointXY, QgsSymbol, QgsSingleSymbolRenderer,
    QgsCoordinateReferenceSystem, QgsCoordinateTransform,
    QgsDistanceArea, QgsUnitTypes
)
from qgis.gui import QgsMapToolEmitPoint, QgsVertexMarker, QgsRubberBand
from ..translations.translate import translate
import processing


class ToolTemplate:
    """
    Template for creating new ISTools-compatible tools.
    
    This template provides a complete structure with all necessary methods
    and patterns for creating professional QGIS tools. It includes:
    - Bilingual translation system
    - Proper resource management
    - Error handling
    - Visual feedback
    - Standard output layer creation
    - Integration with QGIS interface
    
    Replace this docstring with your tool's specific description.
    """
    
    # Tool constants - CUSTOMIZE THESE
    TOOL_NAME = "Tool Template"
    OUTPUT_LAYER_NAME = "TOOL_TEMPLATE_OUTPUT"
    ICON_PATH = ":/plugins/istools/icons/tool_template.png"
    
    # Tool configuration
    GEOMETRY_TYPE = "Point"  # Point, LineString, Polygon
    REQUIRES_SELECTION = False
    SUPPORTS_MULTIPART = True
    
    def __init__(self, iface):
        """
        Initialize the tool template.
        
        Args:
            iface (QgisInterface): QGIS interface object
        """
        # Core QGIS objects
        self.iface = iface
        self.canvas = iface.mapCanvas()
        self.project = QgsProject.instance()
        
        # Tool state
        self.is_active = False
        self.current_layer = None
        self.processing_data = []
        
        # Visual elements
        self.rubber_band = None
        self.markers = []
        self.temp_features = []
        
        # Map tools
        self.map_tool = None
        self.previous_tool = None
        
        # CUSTOMIZE: Add your tool-specific initialization here
        self._initialize_tool_specific()
    
    def _initialize_tool_specific(self):
        """
        Initialize tool-specific components.
        
        CUSTOMIZE: Add your tool's specific initialization logic here.
        Examples:
        - Configure processing algorithms
        - Set up custom parameters
        - Initialize data structures
        - Configure tool behavior
        """
        # Example: Distance calculator for measurement tools
        # self.distance_calc = QgsDistanceArea()
        # self.distance_calc.setSourceCrs(
        #     self.canvas.mapSettings().destinationCrs(),
        #     self.canvas.mapSettings().transformContext()
        # )
        
        # Example: Custom tool parameters
        # self.buffer_distance = 10.0
        # self.snap_tolerance = 5.0
        
        pass
    
    def tr(self, *string):
        """
        Bilingual translation system.
        
        Supports both single strings and bilingual tuples.
        
        Args:
            *string: Single string or (english, portuguese) tuple
            
        Returns:
            str: Translated string according to QGIS locale
            
        Examples:
            self.tr("Hello World")  # Single string
            self.tr("Hello", "Olá")  # Bilingual
        """
        return translate(string, QgsApplication.locale()[:2])
    
    def activate(self):
        """
        Activate the tool and prepare for user interaction.
        
        This method is called when the tool is selected from the toolbar
        or menu. It should prepare the tool for user interaction.
        """
        try:
            if self.is_active:
                return
            
            self.is_active = True
            
            # Store previous map tool
            self.previous_tool = self.canvas.mapTool()
            
            # Setup map tool for interaction
            self._setup_map_tool()
            
            # Setup visual elements
            self._setup_visual_elements()
            
            # Show instructions to user
            self._show_instructions()
            
            # Change cursor
            self._set_cursor()
            
            # Log activation
            QgsMessageLog.logMessage(
                f"{self.TOOL_NAME} activated",
                "ISTools",
                level=Qgis.Info
            )
            
        except Exception as e:
            self._handle_error(
                self.tr("Activation Error", "Erro de Ativação"),
                str(e)
            )
    
    def deactivate(self):
        """
        Deactivate the tool and clean up resources.
        
        This method is called when another tool is selected or when
        the plugin is unloaded. It should clean up all resources.
        """
        try:
            if not self.is_active:
                return
            
            self.is_active = False
            
            # Clean up visual elements
            self._cleanup_visual_elements()
            
            # Restore previous map tool
            self._restore_map_tool()
            
            # Reset cursor
            self._reset_cursor()
            
            # Clear processing data
            self.processing_data.clear()
            
            # Log deactivation
            QgsMessageLog.logMessage(
                f"{self.TOOL_NAME} deactivated",
                "ISTools",
                level=Qgis.Info
            )
            
        except Exception as e:
            self._handle_error(
                self.tr("Deactivation Error", "Erro de Desativação"),
                str(e)
            )
    
    def _setup_map_tool(self):
        """
        Configure map tool for user interaction.
        
        CUSTOMIZE: Implement your tool's specific map tool setup.
        Common patterns:
        - QgsMapToolEmitPoint for point-based tools
        - QgsMapToolIdentify for selection tools
        - Custom map tools for complex interactions
        """
        # Example: Point-based tool
        self.map_tool = QgsMapToolEmitPoint(self.canvas)
        self.map_tool.canvasClicked.connect(self._handle_canvas_click)
        
        # Example: Additional event connections
        # self.map_tool.canvasDoubleClicked.connect(self._handle_double_click)
        # self.map_tool.canvasMoveEvent.connect(self._handle_mouse_move)
        
        # Set the map tool
        self.canvas.setMapTool(self.map_tool)
    
    def _setup_visual_elements(self):
        """
        Setup visual feedback elements.
        
        CUSTOMIZE: Add your tool's specific visual elements.
        Examples:
        - Rubber bands for drawing
        - Vertex markers for points
        - Highlight overlays
        """
        # Example: Rubber band for line/polygon tools
        if self.GEOMETRY_TYPE in ["LineString", "Polygon"]:
            geometry_type = QgsWkbTypes.LineGeometry if self.GEOMETRY_TYPE == "LineString" else QgsWkbTypes.PolygonGeometry
            self.rubber_band = QgsRubberBand(self.canvas, geometry_type)
            self.rubber_band.setColor(QColor(255, 0, 0, 100))
            self.rubber_band.setWidth(2)
    
    def _handle_canvas_click(self, point, button):
        """
        Handle canvas click events.
        
        CUSTOMIZE: Implement your tool's click handling logic.
        
        Args:
            point (QgsPointXY): Clicked point in map coordinates
            button (Qt.MouseButton): Mouse button pressed
        """
        try:
            if button == Qt.LeftButton:
                self._handle_left_click(point)
            elif button == Qt.RightButton:
                self._handle_right_click(point)
            elif button == Qt.MiddleButton:
                self._handle_middle_click(point)
                
        except Exception as e:
            self._handle_error(
                self.tr("Click Handling Error", "Erro no Tratamento de Clique"),
                str(e)
            )
    
    def _handle_left_click(self, point):
        """
        Handle left mouse button clicks.
        
        CUSTOMIZE: Implement your tool's left-click behavior.
        Common patterns:
        - Add points to collection
        - Start/continue drawing
        - Select features
        - Trigger processing
        
        Args:
            point (QgsPointXY): Clicked point
        """
        # Example: Add point to collection
        self.processing_data.append(point)
        
        # Example: Add visual marker
        marker = QgsVertexMarker(self.canvas)
        marker.setCenter(point)
        marker.setColor(QColor(255, 0, 0))
        marker.setIconSize(8)
        marker.setIconType(QgsVertexMarker.ICON_CIRCLE)
        self.markers.append(marker)
        
        # Example: Update rubber band
        if self.rubber_band:
            self.rubber_band.addPoint(point)
        
        # Example: Process after certain number of points
        if len(self.processing_data) >= 2:  # Customize this condition
            self._process_data()
    
    def _handle_right_click(self, point):
        """
        Handle right mouse button clicks.
        
        CUSTOMIZE: Implement your tool's right-click behavior.
        Common patterns:
        - Finish current operation
        - Show context menu
        - Cancel current action
        
        Args:
            point (QgsPointXY): Clicked point
        """
        # Example: Finish current operation
        if len(self.processing_data) > 0:
            self._finish_operation()
        else:
            self._cancel_operation()
    
    def _handle_middle_click(self, point):
        """
        Handle middle mouse button clicks.
        
        CUSTOMIZE: Implement your tool's middle-click behavior.
        
        Args:
            point (QgsPointXY): Clicked point
        """
        # Example: Reset current operation
        self._reset_operation()
    
    def _process_data(self):
        """
        Process collected data and create output.
        
        CUSTOMIZE: Implement your tool's main processing logic.
        This is where the core functionality of your tool should be implemented.
        """
        try:
            if not self.processing_data:
                return
            
            # Example: Create geometry from points
            if self.GEOMETRY_TYPE == "Point" and len(self.processing_data) >= 1:
                geometry = QgsGeometry.fromPointXY(self.processing_data[0])
            elif self.GEOMETRY_TYPE == "LineString" and len(self.processing_data) >= 2:
                geometry = QgsGeometry.fromPolylineXY(self.processing_data)
            elif self.GEOMETRY_TYPE == "Polygon" and len(self.processing_data) >= 3:
                # Close polygon
                closed_points = self.processing_data + [self.processing_data[0]]
                geometry = QgsGeometry.fromPolygonXY([closed_points])
            else:
                return  # Not enough points
            
            # Create output feature
            feature = self._create_output_feature(geometry)
            
            # Add to output layer
            self._add_feature_to_output(feature)
            
            # Show success message
            self._show_success_message()
            
            # Reset for next operation
            self._reset_operation()
            
        except Exception as e:
            self._handle_error(
                self.tr("Processing Error", "Erro de Processamento"),
                str(e)
            )
    
    def _create_output_feature(self, geometry):
        """
        Create output feature with standard attributes.
        
        CUSTOMIZE: Add your tool-specific attributes.
        
        Args:
            geometry (QgsGeometry): Feature geometry
            
        Returns:
            QgsFeature: Created feature
        """
        feature = QgsFeature()
        feature.setGeometry(geometry)
        
        # Standard attributes
        attributes = [
            str(uuid.uuid4()),  # id
            datetime.now(),     # created
            self.TOOL_NAME      # tool
        ]
        
        # CUSTOMIZE: Add tool-specific attributes
        # Example: Add area for polygons
        if self.GEOMETRY_TYPE == "Polygon":
            area = geometry.area()
            attributes.append(area)
        
        # Example: Add length for lines
        if self.GEOMETRY_TYPE == "LineString":
            length = geometry.length()
            attributes.append(length)
        
        feature.setAttributes(attributes)
        return feature
    
    def _add_feature_to_output(self, feature):
        """
        Add feature to output layer, creating layer if necessary.
        
        Args:
            feature (QgsFeature): Feature to add
        """
        # Get or create output layer
        layer = self._get_or_create_output_layer()
        
        # Add feature
        provider = layer.dataProvider()
        provider.addFeature(feature)
        layer.updateExtents()
        
        # Refresh canvas
        self.canvas.refresh()
    
    def _get_or_create_output_layer(self):
        """
        Get existing output layer or create new one.
        
        Returns:
            QgsVectorLayer: Output layer
        """
        # Look for existing layer
        layers = self.project.mapLayersByName(self.OUTPUT_LAYER_NAME)
        if layers:
            return layers[0]
        
        # Create new layer
        return self._create_output_layer()
    
    def _create_output_layer(self):
        """
        Create standardized output layer.
        
        CUSTOMIZE: Modify fields and styling as needed.
        
        Returns:
            QgsVectorLayer: Created layer
        """
        # Get project CRS
        crs = self.project.crs().authid()
        
        # Create layer
        layer = QgsVectorLayer(
            f"{self.GEOMETRY_TYPE}?crs={crs}",
            self.OUTPUT_LAYER_NAME,
            "memory"
        )
        
        # Add fields
        provider = layer.dataProvider()
        fields = [
            QgsField("id", QVariant.String),
            QgsField("created", QVariant.DateTime),
            QgsField("tool", QVariant.String)
        ]
        
        # CUSTOMIZE: Add tool-specific fields
        if self.GEOMETRY_TYPE == "Polygon":
            fields.append(QgsField("area", QVariant.Double))
        
        if self.GEOMETRY_TYPE == "LineString":
            fields.append(QgsField("length", QVariant.Double))
        
        provider.addAttributes(fields)
        layer.updateFields()
        
        # Apply styling
        self._apply_layer_style(layer)
        
        # Add to project
        self.project.addMapLayer(layer)
        
        return layer
    
    def _apply_layer_style(self, layer):
        """
        Apply default styling to output layer.
        
        CUSTOMIZE: Modify styling as needed.
        
        Args:
            layer (QgsVectorLayer): Layer to style
        """
        # Default colors by geometry type
        colors = {
            "Point": QColor(255, 0, 0),      # Red
            "LineString": QColor(0, 0, 255), # Blue
            "Polygon": QColor(0, 255, 0, 100) # Semi-transparent green
        }
        
        color = colors.get(self.GEOMETRY_TYPE, QColor(128, 128, 128))
        
        # Create symbol
        symbol = QgsSymbol.defaultSymbol(layer.geometryType())
        symbol.setColor(color)
        
        # Apply renderer
        renderer = QgsSingleSymbolRenderer(symbol)
        layer.setRenderer(renderer)
        
        # Refresh
        layer.triggerRepaint()
    
    def _finish_operation(self):
        """
        Finish current operation and process collected data.
        """
        if self.processing_data:
            self._process_data()
        else:
            self._show_info_message(
                self.tr("No data to process", "Nenhum dado para processar")
            )
    
    def _cancel_operation(self):
        """
        Cancel current operation without processing.
        """
        self._reset_operation()
        self._show_info_message(
            self.tr("Operation cancelled", "Operação cancelada")
        )
    
    def _reset_operation(self):
        """
        Reset tool state for new operation.
        """
        # Clear data
        self.processing_data.clear()
        
        # Clear visual elements
        self._clear_temp_visuals()
    
    def _clear_temp_visuals(self):
        """
        Clear temporary visual elements.
        """
        # Clear markers
        for marker in self.markers:
            self.canvas.scene().removeItem(marker)
        self.markers.clear()
        
        # Clear rubber band
        if self.rubber_band:
            self.rubber_band.reset()
    
    def _cleanup_visual_elements(self):
        """
        Clean up all visual elements.
        """
        self._clear_temp_visuals()
        
        # Remove rubber band
        if self.rubber_band:
            self.canvas.scene().removeItem(self.rubber_band)
            self.rubber_band = None
    
    def _restore_map_tool(self):
        """
        Restore previous map tool.
        """
        if self.map_tool:
            self.canvas.unsetMapTool(self.map_tool)
            self.map_tool = None
        
        if self.previous_tool:
            self.canvas.setMapTool(self.previous_tool)
            self.previous_tool = None
    
    def _set_cursor(self):
        """
        Set tool-specific cursor.
        
        CUSTOMIZE: Set appropriate cursor for your tool.
        """
        # Example: Crosshair cursor
        self.canvas.setCursor(QCursor(Qt.CrossCursor))
    
    def _reset_cursor(self):
        """
        Reset cursor to default.
        """
        self.canvas.setCursor(QCursor(Qt.ArrowCursor))
    
    def _show_instructions(self):
        """
        Show usage instructions to user.
        
        CUSTOMIZE: Update with your tool's specific instructions.
        """
        message = self.tr(
            "Left-click to add points, right-click to finish",
            "Clique esquerdo para adicionar pontos, clique direito para finalizar"
        )
        
        self.iface.messageBar().pushMessage(
            self.TOOL_NAME,
            message,
            level=Qgis.Info,
            duration=5
        )
    
    def _show_success_message(self):
        """
        Show success message to user.
        """
        message = self.tr(
            "Operation completed successfully",
            "Operação concluída com sucesso"
        )
        
        self.iface.messageBar().pushMessage(
            self.TOOL_NAME,
            message,
            level=Qgis.Success,
            duration=3
        )
    
    def _show_info_message(self, message):
        """
        Show info message to user.
        
        Args:
            message (str): Message to display
        """
        self.iface.messageBar().pushMessage(
            self.TOOL_NAME,
            message,
            level=Qgis.Info,
            duration=3
        )
    
    def _handle_error(self, title, message):
        """
        Handle errors consistently.
        
        Args:
            title (str): Error title
            message (str): Error message
        """
        # Log error
        error_msg = f"{title}: {message}"
        QgsMessageLog.logMessage(
            error_msg,
            "ISTools",
            level=Qgis.Critical
        )
        
        # Show message bar
        self.iface.messageBar().pushMessage(
            title,
            message,
            level=Qgis.Critical,
            duration=10
        )
        
        # Show dialog for critical errors
        QMessageBox.critical(
            self.iface.mainWindow(),
            title,
            message
        )
    
    def _validate_input(self, data):
        """
        Validate input data.
        
        CUSTOMIZE: Add your tool-specific validation logic.
        
        Args:
            data: Data to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        # Example validations
        if not data:
            self._handle_error(
                self.tr("Invalid Input", "Entrada Inválida"),
                self.tr("No data provided", "Nenhum dado fornecido")
            )
            return False
        
        # Add more specific validations as needed
        return True
    
    def get_tool_info(self):
        """
        Get tool information for registration.
        
        Returns:
            dict: Tool information
        """
        return {
            'name': self.TOOL_NAME,
            'icon': self.ICON_PATH,
            'callback': self.activate,
            'description': self.tr(
                "Template tool for ISTools plugin",
                "Ferramenta modelo para plugin ISTools"
            )
        }


# INTEGRATION EXAMPLE:
# To integrate this tool into the main plugin, add the following to istools.py:
#
# 1. Import the tool:
#    from .tool_template import ToolTemplate
#
# 2. In ISTools.__init__():
#    self.tool_template = None
#
# 3. In ISTools.initGui():
#    self.add_action(
#        icon_path=':/plugins/istools/icons/tool_template.png',
#        text=self.tr('Tool Template', 'Modelo de Ferramenta'),
#        callback=self.run_tool_template,
#        parent=self.iface.mainWindow(),
#        add_to_menu=True,
#        add_to_toolbar=True
#    )
#
# 4. Add callback method:
#    def run_tool_template(self):
#        """Run Tool Template"""
#        if not self.tool_template:
#            self.tool_template = ToolTemplate(self.iface)
#        self.tool_template.activate()