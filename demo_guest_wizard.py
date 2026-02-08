#!/usr/bin/env python3
"""
Guest Wizard Demonstration
Shows examples of using the add and search wizards
"""

from guest_wizard import GuestWizard


def demo_add_guest():
    """Demonstrate adding a guest"""
    print("\n" + "=" * 70)
    print("DEMONSTRATION: ADD GUEST WIZARD")
    print("=" * 70)
    print("\nThis wizard will guide you through adding a new guest.")
    print("You'll be prompted for:")
    print("  • Name (required)")
    print("  • Email (optional)")
    print("  • Cell phone - 10 digits (optional)")
    print("  • Full address with City, State, ZIP (optional)")
    print("  • Vehicle information (optional)")
    print("\nLet's try it!\n")
    
    input("Press Enter to start the Add Guest Wizard...")
    
    wizard = GuestWizard()
    guest = wizard.add_guest_wizard()
    
    if guest:
        print("\n" + "🎉" * 35)
        print(f"SUCCESS! Guest '{guest.first_name} {guest.last_name}' has been added to the system.")
        print("🎉" * 35)
    else:
        print("\nGuest was not added.")


def demo_search_guest():
    """Demonstrate searching for guests"""
    print("\n" + "=" * 70)
    print("DEMONSTRATION: SEARCH GUEST WIZARD")
    print("=" * 70)
    print("\nThis wizard will help you find guests using partial matches.")
    print("You can search by:")
    print("  • Name (first or last)")
    print("  • Email")
    print("  • Phone number")
    print("  • Address")
    print("  • Vehicle information (make, model, color)")
    print("\nAll searches use 'contains' logic - partial matches work!")
    print("For example, searching for 'John' will find 'Johnson', 'Johnny', etc.")
    print("\nLet's try it!\n")
    
    input("Press Enter to start the Search Guest Wizard...")
    
    wizard = GuestWizard()
    results = wizard.search_guest_wizard()
    
    if results:
        print("\n" + "🎉" * 35)
        print(f"SEARCH COMPLETE! Found {len(results)} guest(s).")
        print("🎉" * 35)
    else:
        print("\nNo guests found or search was cancelled.")


def main():
    """Main demonstration menu"""
    while True:
        print("\n" + "=" * 70)
        print("GUEST WIZARD DEMONSTRATION")
        print("=" * 70)
        print("\n1. Demo: Add Guest Wizard")
        print("2. Demo: Search Guest Wizard")
        print("3. Run Interactive Menu (Full System)")
        print("4. Exit")
        print()
        
        choice = input("Select an option (1-4): ").strip()
        
        if choice == '1':
            demo_add_guest()
        elif choice == '2':
            demo_search_guest()
        elif choice == '3':
            wizard = GuestWizard()
            wizard.main_menu()
        elif choice == '4':
            print("\n👋 Goodbye!")
            break
        else:
            print("\n❌ Invalid option. Please select 1-4.")


if __name__ == "__main__":
    main()
