#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to compile translation files (.ts) to binary format (.qm)
for the ISTools QGIS plugin.

This script searches for .ts files in the i18n directory and compiles
them to .qm files using Qt's lrelease tool.

Usage:
    python compile_translations.py

Requirements:
    - Qt development tools (lrelease command)
    - Python 3.x
"""

import os
import subprocess
import sys
from pathlib import Path


def find_lrelease():
    """Find the lrelease executable in common Qt installation paths.
    
    Returns:
        str: Path to lrelease executable or None if not found
    """
    # Common lrelease command names
    lrelease_names = ['lrelease', 'lrelease-qt5', 'lrelease-qt6']
    
    # Try to find lrelease in PATH
    for name in lrelease_names:
        try:
            result = subprocess.run([name, '-version'], 
                                   capture_output=True, 
                                   text=True, 
                                   timeout=5)
            if result.returncode == 0:
                return name
        except (subprocess.TimeoutExpired, FileNotFoundError):
            continue
    
    # Common Qt installation paths on Windows
    if sys.platform == 'win32':
        qt_paths = [
            r'C:\Qt\*\bin',
            r'C:\Qt\Tools\*\bin',
            r'C:\Program Files\Qt\*\bin',
            r'C:\Program Files (x86)\Qt\*\bin'
        ]
        
        import glob
        for path_pattern in qt_paths:
            for qt_bin_dir in glob.glob(path_pattern):
                for name in lrelease_names:
                    lrelease_path = os.path.join(qt_bin_dir, f'{name}.exe')
                    if os.path.exists(lrelease_path):
                        return lrelease_path
    
    return None


def compile_translation_file(ts_file, lrelease_cmd):
    """Compile a single .ts file to .qm format.
    
    Args:
        ts_file (Path): Path to the .ts file
        lrelease_cmd (str): Path to lrelease executable
        
    Returns:
        bool: True if compilation successful, False otherwise
    """
    qm_file = ts_file.with_suffix('.qm')
    
    try:
        result = subprocess.run(
            [lrelease_cmd, str(ts_file), '-qm', str(qm_file)],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print(f"✓ Compiled: {ts_file.name} -> {qm_file.name}")
            return True
        else:
            print(f"✗ Failed to compile {ts_file.name}:")
            print(f"  Error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"✗ Timeout while compiling {ts_file.name}")
        return False
    except Exception as e:
        print(f"✗ Exception while compiling {ts_file.name}: {e}")
        return False


def main():
    """Main function to compile all translation files."""
    print("ISTools Translation Compiler")
    print("=" * 40)
    
    # Get script directory and i18n path
    script_dir = Path(__file__).parent
    i18n_dir = script_dir / 'i18n'
    
    # Check if i18n directory exists
    if not i18n_dir.exists():
        print(f"✗ i18n directory not found: {i18n_dir}")
        return 1
    
    # Find lrelease command
    lrelease_cmd = find_lrelease()
    if not lrelease_cmd:
        print("✗ lrelease command not found!")
        print("  Please install Qt development tools or add Qt bin directory to PATH")
        return 1
    
    print(f"Using lrelease: {lrelease_cmd}")
    print()
    
    # Find all .ts files
    ts_files = list(i18n_dir.glob('*.ts'))
    if not ts_files:
        print(f"✗ No .ts files found in {i18n_dir}")
        return 1
    
    print(f"Found {len(ts_files)} translation file(s):")
    for ts_file in ts_files:
        print(f"  - {ts_file.name}")
    print()
    
    # Compile each .ts file
    success_count = 0
    for ts_file in ts_files:
        if compile_translation_file(ts_file, lrelease_cmd):
            success_count += 1
    
    print()
    print(f"Compilation complete: {success_count}/{len(ts_files)} files compiled successfully")
    
    if success_count == len(ts_files):
        print("✓ All translation files compiled successfully!")
        return 0
    else:
        print("✗ Some translation files failed to compile")
        return 1


if __name__ == '__main__':
    sys.exit(main())