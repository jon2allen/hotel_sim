#!/usr/bin/env python3
"""
Test script for guest car fields (make, model, color)
Tests database schema, guest creation, and data retrieval
Updated with full American-style addresses and 10-digit phone numbers
"""

import sqlite3
import sys
from hotel_simulator import HotelSimulator, Guest
from database import HotelDatabase

def test_database_schema():
    """Test that the database schema includes car fields"""
    print("=" * 60)
    print("TEST 1: Database Schema Validation")
    print("=" * 60)
    
    db = HotelDatabase('hotel.db')
    cursor = db.conn.cursor()
    
    # Get table info
    cursor.execute("PRAGMA table_info(guests)")
    columns = cursor.fetchall()
    
    column_names = [col[1] for col in columns]
    
    print(f"\n✓ Guests table has {len(columns)} columns:")
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")
    
    # Check for car fields
    required_fields = ['car_make', 'car_model', 'car_color']
    missing_fields = [field for field in required_fields if field not in column_names]
    
    if missing_fields:
        print(f"\n✗ FAILED: Missing fields: {missing_fields}")
        return False
    else:
        print(f"\n✓ PASSED: All car fields present: {required_fields}")
        return True

def test_create_guest_with_car():
    """Test creating a guest with car information"""
    print("\n" + "=" * 60)
    print("TEST 2: Create Guest with Car Information")
    print("=" * 60)
    
    sim = HotelSimulator('hotel.db')
    
    # Test 1: Guest with full car info
    print("\n[Test 2.1] Creating guest with complete car info...")
    guest1 = sim.create_guest(
        first_name="Alice",
        last_name="Johnson",
        email="alice.johnson@example.com",
        phone="555-123-4567",
        address="123 Main Street, Anytown, CA 90210",
        car_make="Toyota",
        car_model="Camry",
        car_color="Blue"
    )
    
    if guest1.car_make == "Toyota" and guest1.car_model == "Camry" and guest1.car_color == "Blue":
        print(f"✓ PASSED: Guest created with car info")
        print(f"  Name: {guest1.first_name} {guest1.last_name}")
        print(f"  Phone: {guest1.phone}")
        print(f"  Address: {guest1.address}")
        print(f"  Car: {guest1.car_color} {guest1.car_make} {guest1.car_model}")
    else:
        print(f"✗ FAILED: Car info not saved correctly")
        return False
    
    # Test 2: Guest without car info (should default to empty strings)
    print("\n[Test 2.2] Creating guest without car info...")
    guest2 = sim.create_guest(
        first_name="Robert",
        last_name="Smith",
        email="robert.smith@example.com",
        phone="555-234-5678",
        address="456 Oak Avenue, Springfield, IL 62701"
    )
    
    if guest2.car_make == "" and guest2.car_model == "" and guest2.car_color == "":
        print(f"✓ PASSED: Guest created without car info (defaults to empty)")
        print(f"  Name: {guest2.first_name} {guest2.last_name}")
        print(f"  Phone: {guest2.phone}")
        print(f"  Address: {guest2.address}")
        print(f"  Car: (none)")
    else:
        print(f"✗ FAILED: Default car values incorrect")
        return False
    
    # Test 3: Guest with N/A car info
    print("\n[Test 2.3] Creating guest with N/A car info...")
    guest3 = sim.create_guest(
        first_name="Charles",
        last_name="Brown",
        email="charles.brown@example.com",
        phone="555-345-6789",
        address="789 Peanuts Lane, Minneapolis, MN 55401",
        car_make="N/A",
        car_model="N/A",
        car_color="N/A"
    )
    
    if guest3.car_make == "N/A" and guest3.car_model == "N/A" and guest3.car_color == "N/A":
        print(f"✓ PASSED: Guest created with N/A car info")
        print(f"  Name: {guest3.first_name} {guest3.last_name}")
        print(f"  Phone: {guest3.phone}")
        print(f"  Address: {guest3.address}")
        print(f"  Car: {guest3.car_make}")
    else:
        print(f"✗ FAILED: N/A values not saved correctly")
        return False
    
    # Test 4: Partial car info
    print("\n[Test 2.4] Creating guest with partial car info...")
    guest4 = sim.create_guest(
        first_name="Diana",
        last_name="Prince",
        email="diana.prince@example.com",
        phone="555-456-7890",
        address="1600 Pennsylvania Avenue NW, Washington, DC 20500",
        car_make="Honda",
        car_color="Red"
        # Note: car_model is omitted
    )
    
    if guest4.car_make == "Honda" and guest4.car_model == "" and guest4.car_color == "Red":
        print(f"✓ PASSED: Guest created with partial car info")
        print(f"  Name: {guest4.first_name} {guest4.last_name}")
        print(f"  Phone: {guest4.phone}")
        print(f"  Address: {guest4.address}")
        print(f"  Car: {guest4.car_color} {guest4.car_make} (model not specified)")
    else:
        print(f"✗ FAILED: Partial car info not handled correctly")
        return False
    
    return True

