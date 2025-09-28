# ISTools Development Guide - Building New Tools

This document provides detailed instructions for creating new tools compatible with the ISTools plugin, ensuring code consistency, proper integration, and complete functionality.

## File Structure

### Project Organization
```
istools/
├── __init__.py                    # Plugin factory
├── istools.py                     # Main plugin class
├── istools_dialog.py             # Main interface
├── qgis_interface.py             # QGIS interface
├── [your_tool].py                # Your new tool
├── translations/
│   ├── translate.py              # Translation system
│   └── dictionary.py             # Translation dictionary
├── i18n/                         # Translation files (.qm)
├── tests/                        # Unit tests
└── resources/                    # Resources (icons, etc.)
```

## Code Template for New Tool

### Standard Header
```python
# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ISTools - [Tool Name]
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
```

### Standard Imports
```python
import os
import uuid
from qgis.PyQt.QtCore import QVariant, QCoreApplication
from qgis.PyQt.QtGui import QColor, QIcon
from qgis.PyQt.QtWidgets import QMessageBox, QAction
from qgis.core import (
    QgsProject, QgsVectorLayer, QgsFeature, QgsGeometry,
    QgsField, QgsMessageLog, Qgis, QgsApplication,
    QgsWkbTypes, QgsPointXY, QgsSymbol, QgsSingleSymbolRenderer,
    QgsCoordinateReferenceSystem, QgsCoordinateTransform
)
from qgis.gui import QgsMapToolEmitPoint, QgsVertexMarker
from .translations.translate import translate
import processing
```

### Main Class Structure
```python
class MyNewTool:
    """
    Detailed tool description.
    
    This class provides functionality for [describe what the tool does].
    Explain the purpose, use cases, and expected behavior.
    """
    
    # Class constants
    OUTPUT_LAYER_NAME = "MY_OUTPUT_LAYER"
    TOOL_NAME = "My New Tool"
    
    def __init__(self, iface):
        """
        Initialize the tool.
        
        Args:
            iface: QGIS interface (QgisInterface)
        """
        self.iface = iface
        self.canvas = iface.mapCanvas()
        self.project = QgsProject.instance()
        
        # Tool state
        self.is_active = False
        self.current_layer = None
        
        # Map tools
        self.map_tool = None
        
    def tr(self, *string):
        """
        Bilingual translation system.
        
        Args:
            *string: (english, portuguese) or single string
            
        Returns:
            str: Translated string according to QGIS locale
        """
        return translate(string, QgsApplication.locale()[:2])
    
    def activate(self):
        """
        Activate the tool and configure canvas.
        """
        try:
            self.is_active = True
            self._setup_map_tool()
            self._show_instructions()
            
        except Exception as e:
            self._handle_error(
                self.tr("Error activating tool", "Erro ao ativar ferramenta"),
                str(e)
            )
    
    def deactivate(self):
        """
        Deactivate the tool and clean up resources.
        """
        try:
            self.is_active = False
            self._cleanup_map_tool()
            
        except Exception as e:
            self._handle_error(
                self.tr("Error deactivating tool", "Erro ao desativar ferramenta"),
                str(e)
            )
    
    def _setup_map_tool(self):
        """
        Configure map tool for interaction.
        """
        # Implement tool-specific configuration
        pass
    
    def _cleanup_map_tool(self):
        """
        Clean up map tool resources.
        """
        if self.map_tool:
            self.canvas.unsetMapTool(self.map_tool)
            self.map_tool = None
    
    def _show_instructions(self):
        """
        Display instructions to the user.
        """
        message = self.tr(
            "Click on the map to use the tool",
            "Clique no mapa para usar a ferramenta"
        )
        self.iface.messageBar().pushMessage(
            self.TOOL_NAME,
            message,
            level=Qgis.Info,
            duration=5
        )
    
    def _handle_error(self, title, message):
        """
        Handle errors consistently.
        
        Args:
            title (str): Error title
            message (str): Error message
        """
        QgsMessageLog.logMessage(
            f"{title}: {message}",
            "ISTools",
            level=Qgis.Critical
        )
        
        QMessageBox.critical(
            self.iface.mainWindow(),
            title,
            message
        )
    
    def _create_output_layer(self, geometry_type, fields=None):
        """
        Create standardized output layer.
        
        Args:
            geometry_type (str): Geometry type (Point, LineString, Polygon)
            fields (list): List of additional fields
            
        Returns:
            QgsVectorLayer: Created layer
        """
        # Get project CRS
        crs = self.project.crs().authid()
        
        # Create layer
        layer = QgsVectorLayer(
            f"{geometry_type}?crs={crs}",
            self.OUTPUT_LAYER_NAME,
            "memory"
        )
        
        # Add default fields
        provider = layer.dataProvider()
        default_fields = [
            QgsField("id", QVariant.String),
            QgsField("created", QVariant.DateTime),
            QgsField("tool", QVariant.String)
        ]
        
        if fields:
            default_fields.extend(fields)
        
        provider.addAttributes(default_fields)
        layer.updateFields()
        
        # Apply default style
        self._apply_default_style(layer, geometry_type)
        
        return layer
    
    def _apply_default_style(self, layer, geometry_type):
        """
        Apply default style to layer.
        
        Args:
            layer (QgsVectorLayer): Layer to style
            geometry_type (str): Geometry type
        """
        # Default colors by type
        colors = {
            "Point": QColor(255, 0, 0),      # Red
            "LineString": QColor(0, 0, 255), # Blue
            "Polygon": QColor(0, 255, 0)     # Green
        }
        
        color = colors.get(geometry_type, QColor(128, 128, 128))
        
        symbol = QgsSymbol.defaultSymbol(layer.geometryType())
        symbol.setColor(color)
        
        renderer = QgsSingleSymbolRenderer(symbol)
        layer.setRenderer(renderer)
```

