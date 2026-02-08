#!/usr/bin/env python3
"""
Check-in Wizard
Interactive wizard for finding and checking in guests
"""

import sys
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from hotel_simulator import HotelSimulator, ReservationSystem
from database import HotelDatabase


class CheckinWizard:
    """Interactive wizard for guest check-in"""
    
    def __init__(self, db_path: str = 'hotel.db'):
        """Initialize the check-in wizard"""
        self.sim = HotelSimulator(db_path)
        self.db = HotelDatabase(db_path)
        self.res_system = ReservationSystem(self.db)
    
    def search_reservations_wizard(self) -> List[Dict]:
        """Interactive wizard to search for reservations by name, date, and hotel"""
        print("\n" + "=" * 60)
        print("CHECK-IN SEARCH WIZARD")
        print("=" * 60)
        print("\nSearch for reservations to check in guests.")
        print("All fields are optional - leave blank to skip.")
        print("Name search uses 'contains' logic (partial matches).")
        print("Use '*' for hotel_id to search all hotels.")
        print("Date defaults to today if not specified.\n")
        
        try:
            # Get search criteria
            print("SEARCH CRITERIA:")
            print("-" * 40)
            
            first_name = input("First Name (partial match): ").strip()
            last_name = input("Last Name (partial match): ").strip()
            
            date_input = input(f"Date (YYYY-MM-DD, default today {datetime.now().strftime('%Y-%m-%d')}): ").strip()
            
            hotel_input = input("Hotel ID (number or '*' for all): ").strip()
            
            # Parse date - default to today
            if date_input:
                try:
                    search_date = datetime.strptime(date_input, '%Y-%m-%d').date()
                except ValueError:
                    print(f"⚠️  Invalid date format: {date_input}")
                    print(f"📅 Using today's date: {datetime.now().strftime('%Y-%m-%d')}")
                    search_date = datetime.now().date()
            else:
                search_date = datetime.now().date()
            
            # Parse hotel ID
            if hotel_input == '*':
                hotel_id = None  # Search all hotels
            elif hotel_input:
                try:
                    hotel_id = int(hotel_input)
                except ValueError:
                    print(f"⚠️  Invalid hotel ID: {hotel_input}")
                    print("🏨 Searching all hotels instead")
                    hotel_id = None
            else:
                hotel_id = None  # Default to search all hotels
            
            # Build search query
            query = """
                SELECT r.id as reservation_id, 
                       rm.hotel_id as hotel_id, 
                       r.room_id, 
                       r.guest_id, 
                       r.check_in_date, 
                       r.check_out_date, 
                       r.status,
                       g.first_name, 
                       g.last_name,
                       h.name as hotel_name,
                       rm.room_number,
                       rt.name as room_type
                FROM reservations r
                LEFT JOIN guests g ON r.guest_id = g.id
                LEFT JOIN rooms rm ON r.room_id = rm.id
                LEFT JOIN hotel h ON rm.hotel_id = h.id
                LEFT JOIN room_types rt ON rm.room_type_id = rt.id
                WHERE r.status IN ('confirmed', 'checked_in')
            """
            
            params = []
            
            # Add name conditions
            if first_name:
                query += " AND g.first_name LIKE ?"
                params.append(f"%{first_name}%")
            
            if last_name:
                query += " AND g.last_name LIKE ?"
                params.append(f"%{last_name}%")
            
            # Add date condition (check-in date)
            query += " AND r.check_in_date = ?"
            params.append(search_date.strftime('%Y-%m-%d'))
            
            # Add hotel condition
            if hotel_id is not None:
                query += " AND r.hotel_id = ?"
                params.append(hotel_id)
            
            query += " ORDER BY r.check_in_date, h.name, g.last_name, g.first_name"
            
            # Execute search
            results = self.db.execute_query(query, tuple(params), fetch=True)
            
            # Display results
            print("\n" + "=" * 60)
            print("SEARCH RESULTS")
            print("=" * 60)
            
            if not results:
                print(f"\n❌ No reservations found for {search_date.strftime('%Y-%m-%d')}")
                if first_name or last_name:
                    print(f"   matching name criteria")
                if hotel_id is not None:
                    print(f"   in hotel {hotel_id}")
                return []
            
            print(f"\n✅ Found {len(results)} reservation(s) for {search_date.strftime('%Y-%m-%d')}:")
            
            for i, reservation in enumerate(results, 1):
                guest_name = f"{reservation['first_name']} {reservation['last_name']}" if reservation['first_name'] else "(Unknown Guest)"
                hotel_info = f"{reservation['hotel_name']} (ID: {reservation['hotel_id']})" if reservation['hotel_name'] else f"Hotel ID: {reservation['hotel_id']}"
                room_info = f"Room {reservation['room_number']} ({reservation['room_type']})" if reservation['room_number'] else f"Room ID: {reservation['room_id']}"
                
                print(f"\n[{i}] Reservation ID: {reservation['reservation_id']}")
                print(f"    Guest:      {guest_name}")
                print(f"    Hotel:      {hotel_info}")
                print(f"    Room:       {room_info}")
                print(f"    Check-in:   {reservation['check_in_date']}")
                print(f"    Check-out:  {reservation['check_out_date']}")
                print(f"    Status:     {reservation['status']}")
            
            return results
            
        except KeyboardInterrupt:
            print("\n\n❌ Search cancelled.")
            return []
        except Exception as e:
            print(f"\n❌ Error searching reservations: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def check_in_reservation(self, reservation_id: int) -> bool:
        """Check in a specific reservation"""
        try:
            # Get reservation details
            reservation = self.db.get_reservation_by_id(reservation_id)
            
            if not reservation:
                print(f"❌ Reservation {reservation_id} not found!")
                return False
            
            if reservation['status'] == 'checked_in':
                print(f"⚠️  Guest is already checked in!")
                return False
            
            if reservation['status'] != 'confirmed':
                print(f"❌ Cannot check in reservation with status: {reservation['status']}")
                return False
            
            # Perform check-in
            success = self.res_system.check_in(reservation_id)
            
            if success:
                print(f"✅ Successfully checked in reservation {reservation_id}")
                
                # Get guest and room details for confirmation
                guest = self.db.get_guest_by_id(reservation['guest_id'])
                room = self.db.get_room_by_id(reservation['room_id'])
                hotel = self.db.get_hotel_info(reservation['hotel_id'])
                
                guest_name = f"{guest['first_name']} {guest['last_name']}" if guest else "Unknown Guest"
                room_info = f"Room {room['room_number']}" if room else f"Room ID: {reservation['room_id']}"
                hotel_name = hotel['name'] if hotel else f"Hotel ID: {reservation['hotel_id']}"
                
                print(f"\n📋 CHECK-IN CONFIRMATION:")
                print(f"   Guest:      {guest_name}")
                print(f"   Hotel:      {hotel_name}")
                print(f"   Room:       {room_info}")
                print(f"   Check-in:   {reservation['check_in_date']}")
                print(f"   Check-out:  {reservation['check_out_date']}")
                
                return True
            else:
                print(f"❌ Failed to check in reservation {reservation_id}")
                return False
                
        except Exception as e:
            print(f"❌ Error during check-in: {e}")
            return False
    
    def interactive_check_in(self):
        """Interactive check-in process"""
        print("\n" + "=" * 60)
        print("INTERACTIVE CHECK-IN")
        print("=" * 60)
        
        # Step 1: Search for reservations
        reservations = self.search_reservations_wizard()
        
        if not reservations:
            print("\n❌ No reservations available for check-in.")
            return False
        
        # Step 2: Select reservation to check in
        print("\n" + "=" * 60)
        print("SELECT RESERVATION TO CHECK IN")
        print("=" * 60)
        
        try:
            selection = input(f"\nEnter reservation number (1-{len(reservations)}) or '0' to cancel: ").strip()
            
            if selection == '0':
                print("❌ Check-in cancelled.")
                return False
            
            try:
                reservation_index = int(selection) - 1
                if 0 <= reservation_index < len(reservations):
                    selected_reservation = reservations[reservation_index]
                    
                    # Confirm check-in
                    guest_name = f"{selected_reservation['first_name']} {selected_reservation['last_name']}"
                    confirm = input(f"\n🔘 Confirm check-in for {guest_name}? (y/n): ").strip().lower()
                    
                    if confirm == 'y':
                        return self.check_in_reservation(selected_reservation['reservation_id'])
                    else:
                        print("❌ Check-in cancelled.")
                        return False
                else:
                    print(f"❌ Invalid selection. Please enter a number between 1 and {len(reservations)}.")
                    return False
                    
            except ValueError:
                print("❌ Invalid input. Please enter a valid number.")
                return False
                
        except KeyboardInterrupt:
            print("\n\n❌ Check-in cancelled.")
            return False
        except Exception as e:
            print(f"\n❌ Error during check-in: {e}")
            return False
    
    def main_menu(self):
        """Main menu for check-in wizard"""
        while True:
            print("\n" + "=" * 60)
            print("CHECK-IN WIZARD MENU")
            print("=" * 60)
            print("\n1. Search Reservations")
            print("2. Interactive Check-In")
            print("3. Exit")
            print()
            
            choice = input("Select an option (1-3): ").strip()
            
            if choice == '1':
                self.search_reservations_wizard()
            elif choice == '2':
                self.interactive_check_in()
            elif choice == '3':
                print("\n👋 Goodbye!")
                break
            else:
                print("\n❌ Invalid option. Please select 1, 2, or 3.")


def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        if sys.argv[1] == 'search':
            wizard = CheckinWizard()
            wizard.search_reservations_wizard()
        elif sys.argv[1] == 'checkin':
            wizard = CheckinWizard()
            wizard.interactive_check_in()
        elif sys.argv[1] == 'menu':
            wizard = CheckinWizard()
            wizard.main_menu()
        else:
            print("Usage: python3 checkin_wizard.py [search|checkin|menu]")
            print("  search   - Search for reservations")
            print("  checkin  - Interactive check-in process")
            print("  menu     - Show interactive menu")
            sys.exit(1)
    else:
        # Default to main menu
        wizard = CheckinWizard()
        wizard.main_menu()


if __name__ == "__main__":
    main()