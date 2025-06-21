#!/usr/bin/env python3
"""
Test script for save/load functionality
"""

import tkinter as tk
import json
import tempfile
import os

def test_save_load_data():
    """Test the data structure that would be saved/loaded"""
    
    # Sample project data
    sample_data = {
        'project_info': {
            'puits': 'Test Well',
            'sigle': 'TW-001',
            'permis': 'Test Permit',
            'bloc': 'Test Block',
            'echelle': '1/40',
            'carottier': '12345',
            'mud_type': 'OBM',
            'carotte': '1',
            'couronne': '6" x 2 5/8"',
            'd_value': '1.08',
            'tete': '1000m',
            'core_type': 'Test Type',
            'fun_vis': '50',
            'pied': '1100m',
            'carotte_summary': 'Test summary'
        },
        'pages_data': [
            [
                {'content': 'Test content 1', 'bold_ranges': [('1.0', '1.5')]},
                {'content': 'Test content 2', 'bold_ranges': []},
                {'content': 'Test content 3', 'bold_ranges': []},
                {'content': 'Test content 4', 'bold_ranges': []},
                {'content': 'Test content 5', 'bold_ranges': []},
                {'content': 'Test content 6', 'bold_ranges': []},
                {'content': 'Test content 7', 'bold_ranges': []},
                {'content': 'Test content 8', 'bold_ranges': []},
                {'content': 'Test content 9', 'bold_ranges': []},
                {'content': 'Test content 10', 'bold_ranges': []}
            ]
        ],
        'log_boxes_data': [
            [
                {'bg_color': '#FFFFFF', 'texture': '', 'height': 50, 'expandable': True},
                {'bg_color': '#FF0000', 'texture': '++++', 'height': 75, 'expandable': False}
            ]
        ],
        'font_size': 12,
        'version': '1.0'
    }
    
    # Test saving
    with tempfile.NamedTemporaryFile(mode='w', suffix='.sincus', delete=False) as f:
        json.dump(sample_data, f, indent=2, ensure_ascii=False)
        temp_file = f.name
    
    print(f"Saved test data to: {temp_file}")
    
    # Test loading
    with open(temp_file, 'r', encoding='utf-8') as f:
        loaded_data = json.load(f)
    
    print("Loaded data successfully!")
    print(f"Project: {loaded_data['project_info']['puits']}")
    print(f"Pages: {len(loaded_data['pages_data'])}")
    print(f"Log boxes: {len(loaded_data['log_boxes_data'][0])}")
    
    # Clean up
    os.unlink(temp_file)
    print("Test completed successfully!")

if __name__ == "__main__":
    test_save_load_data() 