## Integration Patterns

### 1. Integration with Main Plugin

To integrate your tool into the main plugin, edit the `istools.py` file:

```python
# At the beginning of the file, add the import
from .my_new_tool import MyNewTool

# In the ISTools class, in the __init__ method:
def __init__(self, iface):
    # ... existing code ...
    self.my_new_tool = None

# In the initGui() method:
def initGui(self):
    # ... existing code ...
    
    # Add action for your tool
    self.add_action(
        icon_path=':/plugins/istools/icons/my_tool.png',
        text=self.tr('My New Tool', 'Minha Nova Ferramenta'),
        callback=self.run_my_new_tool,
        parent=self.iface.mainWindow(),
        add_to_menu=True,
        add_to_toolbar=True
    )

# Add callback method:
def run_my_new_tool(self):
    """Run My New Tool"""
    if not self.my_new_tool:
        self.my_new_tool = MyNewTool(self.iface)
    
    self.my_new_tool.activate()
```

### 2. Translation System

#### Basic Usage
```python
# Simple translation (english, portuguese)
message = self.tr("Hello World", "Olá Mundo")

# Single string (will be displayed as is)
message = self.tr("OK")

# Complex messages
error_msg = self.tr(
    "Failed to create layer: {error}",
    "Falha ao criar camada: {error}"
).format(error=str(e))
```

#### Adding Translations for Other Languages

Edit the `translations/dictionary.py` file:

```python
dic = {
    "Hello World": {
        "es": "Hola Mundo",
        "fr": "Bonjour le Monde",
        "de": "Hallo Welt"
    },
    "My New Tool": {
        "es": "Mi Nueva Herramienta",
        "fr": "Mon Nouvel Outil",
        "de": "Mein Neues Werkzeug"
    }
}
```

### 3. Error Handling

```python
def _safe_operation(self):
    """
    Example of operation with robust error handling.
    """
    try:
        # Your operation here
        result = self._do_something_risky()
        
        # Success log
        QgsMessageLog.logMessage(
            self.tr("Operation completed successfully", "Operação concluída com sucesso"),
            "ISTools",
            level=Qgis.Success
        )
        
        return result
        
    except Exception as e:
        # Detailed error log
        error_details = f"Error in {self.__class__.__name__}: {str(e)}"
        QgsMessageLog.logMessage(error_details, "ISTools", level=Qgis.Critical)
        
        # User-friendly message
        self._handle_error(
            self.tr("Operation Failed", "Operação Falhou"),
            self.tr(
                "An error occurred while processing. Check the log for details.",
                "Ocorreu um erro durante o processamento. Verifique o log para detalhes."
            )
        )
        
        return None
```

### 4. Data Validation

