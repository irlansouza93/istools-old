# -*- coding: utf-8 -*-
"""
Extend Lines Tool for QGIS Plugin

This module provides functionality to extend line features to connect
with nearby lines, eliminating loose ends in line networks.

Author: Plugin Author
Date: 2024
"""

from qgis.PyQt.QtCore import QCoreApplication
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
    MAX_EXTENSION_DISTANCE = 100.0  # Maximum distance to search for lines
    CONNECT_TOLERANCE = 1e-6  # Tolerance for considering points connected
    INDEX_BUFFER = 0.001  # Buffer for spatial index searches
    
    def __init__(self, iface):
        """Initialize the ExtendLines tool.
        
        Args:
            iface: QGIS interface object
        """
        self.iface = iface

    def tr(self, message):
        """Get the translation for a string using Qt translation API.
        
        Args:
            message: String to be translated
            
        Returns:
            str: Translated string
        """
        return QCoreApplication.translate('ExtendLines', message)

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
            self.tr("Processing Complete"),
            self.tr("Loose ends connected without creating duplicate vertices. Save the layer to confirm.")
        )
    
    def _validate_input(self):
        """Validate the active layer and feature selection.
        
        Returns:
            bool: True if input is valid, False otherwise
        """
        layer = self.iface.activeLayer()
        
        if not layer or layer.geometryType() != QgsWkbTypes.LineGeometry:
            self.iface.messageBar().pushWarning(
                self.tr("Error"), 
                self.tr("Please select an active line layer.")
            )
            return False
            
        if layer.selectedFeatureCount() == 0:
            self.iface.messageBar().pushWarning(
                self.tr("Error"), 
                self.tr("Please select at least one line feature.")
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
        geometry = feature.geometry()
        vertices = [QgsPointXY(v) for v in geometry.vertices()]
        
        if len(vertices) < 2:
            return  # Skip invalid geometries
        
        # Track if geometry was modified
        geometry_modified = False
        
        # Process both endpoints (first and last vertex)
        for endpoint_index in (0, -1):
            endpoint = vertices[endpoint_index]
            
            # Skip if endpoint is already connected to another line
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
            
            # Update the vertex to the intersection point
            new_vertices = vertices.copy()
            new_vertices[endpoint_index] = intersection_point
            
            # Update the feature geometry
            new_geometry = QgsGeometry.fromPolylineXY(new_vertices)
            feature.setGeometry(new_geometry)
            geometry_modified = True
            
            # Add intersection point as vertex to target feature if needed
            self._add_vertex_to_feature(target_feature, intersection_point, layer)
            
            # Update vertices list for potential second endpoint processing
            vertices = new_vertices
        
        # Update the feature in the layer if it was modified
        if geometry_modified:
            layer.updateFeature(feature)
    
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
        
        # Create a long extension line to find all possible intersections
        max_extended_point = QgsPointXY(
            endpoint.x() + unit_x * self.MAX_EXTENSION_DISTANCE,
            endpoint.y() + unit_y * self.MAX_EXTENSION_DISTANCE
        )
        
        # Create extension line geometry
        extension_line = QgsGeometry.fromPolylineXY([endpoint, max_extended_point])
        
        # Find candidate features using spatial index
        search_rect = extension_line.boundingBox().buffered(self.INDEX_BUFFER)
        candidate_ids = spatial_index.intersects(search_rect)
        
        # Find the closest intersection point
        nearest_feature = None
        nearest_point = None
        min_distance = float('inf')
        
        for candidate_id in candidate_ids:
            if candidate_id == feature.id():
                continue
                
            candidate_feature = layer.getFeature(candidate_id)
            candidate_geometry = candidate_feature.geometry()
            
            # Calculate intersection between extension line and candidate feature
            intersection = extension_line.intersection(candidate_geometry)
            
            if intersection.isEmpty():
                continue
                
            # Process all intersection points to find the closest one
            intersection_points = []
            if intersection.wkbType() == QgsWkbTypes.Point:
                intersection_points = [intersection.asPoint()]
            elif intersection.wkbType() == QgsWkbTypes.MultiPoint:
                intersection_points = [pt.asPoint() for pt in intersection.asGeometryCollection()]
            else:
                # For line intersections, get vertices
                intersection_points = [QgsPointXY(vertex) for vertex in intersection.vertices()]
            
            for intersection_point in intersection_points:
                # Calculate distance from endpoint to intersection
                distance = endpoint.distance(intersection_point)
                
                # Skip if intersection is too close (already connected) or at the same point
                if distance <= self.CONNECT_TOLERANCE:
                    continue
                
                # Check if this intersection is closer than previous ones
                if distance < min_distance:
                    min_distance = distance
                    nearest_point = intersection_point
                    nearest_feature = candidate_feature
        
        return nearest_feature, nearest_point

    def _add_vertex_to_feature(self, feature, point, layer):
        """Add a vertex to a feature at the specified point if it lies on the line.
        
        Args:
            feature: QgsFeature to modify
            point: QgsPointXY where to add the vertex
            layer: QgsVectorLayer containing the feature
        """
        geometry = feature.geometry()
        
        # Check if point is already a vertex (within tolerance)
        for vertex in geometry.vertices():
            vertex_point = QgsPointXY(vertex)
            if vertex_point.distance(point) < self.CONNECT_TOLERANCE:
                return  # Point already exists as vertex
        
        # Find the closest segment and add vertex there
        closest_distance = float('inf')
        closest_segment_index = -1
        
        vertices = [QgsPointXY(v) for v in geometry.vertices()]
        
        for i in range(len(vertices) - 1):
            segment_start = vertices[i]
            segment_end = vertices[i + 1]
            
            # Create line segment
            segment = QgsGeometry.fromPolylineXY([segment_start, segment_end])
            
            # Calculate distance from point to segment
            distance = segment.distance(QgsGeometry.fromPointXY(point))
            
            if distance < closest_distance and distance < self.CONNECT_TOLERANCE:
                closest_distance = distance
                closest_segment_index = i
        
        # Add vertex to the closest segment if found
        if closest_segment_index >= 0:
            new_vertices = vertices.copy()
            # Insert the new vertex after the segment start
            new_vertices.insert(closest_segment_index + 1, point)
            
            # Update feature geometry
            new_geometry = QgsGeometry.fromPolylineXY(new_vertices)
            feature.setGeometry(new_geometry)
            layer.updateFeature(feature)

    def unload(self):
        """Clean up resources when the tool is unloaded.
        
        This method is called when the plugin is being unloaded.
        Currently no cleanup is required for this tool.
        """
        pass