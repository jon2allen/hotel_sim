#!/usr/bin/env python3

import subprocess
import sys

def test_hotel_wizard():
    """Test the interactive hotel creation wizard"""
    
    # Simulate user input for the wizard
    user_input = """Grand Hotel
123 Main Street
5
10
50
1,2,3
1
20
15
10
150.00
200.00
100.00
"""
    
    try:
        # Run the wizard with simulated input
        process = subprocess.Popen(
            [sys.executable, 'hotel_cli.py', 'wizard'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        stdout, stderr = process.communicate(input=user_input)
        
        print("=== Wizard Test Output ===")
        print(stdout)
        
        if stderr:
            print("=== Errors ===")
            print(stderr)
            
        print(f"Return code: {process.returncode}")
        
    except Exception as e:
        print(f"Error running test: {e}")

if __name__ == "__main__":
    test_hotel_wizard()