#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Manual Translation Compiler for ISTools Plugin
Creates basic .qm files from .ts files without requiring Qt tools
"""

import os
import xml.etree.ElementTree as ET
from pathlib import Path

def create_basic_qm_from_ts(ts_file_path, qm_file_path):
    """
    Creates a basic .qm file from a .ts file
    This is a simplified version that creates a text-based .qm file
    """
    try:
        # Parse the .ts file
        tree = ET.parse(ts_file_path)
        root = tree.getroot()
        
        # Extract language
        language = root.get('language', 'en')
        
        # Create basic .qm content
        qm_content = f"""# Compiled translation file for ISTools
# Language: {language}
# Generated from: {os.path.basename(ts_file_path)}

"""
        
        # Extract translations
        for context in root.findall('context'):
            context_name = context.find('name').text
            qm_content += f"[{context_name}]\n"
            
            for message in context.findall('message'):
                source = message.find('source')
                translation = message.find('translation')
                
                if source is not None and translation is not None:
                    source_text = source.text or ""
                    translation_text = translation.text or source_text
                    
                    # Escape special characters
                    source_text = source_text.replace('\n', '\\n').replace('\r', '\\r')
                    translation_text = translation_text.replace('\n', '\\n').replace('\r', '\\r')
                    
                    qm_content += f'"{source_text}" = "{translation_text}"\n'
            
            qm_content += "\n"
        
        # Write .qm file
        with open(qm_file_path, 'w', encoding='utf-8') as f:
            f.write(qm_content)
            
        print(f"Created {qm_file_path} from {ts_file_path}")
        return True
        
    except Exception as e:
        print(f"Error creating {qm_file_path}: {e}")
        return False

def main():
    """Main function to compile all translation files"""
    script_dir = Path(__file__).parent
    
    # Find all .ts files
    ts_files = list(script_dir.glob("*.ts"))
    
    if not ts_files:
        print("No .ts files found in the current directory")
        return
    
    print(f"Found {len(ts_files)} translation files to compile:")
    
    for ts_file in ts_files:
        qm_file = ts_file.with_suffix('.qm')
        print(f"  {ts_file.name} -> {qm_file.name}")
        
        success = create_basic_qm_from_ts(ts_file, qm_file)
        if success:
            print(f"  ✓ Successfully compiled {qm_file.name}")
        else:
            print(f"  ✗ Failed to compile {qm_file.name}")
    
    print("\nCompilation completed!")
    print("\nNote: These are simplified .qm files. For production use,")
    print("consider using Qt's lrelease tool for proper binary compilation.")

if __name__ == "__main__":
    main()