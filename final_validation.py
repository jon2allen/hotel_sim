#!/usr/bin/env python3
"""
Final validation script - runs all tests and generates report
"""

import subprocess
import sys

def run_test(test_file, description):
    """Run a test file and return results"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"File: {test_file}")
    print('='*60)
    
    try:
        result = subprocess.run(
            ['python3', test_file],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        return result.returncode == 0
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def main():
    print("\n" + "🚗" * 30)
    print("FINAL VALIDATION - GUEST CAR FIELDS")
    print("🚗" * 30)
    
    tests = [
        ("test_guest_car_fields.py", "Guest Car Fields Comprehensive Tests"),
        ("test_wizard_with_cars.py", "Wizard Integration with Car Fields"),
        ("test_phase5.py", "Phase 5 CLI Tests (Regression)")
    ]
    
    results = []
    for test_file, description in tests:
        success = run_test(test_file, description)
        results.append((description, success))
    
    # Final Summary
    print("\n" + "="*60)
    print("FINAL VALIDATION SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for description, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status}: {description}")
    
    print(f"\nTotal: {passed}/{total} test suites passed")
    
    if passed == total:
        print("\n" + "🎉" * 30)
        print("ALL VALIDATIONS PASSED!")
        print("Guest car fields implementation is COMPLETE and VALIDATED")
        print("🎉" * 30)
        return 0
    else:
        print(f"\n⚠️  {total - passed} test suite(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
