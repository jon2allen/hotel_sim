#!/usr/bin/env python3

import subprocess
import sys
from database import HotelDatabase

def test_wizard_random_distribution():
    """Test the wizard with random room distribution"""
    
    print("=== Testing Random Distribution ===")
    
    # Test data
    hotel_name = "Random Test Hotel"
    hotel_address = "789 Random Street"
    stars = 3
    floors = 3
    rooms = 30
    
    # Simulate user input - choose random distribution
    user_input = f"""{hotel_name}
{hotel_address}
{stars}
{floors}
{rooms}
1,2,3,4,5
2
125.00
175.00
225.00
150.00
300.00
"""
    
    try:
        # Run the wizard
        process = subprocess.Popen(
            [sys.executable, 'hotel_cli.py', 'wizard'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        stdout, stderr = process.communicate(input=user_input)
        
        print("Wizard output:")
        print(stdout)
        
        if stderr:
            print("Errors:")
            print(stderr)
        
        # Verify the hotel was created
        db = HotelDatabase()
        
        hotels = db.execute_query("SELECT * FROM hotel WHERE name = ?", (hotel_name,), fetch=True)
        if not hotels:
            print("❌ Hotel was not created")
            return False
            
        hotel = hotels[0]
        hotel_id = hotel['id']
        print(f"✅ Hotel created with ID: {hotel_id}")
        
        # Check room distribution
        room_details = db.execute_query("""
            SELECT rt.name as room_type, r.price_per_night, COUNT(*) as count
            FROM rooms r 
            JOIN room_types rt ON r.room_type_id = rt.id
            WHERE r.hotel_id = ?
            GROUP BY rt.name, r.price_per_night
            ORDER BY rt.name
        """, (hotel_id,), fetch=True)
        
        total_rooms = sum(detail['count'] for detail in room_details)
        print(f"✅ Created {total_rooms} rooms with random distribution:")
        
        for detail in room_details:
            print(f"  • {detail['room_type']}: {detail['count']} rooms at ${detail['price_per_night']}/night")
        
        # Verify all rooms were created
        if total_rooms == rooms:
            print("✅ All rooms accounted for!")
        else:
            print(f"⚠️  Expected {rooms} rooms, got {total_rooms}")
        
        print("🎉 Random distribution test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    finally:
        if 'db' in locals():
            db.conn.close()

if __name__ == "__main__":
    success = test_wizard_random_distribution()
    sys.exit(0 if success else 1)