```python
def _validate_input(self, layer):
    """
    Validate input data.
    
    Args:
        layer (QgsVectorLayer): Layer to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not layer:
        self._handle_error(
            self.tr("Invalid Input", "Entrada Inválida"),
            self.tr("No layer selected", "Nenhuma camada selecionada")
        )
        return False
    
    if not layer.isValid():
        self._handle_error(
            self.tr("Invalid Layer", "Camada Inválida"),
            self.tr("Selected layer is not valid", "Camada selecionada não é válida")
        )
        return False
    
    if layer.featureCount() == 0:
        self._handle_error(
            self.tr("Empty Layer", "Camada Vazia"),
            self.tr("Selected layer has no features", "Camada selecionada não possui feições")
        )
        return False
    
    return True
```

## Unit Tests

### Test Structure

Create a file `tests/test_my_new_tool.py`:

```python
# -*- coding: utf-8 -*-

import unittest
from unittest.mock import Mock, patch
import sys
import os

# Add plugin directory to path
plugin_dir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, plugin_dir)

try:
    from qgis.core import QgsApplication
    from my_new_tool import MyNewTool
    QGIS_AVAILABLE = True
except ImportError:
    QGIS_AVAILABLE = False


class TestMyNewTool(unittest.TestCase):
    """Tests for My New Tool"""
    
    def setUp(self):
        """Initial test setup"""
        if QGIS_AVAILABLE:
            self.iface_mock = Mock()
            self.tool = MyNewTool(self.iface_mock)
    
    @unittest.skipUnless(QGIS_AVAILABLE, "QGIS not available")
    def test_initialization(self):
        """Test tool initialization"""
        self.assertIsNotNone(self.tool)
        self.assertEqual(self.tool.TOOL_NAME, "My New Tool")
        self.assertFalse(self.tool.is_active)
    
    @unittest.skipUnless(QGIS_AVAILABLE, "QGIS not available")
    def test_activate_deactivate(self):
        """Test activation and deactivation"""
        self.tool.activate()
        self.assertTrue(self.tool.is_active)
        
        self.tool.deactivate()
        self.assertFalse(self.tool.is_active)
    
    def test_translation_system(self):
        """Test translation system"""
        if QGIS_AVAILABLE:
            # Test with QGIS available
            result = self.tool.tr("Hello", "Olá")
            self.assertIn(result, ["Hello", "Olá"])
        else:
            # Test without QGIS (mock)
            self.assertTrue(True)  # Placeholder


if __name__ == '__main__':
    unittest.main()
```

## Best Practices

### 1. Naming Conventions
- **Classes**: PascalCase (`MyNewTool`)
- **Methods**: snake_case (`my_method`)
- **Constants**: UPPER_CASE (`OUTPUT_LAYER_NAME`)
- **Variables**: snake_case (`my_variable`)

### 2. Documentation
- Use English docstrings for public methods
- Comment complex code in English
- Keep comments up to date

### 3. Performance
- Use `QgsProject.instance()` once in initialization
- Clean up resources properly in `deactivate()`
- Avoid expensive operations on main thread

### 4. Compatibility
- Test with different QGIS versions (3.16+)
- Use stable QGIS APIs
- Handle exceptions properly

### 5. User Interface
- Provide visual feedback to user
- Use QGIS message bar
- Implement cancellation for long operations

## Complete Example: Measurement Tool

