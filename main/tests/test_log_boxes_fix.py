#!/usr/bin/env python3
"""
Test script to verify that the "Add Log" button works after loading a project.
"""

import tkinter as tk
from core.app import Sincus
import json
import tempfile
import os

def create_test_project():
    """Create a test project with some log boxes"""
    # Create a temporary root window
    root = tk.Tk()
    root.withdraw()  # Hide the window
    
    # Create project info
    project_info = {
        'tete': '1000',
        'puits': 'Test Well',
        'sigle': 'TW001',
        'permis': 'Test Permit',
        'bloc': 'Test Block',
        'carotte_summary': 'Test Core Summary',
        'echelle': '1:100',
        'carottier': 'Test Corer',
        'mud_type': 'Test Mud',
        'carotte': 'Test Core',
        'couronne': 'Test Crown',
        'd_value': 'Test D',
        'core_type': 'Test Type',
        'fun_vis': 'Test Fun',
        'pied': '2000'
    }
    
    # Create the app
    app = Sincus(root, project_info)
    
    # Add some log boxes
    print("Adding log boxes...")
    app.add_log_box()
    app.add_log_box()
    app.add_log_box()
    
    # Save the project
    temp_file = tempfile.NamedTemporaryFile(suffix='.sincus', delete=False, mode='w')
    temp_file.close()
    
    # Create save data manually
    save_data = {
        'project_info': project_info,
        'pages_data': [],
        'log_boxes_data': [],
        'font_size': app.root.taille,
        'version': '1.0'
    }
    
    # Save text content from all pages
    for page in app.pages:
        page_data = []
        for text_widget in page:
            text_content = text_widget.get("1.0", "end-1c")
            page_data.append({
                'content': text_content,
                'bold_ranges': []
            })
        save_data['pages_data'].append(page_data)
    
    # Save log boxes data
    for page_log_boxes in app.log_boxes:
        page_boxes_data = []
        for box in page_log_boxes['boxes']:
            box_data = {
                'bg_color': getattr(box['frame'], 'bg_color', '#FFFFFF'),
                'texture': getattr(box['frame'], 'texture', ''),
                'height': box['frame'].winfo_height(),
                'expandable': box.get('expandable', False)
            }
            page_boxes_data.append(box_data)
        save_data['log_boxes_data'].append(page_boxes_data)
    
    # Save to file
    with open(temp_file.name, 'w', encoding='utf-8') as f:
        json.dump(save_data, f, indent=2, ensure_ascii=False)
    
    print(f"Test project saved to: {temp_file.name}")
    
    # Clean up
    root.destroy()
    
    return temp_file.name

def test_load_project(file_path):
    """Test loading the project and verify log boxes functionality"""
    # Create a new root window
    root = tk.Tk()
    root.withdraw()  # Hide the window
    
    try:
        # Load the project
        with open(file_path, 'r', encoding='utf-8') as f:
            save_data = json.load(f)
        
        project_info = save_data.get('project_info', {})
        
        # Create the app
        app = Sincus(root, project_info)
        
        # Load the project data
        app.load_project_data(save_data)
        
        # Test if log boxes structure is properly initialized
        print(f"Number of log box pages: {len(app.log_boxes)}")
        
        if app.log_boxes:
            last_page = app.log_boxes[-1]
            print(f"Last page has {len(last_page['boxes'])} boxes")
            print(f"Current expandable: {last_page['current_expandable'] is not None}")
            print(f"Container valid: {last_page.get('container') is not None}")
            
            # Test adding a new log box
            print("Testing add_log_box...")
            initial_box_count = len(last_page['boxes'])
            app.add_log_box()
            final_box_count = len(last_page['boxes'])
            
            print(f"Box count before: {initial_box_count}, after: {final_box_count}")
            
            if final_box_count > initial_box_count:
                print("SUCCESS: Add Log button works!")
                return True
            else:
                print("FAILURE: Add Log button did not add a new box")
                return False
        else:
            print("FAILURE: No log boxes structure found")
            return False
            
    except Exception as e:
        print(f"ERROR during test: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        root.destroy()

def main():
    """Main test function"""
    print("=== Testing Log Boxes Fix ===")
    
    # Create test project
    print("1. Creating test project...")
    test_file = create_test_project()
    
    # Test loading
    print("2. Testing project loading...")
    success = test_load_project(test_file)
    
    # Clean up
    try:
        os.unlink(test_file)
        print(f"3. Cleaned up test file: {test_file}")
    except:
        pass
    
    if success:
        print("=== TEST PASSED ===")
    else:
        print("=== TEST FAILED ===")
    
    return success

if __name__ == "__main__":
    main() 