# -*- coding: utf-8 -*-
"""
Polygon Generator Tool for QGIS

Generates polygons from lines or areas around a clicked point.
This tool creates polygons by polygonizing visible line and polygon layers
and selecting the polygon that contains the clicked point.

Author: Irlan Souza
Version: 1.2
License: GPL v2
"""

import os
import uuid
from qgis.PyQt.QtCore import QVariant
from qgis.PyQt.QtGui import QColor
from qgis.core import (
    QgsProject, QgsVectorLayer, QgsFeature, QgsGeometry,
    QgsField, QgsMessageLog, Qgis,
    QgsWkbTypes, QgsPointXY, QgsSymbol, QgsSingleSymbolRenderer,
    QgsCoordinateReferenceSystem, QgsCoordinateTransform
)
from qgis.gui import QgsMapToolEmitPoint, QgsVertexMarker
import processing


class QgisPolygonGenerator:
    CAMADA_SAIDA = "POLIGONOS_CRIADOS"

    def __init__(self, iface):
        """Initialize the Polygon Generator tool.
        
        Args:
            iface: QGIS interface instance
        """
        self.iface = iface
        self.canvas = iface.mapCanvas()
        self.tool = QgsMapToolEmitPoint(self.canvas)
        self.marker = None

    def activate_tool(self):
        """Activate the polygon generation tool.
        
        Checks for valid visible layers and sets up the map tool for capturing clicks.
        Shows appropriate messages to guide the user.
        """
        valid_layers = self._get_valid_layers()
        if not valid_layers:
            self.iface.messageBar().pushWarning('PolygonGenerator', 'Nenhuma camada visível de linha ou área encontrada no projeto.')
            return
        
        self.tool.canvasClicked.connect(self.capture_and_create)
        self.canvas.setMapTool(self.tool)
        self.iface.messageBar().pushInfo('PolygonGenerator', 'Clique no mapa para definir o centro. Clique com o botão direito para cancelar.')
    
    def _get_valid_layers(self):
        """Get list of valid visible line and polygon layers.
        
        Returns:
            list: List of valid QgsVectorLayer instances
        """
        root = QgsProject.instance().layerTreeRoot()
        valid_layers = []

        for lyr in QgsProject.instance().mapLayers().values():
            if not isinstance(lyr, QgsVectorLayer):
                continue

            # checar visibilidade pelo layer tree
            node = root.findLayer(lyr.id())
            if node is None or not node.isVisible():
                continue

            # aceitar apenas linhas e polígonos
            if QgsWkbTypes.geometryType(lyr.wkbType()) in [QgsWkbTypes.LineGeometry, QgsWkbTypes.PolygonGeometry]:
                valid_layers.append(lyr)

        return valid_layers

    def capture_and_create(self, point, button):
        """Handle map clicks for polygon creation.
        
        Args:
            point: QgsPointXY representing the clicked point
            button: Mouse button pressed (1=left, 2=right)
        """
        if button == 2:  # clique com botão direito = cancelar
            self._cleanup_marker()
            self.canvas.unsetMapTool(self.tool)
            self.iface.messageBar().pushInfo('PolygonGenerator', 'Operação cancelada.')
            return

        # Clean up existing marker
        if self.marker:
            self.marker.hide()
            self.marker = None

        # Create new marker at clicked point
        self._create_marker(point)
        self.process_polygon(point)
    
    def _create_marker(self, point):
        """Create a visual marker at the clicked point.
        
        Args:
            point: QgsPointXY where to place the marker
        """
        self.marker = QgsVertexMarker(self.canvas)
        self.marker.setCenter(point)
        self.marker.setColor(QColor(255, 0, 0))
        self.marker.setFillColor(QColor(255, 0, 0, 100))
        self.marker.setIconType(QgsVertexMarker.ICON_CIRCLE)
        self.marker.setIconSize(12)
        self.marker.setPenWidth(3)

    def process_polygon(self, point):
        """Process polygon creation from the clicked point.
        
        Creates a temporary layer with all valid geometries, runs polygonize,
        and selects the polygon containing the clicked point.
        
        Args:
            point: QgsPointXY representing the clicked point
        """
        pt = QgsPointXY(point)
        center_geometry = QgsGeometry.fromPointXY(pt)

        # Create temporary layer for polygonization
        temp_layer = self._create_temp_layer()
        features = self._collect_valid_features()
        
        if not features:
            self.iface.messageBar().pushWarning('PolygonGenerator', 'Nenhuma geometria válida encontrada.')
            self._cleanup_marker()
            return

        temp_layer.dataProvider().addFeatures(features)
        temp_layer.updateExtents()
        
        # Run polygonize and find containing polygon
        polygon_layer = self._run_polygonize(temp_layer)
        if not polygon_layer:
            return
            
        selected_polygon = self._find_containing_polygon(polygon_layer, center_geometry)
        if not selected_polygon:
            self.iface.messageBar().pushWarning('PolygonGenerator', 'Nenhum polígono válido encontrado.')
            self._cleanup_marker()
            return
        
        # Add the selected polygon to output layer
        self._add_polygon_to_output_layer(selected_polygon)
    
    def _create_temp_layer(self):
        """Create temporary layer for polygonization.
        
        Returns:
            QgsVectorLayer: Temporary line layer
        """
        crs_authid = self.canvas.mapSettings().destinationCrs().authid()
        return QgsVectorLayer(
            f"LineString?crs={crs_authid}",
            "_tmp_lines", 
            "memory"
        )
    
    def _collect_valid_features(self):
        """Collect valid features from visible layers.
        
        Returns:
            list: List of QgsFeature objects ready for polygonization
        """
        features = []
        root = QgsProject.instance().layerTreeRoot()
        
        for layer in QgsProject.instance().mapLayers().values():
            if not isinstance(layer, QgsVectorLayer):
                continue

            node = root.findLayer(layer.id())
            if node is None or not node.isVisible():
                continue
                
            geom_type = QgsWkbTypes.geometryType(layer.wkbType())
            if geom_type not in [QgsWkbTypes.LineGeometry, QgsWkbTypes.PolygonGeometry]:
                continue
                
            for feature in layer.getFeatures():
                geometry = feature.geometry()
                if not geometry.isGeosValid() or geometry.isEmpty():
                    continue
                    
                new_feature = QgsFeature()
                if geom_type == QgsWkbTypes.PolygonGeometry:
                    # converter polígono em linhas (contorno)
                    boundaries = geometry.convertToType(QgsWkbTypes.LineGeometry, True)
                    if boundaries and not boundaries.isEmpty():
                        new_feature.setGeometry(boundaries)
                        features.append(new_feature)
                else:
                    # Use line geometry directly
                    new_feature.setGeometry(geometry)
                    features.append(new_feature)
                    
        return features

    def _run_polygonize(self, temp_layer):
        """Run the polygonize algorithm on the temporary layer.
        
        Args:
            temp_layer: QgsVectorLayer with line geometries
            
        Returns:
            QgsVectorLayer: Polygonized layer or None if failed
        """
        try:
            result = processing.run(
                'qgis:polygonize',
                {'INPUT': temp_layer, 'KEEP_FIELDS': False, 'OUTPUT': 'memory:'}
            )
            return result['OUTPUT']
        except Exception as e:
            self.iface.messageBar().pushCritical('PolygonGenerator', f'Erro ao executar polygonize: {str(e)}')
            self._cleanup_marker()
            return None
    
    def _find_containing_polygon(self, polygon_layer, center_geometry):
        """Find the polygon that contains the clicked point.
        
        Args:
            polygon_layer: QgsVectorLayer with polygons
            center_geometry: QgsGeometry of the clicked point
            
        Returns:
            QgsGeometry: The containing polygon or None if not found
        """
        for feature in polygon_layer.getFeatures():
            geometry = feature.geometry()
            if geometry.contains(center_geometry) and geometry.isGeosValid():
                return geometry
        return None

    def _add_polygon_to_output_layer(self, polygon_geometry):
        """Add the selected polygon to the output layer.
        
        Args:
            polygon_geometry: QgsGeometry of the polygon to add
        """
        output_layer = self._get_or_create_output_layer()
        
        if not output_layer.isEditable():
            output_layer.startEditing()
        
        # Check if polygon already exists
        if self._polygon_exists(output_layer, polygon_geometry):
            self.iface.messageBar().pushInfo('PolygonGenerator', 'Polígono já existe.')
            self._cleanup_marker()
            return
        
        # Create and add new feature
        feature = self._create_polygon_feature(output_layer, polygon_geometry)
        if not output_layer.addFeature(feature):
            self.iface.messageBar().pushCritical('PolygonGenerator', 'Erro ao adicionar feição.')
            self._cleanup_marker()
            return
        
        # Update layer and interface
        output_layer.updateExtents()
        output_layer.triggerRepaint()
        self.canvas.refreshAllLayers()
        
        feature_id = feature.attribute('id')
        QgsMessageLog.logMessage(f'Feição adicionada com ID {feature_id}. Total: {output_layer.featureCount()}', 'PolygonGenerator', Qgis.Info)
        self.iface.messageBar().pushInfo('PolygonGenerator', f'Polígono adicionado com ID {feature_id}. A camada está em modo de edição.')
        
        self._cleanup_marker()
    
    def _get_or_create_output_layer(self):
        """Get existing output layer or create a new one.
        
        Returns:
            QgsVectorLayer: The output layer for created polygons
        """
        # Look for existing output layer
        for layer in QgsProject.instance().mapLayers().values():
            if (layer.name() == self.CAMADA_SAIDA and 
                isinstance(layer, QgsVectorLayer)):
                return layer
        
        # Create new output layer
        crs_authid = self.canvas.mapSettings().destinationCrs().authid()
        output_layer = QgsVectorLayer(
            f"Polygon?crs={crs_authid}",
            self.CAMADA_SAIDA, 
            "memory"
        )
        
        # Add fields
        provider = output_layer.dataProvider()
        provider.addAttributes([
            QgsField('id', QVariant.String),
            QgsField('descricao', QVariant.String),
            QgsField('area_otf', QVariant.Double)
        ])
        output_layer.updateFields()
        
        # Set symbology
        symbol = QgsSymbol.defaultSymbol(output_layer.geometryType())
        symbol.setColor(QColor(255, 0, 0, 100))
        renderer = QgsSingleSymbolRenderer(symbol)
        output_layer.setRenderer(renderer)
        
        QgsProject.instance().addMapLayer(output_layer)
        return output_layer
    
    def _polygon_exists(self, layer, geometry):
        """Check if a polygon with the same geometry already exists.
        
        Args:
            layer: QgsVectorLayer to check
            geometry: QgsGeometry to compare
            
        Returns:
            bool: True if polygon exists, False otherwise
        """
        for feature in layer.getFeatures():
            if feature.geometry().equals(geometry):
                return True
        return False
    
    def _create_polygon_feature(self, layer, geometry):
        """Create a new polygon feature with attributes.
        
        Args:
            layer: QgsVectorLayer where the feature will be added
            geometry: QgsGeometry of the polygon
            
        Returns:
            QgsFeature: The created feature with attributes
        """
        feature = QgsFeature(layer.fields())
        feature.setGeometry(geometry)
        
        # Generate unique ID
        feature_id = str(uuid.uuid4()).replace('{', '').replace('}', '')
        
        # Set attributes
        attributes = [None] * layer.fields().count()
        attributes[layer.fields().indexFromName('id')] = feature_id
        attributes[layer.fields().indexFromName('descricao')] = None
        
        # Calculate area in metric system (EPSG:31985 - SIRGAS 2000 / UTM zone 25S)
        try:
            source_crs = self.canvas.mapSettings().destinationCrs()
            if source_crs.isGeographic():
                # se for geográfico (graus), converte para projetado em metros
                target_crs = QgsCoordinateReferenceSystem('EPSG:31985')  # SIRGAS 2000 / UTM 25S
            else:
                target_crs = source_crs

            transform_context = QgsProject.instance().transformContext()
            xform = QgsCoordinateTransform(source_crs, target_crs, transform_context)

            geom_m = geometry.clone()
            geom_m.transform(xform)
            attributes[layer.fields().indexFromName('area_otf')] = geom_m.area()
        except Exception as e:
            QgsMessageLog.logMessage(f"Erro no cálculo de área: {str(e)}", 'PolygonGenerator', Qgis.Warning)
            attributes[layer.fields().indexFromName('area_otf')] = geometry.area()
        
        feature.setAttributes(attributes)
        return feature

    def _cleanup_marker(self):
        if self.marker:
            self.marker.hide()
            self.marker = None

    def unload(self):
        try:
            self.tool.canvasClicked.disconnect(self.capture_and_create)
        except Exception:
            pass
        self._cleanup_marker()
        self.canvas.unsetMapTool(self.tool)