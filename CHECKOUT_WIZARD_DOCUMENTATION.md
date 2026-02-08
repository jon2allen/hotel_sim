# Checkout Wizard Documentation

## Overview

The **Checkout Wizard** is a streamlined command-line tool for processing guest checkouts in the Hotel Simulator system. It provides a minimalist yet powerful interface that allows hotel staff to quickly find and checkout guests using the minimum identification required: name, room number, or hotel ID.

## Features

### Minimum Identification Requirements
The checkout wizard supports finding reservations using any combination of:

- **Name** (first name, last name, or both)
- **Room Number** (partial or full room number)
- **Hotel ID** (specific hotel identifier)

**Key Design Principle**: At least one identification criterion must be provided, but users can choose the most convenient method for their workflow.

### Checkout Modes

1. **Interactive Checkout**: Search for reservations and process checkout
2. **Quick Checkout**: Direct checkout using reservation ID
3. **Menu System**: Interactive menu for easy navigation

## Installation & Usage

### Prerequisites
- Python 3.7+
- Existing hotel database with checked-in reservations
- Required Python packages (see main project requirements)

### Running the Wizard

#### Command Line Options

```bash
# Run the interactive menu (default)
python3 checkout_wizard.py

# Interactive checkout with search
python3 checkout_wizard.py interactive

# Quick checkout by reservation ID
python3 checkout_wizard.py quick <reservation_id>

# Run the main menu
python3 checkout_wizard.py menu
```

#### Interactive Menu

```
CHECKOUT WIZARD MENU
============================

1. Interactive Checkout (Search & Checkout)
2. Quick Checkout by Reservation ID
3. Exit
```

## Interactive Checkout Workflow

### Step 1: Find Reservation
- **First Name**: Optional guest first name (partial match)
- **Last Name**: Optional guest last name (partial match)
- **Room Number**: Optional room number (partial match)
- **Hotel ID**: Optional hotel identifier

**Validation**: At least one search criterion must be provided

### Step 2: Select Reservation
- Displays all matching checked-in reservations
- Shows guest name, hotel, room, dates, status, and total
- User selects reservation by number

### Step 3: Process Checkout
- Displays reservation details for confirmation
- Requires explicit confirmation before processing
- Processes checkout and updates database
- Updates room status to available

## Quick Checkout Workflow

### Direct Checkout by Reservation ID
```bash
python3 checkout_wizard.py quick 123
```

- Validates reservation exists and is checked-in
- Displays reservation details
- Processes checkout with confirmation
- Returns success/failure status

## Technical Implementation

### Class Structure

```python
class CheckoutWizard:
    def __init__(self, db_path: str = 'hotel.db')
    
    def find_reservation_by_identification() -> Optional[Dict]
    def process_checkout(reservation: Dict) -> Tuple[bool, float]
    def interactive_checkout() -> bool
    def quick_checkout_by_id(reservation_id: int) -> Tuple[bool, float]
    def main_menu()
```

### Key Methods

#### `find_reservation_by_identification()`
- Interactive reservation search interface
- Supports partial matching on name, room number, and hotel ID
- Requires at least one search criterion
- Returns selected reservation or None if cancelled

#### `process_checkout(reservation: Dict)`
- Processes checkout for a specific reservation
- Displays confirmation before processing
- Updates reservation status to 'checked_out'
- Updates room status to 'available'
- Creates payment transaction
- Returns (success: bool, final_amount: float)

#### `interactive_checkout()`
- Complete interactive checkout process
- Combines search and checkout steps
- Handles user cancellation gracefully

#### `quick_checkout_by_id(reservation_id: int)`
- Direct checkout using reservation ID
- Validates reservation exists and is checked-in
- Processes checkout with minimal interaction

### Database Integration

The wizard integrates with the existing database schema:

- **reservations**: Updates status to 'checked_out'
- **rooms**: Updates status to 'available'
- **transactions**: Creates payment transaction
- **guests**: Reference for guest information
- **hotel**: Reference for hotel information

### Validation Logic

1. **Search Validation**: Ensures at least one criterion provided
2. **Reservation Validation**: Only shows checked-in reservations
3. **Checkout Validation**: Prevents duplicate checkouts
4. **Confirmation**: Requires explicit user confirmation

## Error Handling

### User Cancellation
- Handles `KeyboardInterrupt` (Ctrl+C) gracefully
- Provides clear cancellation messages
- Returns None for cancelled operations

### Data Validation Errors
- Clear error messages for invalid inputs
- Specific validation for reservation existence
- Opportunity to correct errors or cancel

### Database Errors
- Comprehensive exception handling
- Transaction rollback on failure
- Detailed error messages for debugging

## Example Usage

### Interactive Checkout

```
============================================================
INTERACTIVE CHECKOUT WIZARD
============================================================

============================================================
FIND RESERVATION FOR CHECKOUT
============================================================

Find reservation using minimum identification.
Provide at least one of: name, room number, or hotel ID.

SEARCH CRITERIA:
----------------------------------------
First Name (optional): John
Last Name (optional): Doe
Room Number (optional): 
Hotel ID (optional): 

============================================================
SEARCH RESULTS
============================================================

✅ Found 1 checked-in reservation(s):

[1] Reservation ID: 101
    Guest:      John Doe
    Hotel:      Grand Hotel (ID: 1)
    Room:       Room 101 (Standard Room)
    Check-in:   2024-01-15
    Check-out:  2024-01-18
    Status:     checked_in
    Total:      $389.97

============================================================
SELECT RESERVATION FOR CHECKOUT
============================================================

Enter reservation number (1-1) or '0' to cancel: 1

============================================================
PROCESS CHECKOUT
============================================================

Processing checkout for:
  Guest:      John Doe
  Hotel:      Grand Hotel
  Room:       Room 101
  Check-in:   2024-01-15
  Check-out:  2024-01-18
  Expected Total: $389.97

🔘 Confirm checkout? (y/n): y

✅ Checkout completed successfully!
  Final Amount: $389.97
  Reservation #101 is now checked out
```

