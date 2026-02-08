# Guest Management Wizards - User Guide

## Overview

The Guest Management Wizards provide interactive, user-friendly interfaces for adding and searching guests in the hotel simulator system.

---

## Features

### 1. Add Guest Wizard
Interactive wizard that guides you through adding a new guest with:
- ✅ Required fields validation
- ✅ Optional field support
- ✅ Phone number format validation (10-digit)
- ✅ Full American-style address support
- ✅ Vehicle information (make, model, color)
- ✅ Confirmation before saving

### 2. Search Guest Wizard
Powerful search tool with:
- ✅ **Partial matching** ("contains" logic)
- ✅ Search by any field combination
- ✅ Multiple search criteria support
- ✅ Detailed results display
- ✅ Results limited to 50 for performance

---

## Usage

### Running the Wizards

#### Option 1: Main Menu (Recommended)
```bash
python3 guest_wizard.py
```
or
```bash
python3 guest_wizard.py menu
```

This shows an interactive menu where you can choose:
1. Add New Guest
2. Search for Guests
3. Exit

#### Option 2: Direct Add Guest
```bash
python3 guest_wizard.py add
```

#### Option 3: Direct Search
```bash
python3 guest_wizard.py search
```

#### Option 4: Demo Mode
```bash
python3 demo_guest_wizard.py
```

---

## Add Guest Wizard

### Fields

#### Required Fields:
- **First Name** - Guest's first name
- **Last Name** - Guest's last name

#### Optional Fields:
- **Email** - Email address
- **Cell Phone** - 10-digit phone number (format: 555-123-4567)
- **Address** - Full address (Street, City, State ZIP)
- **Car Make** - Vehicle manufacturer (e.g., Toyota, Honda)
- **Car Model** - Vehicle model (e.g., Camry, Accord)
- **Car Color** - Vehicle color (e.g., Blue, Red)

### Example Session

```
============================================================
ADD GUEST WIZARD
============================================================

Please enter the guest information.
(Press Enter to skip optional fields)

REQUIRED INFORMATION:
----------------------------------------
First Name: Sarah
Last Name: Williams

CONTACT INFORMATION (Optional):
----------------------------------------
Email Address: sarah.williams@example.com
Cell Phone (10-digit, e.g., 555-123-4567): 555-789-1234

ADDRESS INFORMATION (Optional):
----------------------------------------
Format: Street, City, State ZIP
Example: 123 Main Street, Anytown, CA 90210
Full Address: 789 Oak Street, Portland, OR 97201

VEHICLE INFORMATION (Optional):
----------------------------------------
Enter vehicle details or 'N/A' if no vehicle
Car Make (e.g., Toyota, Honda): Honda
Car Model (e.g., Camry, Accord): Civic
Car Color (e.g., Blue, Red): Silver

============================================================
GUEST INFORMATION SUMMARY
============================================================
Name:     Sarah Williams
Email:    sarah.williams@example.com
Phone:    555-789-1234
Address:  789 Oak Street, Portland, OR 97201
Vehicle:  Silver Honda Civic
============================================================

Create this guest? (y/n): y

✅ Guest created successfully!
Guest ID: 2826
Name: Sarah Williams
```

### Phone Number Validation

The wizard validates that phone numbers have 10 digits:
- ✅ Valid: `555-123-4567` (10 digits)
- ✅ Valid: `5551234567` (10 digits)
- ⚠️ Warning: `555-1234` (7 digits) - asks for confirmation
- ⚠️ Warning: `555-123-4567-890` (13 digits) - asks for confirmation

---

## Search Guest Wizard

### Search Criteria

You can search by any combination of:
- **First Name** - Partial match
- **Last Name** - Partial match
- **Email** - Partial match
- **Phone** - Partial match
- **Address** - Partial match
- **Car Make** - Partial match
- **Car Model** - Partial match
- **Car Color** - Partial match

### How Partial Matching Works

The search uses SQL `LIKE` with wildcards, so:
- Searching for `"John"` finds: **John**, **John**son, **John**ny, etc.
- Searching for `"555"` finds any phone with **555** in it
- Searching for `"CA"` in address finds all California addresses
- Searching for `"Toyota"` finds all Toyota vehicles

### Example Search Sessions

#### Example 1: Search by Last Name
```
============================================================
SEARCH GUEST WIZARD
============================================================

Search for guests using any combination of criteria.
Leave fields blank to skip that search criterion.
Search uses 'contains' logic (partial matches).

SEARCH CRITERIA:
----------------------------------------
First Name (partial match): 
Last Name (partial match): Johnson
Email (partial match): 
Phone (partial match): 
Address (partial match): 
Car Make (partial match): 
Car Model (partial match): 
Car Color (partial match): 

============================================================
SEARCH RESULTS
============================================================

✅ Found 3 guest(s):

[1] Alice Johnson (ID: 2786)
    Email:   alice.johnson@example.com
    Phone:   555-123-4567
    Address: 123 Main Street, Anytown, CA 90210
    Vehicle: Blue Toyota Camry

[2] Bob Johnson (ID: 1523)
    Email:   bob.j@email.com
    Phone:   555-234-5678
    Address: 456 Elm Street, Springfield, IL 62701
    Vehicle: (none)

[3] Carol Johnson (ID: 2104)
    Email:   (none)
    Phone:   555-345-6789
    Address: 789 Pine Road, Seattle, WA 98101
    Vehicle: N/A
```

