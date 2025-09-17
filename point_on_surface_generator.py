# -*- coding: utf-8 -*-
"""
Point on Surface Generator

This module provides functionality to generate representative points within polygon features.
The generated points are guaranteed to be inside the polygon boundaries.
"""

from qgis.core import (
    QgsProject,
    QgsVectorLayer,
    QgsFeature,
    QgsGeometry,
    QgsField,
    QgsWkbTypes,
)
from qgis.PyQt.QtCore import QVariant


class PointOnSurfaceGenerator:
    """Generator for creating representative points within polygon features.
    
    This class provides functionality to create point features that are guaranteed
    to be located within the boundaries of selected polygon features.
    """
    
    # Class constants
    OUTPUT_LAYER_NAME = "Central Points"
    ID_FIELD_NAME = "ID"
    
    def __init__(self, iface):
        """Initialize the Point on Surface Generator.
        
        Args:
            iface: QGIS interface object for accessing the application
        """
        self.iface = iface

    def run(self):
        """Execute the point generation process.
        
        Validates the active layer and selected features, then generates
        representative points for each selected polygon.
        """
        try:
            # Validate input layer and selection
            layer, selected_features = self._validate_input()
            
            # Create output point layer
            point_layer = self._create_output_layer(layer)
            
            # Generate points for selected features
            self._generate_points(selected_features, point_layer)
            
            # Add layer to project and show success message
            QgsProject.instance().addMapLayer(point_layer)
            self.iface.messageBar().pushSuccess(
                "Success", 
                f"Layer '{self.OUTPUT_LAYER_NAME}' created successfully."
            )
            
        except Exception as error:
            self.iface.messageBar().pushCritical(self.tr("Error"), str(error))
    
    def _validate_input(self):
        """Validate the active layer and selected features.
        
        Returns:
            tuple: (layer, selected_features) if validation passes
            
        Raises:
            Exception: If validation fails
        """
        layer = self.iface.activeLayer()
        
        if not layer:
            raise Exception("No active layer found. Please select a polygon layer.")
            
        if layer.geometryType() != QgsWkbTypes.PolygonGeometry:
            raise Exception("Active layer must be a polygon layer.")
            
        selected_features = layer.selectedFeatures()
        if not selected_features:
            raise Exception(
                "No features selected. Please select the desired polygons."
            )
            
        return layer, selected_features
    
    def _create_output_layer(self, source_layer):
        """Create the output point layer with appropriate CRS and fields.
        
        Args:
            source_layer: Source polygon layer for CRS reference
            
        Returns:
            QgsVectorLayer: Configured point layer
        """
        crs = source_layer.crs().authid()
        point_layer = QgsVectorLayer(
            f"Point?crs={crs}", 
            self.OUTPUT_LAYER_NAME, 
            "memory"
        )
        
        # Add ID field
        provider = point_layer.dataProvider()
        provider.addAttributes([QgsField(self.ID_FIELD_NAME, QVariant.Int)])
        point_layer.updateFields()
        
        return point_layer
    
    def _generate_points(self, selected_features, point_layer):
        """Generate representative points for selected polygon features.
        
        Args:
            selected_features: List of selected polygon features
            point_layer: Output point layer to add points to
        """
        provider = point_layer.dataProvider()
        
        for feature in selected_features:
            geometry = feature.geometry()
            
            if not geometry or geometry.isEmpty():
                continue
                
            # Generate point on surface (guaranteed to be inside polygon)
            point_geometry = geometry.pointOnSurface()
            
            # Create new point feature
            point_feature = QgsFeature()
            point_feature.setGeometry(point_geometry)
            point_feature.setAttributes([feature.id()])
            
            provider.addFeature(point_feature)

    def unload(self):
        """Clean up resources when the tool is unloaded.
        
        This method is called when the plugin is disabled or QGIS is closed.
        Currently no specific cleanup is required.
        """
        pass