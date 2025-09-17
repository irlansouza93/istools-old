# -*- coding: utf-8 -*-
"""
Bounded Polygon Generator Tool for QGIS Plugin

This module provides functionality to generate polygons bounded by frame layers
and delimited by line and polygon layers using QGIS processing algorithms.

Author: Plugin Author
Date: 2024
"""

from qgis.PyQt.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QListWidget, QListWidgetItem,
    QPushButton, QComboBox, QMessageBox
)
from qgis.core import (
    QgsProject, QgsVectorLayer, QgsWkbTypes, QgsProcessingContext,
    QgsProcessingFeedback
)
import processing


class BoundedPolygonGenerator:
    """Tool for generating bounded polygons from frame and delimiter layers.
    
    This class provides functionality to create polygons that are bounded by
    a frame layer and delimited by line and/or polygon layers using QGIS
    processing algorithms.
    """
    
    # Output layer configuration
    OUTPUT_LAYER_NAME = "BOUNDED_POLYGONS"
    TARGET_CRS = "EPSG:31985"  # SIRGAS 2000 / UTM zone 25S
    
    def __init__(self, iface):
        """Initialize the BoundedPolygonGenerator tool.
        
        Args:
            iface: QGIS interface object
        """
        self.iface = iface
        self.dialog = None

    def activate_tool(self):
        """Activate the bounded polygon generator tool.
        
        Creates and shows the dialog for selecting layers and generating polygons.
        """
        self.dialog = PolygonGeneratorDialog(self.iface)
        self.dialog.show()

    def unload(self):
        """Clean up resources when the tool is unloaded.
        
        Closes the dialog and clears references.
        """
        if self.dialog:
            self.dialog.close()
            self.dialog = None

