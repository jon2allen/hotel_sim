#!/usr/bin/env python3
"""
Test script for wizard functionality with guest car fields
Tests guest creation with various car field combinations
Updated with full American-style addresses and 10-digit phone numbers
"""

import sys
from hotel_simulator import HotelSimulator
from database import HotelDatabase

def test_wizard_with_guest_cars():
    """Test creating guests with car information through the simulator"""
    
    print("=" * 60)
    print("WIZARD TEST: Guest Creation with Car Fields")
    print("American-Style Addresses & Phone Numbers")
    print("=" * 60)
    
    try:
        # Initialize simulator
        sim = HotelSimulator('hotel.db')
        
        # Create a test hotel if needed
        hotels = sim.db.execute_query("SELECT * FROM hotel LIMIT 1", fetch=True)
        if not hotels:
            print("\n[Setup] Creating test hotel...")
            hotel_id = sim.db.create_hotel(
                name="Car Test Hotel",
                address="123 Test Street",
                stars=4,
                total_floors=3,
                total_rooms=30
            )
            print(f"✓ Created test hotel with ID: {hotel_id}")
        else:
            hotel_id = hotels[0]['id']
            print(f"\n[Setup] Using existing hotel ID: {hotel_id}")
        
        # Test scenarios with American-style addresses and phone numbers
        test_cases = [
            {
                "name": "Luxury Guest with Sports Car",
                "first_name": "James",
                "last_name": "Bond",
                "email": "james.bond@mi6.gov.uk",
                "phone": "555-007-0007",
                "address": "1007 Secret Service Drive, Langley, VA 22101",
                "car_make": "Aston Martin",
                "car_model": "DB5",
                "car_color": "Silver"
            },
            {
                "name": "Business Traveler with Sedan",
                "first_name": "Sarah",
                "last_name": "Connor",
                "email": "sarah.connor@cyberdyne.com",
                "phone": "555-198-4000",
                "address": "2029 Skynet Boulevard, Los Angeles, CA 90001",
                "car_make": "BMW",
                "car_model": "5 Series",
                "car_color": "Black"
            },
            {
                "name": "Family Vacation with SUV",
                "first_name": "Homer",
                "last_name": "Simpson",
                "email": "homer.simpson@springfieldnpp.com",
                "phone": "555-733-4000",
                "address": "742 Evergreen Terrace, Springfield, OR 97477",
                "car_make": "Ford",
                "car_model": "Explorer",
                "car_color": "Red"
            },
            {
                "name": "Eco-Conscious Guest with Electric Car",
                "first_name": "Elon",
                "last_name": "Musk",
                "email": "elon.musk@tesla.com",
                "phone": "555-837-5200",
                "address": "3500 Deer Creek Road, Palo Alto, CA 94304",
                "car_make": "Tesla",
                "car_model": "Model S",
                "car_color": "White"
            },
            {
                "name": "Guest Without Car (Public Transit)",
                "first_name": "Rachel",
                "last_name": "Green",
                "email": "rachel.green@bloomingdales.com",
                "phone": "555-212-5000",
                "address": "90 Bedford Street, New York, NY 10014",
                "car_make": "",
                "car_model": "",
                "car_color": ""
            },
            {
                "name": "Guest with N/A Car (Ride Share)",
                "first_name": "Michael",
                "last_name": "Scott",
                "email": "michael.scott@dundermifflin.com",
                "phone": "555-570-3200",
                "address": "1725 Slough Avenue, Scranton, PA 18503",
                "car_make": "N/A",
                "car_model": "N/A",
                "car_color": "N/A"
            },
            {
                "name": "Tech Professional with Hybrid",
                "first_name": "Grace",
                "last_name": "Hopper",
                "email": "grace.hopper@navy.mil",
                "phone": "555-194-6000",
                "address": "1000 Navy Pentagon, Washington, DC 20350",
                "car_make": "Toyota",
                "car_model": "Prius",
                "car_color": "Blue"
            },
            {
                "name": "Retiree with Classic Car",
                "first_name": "Walter",
                "last_name": "White",
                "email": "walter.white@graymatter.com",
                "phone": "555-505-2000",
                "address": "308 Negra Arroyo Lane, Albuquerque, NM 87104",
                "car_make": "Pontiac",
                "car_model": "Aztek",
                "car_color": "Green"
            }
        ]
        
        print("\n" + "=" * 60)
        print("Creating Test Guests")
        print("=" * 60)
        
        created_guests = []
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n[Test {i}] {test_case['name']}")
            print("-" * 40)
            
            guest = sim.create_guest(
                first_name=test_case['first_name'],
                last_name=test_case['last_name'],
                email=test_case['email'],
                phone=test_case['phone'],
                address=test_case['address'],
                car_make=test_case['car_make'],
                car_model=test_case['car_model'],
                car_color=test_case['car_color']
            )
            
            created_guests.append(guest)
            
            # Verify the guest was created correctly
            print(f"  Name: {guest.first_name} {guest.last_name}")
            print(f"  Email: {guest.email}")
            print(f"  Phone: {guest.phone}")
            print(f"  Address: {guest.address}")
            
            if guest.car_make and guest.car_make != "N/A":
                print(f"  Vehicle: {guest.car_color} {guest.car_make} {guest.car_model}")
            elif guest.car_make == "N/A":
                print(f"  Vehicle: {guest.car_make}")
            else:
                print(f"  Vehicle: (none)")
            
            print("  ✓ Guest created successfully")
        
        # Verify data in database
        print("\n" + "=" * 60)
        print("Database Verification")
        print("=" * 60)
        
        db = HotelDatabase('hotel.db')
        
        # Check all created guests
        for guest in created_guests:
            query = """
                SELECT first_name, last_name, email, phone, address, 
                       car_make, car_model, car_color
                FROM guests
                WHERE id = ?
            """
            result = db.execute_query(query, (guest.id,), fetch=True)
            
            if result:
                db_guest = result[0]
                print(f"\n✓ Verified guest {db_guest['first_name']} {db_guest['last_name']} in database")
                print(f"  Phone: {db_guest['phone']}")
                print(f"  Address: {db_guest['address']}")
                
                # Verify car fields match
                if (db_guest['car_make'] == guest.car_make and 
                    db_guest['car_model'] == guest.car_model and 
                    db_guest['car_color'] == guest.car_color):
                    if db_guest['car_make'] and db_guest['car_make'] != 'N/A':
                        print(f"  ✓ Car fields match: {db_guest['car_make']} {db_guest['car_model']}")
                    else:
                        print(f"  ✓ Car fields match (no vehicle)")
                else:
                    print(f"  ✗ Car fields mismatch!")
                    return False
            else:
                print(f"✗ Guest {guest.first_name} {guest.last_name} not found in database!")
                return False
        
        # Statistics
        print("\n" + "=" * 60)
        print("Guest Statistics")
        print("=" * 60)
        
        # Count guests by car make
        query = """
            SELECT car_make, COUNT(*) as count
            FROM guests
            WHERE car_make IS NOT NULL AND car_make != '' AND car_make != 'N/A'
            GROUP BY car_make
            ORDER BY count DESC
            LIMIT 10
        """
        car_stats = db.execute_query(query, fetch=True)
        
        print("\nTop Car Makes:")
        for stat in car_stats:
            print(f"  {stat['car_make']}: {stat['count']} guest(s)")
        
        # Count guests by car color
        query = """
            SELECT car_color, COUNT(*) as count
            FROM guests
            WHERE car_color IS NOT NULL AND car_color != '' AND car_color != 'N/A'
            GROUP BY car_color
            ORDER BY count DESC
            LIMIT 10
        """
        color_stats = db.execute_query(query, fetch=True)
        
        print("\nTop Car Colors:")
        for stat in color_stats:
            print(f"  {stat['car_color']}: {stat['count']} guest(s)")
        
        # Phone number format verification
        print("\n" + "=" * 60)
        print("Phone Number Format Verification")
        print("=" * 60)
        
        for guest in created_guests:
            if guest.phone:
                # Check if it's a 10-digit American format
                digits = ''.join(c for c in guest.phone if c.isdigit())
                if len(digits) == 10:
                    print(f"✓ {guest.first_name} {guest.last_name}: {guest.phone} (10 digits)")
                else:
                    print(f"⚠ {guest.first_name} {guest.last_name}: {guest.phone} ({len(digits)} digits)")
        
        print("\n" + "=" * 60)
        print("✅ ALL WIZARD TESTS PASSED!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_wizard_with_guest_cars()
    sys.exit(0 if success else 1)
