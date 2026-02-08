# Check-in Wizard Documentation

## Overview

The Check-in Wizard provides a comprehensive solution for finding and checking in guests at your hotel. It features flexible search capabilities and an intuitive interactive interface that integrates seamlessly with the Hotel Simulator CLI.

## Features

### 🔍 Flexible Search
- **Name Search**: Search by first name, last name, or both using partial matching (contains logic)
- **Date Search**: Search by check-in date with automatic default to today's date
- **Hotel Search**: Search by specific hotel ID or use `*` to search across all hotels
- **All Optional**: All search criteria are optional - leave blank to skip

### 🏨 Check-in Process
- **Reservation Selection**: Browse and select from found reservations
- **Confirmation Dialog**: Review guest details before finalizing check-in
- **Success Feedback**: Receive confirmation with complete check-in information
- **Error Handling**: Graceful handling of invalid inputs and edge cases

### 🎯 Integration
- **CLI Commands**: Three dedicated commands in the Hotel Simulator CLI
- **Menu System**: Full menu interface for easy navigation
- **Database Integration**: Proper handling of hotel, room, and guest relationships

## Installation

The Check-in Wizard is automatically available when you have the `checkin_wizard.py` file in the same directory as your Hotel Simulator.

## Usage

### Command Line Interface

```bash
# Search for reservations
python3 checkin_wizard.py search

# Interactive check-in process
python3 checkin_wizard.py checkin

# Full menu interface
python3 checkin_wizard.py menu
```

### Hotel Simulator CLI Integration

```bash
# Start interactive CLI
python3 hotel_cli.py interactive

# Available check-in commands:
> search_checkins          # Search for reservations to check in
> interactive_checkin     # Full interactive check-in process
> checkin_menu            # Check-in management menu
```

## Search Criteria

### Name Search
- **First Name**: Partial match (contains logic)
- **Last Name**: Partial match (contains logic)
- **Example**: Searching for "Joh" will find "Johnson", "Johansson", etc.

### Date Search
- **Format**: `YYYY-MM-DD`
- **Default**: Today's date (automatic)
- **Example**: `2026-02-07` or press Enter for today

### Hotel Search
- **Specific Hotel**: Enter hotel ID (e.g., `1`, `2`, `18`)
- **All Hotels**: Enter `*` (wildcard)
- **Default**: All hotels (when left blank)

## Step-by-Step Guide

### 1. Search for Reservations

```
============================================================
CHECK-IN SEARCH WIZARD
============================================================

Search for reservations to check in guests.
All fields are optional - leave blank to skip.
Name search uses 'contains' logic (partial matches).
Use '*' for hotel_id to search all hotels.
Date defaults to today if not specified.

SEARCH CRITERIA:
----------------------------------------
First Name (partial match): 
Last Name (partial match): Smith
Date (YYYY-MM-DD, default today 2026-02-07): 
Hotel ID (number or '*' for all): *
```

### 2. Review Search Results

```
============================================================
SEARCH RESULTS
============================================================

✅ Found 3 reservation(s) for 2026-02-07:

[1] Reservation ID: 290
    Guest:      John Smith
    Hotel:      Hotel Emerald Isle (ID: 18)
    Room:       Room 202 (Deluxe)
    Check-in:   2026-02-07
    Check-out:  2026-02-10
    Status:     confirmed

[2] Reservation ID: 305
    Guest:      Sarah Smith
    Hotel:      Phase5 Test (ID: 39)
    Room:       Room 101 (Standard)
    Check-in:   2026-02-07
    Check-out:  2026-02-10
    Status:     confirmed
```

### 3. Select and Check In

```
============================================================
SELECT RESERVATION TO CHECK IN
============================================================

Enter reservation number (1-3) or '0' to cancel: 1

🔘 Confirm check-in for John Smith? (y/n): y

✅ Successfully checked in reservation 290

📋 CHECK-IN CONFIRMATION:
   Guest:      John Smith
   Hotel:      Hotel Emerald Isle
   Room:       Room 202
   Check-in:   2026-02-07
   Check-out:  2026-02-10
```

## Common Scenarios