```python
# -*- coding: utf-8 -*-
"""
Complete example of a measurement tool following ISTools patterns.
"""

import math
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QColor
from qgis.core import (
    QgsDistanceArea, QgsUnitTypes, QgsPointXY,
    QgsGeometry, QgsWkbTypes, Qgis
)
from qgis.gui import QgsMapToolEmitPoint, QgsVertexMarker, QgsRubberBand
from .translations.translate import translate


class MeasurementTool:
    """
    Distance and area measurement tool.
    
    Allows user to measure distances by clicking points on the map
    and displays the result in real time.
    """
    
    TOOL_NAME = "Measurement Tool"
    
    def __init__(self, iface):
        """Initialize measurement tool."""
        self.iface = iface
        self.canvas = iface.mapCanvas()
        
        # Tool state
        self.is_active = False
        self.points = []
        
        # Visual elements
        self.rubber_band = None
        self.markers = []
        
        # Distance calculator
        self.distance_calc = QgsDistanceArea()
        self.distance_calc.setSourceCrs(
            self.canvas.mapSettings().destinationCrs(),
            self.canvas.mapSettings().transformContext()
        )
        
        # Map tool
        self.map_tool = QgsMapToolEmitPoint(self.canvas)
        self.map_tool.canvasClicked.connect(self._handle_click)
    
    def tr(self, *string):
        """Bilingual translation system."""
        return translate(string, QgsApplication.locale()[:2])
    
    def activate(self):
        """Activate measurement tool."""
        self.is_active = True
        self.canvas.setMapTool(self.map_tool)
        self._setup_rubber_band()
        
        self.iface.messageBar().pushMessage(
            self.TOOL_NAME,
            self.tr(
                "Click to start measuring. Right-click to finish.",
                "Clique para começar a medir. Clique direito para finalizar."
            ),
            level=Qgis.Info,
            duration=5
        )
    
    def deactivate(self):
        """Deactivate tool and clean up resources."""
        self.is_active = False
        self._cleanup()
    
    def _setup_rubber_band(self):
        """Set up visual measurement line."""
        self.rubber_band = QgsRubberBand(self.canvas, QgsWkbTypes.LineGeometry)
        self.rubber_band.setColor(QColor(255, 0, 0))
        self.rubber_band.setWidth(2)
    
    def _handle_click(self, point, button):
        """
        Handle map clicks.
        
        Args:
            point (QgsPointXY): Clicked point
            button: Mouse button
        """
        if button == Qt.LeftButton:
            self._add_point(point)
        elif button == Qt.RightButton:
            self._finish_measurement()
    
    def _add_point(self, point):
        """
        Add point to measurement.
        
        Args:
            point (QgsPointXY): Point to add
        """
        self.points.append(point)
        
        # Add visual marker
        marker = QgsVertexMarker(self.canvas)
        marker.setCenter(point)
        marker.setColor(QColor(255, 0, 0))
        marker.setIconSize(10)
        self.markers.append(marker)
        
        # Update line
        self.rubber_band.addPoint(point)
        
        # Calculate and display distance
        if len(self.points) > 1:
            self._update_measurement()
    
    def _update_measurement(self):
        """Update and display current measurement."""
        if len(self.points) < 2:
            return
        
        # Calculate total distance
        total_distance = 0
        for i in range(1, len(self.points)):
            distance = self.distance_calc.measureLine(
                self.points[i-1], 
                self.points[i]
            )
            total_distance += distance
        
        # Convert to appropriate unit
        unit = self.distance_calc.lengthUnits()
        distance_text = QgsDistanceArea.formatDistance(
            total_distance, 
            2, 
            unit
        )
        
        # Display result
        message = self.tr(
            f"Distance: {distance_text}",
            f"Distância: {distance_text}"
        )
        
        self.iface.messageBar().clearWidgets()
        self.iface.messageBar().pushMessage(
            self.TOOL_NAME,
            message,
            level=Qgis.Info,
            duration=0  # Keep until next measurement
        )
    
    def _finish_measurement(self):
        """Finish current measurement."""
        if len(self.points) > 1:
            self._update_measurement()
        
        # Clear for new measurement
        self.points.clear()
        self.rubber_band.reset()
        
        # Keep markers for a few seconds
        self.iface.messageBar().pushMessage(
            self.TOOL_NAME,
            self.tr(
                "Measurement finished. Click to start new measurement.",
                "Medição finalizada. Clique para iniciar nova medição."
            ),
            level=Qgis.Success,
            duration=3
        )
    
    def _cleanup(self):
        """Clean up all visual resources."""
        if self.rubber_band:
            self.canvas.scene().removeItem(self.rubber_band)
            self.rubber_band = None
        
        for marker in self.markers:
            self.canvas.scene().removeItem(marker)
        self.markers.clear()
        
        self.points.clear()
        self.canvas.unsetMapTool(self.map_tool)
```

## Conclusion

This guide provides a solid foundation for developing tools compatible with ISTools. Follow the established patterns, use the translation system properly, and maintain consistency with the existing project.

For questions or suggestions, consult the code of existing tools as reference or contact the development team.

---

**ISTools - Professional vectorization toolkit for QGIS**  
*Developed by Irlan Souza, 3° Sgt Brazilian Army*