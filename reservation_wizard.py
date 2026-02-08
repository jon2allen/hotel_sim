#!/usr/bin/env python3
"""
Reservation Wizard
Interactive wizard for creating new hotel reservations
"""

import sys
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from hotel_simulator import HotelSimulator, ReservationSystem, Guest
from database import HotelDatabase


class ReservationWizard:
    """Interactive wizard for creating hotel reservations"""
    
    def __init__(self, db_path: str = 'hotel.db'):
        """Initialize the reservation wizard"""
        self.sim = HotelSimulator(db_path)
        self.db = HotelDatabase(db_path)
        self.res_system = ReservationSystem(self.db)
    
    def create_reservation_wizard(self) -> Optional[Dict]:
        """Interactive wizard to create a new reservation"""
        print("\n" + "=" * 60)
        print("CREATE RESERVATION WIZARD")
        print("=" * 60)
        print("\nPlease enter the reservation information.")
        print("(Required fields are marked with *)")
        
        try:
            # Step 1: Hotel Selection
            print("\n" + "=" * 60)
            print("HOTEL INFORMATION")
            print("=" * 60)
            
            # List available hotels
            hotels = self.db.execute_query("SELECT id, name, address FROM hotel ORDER BY name", fetch=True)
            
            if not hotels:
                print("❌ No hotels available in the system!")
                print("Please create a hotel first using the hotel CLI.")
                return None
            
            print("Available Hotels:")
            for hotel in hotels:
                address_display = f" - {hotel['address']}" if hotel['address'] else ""
                print(f"  [{hotel['id']}] {hotel['name']}{address_display}")
            
            hotel_id_input = input("\n* Hotel ID: ").strip()
            if not hotel_id_input:
                print("❌ Hotel ID is required!")
                return None
            
            try:
                hotel_id = int(hotel_id_input)
                # Verify hotel exists
                hotel = self.db.get_hotel_info(hotel_id)
                if not hotel:
                    print(f"❌ Hotel with ID {hotel_id} not found!")
                    return None
            except ValueError:
                print("❌ Invalid hotel ID. Please enter a valid number.")
                return None
            
            # Step 2: Guest Information
            print("\n" + "=" * 60)
            print("GUEST INFORMATION")
            print("=" * 60)
            
            first_name = input("* First Name: ").strip()
            if not first_name:
                print("❌ First name is required!")
                return None
            
            last_name = input("* Last Name: ").strip()
            if not last_name:
                print("❌ Last name is required!")
                return None
            
            phone = input("* Phone Number (10-digit, e.g., 555-123-4567): ").strip()
            if not phone:
                print("❌ Phone number is required!")
                return None
            
            # Validate phone format
            digits = ''.join(c for c in phone if c.isdigit())
            if len(digits) != 10:
                print(f"⚠️  Warning: Phone should be 10 digits (got {len(digits)})")
                confirm = input("Continue anyway? (y/n): ").strip().lower()
                if confirm != 'y':
                    return None
            
            # Optional guest information
            email = input("Email Address (optional): ").strip()
            address = input("Address (optional): ").strip()
            
            # Step 3: Reservation Dates
            print("\n" + "=" * 60)
            print("RESERVATION DATES")
            print("=" * 60)
            
            today = datetime.now().date()
            tomorrow = today + timedelta(days=1)
            
            check_in_input = input(f"* Check-in Date (YYYY-MM-DD, default today {today}): ").strip()
            if check_in_input:
                try:
                    check_in_date = datetime.strptime(check_in_input, '%Y-%m-%d').date()
                    if check_in_date < today:
                        print("⚠️  Warning: Check-in date is in the past!")
                        confirm = input("Continue anyway? (y/n): ").strip().lower()
                        if confirm != 'y':
                            return None
                except ValueError:
                    print(f"❌ Invalid date format: {check_in_input}")
                    print("Please use YYYY-MM-DD format.")
                    return None
            else:
                check_in_date = today
            
            check_out_input = input(f"* Check-out Date (YYYY-MM-DD, default tomorrow {tomorrow}): ").strip()
            if check_out_input:
                try:
                    check_out_date = datetime.strptime(check_out_input, '%Y-%m-%d').date()
                    if check_out_date <= check_in_date:
                        print("❌ Check-out date must be after check-in date!")
                        return None
                except ValueError:
                    print(f"❌ Invalid date format: {check_out_input}")
                    print("Please use YYYY-MM-DD format.")
                    return None
            else:
                check_out_date = tomorrow
            
            # Step 4: Room Selection
            print("\n" + "=" * 60)
            print("ROOM SELECTION")
            print("=" * 60)
            
            # Find available rooms for the selected hotel and dates
            available_rooms = self.db.execute_query("""
                SELECT r.id, r.room_number, rt.name as room_type, rt.base_price, r.price_per_night
                FROM rooms r
                LEFT JOIN room_types rt ON r.room_type_id = rt.id
                WHERE r.hotel_id = ?
                AND r.status = 'available'
                AND r.id NOT IN (
                    SELECT room_id FROM reservations 
                    WHERE (check_in_date <= ? AND check_out_date >= ?)
                    AND status IN ('confirmed', 'checked_in')
                )
                ORDER BY r.room_number
            """, (hotel_id, check_out_date.strftime('%Y-%m-%d'), check_in_date.strftime('%Y-%m-%d')), fetch=True)
            
            if not available_rooms:
                print(f"❌ No available rooms found for {hotel['name']} from {check_in_date} to {check_out_date}")
                return None
            
            print(f"Available Rooms at {hotel['name']}:")
            for i, room in enumerate(available_rooms, 1):
                price = room['price_per_night'] if room['price_per_night'] else room['base_price']
                print(f"  [{i}] Room {room['room_number']} - {room['room_type']} (${price:.2f}/night)")
            
            room_choice = input(f"\n* Select room number (1-{len(available_rooms)}): ").strip()
            if not room_choice:
                print("❌ Room selection is required!")
                return None
            
            try:
                room_index = int(room_choice) - 1
                if 0 <= room_index < len(available_rooms):
                    selected_room = available_rooms[room_index]
                else:
                    print(f"❌ Invalid room selection. Please enter a number between 1 and {len(available_rooms)}.")
                    return None
            except ValueError:
                print("❌ Invalid input. Please enter a valid number.")
                return None
            
            # Step 5: Confirmation
            print("\n" + "=" * 60)
            print("RESERVATION SUMMARY")
            print("=" * 60)
            
            guest_name = f"{first_name} {last_name}"
            room_info = f"Room {selected_room['room_number']} ({selected_room['room_type']})"
            price_per_night = selected_room['price_per_night'] if selected_room['price_per_night'] else selected_room['base_price']
            nights = (check_out_date - check_in_date).days
            estimated_total = price_per_night * nights
            
            print(f"Hotel:      {hotel['name']}")
            print(f"Guest:      {guest_name}")
            print(f"Phone:      {phone}")
            if email:
                print(f"Email:      {email}")
            if address:
                print(f"Address:    {address}")
            print(f"Room:       {room_info}")
            print(f"Price:      ${price_per_night:.2f}/night")
            print(f"Check-in:   {check_in_date.strftime('%Y-%m-%d')}")
            print(f"Check-out:  {check_out_date.strftime('%Y-%m-%d')}")
            print(f"Nights:     {nights}")
            print(f"Estimated Total: ${estimated_total:.2f}")
            
            print("=" * 60)
            
            confirm = input("\n* Create this reservation? (y/n): ").strip().lower()
            if confirm != 'y':
                print("❌ Reservation creation cancelled.")
                return None
            
            # Create the guest first
            guest = self.sim.create_guest(
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                address=address
            )
            
            # Get the room object
            room = self.sim.get_room_by_id(selected_room['id'])
            
            # Create the reservation
            reservation = self.res_system.create_reservation(
                hotel_sim=self.sim,
                guest=guest,
                room=room,
                check_in=check_in_date.strftime('%Y-%m-%d'),
                check_out=check_out_date.strftime('%Y-%m-%d')
            )
            
            print("\n✅ Reservation created successfully!")
            print(f"Reservation ID: {reservation.id}")
            print(f"Guest ID: {guest.id}")
            print(f"Confirmation: {guest_name} at {hotel['name']}")
            print(f"Dates: {check_in_date.strftime('%Y-%m-%d')} to {check_out_date.strftime('%Y-%m-%d')}")
            
            return {
                'reservation_id': reservation.id,
                'guest_id': guest.id,
                'hotel_id': hotel_id,
                'room_id': room.id,
                'check_in': check_in_date.strftime('%Y-%m-%d'),
                'check_out': check_out_date.strftime('%Y-%m-%d'),
                'total_price': reservation.total_price
            }
            
        except KeyboardInterrupt:
            print("\n\n❌ Reservation creation cancelled.")
            return None
        except Exception as e:
            print(f"\n❌ Error creating reservation: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def search_reservations_wizard(self) -> List[Dict]:
        """Interactive wizard to search for existing reservations"""
        print("\n" + "=" * 60)
        print("SEARCH RESERVATIONS WIZARD")
        print("=" * 60)
        print("\nSearch for existing reservations.")
        print("Leave fields blank to skip that search criterion.")
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
                       r.hotel_id, 
                       r.room_id, 
                       r.guest_id, 
                       r.check_in_date, 
                       r.check_out_date, 
                       r.status,
                       r.total_price,
                       g.first_name, 
                       g.last_name,
                       g.phone,
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
                print(f"    Phone:      {reservation['phone']}")
                print(f"    Hotel:      {hotel_info}")
                print(f"    Room:       {room_info}")
                print(f"    Check-in:   {reservation['check_in_date']}")
                print(f"    Check-out:  {reservation['check_out_date']}")
                print(f"    Status:     {reservation['status']}")
                print(f"    Total:      ${reservation['total_price']:.2f}")
            
            return results
            
        except KeyboardInterrupt:
            print("\n\n❌ Search cancelled.")
            return []
        except Exception as e:
            print(f"\n❌ Error searching reservations: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def main_menu(self):
        """Main menu for reservation wizard"""
        while True:
            print("\n" + "=" * 60)
            print("RESERVATION WIZARD MENU")
            print("=" * 60)
            print("\n1. Create New Reservation")
            print("2. Search Reservations")
            print("3. Exit")
            print()
            
            choice = input("Select an option (1-3): ").strip()
            
            if choice == '1':
                self.create_reservation_wizard()
            elif choice == '2':
                self.search_reservations_wizard()
            elif choice == '3':
                print("\n👋 Goodbye!")
                break
            else:
                print("\n❌ Invalid option. Please select 1, 2, or 3.")


def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        if sys.argv[1] == 'create':
            wizard = ReservationWizard()
            wizard.create_reservation_wizard()
        elif sys.argv[1] == 'search':
            wizard = ReservationWizard()
            wizard.search_reservations_wizard()
        elif sys.argv[1] == 'menu':
            wizard = ReservationWizard()
            wizard.main_menu()
        else:
            print("Usage: python3 reservation_wizard.py [create|search|menu]")
            print("  create  - Run the create reservation wizard")
            print("  search  - Run the search reservations wizard")
            print("  menu    - Show interactive menu")
            sys.exit(1)
    else:
        # Default to main menu
        wizard = ReservationWizard()
        wizard.main_menu()


if __name__ == "__main__":
    main()