#### Example 2: Search by Car Make
```
SEARCH CRITERIA:
----------------------------------------
First Name (partial match): 
Last Name (partial match): 
Email (partial match): 
Phone (partial match): 
Address (partial match): 
Car Make (partial match): Tesla
Car Model (partial match): 
Car Color (partial match): 

============================================================
SEARCH RESULTS
============================================================

✅ Found 2 guest(s):

[1] Elon Musk (ID: 2793)
    Email:   elon.musk@tesla.com
    Phone:   555-837-5200
    Address: 3500 Deer Creek Road, Palo Alto, CA 94304
    Vehicle: White Tesla Model S

[2] John Doe (ID: 2825)
    Email:   john.doe@example.com
    Phone:   555-987-6543
    Address: 456 Test Avenue, TestCity, TX 75001
    Vehicle: Red Tesla Model 3
```

#### Example 3: Combined Search (Name + Location)
```
SEARCH CRITERIA:
----------------------------------------
First Name (partial match): Sarah
Last Name (partial match): 
Email (partial match): 
Phone (partial match): 
Address (partial match): CA
Car Make (partial match): 
Car Model (partial match): 
Car Color (partial match): 

============================================================
SEARCH RESULTS
============================================================

✅ Found 1 guest(s):

[1] Sarah Connor (ID: 2791)
    Email:   sarah.connor@cyberdyne.com
    Phone:   555-198-4000
    Address: 2029 Skynet Boulevard, Los Angeles, CA 90001
    Vehicle: Black BMW 5 Series
```

#### Example 4: Search by Phone Area Code
```
SEARCH CRITERIA:
----------------------------------------
First Name (partial match): 
Last Name (partial match): 
Email (partial match): 
Phone (partial match): 555-123
Car Make (partial match): 
Car Model (partial match): 
Car Color (partial match): 

============================================================
SEARCH RESULTS
============================================================

✅ Found 5 guest(s):

[1] Alice Johnson (ID: 2786)
    Phone:   555-123-4567
    ...
```

---

## Tips and Best Practices

### Adding Guests

1. **Required Fields**: Always provide first and last name
2. **Phone Numbers**: Use 10-digit format (555-123-4567) for consistency
3. **Addresses**: Include full address with City, State, ZIP for completeness
4. **Vehicle Info**: Enter "N/A" if guest explicitly has no vehicle, or leave blank if unknown
5. **Review Before Saving**: Always check the summary before confirming

### Searching Guests

1. **Start Broad**: Begin with one criterion, then refine if too many results
2. **Use Partial Matches**: Search for "John" instead of "Johnson" to catch variations
3. **Combine Criteria**: Use multiple fields for more specific searches
4. **Phone Searches**: Just the area code (555) can find all guests from that area
5. **Address Searches**: Search by state code (CA, NY) to find all guests from that state
6. **50 Result Limit**: If you hit the limit, add more search criteria to narrow results

---

## Technical Details

### Database Fields

The wizards interact with the following `guests` table fields:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | INTEGER | Auto | Unique identifier |
| first_name | TEXT | Yes | Guest's first name |
| last_name | TEXT | Yes | Guest's last name |
| email | TEXT | No | Email address |
| phone | TEXT | No | Cell phone (10-digit) |
| address | TEXT | No | Full address |
| car_make | TEXT | No | Vehicle manufacturer |
| car_model | TEXT | No | Vehicle model |
| car_color | TEXT | No | Vehicle color |
| loyalty_points | INTEGER | Auto | Loyalty points (default 0) |
| created_at | TIMESTAMP | Auto | Creation timestamp |

### Search Query Logic

The search wizard builds dynamic SQL queries using `LIKE` operators:

```sql
SELECT * FROM guests 
WHERE first_name LIKE '%search_term%' 
  AND last_name LIKE '%search_term%'
  AND car_make LIKE '%search_term%'
ORDER BY last_name, first_name 
LIMIT 50
```

---

## Files

- **`guest_wizard.py`** - Main wizard implementation
- **`demo_guest_wizard.py`** - Demonstration and tutorial mode
- **`test_guest_wizard.py`** - Automated tests
- **`GUEST_WIZARD_GUIDE.md`** - This documentation

---

## Examples of Real-World Usage

### Scenario 1: Front Desk Check-In
Guest arrives without reservation:
1. Run: `python3 guest_wizard.py add`
2. Enter guest information
3. Guest is added and ready for room assignment

### Scenario 2: Finding a Guest by Phone
Guest calls, you only have their phone number:
1. Run: `python3 guest_wizard.py search`
2. Enter partial phone number (e.g., "555-789")
3. Find guest and retrieve their information

### Scenario 3: Parking Management
Need to find all guests with red cars:
1. Run: `python3 guest_wizard.py search`
2. Search by car color: "Red"
3. Get list of all guests with red vehicles

### Scenario 4: Regional Marketing
Find all guests from California:
1. Run: `python3 guest_wizard.py search`
2. Search by address: "CA"
3. Export list for marketing campaign

---

## Troubleshooting

### Issue: Phone validation warning
**Solution**: Ensure phone number has exactly 10 digits. Format doesn't matter (555-123-4567 or 5551234567 both work)

### Issue: No search results
**Solution**: 
- Try broader search terms
- Check spelling
- Try searching one field at a time
- Leave more fields blank

### Issue: Too many results (50 limit)
**Solution**: Add more search criteria to narrow down results

---

## Quick Reference

### Add Guest
```bash
python3 guest_wizard.py add
```

### Search Guests
```bash
python3 guest_wizard.py search
```

### Interactive Menu
```bash
python3 guest_wizard.py
```

### Demo Mode
```bash
python3 demo_guest_wizard.py
```

---

**Last Updated**: 2026-02-06  
**Version**: 1.0
