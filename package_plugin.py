#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to package the ISTools QGIS plugin for distribution.

This script creates a ZIP file containing all necessary plugin files
while excluding development and temporary files.

Usage:
    python package_plugin.py

Output:
    Creates istools.zip in the parent directory
"""

import os
import zipfile
import sys
from pathlib import Path
import shutil
from datetime import datetime


def should_exclude_file(file_path, base_path):
    """Check if a file should be excluded from the package.
    
    Args:
        file_path (Path): Path to the file
        base_path (Path): Base plugin directory path
        
    Returns:
        bool: True if file should be excluded
    """
    # Get relative path
    try:
        rel_path = file_path.relative_to(base_path)
    except ValueError:
        return True
    
    # Convert to string for easier checking
    rel_path_str = str(rel_path).replace('\\', '/')
    
    # Files and patterns to exclude
    exclude_patterns = [
        # Python cache and compiled files
        '__pycache__',
        '*.pyc',
        '*.pyo',
        '*.pyd',
        
        # Development files
        '.git',
        '.gitignore',
        '.vscode',
        '.idea',
        '*.swp',
        '*.swo',
        '*~',
        
        # Temporary files
        '*.tmp',
        '*.temp',
        '*.bak',
        '*.backup',
        
        # Development scripts
        'package_plugin.py',
        'compile_translations.py',
        
        # Test files
        'test_*',
        'tests/',
        
        # Documentation build
        'docs/build/',
        'docs/_build/',
        
        # OS specific
        '.DS_Store',
        'Thumbs.db',
        'desktop.ini',
        
        # Duplicate icon directory (keep only root icons)
        'iconss/',
    ]
    
    # Check against exclude patterns
    for pattern in exclude_patterns:
        if pattern.endswith('/'):
            # Directory pattern
            if rel_path_str.startswith(pattern) or f'/{pattern}' in rel_path_str:
                return True
        elif '*' in pattern:
            # Wildcard pattern
            import fnmatch
            if fnmatch.fnmatch(rel_path_str, pattern) or fnmatch.fnmatch(file_path.name, pattern):
                return True
        else:
            # Exact match
            if rel_path_str == pattern or file_path.name == pattern:
                return True
    
    return False


def get_plugin_version(metadata_file):
    """Extract version from metadata.txt file.
    
    Args:
        metadata_file (Path): Path to metadata.txt
        
    Returns:
        str: Plugin version or 'unknown'
    """
    try:
        with open(metadata_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('version='):
                    return line.split('=', 1)[1].strip()
    except Exception:
        pass
    return 'unknown'


def create_plugin_package(plugin_dir, output_dir=None):
    """Create a ZIP package of the plugin.
    
    Args:
        plugin_dir (Path): Path to the plugin directory
        output_dir (Path): Output directory for the ZIP file
        
    Returns:
        Path: Path to the created ZIP file
    """
    plugin_dir = Path(plugin_dir)
    
    if output_dir is None:
        output_dir = plugin_dir.parent
    else:
        output_dir = Path(output_dir)
    
    # Get plugin version
    metadata_file = plugin_dir / 'metadata.txt'
    version = get_plugin_version(metadata_file)
    
    # Create output filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    if version != 'unknown':
        zip_filename = f'istools_v{version}.zip'
    else:
        zip_filename = f'istools_{timestamp}.zip'
    
    zip_path = output_dir / zip_filename
    
    print(f"Creating plugin package: {zip_filename}")
    print(f"Plugin directory: {plugin_dir}")
    print(f"Output directory: {output_dir}")
    print()
    
    # Create ZIP file
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        file_count = 0
        excluded_count = 0
        
        # Walk through all files in plugin directory
        for root, dirs, files in os.walk(plugin_dir):
            root_path = Path(root)
            
            # Filter directories
            dirs[:] = [d for d in dirs if not should_exclude_file(root_path / d, plugin_dir)]
            
            for file in files:
                file_path = root_path / file
                
                # Check if file should be excluded
                if should_exclude_file(file_path, plugin_dir):
                    excluded_count += 1
                    print(f"  Excluded: {file_path.relative_to(plugin_dir)}")
                    continue
                
                # Add file to ZIP
                arcname = f"istools/{file_path.relative_to(plugin_dir)}"
                zipf.write(file_path, arcname)
                file_count += 1
                print(f"  Added: {file_path.relative_to(plugin_dir)}")
    
    print()
    print(f"Package created successfully!")
    print(f"  Files included: {file_count}")
    print(f"  Files excluded: {excluded_count}")
    print(f"  Package size: {zip_path.stat().st_size / 1024:.1f} KB")
    print(f"  Output file: {zip_path}")
    
    return zip_path


def validate_plugin_structure(plugin_dir):
    """Validate that the plugin has all required files.
    
    Args:
        plugin_dir (Path): Path to the plugin directory
        
    Returns:
        bool: True if structure is valid
    """
    plugin_dir = Path(plugin_dir)
    
    required_files = [
        '__init__.py',
        'metadata.txt',
        'istools.py',
    ]
    
    print("Validating plugin structure...")
    
    missing_files = []
    for file in required_files:
        file_path = plugin_dir / file
        if not file_path.exists():
            missing_files.append(file)
        else:
            print(f"  ✓ {file}")
    
    if missing_files:
        print("\n✗ Missing required files:")
        for file in missing_files:
            print(f"  - {file}")
        return False
    
    print("✓ Plugin structure is valid")
    return True


def main():
    """Main function to package the plugin."""
    print("ISTools Plugin Packager")
    print("=" * 40)
    
    # Get plugin directory (current directory)
    plugin_dir = Path(__file__).parent
    
    # Validate plugin structure
    if not validate_plugin_structure(plugin_dir):
        print("\n✗ Plugin structure validation failed!")
        return 1
    
    print()
    
    try:
        # Create package
        zip_path = create_plugin_package(plugin_dir)
        
        print("\n✓ Plugin packaged successfully!")
        print(f"\nTo install:")
        print(f"1. Open QGIS")
        print(f"2. Go to Plugins > Manage and Install Plugins")
        print(f"3. Click 'Install from ZIP'")
        print(f"4. Select: {zip_path}")
        print(f"5. Click 'Install Plugin'")
        
        return 0
        
    except Exception as e:
        print(f"\n✗ Error creating package: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())