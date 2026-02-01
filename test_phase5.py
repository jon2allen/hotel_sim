#!/usr/bin/env python3
"""
Test script for Phase 5 CLI functionality
"""

import subprocess
import sys
import os

def run_command(cmd, input_data=None):
    """Run a command and return the result"""
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            capture_output=True, 
            text=True,
            input=input_data
        )
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return -1, "", str(e)

def test_help():
    """Test help command"""
    print("Testing help command...")
    code, stdout, stderr = run_command("python3 hotel_cli.py --help")
    
    if code == 0 and "Hotel Simulator CLI" in stdout:
        print("✓ Help command works")
        return True
    else:
        print(f"✗ Help command failed: {stderr}")
        return False

def test_interactive_mode():
    """Test interactive mode"""
    print("Testing interactive mode...")
    
    # Test basic interactive commands
    commands = """help
exit"""
    
    code, stdout, stderr = run_command("python3 hotel_cli.py interactive", commands)
    
    if code == 0 and "Welcome to Hotel Simulator CLI" in stdout:
        print("✓ Interactive mode works")
        return True
    else:
        print(f"✗ Interactive mode failed: {stderr}")
        return False

def test_batch_mode():
    """Test batch simulation mode"""
    print("Testing batch simulation mode...")
    
    # First create a test hotel
    code, stdout, stderr = run_command("python3 hotel_cli.py create --name 'Phase5 Test' --address 'Test Address' --stars 3 --floors 2 --rooms 10")
    
    if code != 0:
        print(f"✗ Failed to create test hotel: {stderr}")
        return False
    
    # Extract hotel ID from output
    hotel_id = None
    for line in stdout.split('\n'):
        if 'Hotel created with ID:' in line:
            hotel_id = line.split(':')[-1].strip()
            break
    
    if not hotel_id:
        print("✗ Could not extract hotel ID")
        return False
    
    # Add some rooms
    code1, _, _ = run_command(f"python3 hotel_cli.py room --hotel-id {hotel_id} --floor 1 --room-number '101' --room-type 'Standard'")
    code2, _, _ = run_command(f"python3 hotel_cli.py room --hotel-id {hotel_id} --floor 1 --room-number '102' --room-type 'Standard'")
    
    if code1 != 0 or code2 != 0:
        print("✗ Failed to create test rooms")
        return False
    
    # Run batch simulation
    code, stdout, stderr = run_command(f"python3 hotel_cli.py batch --hotel-id {hotel_id} --days 2")
    
    if code == 0 and "Batch simulation completed successfully!" in stdout:
        print("✓ Batch simulation mode works")
        return True
    else:
        print(f"✗ Batch simulation failed: {stderr}")
        return False

def test_cli_commands():
    """Test various CLI commands"""
    print("Testing CLI commands...")
    
    # Test list command
    code, stdout, stderr = run_command("python3 hotel_cli.py list")
    
    if code != 0:
        print(f"✗ List command failed: {stderr}")
        return False
    
    # Test info command (use hotel ID 1 if available)
    code, stdout, stderr = run_command("python3 hotel_cli.py info --hotel-id 1")
    
    # Test list-rooms command
    code, stdout, stderr = run_command("python3 hotel_cli.py list-rooms --hotel-id 1")
    
    if code == 0:
        print("✓ Basic CLI commands work")
        return True
    else:
        print(f"✗ CLI commands failed: {stderr}")
        return False

def test_interactive_commands():
    """Test interactive mode commands"""
    print("Testing interactive mode commands...")
    
    commands = """list_hotels
hotel_info 1
list_rooms 1
hotel_status 1
financial_report 1
occupancy_report 1
exit"""
    
    code, stdout, stderr = run_command("python3 hotel_cli.py interactive", commands)
    
    if code == 0 and "Hotel Report:" in stdout:
        print("✓ Interactive commands work")
        return True
    else:
        print(f"✗ Interactive commands failed: {stderr}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("PHASE 5 CLI TESTING")
    print("=" * 60)
    
    tests = [
        test_help,
        test_interactive_mode,
        test_batch_mode,
        test_cli_commands,
        test_interactive_commands
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 60)
    print(f"RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Phase 5 implementation is complete.")
        return 0
    else:
        print("❌ Some tests failed. Please review the implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())