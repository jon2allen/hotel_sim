#!/usr/bin/env python3
"""
Checkout Wizard
Interactive wizard for processing guest checkouts
"""

import sys
from typing import Optional, List, Dict, Tuple
from hotel_simulator import HotelSimulator, ReservationStatus
from database import HotelDatabase


class CheckoutWizard:
    """Interactive wizard for processing guest checkouts"""
    
    def __init__(self, db_path: str = 'hotel.db'):
        """Initialize the checkout wizard"""
        self.sim = HotelSimulator(db_path)
        self.db = HotelDatabase(db_path)
    
    def find_reservation_by_identification(self) -> Optional[Dict]:
        """Find reservation using minimum identification: name, room number, or hotel ID"""
        print("\n" + "=" * 60)
        print("FIND RESERVATION FOR CHECKOUT")
        print("=" * 60)
        print("\nFind reservation using minimum identification.")
        print("Provide at least one of: name, room number, or hotel ID.\n")
        
        try:
            # Get search criteria
            print("SEARCH CRITERIA:")
            print("-" * 40)
            
            first_name = input("First Name (optional): ").strip()
            last_name = input("Last Name (optional): ").strip()
            room_number = input("Room Number (optional): ").strip()
            hotel_id_input = input("Hotel ID (optional): ").strip()
            
            # Validate that at least one search criterion is provided
            if not (first_name or last_name or room_number or hotel_id_input):
                print("❌ Please provide at least one search criterion!")
                return None
            
            # Parse hotel ID if provided
            hotel_id = None
            if hotel_id_input:
                try:
                    hotel_id = int(hotel_id_input)
                except ValueError:
                    print(f"⚠️  Invalid hotel ID: {hotel_id_input}")
                    # Continue without hotel ID filter
                    hotel_id = None
            
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
                       h.name as hotel_name,
                       rm.room_number,
                       rt.name as room_type
                FROM reservations r
                LEFT JOIN guests g ON r.guest_id = g.id
                LEFT JOIN rooms rm ON r.room_id = rm.id
                LEFT JOIN hotel h ON rm.hotel_id = h.id
                LEFT JOIN room_types rt ON rm.room_type_id = rt.id
                WHERE r.status = 'checked_in'
            """
            
            params = []
            
            # Add name conditions
            if first_name:
                query += " AND g.first_name LIKE ?"
                params.append(f"%{first_name}%")
            
            if last_name:
                query += " AND g.last_name LIKE ?"
                params.append(f"%{last_name}%")
            
            # Add room number condition
            if room_number:
                query += " AND rm.room_number LIKE ?"
                params.append(f"%{room_number}%")
            
            # Add hotel condition
            if hotel_id is not None:
                query += " AND r.hotel_id = ?"
                params.append(hotel_id)
            
            query += " ORDER BY h.name, rm.room_number, g.last_name, g.first_name"
            
            # Execute search
            results = self.db.execute_query(query, tuple(params), fetch=True)
            
            # Display results
            print("\n" + "=" * 60)
            print("SEARCH RESULTS")
            print("=" * 60)
            
            if not results:
                print("\n❌ No checked-in reservations found matching your criteria.")
                return None
            
            print(f"\n✅ Found {len(results)} checked-in reservation(s):")
            
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
                print(f"    Total:      ${reservation['total_price']:.2f}")
            
            # Select reservation for checkout
            print("\n" + "=" * 60)
            print("SELECT RESERVATION FOR CHECKOUT")
            print("=" * 60)
            
            selection = input(f"\nEnter reservation number (1-{len(results)}) or '0' to cancel: ").strip()
            
            if selection == '0':
                print("❌ Checkout cancelled.")
                return None
            
            try:
                reservation_index = int(selection) - 1
                if 0 <= reservation_index < len(results):
                    return results[reservation_index]
                else:
                    print(f"❌ Invalid selection. Please enter a number between 1 and {len(results)}.")
                    return None
            except ValueError:
                print("❌ Invalid input. Please enter a valid number.")
                return None
            
        except KeyboardInterrupt:
            print("\n\n❌ Search cancelled.")
            return None
        except Exception as e:
            print(f"\n❌ Error searching reservations: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def process_checkout(self, reservation: Dict) -> Tuple[bool, float]:
        """Process the checkout for a specific reservation"""
        print("\n" + "=" * 60)
        print("PROCESS CHECKOUT")
        print("=" * 60)
        
        try:
            reservation_id = reservation['reservation_id']
            guest_name = f"{reservation['first_name']} {reservation['last_name']}"
            room_info = f"Room {reservation['room_number']}" if reservation['room_number'] else f"Room ID: {reservation['room_id']}"
            hotel_name = reservation['hotel_name'] if reservation['hotel_name'] else f"Hotel ID: {reservation['hotel_id']}"
            
            print(f"\nProcessing checkout for:")
            print(f"  Guest:      {guest_name}")
            print(f"  Hotel:      {hotel_name}")
            print(f"  Room:       {room_info}")
            print(f"  Check-in:   {reservation['check_in_date']}")
            print(f"  Check-out:  {reservation['check_out_date']}")
            print(f"  Expected Total: ${reservation['total_price']:.2f}")
            
            # Confirm checkout
            confirm = input("\n🔘 Confirm checkout? (y/n): ").strip().lower()
            if confirm != 'y':
                print("❌ Checkout cancelled.")
                return False, 0.0
            
            # Process the checkout
            success, final_amount = self.sim.check_out(reservation_id)
            
            if success:
                print(f"\n✅ Checkout completed successfully!")
                print(f"  Final Amount: ${final_amount:.2f}")
                print(f"  Reservation #{reservation_id} is now checked out")
                
                # Update room status
                self.db.execute_query(
                    "UPDATE rooms SET status = 'available' WHERE id = ?",
                    (reservation['room_id'],)
                )
                
                return True, final_amount
            else:
                print(f"\n❌ Checkout failed for reservation #{reservation_id}")
                return False, 0.0
                
        except Exception as e:
            print(f"\n❌ Error during checkout: {e}")
            import traceback
            traceback.print_exc()
            return False, 0.0
    
    def interactive_checkout(self) -> bool:
        """Complete interactive checkout process"""
        print("\n" + "=" * 60)
        print("INTERACTIVE CHECKOUT WIZARD")
        print("=" * 60)
        
        # Step 1: Find reservation
        reservation = self.find_reservation_by_identification()
        
        if not reservation:
            return False
        
        # Step 2: Process checkout
        success, amount = self.process_checkout(reservation)
        
        return success
    
    def quick_checkout_by_id(self, reservation_id: int) -> Tuple[bool, float]:
        """Quick checkout using reservation ID"""
        print("\n" + "=" * 60)
        print("QUICK CHECKOUT")
        print("=" * 60)
        
        try:
            # Get reservation details
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
                       h.name as hotel_name,
                       rm.room_number,
                       rt.name as room_type
                FROM reservations r
                LEFT JOIN guests g ON r.guest_id = g.id
                LEFT JOIN rooms rm ON r.room_id = rm.id
                LEFT JOIN hotel h ON rm.hotel_id = h.id
                LEFT JOIN room_types rt ON rm.room_type_id = rt.id
                WHERE r.id = ? AND r.status = 'checked_in'
            """
            
            results = self.db.execute_query(query, (reservation_id,), fetch=True)
            
            if not results:
                print(f"❌ No checked-in reservation found with ID {reservation_id}")
                return False, 0.0
            
            reservation = results[0]
            
            # Process checkout
            return self.process_checkout(reservation)
            
        except Exception as e:
            print(f"❌ Error in quick checkout: {e}")
            return False, 0.0
    
    def main_menu(self):
        """Main menu for checkout wizard"""
        while True:
            print("\n" + "=" * 60)
            print("CHECKOUT WIZARD MENU")
            print("=" * 60)
            print("\n1. Interactive Checkout (Search & Checkout)")
            print("2. Quick Checkout by Reservation ID")
            print("3. Exit")
            print()
            
            choice = input("Select an option (1-3): ").strip()
            
            if choice == '1':
                self.interactive_checkout()
            elif choice == '2':
                reservation_id_input = input("Enter Reservation ID: ").strip()
                try:
                    reservation_id = int(reservation_id_input)
                    self.quick_checkout_by_id(reservation_id)
                except ValueError:
                    print("❌ Invalid Reservation ID. Please enter a valid number.")
            elif choice == '3':
                print("\n👋 Goodbye!")
                break
            else:
                print("\n❌ Invalid option. Please select 1, 2, or 3.")


def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        if sys.argv[1] == 'interactive':
            wizard = CheckoutWizard()
            wizard.interactive_checkout()
        elif sys.argv[1] == 'quick':
            if len(sys.argv) > 2:
                wizard = CheckoutWizard()
                try:
                    reservation_id = int(sys.argv[2])
                    wizard.quick_checkout_by_id(reservation_id)
                except ValueError:
                    print("Usage: python3 checkout_wizard.py quick <reservation_id>")
                    print("  reservation_id - The ID of the reservation to check out")
                    sys.exit(1)
            else:
                print("Usage: python3 checkout_wizard.py quick <reservation_id>")
                sys.exit(1)
        elif sys.argv[1] == 'menu':
            wizard = CheckoutWizard()
            wizard.main_menu()
        else:
            print("Usage: python3 checkout_wizard.py [interactive|quick|menu]")
            print("  interactive - Interactive checkout with search")
            print("  quick       - Quick checkout by reservation ID")
            print("  menu        - Show interactive menu")
            sys.exit(1)
    else:
        # Default to main menu
        wizard = CheckoutWizard()
        wizard.main_menu()


if __name__ == "__main__":
    main()