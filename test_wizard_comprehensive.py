#!/usr/bin/env python3

import subprocess
import sys
from database import HotelDatabase

def test_wizard_comprehensive():
    """Comprehensive test of the hotel creation wizard"""
    
    print("=== Comprehensive Hotel Wizard Test ===")
    
    # Test data
    hotel_name = "Test Wizard Hotel"
    hotel_address = "456 Test Avenue"
    stars = 4
    floors = 5
    rooms = 20
    
    # Simulate user input
    user_input = f"""{hotel_name}
{hotel_address}
{stars}
{floors}
{rooms}
1,2
1
10
10
150.00
200.00
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
        
        # Verify the hotel was created correctly
        db = HotelDatabase()
        
        # Find the hotel
        hotels = db.execute_query("SELECT * FROM hotel WHERE name = ?", (hotel_name,), fetch=True)
        if not hotels:
            print("❌ Hotel was not created")
            return False
            
        hotel = hotels[0]
        hotel_id = hotel['id']
        print(f"✅ Hotel created with ID: {hotel_id}")
        
        # Verify hotel details
        assert hotel['address'] == hotel_address, f"Address mismatch: {hotel['address']} != {hotel_address}"
        assert hotel['stars'] == stars, f"Stars mismatch: {hotel['stars']} != {stars}"
        assert hotel['total_floors'] == floors, f"Floors mismatch: {hotel['total_floors']} != {floors}"
        assert hotel['total_rooms'] == rooms, f"Rooms mismatch: {hotel['total_rooms']} != {rooms}"
        print("✅ Hotel details are correct")
        
        # Verify floors were created
        floor_count = db.execute_query("SELECT COUNT(*) as count FROM floors WHERE hotel_id = ?", (hotel_id,), fetch=True)[0]['count']
        assert floor_count == floors, f"Floor count mismatch: {floor_count} != {floors}"
        print(f"✅ {floor_count} floors created")
        
        # Verify rooms were created
        room_count = db.execute_query("SELECT COUNT(*) as count FROM rooms WHERE hotel_id = ?", (hotel_id,), fetch=True)[0]['count']
        assert room_count == rooms, f"Room count mismatch: {room_count} != {rooms}"
        print(f"✅ {room_count} rooms created")
        
        # Check room types and prices
        room_details = db.execute_query("""
            SELECT rt.name as room_type, r.price_per_night, COUNT(*) as count
            FROM rooms r 
            JOIN room_types rt ON r.room_type_id = rt.id
            WHERE r.hotel_id = ?
            GROUP BY rt.name, r.price_per_night
        """, (hotel_id,), fetch=True)
        
        print("✅ Room type distribution:")
        for detail in room_details:
            print(f"  • {detail['room_type']}: {detail['count']} rooms at ${detail['price_per_night']}/night")
        
        print("🎉 All tests passed! Hotel creation wizard is working correctly.")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    finally:
        if 'db' in locals():
            db.conn.close()

if __name__ == "__main__":
    success = test_wizard_comprehensive()
    sys.exit(0 if success else 1)