### 🔎 Find a Guest by Name
```
First Name (partial match): John
Last Name (partial match): Smith
Date (YYYY-MM-DD, default today 2026-02-07): 
Hotel ID (number or '*' for all): *
```

### 🏢 Check All Today's Arrivals
```
First Name (partial match): 
Last Name (partial match): 
Date (YYYY-MM-DD, default today 2026-02-07): 
Hotel ID (number or '*' for all): *
```

### 📅 Find Reservations for Specific Date
```
First Name (partial match): 
Last Name (partial match): 
Date (YYYY-MM-DD, default today 2026-02-07): 2026-02-10
Hotel ID (number or '*' for all): *
```

### 🏨 Check Arrivals at Specific Hotel
```
First Name (partial match): 
Last Name (partial match): 
Date (YYYY-MM-DD, default today 2026-02-07): 
Hotel ID (number or '*' for all): 18
```

## Error Handling

### Invalid Date Format
```
Date (YYYY-MM-DD, default today 2026-02-07): 02-07-2026
⚠️  Invalid date format: 02-07-2026
📅 Using today's date: 2026-02-07
```

### Invalid Hotel ID
```
Hotel ID (number or '*' for all): abc
⚠️  Invalid hotel ID: abc
🏨 Searching all hotels instead
```

### No Results Found
```
❌ No reservations found for 2026-02-07
   matching name criteria
   in hotel 18
```

## Technical Details

### Database Schema
The wizard properly handles the database relationships:
- `reservations` → `rooms` → `hotel`
- `reservations` → `guests`
- `rooms` → `room_types`

### Search Query
```sql
SELECT r.id as reservation_id,
       rm.hotel_id,
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
  AND (g.first_name LIKE '%John%' OR 1=1)  -- Optional first name
  AND (g.last_name LIKE '%Smith%' OR 1=1) -- Optional last name
  AND r.check_in_date = '2026-02-07'       -- Date filter
  AND (rm.hotel_id = 18 OR 1=1)           -- Optional hotel filter
ORDER BY r.check_in_date, h.name, g.last_name, g.first_name
```

## Troubleshooting

### Wizard not available in CLI
**Issue**: Check-in commands not showing in `help`
**Solution**: Ensure `checkin_wizard.py` is in the same directory as `hotel_cli.py`

### No reservations found
**Possible Causes**:
- No reservations for the selected date
- No matching names in the database
- Hotel ID doesn't exist
- All matching reservations are already checked out or cancelled

**Solutions**:
- Try searching all hotels with `*`
- Try a different date
- Try searching without name criteria
- Verify reservations exist in the database

### Database connection errors
**Issue**: Connection or query execution errors
**Solution**: Ensure the database file (`hotel.db`) is accessible and not corrupted

## Best Practices

1. **Start with broad searches**: Search all hotels first, then narrow down
2. **Use partial names**: "Joh" instead of "John" to find variations
3. **Check today's date first**: Most check-ins are for the current day
4. **Verify guest identity**: Always confirm the guest name before check-in
5. **Handle duplicates carefully**: When multiple guests have similar names

## Menu System

The Check-in Wizard includes a comprehensive menu system:

```
============================================================
CHECK-IN WIZARD MENU
============================================================

1. Search Reservations
2. Interactive Check-In
3. Exit

Select an option (1-3):
```

### Menu Options

1. **Search Reservations**: Search for reservations without checking in
2. **Interactive Check-In**: Full check-in process (search + check-in)
3. **Exit**: Return to previous menu

## Integration with Hotel Simulator

The Check-in Wizard integrates with:
- **Hotel Simulator**: Uses existing database and simulation engine
- **Reservation System**: Properly updates reservation statuses
- **Guest Management**: Links to guest information
- **Room Management**: Updates room occupancy status

## Future Enhancements

Potential features for future versions:
- Bulk check-in for groups
- Early check-in handling
- Late check-in notifications
- Special requests capture
- Payment processing integration
- Digital signature capture
- ID verification

## Support

For issues or questions:
- Check the database schema matches requirements
- Verify file permissions
- Review error messages for specific guidance
- Consult the Hotel Simulator documentation

## License

This Check-in Wizard is part of the Hotel Simulator system and is subject to the same licensing terms.

---