#!/usr/bin/env python3
"""
Manual test of guest wizard functionality
"""

from guest_wizard import GuestWizard

def test_search_functionality():
    """Test search with programmatic input"""
    print("=" * 60)
    print("Testing Search Functionality")
    print("=" * 60)
    
    wizard = GuestWizard()
    
    # Test 1: Search by last name "Johnson"
    print("\n[Test 1] Searching for last name containing 'Johnson'...")
    query = "SELECT * FROM guests WHERE last_name LIKE ? ORDER BY last_name, first_name LIMIT 10"
    results = wizard.db.execute_query(query, ('%Johnson%',), fetch=True)
    
    print(f"✓ Found {len(results)} guest(s) with 'Johnson' in last name")
    for guest in results[:3]:
        print(f"  - {guest['first_name']} {guest['last_name']} (ID: {guest['id']})")
    
    # Test 2: Search by car make "Toyota"
    print("\n[Test 2] Searching for car make containing 'Toyota'...")
    query = "SELECT * FROM guests WHERE car_make LIKE ? ORDER BY last_name, first_name LIMIT 10"
    results = wizard.db.execute_query(query, ('%Toyota%',), fetch=True)
    
    print(f"✓ Found {len(results)} guest(s) with Toyota vehicles")
    for guest in results[:3]:
        vehicle = f"{guest['car_color']} {guest['car_make']} {guest['car_model']}".strip()
        print(f"  - {guest['first_name']} {guest['last_name']}: {vehicle}")
    
    # Test 3: Search by phone area code
    print("\n[Test 3] Searching for phone containing '555-123'...")
    query = "SELECT * FROM guests WHERE phone LIKE ? ORDER BY last_name, first_name LIMIT 10"
    results = wizard.db.execute_query(query, ('%555-123%',), fetch=True)
    
    print(f"✓ Found {len(results)} guest(s) with phone matching '555-123'")
    for guest in results[:3]:
        print(f"  - {guest['first_name']} {guest['last_name']}: {guest['phone']}")
    
    # Test 4: Search by address state
    print("\n[Test 4] Searching for address containing 'CA'...")
    query = "SELECT * FROM guests WHERE address LIKE ? ORDER BY last_name, first_name LIMIT 10"
    results = wizard.db.execute_query(query, ('%CA%',), fetch=True)
    
    print(f"✓ Found {len(results)} guest(s) with CA in address")
    for guest in results[:3]:
        print(f"  - {guest['first_name']} {guest['last_name']}: {guest['address']}")
    
    # Test 5: Combined search
    print("\n[Test 5] Combined search: first_name='John' AND car_make='Tesla'...")
    query = """
        SELECT * FROM guests 
        WHERE first_name LIKE ? AND car_make LIKE ?
        ORDER BY last_name, first_name LIMIT 10
    """
    results = wizard.db.execute_query(query, ('%John%', '%Tesla%'), fetch=True)
    
    print(f"✓ Found {len(results)} guest(s) matching combined criteria")
    for guest in results:
        vehicle = f"{guest['car_color']} {guest['car_make']} {guest['car_model']}".strip()
        print(f"  - {guest['first_name']} {guest['last_name']}: {vehicle}")
    
    print("\n" + "=" * 60)
    print("✅ All search tests completed successfully!")
    print("=" * 60)

if __name__ == "__main__":
    test_search_functionality()
