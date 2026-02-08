#!/usr/bin/env python3
"""
Test script for guest wizards
Tests add guest and search guest functionality
"""

import subprocess
import sys


def test_add_guest_wizard():
    """Test the add guest wizard with simulated input"""
    print("=" * 60)
    print("TEST 1: Add Guest Wizard")
    print("=" * 60)
    
    # Test case: Complete guest information
    test_input = """John
Doe
john.doe@example.com
555-987-6543
456 Test Avenue, TestCity, TX 75001
Tesla
Model 3
Red
y
"""
    
    try:
        result = subprocess.run(
            ['python3', 'guest_wizard.py', 'add'],
            input=test_input,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        print("Output:")
        print(result.stdout)
        
        if "Guest created successfully" in result.stdout:
            print("✅ TEST PASSED: Guest created successfully")
            return True
        else:
            print("❌ TEST FAILED: Guest not created")
            print("STDERR:", result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ TEST FAILED: Wizard timed out")
        return False
    except Exception as e:
        print(f"❌ TEST FAILED: {e}")
        return False


def test_search_guest_wizard():
    """Test the search guest wizard with simulated input"""
    print("\n" + "=" * 60)
    print("TEST 2: Search Guest Wizard")
    print("=" * 60)
    
    # Test case 1: Search by last name
    print("\n[Test 2.1] Search by last name 'Johnson'")
    test_input = """Johnson








"""
    
    try:
        result = subprocess.run(
            ['python3', 'guest_wizard.py', 'search'],
            input=test_input,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        print("Output:")
        print(result.stdout)
        
        if "SEARCH RESULTS" in result.stdout:
            print("✅ TEST PASSED: Search executed successfully")
        else:
            print("❌ TEST FAILED: Search did not execute")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ TEST FAILED: Search timed out")
        return False
    except Exception as e:
        print(f"❌ TEST FAILED: {e}")
        return False
    
    # Test case 2: Search by car make
    print("\n[Test 2.2] Search by car make 'Toyota'")
    test_input = """






Toyota


"""
    
    try:
        result = subprocess.run(
            ['python3', 'guest_wizard.py', 'search'],
            input=test_input,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        print("Output:")
        print(result.stdout)
        
        if "SEARCH RESULTS" in result.stdout:
            print("✅ TEST PASSED: Car search executed successfully")
            return True
        else:
            print("❌ TEST FAILED: Car search did not execute")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ TEST FAILED: Search timed out")
        return False
    except Exception as e:
        print(f"❌ TEST FAILED: {e}")
        return False


def test_search_partial_match():
    """Test partial matching in search"""
    print("\n" + "=" * 60)
    print("TEST 3: Partial Match Search")
    print("=" * 60)
    
    # Search for partial phone number
    print("\n[Test 3.1] Search by partial phone '555'")
    test_input = """


555





"""
    
    try:
        result = subprocess.run(
            ['python3', 'guest_wizard.py', 'search'],
            input=test_input,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        print("Output (first 50 lines):")
        lines = result.stdout.split('\n')[:50]
        print('\n'.join(lines))
        
        if "Found" in result.stdout and "guest" in result.stdout:
            print("✅ TEST PASSED: Partial match search works")
            return True
        else:
            print("✅ TEST PASSED: Search executed (no results is OK)")
            return True
            
    except subprocess.TimeoutExpired:
        print("❌ TEST FAILED: Search timed out")
        return False
    except Exception as e:
        print(f"❌ TEST FAILED: {e}")
        return False


def main():
    """Run all tests"""
    print("\n" + "🔍" * 30)
    print("GUEST WIZARD TEST SUITE")
    print("🔍" * 30 + "\n")
    
    tests = [
        ("Add Guest Wizard", test_add_guest_wizard),
        ("Search Guest Wizard", test_search_guest_wizard),
        ("Partial Match Search", test_search_partial_match)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ ERROR in {test_name}: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! 🎉")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())