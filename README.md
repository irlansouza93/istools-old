# ISTools Plugin for QGIS

ISTools (Irlan Souza Tools) is a comprehensive collection of vectorization tools for QGIS, designed to facilitate vector operations and spatial analysis.

## Overview

This plugin provides essential tools for working with vector data in QGIS, including line extension, polygon generation, bounded polygon creation, and point-on-surface generation. All tools feature intuitive user interfaces, comprehensive error handling, and support for various coordinate systems.

## Tools Included

### 1. Extend Lines
Automatically extends loose line endpoints to connect with nearby features within the same layer.

**How to use:**
1. Select a line layer in the Layers panel
2. Select one or more line features
3. Click the "Extend Lines" icon in the toolbar
4. The tool will automatically extend selected lines to connect with nearby features

### 2. Polygon Generator
Creates polygons from point coordinates with automatic validation.

**How to use:**
1. Ensure you have line or polygon layers in your project
2. Click the "Polygon Generator" icon in the toolbar
3. Click on the map to define the center point for polygon generation
4. Right-click to cancel the operation
5. The tool will generate polygons based on surrounding features

### 3. Bounded Polygon Generator
Generates polygons within a frame using delimiter layers (lines and/or polygons).

**How to use:**
1. Load frame layer (polygon) and delimiter layers (lines/polygons)
2. Click the "Bounded Polygon Generator" icon
3. Select frame layer and delimiter layers in the dialog
4. Click "Run" to generate bounded polygons
5. The result will be added as a new layer

### 4. Point on Surface Generator
Generates representative points within polygon features, guaranteed to be inside polygon boundaries.

**How to use:**
1. Select a polygon layer as the active layer
2. Select one or more polygon features
3. Click the "Point on Surface Generator" icon
4. Central points will be generated for each selected polygon

## Requirements

- QGIS 3.0 or higher
- Vector layers (lines, polygons, or points depending on the tool)
- Appropriate coordinate reference system (CRS) for your data

## Installation

### Method 1: QGIS Plugin Repository (Recommended)
1. Open QGIS
2. Go to `Plugins` > `Manage and Install Plugins`
3. Search for "ISTools"
4. Click "Install Plugin"
5. The plugin icons will appear in the toolbar

### Method 2: Manual Installation from ZIP
1. Download the plugin ZIP file from the repository
2. Open QGIS
3. Go to `Plugins` > `Manage and Install Plugins`
4. Click "Install from ZIP"
5. Select the downloaded ZIP file
6. Click "Install Plugin"
7. Enable the plugin in the "Installed" tab

### Method 3: Development Installation
1. Clone or download the repository
2. Copy the `istools` folder to your QGIS plugins directory:
   - **Windows:** `C:\Users\[username]\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\`
   - **macOS:** `~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/`
   - **Linux:** `~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/`
3. Restart QGIS
4. Enable the plugin in `Plugins` > `Manage and Install Plugins` > `Installed`

## Usage Tips

- Always ensure your data has a proper coordinate reference system (CRS) assigned
- For best results with line extension, use snapping settings to ensure proper connectivity
- When generating polygons, make sure delimiter layers form closed boundaries
- Use the QGIS Processing Toolbox for batch operations with multiple datasets
- Check the QGIS message bar for success/error messages after running tools

## Troubleshooting

### Common Issues

**Tool icons not appearing:**
- Ensure the plugin is properly installed and enabled
- Restart QGIS after installation
- Check the plugin is compatible with your QGIS version

**"No active layer" error:**
- Select a layer in the Layers panel before running the tool
- Ensure the selected layer has the correct geometry type for the tool

**"No features selected" error:**
- Select features using the selection tools before running the tool
- Use Ctrl+A to select all features in a layer

**Processing errors:**
- Check that your data has valid geometries
- Ensure coordinate reference systems are properly defined
- Verify that input layers contain the expected geometry types

## Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This plugin is licensed under the GNU General Public License v2.0. See the LICENSE file for details.

## Author

Developed by Irlan Souza, 3° Sgt Brazilian Army

## Support

For support, please:
1. Check this README for common solutions
2. Search existing issues in the repository
3. Create a new issue with detailed information about your problem
4. Include QGIS version, plugin version, and error messages if applicable