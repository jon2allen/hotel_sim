# Reservation Wizard Documentation

## Overview

The **Reservation Wizard** is an interactive command-line tool for creating and managing hotel reservations in the Hotel Simulator system. It provides a user-friendly interface for hotel staff to quickly create new reservations while ensuring all required information is collected.

## Features

### Required Fields
The reservation wizard enforces the following required fields:

- **Hotel ID**: The ID of the hotel where the reservation is being made
- **Guest Name**: First and last name of the guest (both required)
- **Phone Number**: 10-digit phone number for the guest (required)
- **Reservation Dates**: Check-in and check-out dates (both required)

### Optional Fields
- **Guest Email**: Email address for the guest
- **Guest Address**: Physical address for the guest
- **Room Selection**: Choice from available rooms at the selected hotel

## Installation & Usage

### Prerequisites
- Python 3.7+
- Existing hotel database with at least one hotel created
- Required Python packages (see main project requirements)

### Running the Wizard

#### Command Line Options

```bash
# Run the interactive menu (default)
python3 reservation_wizard.py

# Direct access to create reservation
python3 reservation_wizard.py create

# Direct access to search reservations
python3 reservation_wizard.py search

# Run the main menu
python3 reservation_wizard.py menu
```

#### Interactive Menu

```
RESERVATION WIZARD MENU
============================

1. Create New Reservation
2. Search Reservations
3. Exit
```

## Create Reservation Workflow

### Step 1: Hotel Selection
- Lists all available hotels in the system
- Shows hotel ID, name, and address
- User selects hotel by entering the hotel ID

### Step 2: Guest Information
- **First Name** (required): Guest's first name
- **Last Name** (required): Guest's last name  
- **Phone Number** (required): 10-digit phone number with validation
- **Email Address** (optional): Guest's email address
- **Address** (optional): Guest's physical address

### Step 3: Reservation Dates
- **Check-in Date**: Defaults to today, can be customized
- **Check-out Date**: Defaults to tomorrow, must be after check-in
- Date format: YYYY-MM-DD
- Includes validation for past dates and date order

### Step 4: Room Selection
- Shows available rooms for the selected hotel and dates
- Displays room number, type, and price
- User selects room by number
- Automatically filters out rooms that are already reserved

### Step 5: Confirmation
- Displays complete reservation summary
- Shows estimated total based on room price and nights
- Requires explicit confirmation before creating reservation

## Search Reservations Workflow

### Search Criteria
- **First Name**: Partial match search
- **Last Name**: Partial match search
- **Date**: Check-in date (defaults to today)
- **Hotel ID**: Specific hotel or all hotels (use '*' for all)

### Search Results
- Displays all matching reservations
- Shows reservation ID, guest info, hotel, room, dates, status, and total price
- Results are ordered by date, hotel name, and guest name

## Technical Implementation

### Class Structure

```python
class ReservationWizard:
    def __init__(self, db_path: str = 'hotel.db')
    
    def create_reservation_wizard() -> Optional[Dict]
    def search_reservations_wizard() -> List[Dict]
    def main_menu()
```

### Key Methods

#### `create_reservation_wizard()`
- Interactive reservation creation process
- Validates all required fields
- Creates guest record if not existing
- Creates reservation record with proper relationships
- Returns reservation details or None if cancelled

#### `search_reservations_wizard()`
- Interactive reservation search interface
- Supports partial name matching
- Filters by date and hotel
- Returns list of matching reservations

### Database Integration

The wizard integrates with the existing database schema:

- **hotel**: Hotel information
- **guests**: Guest records
- **rooms**: Room availability and details
- **reservations**: Reservation records
- **room_types**: Room type information

### Validation Logic

1. **Hotel Validation**: Ensures selected hotel exists
2. **Guest Validation**: Requires first name, last name, and phone
3. **Phone Validation**: Validates 10-digit format
4. **Date Validation**: Ensures check-out is after check-in
5. **Room Validation**: Only shows available rooms for selected dates

## Error Handling

### User Cancellation
- Handles `KeyboardInterrupt` (Ctrl+C) gracefully
- Provides clear cancellation messages
- Returns None for cancelled operations

### Data Validation Errors
- Clear error messages for invalid inputs
- Specific validation for dates, numbers, and formats
- Opportunity to correct errors or cancel

### Database Errors
- Comprehensive exception handling
- Detailed error messages with stack traces for debugging
- Graceful failure without crashing

## Example Usage

### Creating a Reservation