class PolygonGeneratorDialog(QDialog):
    """Dialog for bounded polygon generation configuration.
    
    This dialog allows users to select frame layers and delimiter layers
    for generating bounded polygons.
    """
    
    def __init__(self, iface):
        """Initialize the polygon generator dialog.
        
        Args:
            iface: QGIS interface object
        """
        super().__init__()
        self.iface = iface
        self._setup_ui()
        self.populate_layers()
    
    def _setup_ui(self):
        """Set up the user interface components."""
        self.setWindowTitle("Bounded Polygon Generator")
        layout = QVBoxLayout()
        
        # Frame layer selection
        layout.addWidget(QLabel("Frame Layer (Polygon):"))
        self.frame_layer_combo = QComboBox()
        layout.addWidget(self.frame_layer_combo)
        
        # Line delimiter layers
        layout.addWidget(QLabel("Delimiter Layers (Line):"))
        self.line_layer_list = QListWidget()
        self.line_layer_list.setSelectionMode(QListWidget.MultiSelection)
        layout.addWidget(self.line_layer_list)
        
        # Polygon delimiter layers
        layout.addWidget(QLabel("Delimiter Layers (Polygon):"))
        self.poly_layer_list = QListWidget()
        self.poly_layer_list.setSelectionMode(QListWidget.MultiSelection)
        layout.addWidget(self.poly_layer_list)
        
        # Generate button
        self.run_button = QPushButton("Generate Polygons")
        self.run_button.clicked.connect(self.run_script)
        layout.addWidget(self.run_button)
        
        self.setLayout(layout)

    def populate_layers(self):
        """Populate the layer selection widgets with available vector layers.
        
        Organizes layers by geometry type:
        - Polygon layers: available for frame and polygon delimiters
        - Line layers: available for line delimiters
        """
        layers = QgsProject.instance().mapLayers().values()
        
        for layer in layers:
            if not isinstance(layer, QgsVectorLayer):
                continue
                
            layer_name = layer.name()
            list_item = QListWidgetItem(layer_name)
            list_item.setData(1000, layer)
            
            if layer.geometryType() == QgsWkbTypes.PolygonGeometry:
                # Add to frame layer combo and polygon delimiter list
                self.frame_layer_combo.addItem(layer_name, layer)
                self.poly_layer_list.addItem(list_item)
            elif layer.geometryType() == QgsWkbTypes.LineGeometry:
                # Add to line delimiter list
                self.line_layer_list.addItem(list_item)

    def run_script(self):
        """Execute the bounded polygon generation process.
        
        Validates input selections and runs the processing workflow
        to generate bounded polygons.
        """
        try:
            # Validate input selections
            frame_layer, line_layers, poly_layers = self._validate_selections()
            
            # Initialize processing context
            feedback = QgsProcessingFeedback()
            context = QgsProcessingContext()
            
            # Execute the processing workflow
            result_layer = self._execute_processing_workflow(
                frame_layer, line_layers, poly_layers, context, feedback
            )
            
            # Add result to project and close dialog
            result_layer.setName(BoundedPolygonGenerator.OUTPUT_LAYER_NAME)
            QgsProject.instance().addMapLayer(result_layer)
            self.close()
            
            self.iface.messageBar().pushSuccess(
                "Success", 
                f"Layer '{BoundedPolygonGenerator.OUTPUT_LAYER_NAME}' created successfully."
            )
            
        except Exception as error:
            QMessageBox.critical(self, self.tr("Error"), str(error))
    
    def _validate_selections(self):
        """Validate user layer selections.
        
        Returns:
            tuple: (frame_layer, selected_line_layers, selected_poly_layers)
            
        Raises:
            Exception: If validation fails
        """
        frame_layer = self.frame_layer_combo.currentData()
        if not frame_layer:
            raise Exception("Please select a frame layer.")
            
        selected_line_layers = [
            item.data(1000) for item in self.line_layer_list.selectedItems()
        ]
        selected_poly_layers = [
            item.data(1000) for item in self.poly_layer_list.selectedItems()
        ]
        
        if not selected_line_layers and not selected_poly_layers:
            raise Exception(
                "Please select at least one delimiter layer (line or polygon)."
            )
            
        return frame_layer, selected_line_layers, selected_poly_layers
    
    def _execute_processing_workflow(self, frame_layer, line_layers, poly_layers, context, feedback):
        """Execute the complete processing workflow.
        
        Args:
            frame_layer: QgsVectorLayer used as frame boundary
            line_layers: List of line delimiter layers
            poly_layers: List of polygon delimiter layers
            context: QgsProcessingContext for processing operations
            feedback: QgsProcessingFeedback for progress reporting
            
        Returns:
            QgsVectorLayer: The final result layer with bounded polygons
        """
        # Convert polygon delimiters to lines
        poly_line_layers = self._convert_polygons_to_lines(poly_layers, context, feedback)
        
        # Convert frame to lines
        frame_lines = self._convert_frame_to_lines(frame_layer, context, feedback)
        
        # Merge all line layers
        merged_lines = self._merge_all_lines(
            line_layers, poly_line_layers, frame_lines, context, feedback
        )
        
        # Process lines and create polygons
        polygons = self._create_polygons_from_lines(merged_lines, context, feedback)
        
        # Clip polygons by frame
        bounded_polygons = self._clip_by_frame(polygons, frame_layer, context, feedback)
        
        # Remove overlaps with polygon delimiters
        if poly_layers:
            final_polygons = self._remove_polygon_overlaps(
                bounded_polygons, poly_layers, context, feedback
            )
        else:
            final_polygons = bounded_polygons
        
        # Add attributes and reproject
        return self._finalize_result_layer(final_polygons, context, feedback)
    
    def _convert_polygons_to_lines(self, poly_layers, context, feedback):
        """Convert polygon layers to line layers.
        
        Args:
            poly_layers: List of polygon layers to convert
            context: QgsProcessingContext for processing operations
            feedback: QgsProcessingFeedback for progress reporting
            
        Returns:
            list: List of converted line layers
        """
        poly_line_layers = []
        for poly_layer in poly_layers:
            result = processing.run("native:polygonstolines", {
                'INPUT': poly_layer,
                'OUTPUT': 'memory:'
            }, context=context, feedback=feedback)
            poly_line_layers.append(result['OUTPUT'])
        return poly_line_layers
    
    def _convert_frame_to_lines(self, frame_layer, context, feedback):
        """Convert frame polygon layer to lines.
        
        Args:
            frame_layer: Frame polygon layer to convert
            context: QgsProcessingContext for processing operations
            feedback: QgsProcessingFeedback for progress reporting
            
        Returns:
            QgsVectorLayer: Converted frame lines layer
        """
        result = processing.run("native:polygonstolines", {
            'INPUT': frame_layer,
            'OUTPUT': 'memory:'
        }, context=context, feedback=feedback)
        return result['OUTPUT']
    
    def _merge_all_lines(self, line_layers, poly_line_layers, frame_lines, context, feedback):
        """Merge all line layers into a single layer.
        
        Args:
            line_layers: Original line delimiter layers
            poly_line_layers: Converted polygon delimiter layers
            frame_lines: Converted frame lines
            context: QgsProcessingContext for processing operations
            feedback: QgsProcessingFeedback for progress reporting
            
        Returns:
            QgsVectorLayer: Merged and dissolved lines layer
        """
        # Merge all line layers
        all_layers = line_layers + poly_line_layers + [frame_lines]
        merged_result = processing.run("native:mergevectorlayers", {
            'LAYERS': all_layers,
            'OUTPUT': 'memory:'
        }, context=context, feedback=feedback)
        
        # Dissolve merged lines
        dissolved_result = processing.run("native:dissolve", {
            'INPUT': merged_result['OUTPUT'],
            'OUTPUT': 'memory:'
        }, context=context, feedback=feedback)
        
        return dissolved_result['OUTPUT']
    
    def _create_polygons_from_lines(self, merged_lines, context, feedback):
        """Create polygons from merged lines.
        
        Args:
            merged_lines: Merged line layer
            context: QgsProcessingContext for processing operations
            feedback: QgsProcessingFeedback for progress reporting
            
        Returns:
            QgsVectorLayer: Polygonized layer
        """
        # Fix geometries first
        fixed_result = processing.run("native:fixgeometries", {
            'INPUT': merged_lines,
            'OUTPUT': 'memory:'
        }, context=context, feedback=feedback)
        
        # Try polygonize, fallback to linestopolygons if needed
        try:
            polygonize_result = processing.run("native:linestopolygons", {
                'INPUT': fixed_result['OUTPUT'],
                'OUTPUT': 'memory:'
            }, context=context, feedback=feedback)
        except:
            polygonize_result = processing.run("native:polygonize", {
                'INPUT': fixed_result['OUTPUT'],
                'OUTPUT': 'memory:'
            }, context=context, feedback=feedback)
        
        return polygonize_result['OUTPUT']
    
    def _clip_by_frame(self, polygons, frame_layer, context, feedback):
        """Clip polygons by frame boundary.
        
        Args:
            polygons: Polygon layer to clip
            frame_layer: Frame layer for clipping
            context: QgsProcessingContext for processing operations
            feedback: QgsProcessingFeedback for progress reporting
            
        Returns:
            QgsVectorLayer: Clipped polygons
        """
        intersection_result = processing.run("native:intersection", {
            'INPUT': polygons,
            'OVERLAY': frame_layer,
            'OUTPUT': 'memory:'
        }, context=context, feedback=feedback)
        
        return intersection_result['OUTPUT']
    
    def _remove_polygon_overlaps(self, polygons, poly_layers, context, feedback):
        """Remove overlaps with polygon delimiter layers.
        
        Args:
            polygons: Polygon layer to process
            poly_layers: Polygon delimiter layers
            context: QgsProcessingContext for processing operations
            feedback: QgsProcessingFeedback for progress reporting
            
        Returns:
            QgsVectorLayer: Polygons with overlaps removed
        """
        # Merge all polygon delimiter layers
        merged_polys_result = processing.run("native:mergevectorlayers", {
            'LAYERS': poly_layers,
            'OUTPUT': 'memory:'
        }, context=context, feedback=feedback)
        
        # Remove overlaps using difference
        difference_result = processing.run("native:difference", {
            'INPUT': polygons,
            'OVERLAY': merged_polys_result['OUTPUT'],
            'OUTPUT': 'memory:'
        }, context=context, feedback=feedback)
        
        return difference_result['OUTPUT']
    
    def _finalize_result_layer(self, polygons, context, feedback):
        """Add attributes and reproject the final layer.
        
        Args:
            polygons: Polygon layer to finalize
            context: QgsProcessingContext for processing operations
            feedback: QgsProcessingFeedback for progress reporting
            
        Returns:
            QgsVectorLayer: Final processed layer
        """
        # Add ID field with UUID
        with_id_result = processing.run("qgis:fieldcalculator", {
            'INPUT': polygons,
            'FIELD_NAME': 'id',
            'FIELD_TYPE': 2,  # Text
            'FIELD_LENGTH': 40,
            'FIELD_PRECISION': 0,
            'NEW_FIELD': True,
            'FORMULA': "replace(replace(uuid(), '{', ''), '}', '')",
            'OUTPUT': 'memory:'
        }, context=context, feedback=feedback)
        
        # Add description field
        with_desc_result = processing.run("qgis:fieldcalculator", {
            'INPUT': with_id_result['OUTPUT'],
            'FIELD_NAME': 'descricao',
            'FIELD_TYPE': 2,  # Text
            'FIELD_LENGTH': 255,
            'FIELD_PRECISION': 0,
            'NEW_FIELD': True,
            'FORMULA': "NULL",
            'OUTPUT': 'memory:'
        }, context=context, feedback=feedback)
        
        # Reproject to target CRS
        reprojected_result = processing.run("native:reprojectlayer", {
            'INPUT': with_desc_result['OUTPUT'],
            'TARGET_CRS': BoundedPolygonGenerator.TARGET_CRS,
            'OUTPUT': 'memory:'
        }, context=context, feedback=feedback)
        
        # Add area field (calculated after reprojection)
        with_area_result = processing.run("qgis:fieldcalculator", {
            'INPUT': reprojected_result['OUTPUT'],
            'FIELD_NAME': 'area_otf',
            'FIELD_TYPE': 0,  # Numeric decimal
            'FIELD_LENGTH': 20,
            'FIELD_PRECISION': 2,
            'NEW_FIELD': True,
            'FORMULA': "$area",
            'OUTPUT': 'memory:'
        }, context=context, feedback=feedback)
        
        return with_area_result['OUTPUT']