def test_retrieve_guest_data():
    """Test retrieving guest data from database"""
    print("\n" + "=" * 60)
    print("TEST 3: Retrieve Guest Data from Database")
    print("=" * 60)
    
    db = HotelDatabase('hotel.db')
    cursor = db.conn.cursor()
    
    # Get the most recent guests with car info
    query = """
        SELECT first_name, last_name, email, phone, address, car_make, car_model, car_color
        FROM guests
        WHERE car_make IS NOT NULL AND car_make != ''
        ORDER BY id DESC
        LIMIT 5
    """
    
    cursor.execute(query)
    guests_with_cars = cursor.fetchall()
    
    print(f"\n✓ Found {len(guests_with_cars)} recent guests with car information:")
    for guest in guests_with_cars:
        fname, lname, email, phone, address, make, model, color = guest
        print(f"  - {fname} {lname}")
        print(f"    Phone: {phone}")
        print(f"    Address: {address}")
        print(f"    Car: {color} {make} {model}")
    
    # Get count of guests with and without car info
    cursor.execute("SELECT COUNT(*) FROM guests WHERE car_make IS NOT NULL AND car_make != '' AND car_make != 'N/A'")
    with_cars = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM guests WHERE car_make IS NULL OR car_make = '' OR car_make = 'N/A'")
    without_cars = cursor.fetchone()[0]
    
    print(f"\n✓ Guest statistics:")
    print(f"  - Guests with car info: {with_cars}")
    print(f"  - Guests without car info: {without_cars}")
    
    return True

def test_query_by_car():
    """Test querying guests by car information"""
    print("\n" + "=" * 60)
    print("TEST 4: Query Guests by Car Information")
    print("=" * 60)
    
    db = HotelDatabase('hotel.db')
    cursor = db.conn.cursor()
    
    # Find all Toyota owners
    print("\n[Test 4.1] Finding all Toyota owners...")
    cursor.execute("""
        SELECT first_name, last_name, phone, address, car_model, car_color
        FROM guests
        WHERE car_make = 'Toyota'
        ORDER BY last_name
    """)
    toyota_owners = cursor.fetchall()
    
    print(f"✓ Found {len(toyota_owners)} Toyota owner(s):")
    for owner in toyota_owners:
        print(f"  - {owner[0]} {owner[1]}")
        print(f"    Phone: {owner[2]}")
        print(f"    Address: {owner[3]}")
        print(f"    Car: {owner[5]} {owner[4]}")
    
    # Find all blue cars
    print("\n[Test 4.2] Finding all blue cars...")
    cursor.execute("""
        SELECT first_name, last_name, phone, address, car_make, car_model
        FROM guests
        WHERE car_color = 'Blue'
        ORDER BY last_name
    """)
    blue_cars = cursor.fetchall()
    
    print(f"✓ Found {len(blue_cars)} guest(s) with blue cars:")
    for owner in blue_cars:
        print(f"  - {owner[0]} {owner[1]}")
        print(f"    Phone: {owner[2]}")
        print(f"    Address: {owner[3]}")
        print(f"    Car: {owner[4]} {owner[5]}")
    
    # Group by car make
    print("\n[Test 4.3] Car makes summary...")
    cursor.execute("""
        SELECT car_make, COUNT(*) as count
        FROM guests
        WHERE car_make IS NOT NULL AND car_make != '' AND car_make != 'N/A'
        GROUP BY car_make
        ORDER BY count DESC
    """)
    car_makes = cursor.fetchall()
    
    print(f"✓ Car makes distribution:")
    for make, count in car_makes:
        print(f"  - {make}: {count} guest(s)")
    
    return True

def main():
    """Run all tests"""
    print("\n" + "🚗" * 30)
    print("GUEST CAR FIELDS TEST SUITE")
    print("American-Style Addresses & Phone Numbers")
    print("🚗" * 30 + "\n")
    
    tests = [
        ("Database Schema", test_database_schema),
        ("Create Guest with Car", test_create_guest_with_car),
        ("Retrieve Guest Data", test_retrieve_guest_data),
        ("Query by Car", test_query_by_car)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ ERROR in {test_name}: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
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