```
============================================================
CREATE RESERVATION WIZARD
============================================================

Please enter the reservation information.
(Required fields are marked with *)

============================================================
HOTEL INFORMATION
============================================================
Available Hotels:
  [1] Grand Hotel - 123 Main Street
  [2] Beach Resort

* Hotel ID: 1

============================================================
GUEST INFORMATION
============================================================
* First Name: John
* Last Name: Doe
* Phone Number (10-digit, e.g., 555-123-4567): 555-123-4567
Email Address (optional): john.doe@example.com
Address (optional): 456 Oak Avenue

============================================================
RESERVATION DATES
============================================================
* Check-in Date (YYYY-MM-DD, default today 2024-01-15): 
* Check-out Date (YYYY-MM-DD, default tomorrow 2024-01-16): 

============================================================
ROOM SELECTION
============================================================
Available Rooms at Grand Hotel:
  [1] Room 101 - Standard Room ($129.99/night)
  [2] Room 102 - Deluxe Room ($199.99/night)

* Select room number (1-2): 1

============================================================
RESERVATION SUMMARY
============================================================
Hotel:      Grand Hotel
Guest:      John Doe
Phone:      555-123-4567
Email:      john.doe@example.com
Address:    456 Oak Avenue
Room:       Room 101 (Standard Room)
Price:      $129.99/night
Check-in:   2024-01-15
Check-out:  2024-01-16
Nights:     1
Estimated Total: $129.99
============================================================

* Create this reservation? (y/n): y

✅ Reservation created successfully!
Reservation ID: 101
Guest ID: 50
Confirmation: John Doe at Grand Hotel
Dates: 2024-01-15 to 2024-01-16
```

### Searching Reservations

```
============================================================
SEARCH RESERVATIONS WIZARD
============================================================

Search for existing reservations.
Leave fields blank to skip that search criterion.
Name search uses 'contains' logic (partial matches).
Use '*' for hotel_id to search all hotels.
Date defaults to today if not specified.

SEARCH CRITERIA:
----------------------------------------
First Name (partial match): John
Last Name (partial match): Doe
Date (YYYY-MM-DD, default today 2024-01-15): 
Hotel ID (number or '*' for all): *

============================================================
SEARCH RESULTS
============================================================

✅ Found 1 reservation(s) for 2024-01-15:

[1] Reservation ID: 101
    Guest:      John Doe
    Phone:      555-123-4567
    Hotel:      Grand Hotel (ID: 1)
    Room:       Room 101 (Standard Room)
    Check-in:   2024-01-15
    Check-out:  2024-01-16
    Status:     confirmed
    Total:      $129.99
```

## Integration with Hotel Simulator

The Reservation Wizard integrates seamlessly with the existing Hotel Simulator ecosystem:

- **Hotel CLI**: Can be called from the main CLI or run standalone
- **Database**: Uses the same SQLite database as other components
- **Guest Management**: Creates guest records using the same Guest class
- **Reservation System**: Uses the existing ReservationSystem for consistency

## Best Practices

### Data Entry
- Use consistent date formats (YYYY-MM-DD)
- Validate phone numbers before submission
- Double-check reservation details before confirmation
- Use the search function to verify reservations were created correctly

### Error Recovery
- If a reservation fails, check the error message for details
- Verify that the hotel has available rooms for the selected dates
- Ensure all required fields are properly filled out
- Check that the guest's phone number is valid

### Performance
- The wizard is optimized for quick data entry
- Search results are limited to reasonable numbers
- Database queries are efficient and indexed

## Troubleshooting

### Common Issues

**No hotels available**:
- Solution: Create a hotel using the hotel CLI first

**No available rooms**:
- Solution: Check room availability or select different dates

**Invalid phone number**:
- Solution: Enter a 10-digit phone number

**Date format errors**:
- Solution: Use YYYY-MM-DD format for dates

### Debugging

For detailed error information, run with:
```bash
python3 -v reservation_wizard.py
```

Or check the console output for stack traces when errors occur.

## Future Enhancements

Potential improvements for future versions:

- **Payment Processing**: Add payment collection during reservation
- **Room Preferences**: Allow guests to specify room preferences
- **Special Requests**: Field for special requests or notes
- **Multiple Guests**: Support for multiple guests per reservation
- **Group Bookings**: Handling for group reservations
- **Export Functionality**: Export reservation data to CSV/PDF
- **Email Confirmation**: Send confirmation emails to guests

## Conclusion

The Reservation Wizard provides a comprehensive, user-friendly interface for creating and managing hotel reservations. It enforces data quality through validation while maintaining flexibility for hotel staff to work efficiently. The wizard integrates seamlessly with the existing Hotel Simulator ecosystem and follows established patterns from other wizards in the system.