### Quick Checkout

```
============================================================
QUICK CHECKOUT
============================================================

Processing checkout for:
  Guest:      John Doe
  Hotel:      Grand Hotel
  Room:       Room 101
  Check-in:   2024-01-15
  Check-out:  2024-01-18
  Expected Total: $389.97

🔘 Confirm checkout? (y/n): y

✅ Checkout completed successfully!
  Final Amount: $389.97
  Reservation #101 is now checked out
```

### Search by Room Number Only

```
============================================================
FIND RESERVATION FOR CHECKOUT
============================================================

Find reservation using minimum identification.
Provide at least one of: name, room number, or hotel ID.

SEARCH CRITERIA:
----------------------------------------
First Name (optional): 
Last Name (optional): 
Room Number (optional): 101
Hotel ID (optional): 

============================================================
SEARCH RESULTS
============================================================

✅ Found 1 checked-in reservation(s):

[1] Reservation ID: 101
    Guest:      John Doe
    Hotel:      Grand Hotel (ID: 1)
    Room:       Room 101 (Standard Room)
    Check-in:   2024-01-15
    Check-out:  2024-01-18
    Status:     checked_in
    Total:      $389.97
```

### Search by Hotel ID Only

```
============================================================
FIND RESERVATION FOR CHECKOUT
============================================================

Find reservation using minimum identification.
Provide at least one of: name, room number, or hotel ID.

SEARCH CRITERIA:
----------------------------------------
First Name (optional): 
Last Name (optional): 
Room Number (optional): 
Hotel ID (optional): 1

============================================================
SEARCH RESULTS
============================================================

✅ Found 3 checked-in reservation(s):

[1] Reservation ID: 101
    Guest:      John Doe
    Hotel:      Grand Hotel (ID: 1)
    Room:       Room 101 (Standard Room)
    Check-in:   2024-01-15
    Check-out:  2024-01-18
    Status:     checked_in
    Total:      $389.97

[2] Reservation ID: 102
    Guest:      Jane Smith
    Hotel:      Grand Hotel (ID: 1)
    Room:       Room 102 (Deluxe Room)
    Check-in:   2024-01-16
    Check-out:  2024-01-19
    Status:     checked_in
    Total:      $599.97

[3] Reservation ID: 103
    Guest:      Bob Johnson
    Hotel:      Grand Hotel (ID: 1)
    Room:       Room 103 (Suite)
    Check-in:   2024-01-14
    Check-out:  2024-01-17
    Status:     checked_in
    Total:      $799.97
```

## Integration with Hotel Simulator

The Checkout Wizard integrates seamlessly with the existing Hotel Simulator ecosystem:

- **Hotel CLI**: Can be called from the main CLI or run standalone
- **Database**: Uses the same SQLite database as other components
- **Reservation System**: Uses the existing checkout functionality
- **Transaction System**: Creates proper payment transactions

## Best Practices

### Data Entry
- Use the most convenient identification method for the situation
- Double-check reservation details before confirmation
- Use partial matching for quick searches (e.g., "10" for room 101-109)
- Combine search criteria for more precise results

### Error Recovery
- If checkout fails, check the error message for details
- Verify that the reservation is in 'checked_in' status
- Ensure the reservation ID is correct for quick checkout
- Check that at least one search criterion is provided

### Performance
- The wizard is optimized for quick checkout processing
- Search results are limited to checked-in reservations only
- Database queries are efficient and indexed
- Minimal user interaction for experienced staff

## Troubleshooting

### Common Issues

**No reservations found**:
- Solution: Verify the guest is checked in (not just confirmed)
- Solution: Check that search criteria are correct
- Solution: Try different combinations of search criteria

**Reservation already checked out**:
- Solution: The reservation was already processed
- Solution: Check reservation status in the database

**Invalid reservation ID**:
- Solution: Verify the reservation ID exists
- Solution: Use interactive mode to find the correct ID

**Database errors**:
- Solution: Check database connection
- Solution: Verify database schema is up to date

### Debugging

For detailed error information, run with:
```bash
python3 -v checkout_wizard.py
```

Or check the console output for stack traces when errors occur.

## Future Enhancements

Potential improvements for future versions:

- **Express Checkout**: One-click checkout for known reservations
- **Batch Checkout**: Process multiple checkouts at once
- **Late Checkout Handling**: Special processing for late checkouts
- **Early Checkout Handling**: Prorated refunds for early departures
- **Receipt Printing**: Generate and print receipts
- **Email Confirmation**: Send checkout confirmation emails
- **Luggage Storage**: Option to store luggage after checkout
- **Transportation Arrangement**: Arrange airport transfers
- **Feedback Collection**: Gather guest feedback at checkout

## Security Considerations

- **Data Privacy**: Only displays necessary guest information
- **Confirmation Required**: Explicit confirmation before processing
- **Audit Trail**: Creates transaction records for all checkouts
- **Status Validation**: Prevents duplicate checkouts

## Conclusion

The Checkout Wizard provides a minimalist yet powerful interface for processing guest checkouts. It supports the minimum identification requirements (name, room number, or hotel ID) while maintaining flexibility and efficiency. The wizard integrates seamlessly with the existing Hotel Simulator ecosystem and follows established patterns for consistency and reliability.

By focusing on the essential identification methods and providing both interactive and quick checkout options, the Checkout Wizard enables hotel staff to process checkouts efficiently while minimizing data entry requirements.