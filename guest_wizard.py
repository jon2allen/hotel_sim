#!/usr/bin/env python3
"""
Guest Management Wizards
Interactive wizards for adding and searching guests
"""

import sys
from typing import Optional, List, Dict
from hotel_simulator import HotelSimulator, Guest
from database import HotelDatabase


class GuestWizard:
    """Interactive wizards for guest management"""
    
    def __init__(self, db_path: str = 'hotel.db'):
        """Initialize the guest wizard"""
        self.sim = HotelSimulator(db_path)
        self.db = HotelDatabase(db_path)
    
    def add_guest_wizard(self) -> Optional[Guest]:
        """Interactive wizard to add a new guest"""
        print("\n" + "=" * 60)
        print("ADD GUEST WIZARD")
        print("=" * 60)
        print("\nPlease enter the guest information.")
        print("(Press Enter to skip optional fields)\n")
        
        try:
            # Required fields
            print("REQUIRED INFORMATION:")
            print("-" * 40)
            
            first_name = input("First Name: ").strip()
            if not first_name:
                print("❌ First name is required!")
                return None
            
            last_name = input("Last Name: ").strip()
            if not last_name:
                print("❌ Last name is required!")
                return None
            
            # Optional contact information
            print("\nCONTACT INFORMATION (Optional):")
            print("-" * 40)
            
            email = input("Email Address: ").strip()
            
            phone = input("Cell Phone (10-digit, e.g., 555-123-4567): ").strip()
            if phone:
                # Validate 10-digit format
                digits = ''.join(c for c in phone if c.isdigit())
                if len(digits) != 10:
                    print(f"⚠️  Warning: Phone should be 10 digits (got {len(digits)})")
                    confirm = input("Continue anyway? (y/n): ").strip().lower()
                    if confirm != 'y':
                        return None
            
            # Address information
            print("\nADDRESS INFORMATION (Optional):")
            print("-" * 40)
            print("Format: Street, City, State ZIP")
            print("Example: 123 Main Street, Anytown, CA 90210")
            
            address = input("Full Address: ").strip()
            
            # Vehicle information
            print("\nVEHICLE INFORMATION (Optional):")
            print("-" * 40)
            print("Enter vehicle details or 'N/A' if no vehicle")
            
            car_make = input("Car Make (e.g., Toyota, Honda): ").strip()
            car_model = input("Car Model (e.g., Camry, Accord): ").strip()
            car_color = input("Car Color (e.g., Blue, Red): ").strip()
            
            # Confirmation
            print("\n" + "=" * 60)
            print("GUEST INFORMATION SUMMARY")
            print("=" * 60)
            print(f"Name:     {first_name} {last_name}")
            print(f"Email:    {email if email else '(not provided)'}")
            print(f"Phone:    {phone if phone else '(not provided)'}")
            print(f"Address:  {address if address else '(not provided)'}")
            
            if car_make or car_model or car_color:
                vehicle = f"{car_color} {car_make} {car_model}".strip()
                print(f"Vehicle:  {vehicle if vehicle else '(not provided)'}")
            else:
                print(f"Vehicle:  (not provided)")
            
            print("=" * 60)
            
            confirm = input("\nCreate this guest? (y/n): ").strip().lower()
            if confirm != 'y':
                print("❌ Guest creation cancelled.")
                return None
            
            # Create the guest
            guest = self.sim.create_guest(
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                address=address,
                car_make=car_make,
                car_model=car_model,
                car_color=car_color
            )
            
            print("\n✅ Guest created successfully!")
            print(f"Guest ID: {guest.id}")
            print(f"Name: {guest.first_name} {guest.last_name}")
            
            return guest
            
        except KeyboardInterrupt:
            print("\n\n❌ Guest creation cancelled.")
            return None
        except Exception as e:
            print(f"\n❌ Error creating guest: {e}")
            return None
    
    def search_guest_wizard(self) -> List[Dict]:
        """Interactive wizard to search for guests"""
        print("\n" + "=" * 60)
        print("SEARCH GUEST WIZARD")
        print("=" * 60)
        print("\nSearch for guests using any combination of criteria.")
        print("Leave fields blank to skip that search criterion.")
        print("Search uses 'contains' logic (partial matches).\n")
        
        try:
            # Get search criteria
            print("SEARCH CRITERIA:")
            print("-" * 40)
            
            first_name = input("First Name (partial match): ").strip()
            last_name = input("Last Name (partial match): ").strip()
            email = input("Email (partial match): ").strip()
            phone = input("Phone (partial match): ").strip()
            address = input("Address (partial match): ").strip()
            car_make = input("Car Make (partial match): ").strip()
            car_model = input("Car Model (partial match): ").strip()
            car_color = input("Car Color (partial match): ").strip()
            
            # Build search query
            conditions = []
            params = []
            
            if first_name:
                conditions.append("first_name LIKE ?")
                params.append(f"%{first_name}%")
            
            if last_name:
                conditions.append("last_name LIKE ?")
                params.append(f"%{last_name}%")
            
            if email:
                conditions.append("email LIKE ?")
                params.append(f"%{email}%")
            
            if phone:
                conditions.append("phone LIKE ?")
                params.append(f"%{phone}%")
            
            if address:
                conditions.append("address LIKE ?")
                params.append(f"%{address}%")
            
            if car_make:
                conditions.append("car_make LIKE ?")
                params.append(f"%{car_make}%")
            
            if car_model:
                conditions.append("car_model LIKE ?")
                params.append(f"%{car_model}%")
            
            if car_color:
                conditions.append("car_color LIKE ?")
                params.append(f"%{car_color}%")
            
            if not conditions:
                print("\n⚠️  No search criteria provided. Showing all guests (limited to 50).")
                query = "SELECT * FROM guests ORDER BY last_name, first_name LIMIT 50"
                params = []
            else:
                where_clause = " AND ".join(conditions)
                query = f"SELECT * FROM guests WHERE {where_clause} ORDER BY last_name, first_name LIMIT 50"
            
            # Execute search
            results = self.db.execute_query(query, tuple(params), fetch=True)
            
            # Display results
            print("\n" + "=" * 60)
            print("SEARCH RESULTS")
            print("=" * 60)
            
            if not results:
                print("\n❌ No guests found matching your criteria.")
                return []
            
            print(f"\n✅ Found {len(results)} guest(s):\n")
            
            for i, guest in enumerate(results, 1):
                print(f"[{i}] {guest['first_name']} {guest['last_name']} (ID: {guest['id']})")
                print(f"    Email:   {guest['email'] if guest['email'] else '(none)'}")
                print(f"    Phone:   {guest['phone'] if guest['phone'] else '(none)'}")
                print(f"    Address: {guest['address'] if guest['address'] else '(none)'}")
                
                if guest['car_make'] and guest['car_make'] != 'N/A':
                    vehicle = f"{guest['car_color']} {guest['car_make']} {guest['car_model']}".strip()
                    print(f"    Vehicle: {vehicle}")
                elif guest['car_make'] == 'N/A':
                    print(f"    Vehicle: N/A")
                else:
                    print(f"    Vehicle: (none)")
                print()
            
            if len(results) == 50:
                print("⚠️  Results limited to 50. Refine your search for more specific results.")
            
            return results
            
        except KeyboardInterrupt:
            print("\n\n❌ Search cancelled.")
            return []
        except Exception as e:
            print(f"\n❌ Error searching guests: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def main_menu(self):
        """Main menu for guest wizards"""
        while True:
            print("\n" + "=" * 60)
            print("GUEST MANAGEMENT WIZARDS")
            print("=" * 60)
            print("\n1. Add New Guest")
            print("2. Search for Guests")
            print("3. Exit")
            print()
            
            choice = input("Select an option (1-3): ").strip()
            
            if choice == '1':
                self.add_guest_wizard()
            elif choice == '2':
                self.search_guest_wizard()
            elif choice == '3':
                print("\n👋 Goodbye!")
                break
            else:
                print("\n❌ Invalid option. Please select 1, 2, or 3.")


def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        if sys.argv[1] == 'add':
            wizard = GuestWizard()
            wizard.add_guest_wizard()
        elif sys.argv[1] == 'search':
            wizard = GuestWizard()
            wizard.search_guest_wizard()
        elif sys.argv[1] == 'menu':
            wizard = GuestWizard()
            wizard.main_menu()
        else:
            print("Usage: python3 guest_wizard.py [add|search|menu]")
            print("  add    - Run the add guest wizard")
            print("  search - Run the search guest wizard")
            print("  menu   - Show interactive menu")
            sys.exit(1)
    else:
        # Default to main menu
        wizard = GuestWizard()
        wizard.main_menu()


if __name__ == "__main__":
    main()
