# -*- coding: utf-8 -*-
"""
Extend Lines Tool for QGIS Plugin

This module provides functionality to extend line features to connect
with nearby lines, eliminating loose ends in line networks.

Author: Plugin Author
Date: 2024
"""

from qgis.core import (
    QgsPointXY,
    QgsGeometry,
    QgsFeatureRequest,
    QgsWkbTypes,
    QgsSpatialIndex
)
import math


class ExtendLines:
    """Tool for extending line features to connect with nearby lines.
    
    This class provides functionality to automatically extend line endpoints
    to connect with nearby line features, helping to create connected
    line networks without manual editing.
    """
    
    # Configuration constants
    EXTENSION_DISTANCE = 0.005
    CONNECT_TOLERANCE = 1e-9
    INDEX_BUFFER = 0.0001
    
    def __init__(self, iface):
        """Initialize the ExtendLines tool.
        
        Args:
            iface: QGIS interface object
        """
        self.iface = iface

    def run(self):
        """Execute the line extension process.
        
        This method processes selected line features and extends their endpoints
        to connect with nearby lines within the extension distance.
        """
        # Validate input layer and selection
        if not self._validate_input():
            return
        
        layer = self.iface.activeLayer()
        
        # Ensure layer is editable
        if not layer.isEditable():
            layer.startEditing()
        
        # Create spatial index for efficient intersection queries
        spatial_index = QgsSpatialIndex(layer.getFeatures())
        
        # Process each selected feature
        self._process_selected_features(layer, spatial_index)
        
        # Show completion message
        self.iface.messageBar().pushInfo(
            "Processing Complete",
            "Loose ends connected without creating duplicate vertices. Save the layer to confirm."
        )
    
    def _validate_input(self):
        """Validate the active layer and feature selection.
        
        Returns:
            bool: True if input is valid, False otherwise
        """
        layer = self.iface.activeLayer()
        
        if not layer or layer.geometryType() != QgsWkbTypes.LineGeometry:
            self.iface.messageBar().pushWarning(
                "Error", 
                "Please select an active line layer."
            )
            return False
            
        if layer.selectedFeatureCount() == 0:
            self.iface.messageBar().pushWarning(
                "Error", 
                "Please select at least one line feature."
            )
            return False
            
        return True
    
    def _process_selected_features(self, layer, spatial_index):
        """Process all selected features for line extension.
        
        Args:
            layer: QgsVectorLayer containing the line features
            spatial_index: QgsSpatialIndex for efficient spatial queries
        """
        for feature in layer.selectedFeatures():
            self._extend_feature_endpoints(feature, layer, spatial_index)

    def _extend_feature_endpoints(self, feature, layer, spatial_index):
        """Extend the endpoints of a line feature to connect with nearby lines.
        
        Args:
            feature: QgsFeature to process
            layer: QgsVectorLayer containing the features
            spatial_index: QgsSpatialIndex for spatial queries
        """
        vertices = [QgsPointXY(v) for v in feature.geometry().vertices()]
        
        # Process both endpoints (first and last vertex)
        for endpoint_index in (0, -1):
            endpoint = vertices[endpoint_index]
            
            # Skip if endpoint is already connected
            if self._is_point_connected(endpoint, feature.id(), layer):
                continue
            
            # Get the neighboring vertex to determine extension direction
            neighbor_index = 1 if endpoint_index == 0 else len(vertices) - 2
            neighbor_point = vertices[neighbor_index]
            
            # Find nearest intersection point
            target_feature, intersection_point = self._find_nearest_intersection(
                feature, endpoint, neighbor_point, layer, spatial_index
            )
            
            if not target_feature or not intersection_point:
                continue
            
            # Update the feature geometry
            new_vertices = vertices.copy()
            new_vertices[endpoint_index] = intersection_point
            feature.setGeometry(QgsGeometry.fromPolylineXY(new_vertices))
            layer.updateFeature(feature)
            
            # Add intersection point to target feature if needed
            self._add_vertex_to_feature(target_feature, intersection_point, layer)
    
    def _is_point_connected(self, point, feature_id, layer):
        """Check if a point is already connected to other features.
        
        Args:
            point: QgsPointXY to check
            feature_id: ID of the feature to exclude from check
            layer: QgsVectorLayer to search in
            
        Returns:
            bool: True if point is connected, False otherwise
        """
        buffer_geometry = QgsGeometry.fromPointXY(point).buffer(
            self.CONNECT_TOLERANCE, 1
        )
        request = QgsFeatureRequest().setFilterRect(buffer_geometry.boundingBox())
        
        for feature in layer.getFeatures(request):
            if feature.id() == feature_id:
                continue
            if feature.geometry().distance(QgsGeometry.fromPointXY(point)) <= self.CONNECT_TOLERANCE:
                return True
        return False
    
    def _find_nearest_intersection(self, feature, endpoint, neighbor_point, layer, spatial_index):
        """Find the nearest intersection point for line extension.
        
        Args:
            feature: QgsFeature being extended
            endpoint: QgsPointXY of the line endpoint
            neighbor_point: QgsPointXY of the neighboring vertex
            layer: QgsVectorLayer containing features
            spatial_index: QgsSpatialIndex for spatial queries
            
        Returns:
            tuple: (target_feature, intersection_point) or (None, None)
        """
        # Calculate extension direction
        dx = endpoint.x() - neighbor_point.x()
        dy = endpoint.y() - neighbor_point.y()
        segment_length = math.hypot(dx, dy)
        
        if segment_length == 0:
            return None, None
            
        # Unit vector for extension direction
        unit_x, unit_y = dx / segment_length, dy / segment_length
        
        # Create extended point
        extended_point = QgsPointXY(
            endpoint.x() + unit_x * self.EXTENSION_DISTANCE,
            endpoint.y() + unit_y * self.EXTENSION_DISTANCE
        )
        
        # Create extension line geometry
        extension_line = QgsGeometry.fromPolylineXY([endpoint, extended_point])
        
        # Find candidate features using spatial index
        search_rect = extension_line.boundingBox().buffered(self.INDEX_BUFFER)
        candidate_ids = spatial_index.intersects(search_rect)
        
        # Find nearest intersection
        nearest_feature = None
        nearest_point = None
        min_distance = self.EXTENSION_DISTANCE
        
        for candidate_id in candidate_ids:
            if candidate_id == feature.id():
                continue
                
            candidate_feature = layer.getFeature(candidate_id)
            intersection = extension_line.intersection(candidate_feature.geometry())
            
            if intersection.isEmpty():
                continue
                
            # Check all intersection points
            for vertex in intersection.vertices():
                intersection_point = QgsPointXY(vertex)
                distance = endpoint.distance(intersection_point)
                
                if self.CONNECT_TOLERANCE < distance < min_distance:
                    min_distance = distance
                    nearest_point = intersection_point
                    nearest_feature = candidate_feature
        
        return nearest_feature, nearest_point

    def _add_vertex_to_feature(self, target_feature, intersection_point, layer):
        """Add a vertex to the target feature at the intersection point.
        
        Args:
            target_feature: QgsFeature to modify
            intersection_point: QgsPointXY where to add the vertex
            layer: QgsVectorLayer containing the feature
        """
        target_geometry = target_feature.geometry()
        
        # Check if vertex already exists at this location
        vertex_exists = any(
            QgsPointXY(vertex).distance(intersection_point) <= self.CONNECT_TOLERANCE 
            for vertex in target_geometry.vertices()
        )
        
        if vertex_exists:
            return
        
        # Find the closest segment and insert vertex
        segment_info = target_geometry.closestSegmentWithContext(intersection_point)
        distance_to_segment = segment_info[0]
        insert_after_index = segment_info[2]
        
        # Only insert if point is close enough to the segment
        if distance_to_segment > self.CONNECT_TOLERANCE:
            return
        
        # Insert the vertex
        target_geometry.insertVertex(
            intersection_point.x(), 
            intersection_point.y(), 
            insert_after_index
        )
        target_feature.setGeometry(target_geometry)
        layer.updateFeature(target_feature)

    def unload(self):
        """Clean up resources when the tool is unloaded.
        
        This method is called when the plugin is being unloaded.
        Currently no cleanup is required for this tool.
        """
        pass