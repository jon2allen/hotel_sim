# Guest Table Field Specifications

## Date: 2026-02-06
## Hotel Simulator Database Documentation

---

## Guest Table Schema

### Complete Field List

| Field Name | Type | Required | Description | Notes |
|------------|------|----------|-------------|-------|
| `id` | INTEGER | Yes (Auto) | Unique guest identifier | Primary key, auto-increment |
| `first_name` | TEXT | Yes | Guest's first name | Not null |
| `last_name` | TEXT | Yes | Guest's last name | Not null |
| `email` | TEXT | No | Guest's email address | Optional, nullable |
| **`phone`** | **TEXT** | **No** | **Guest's cell/mobile phone number** | **CELL NUMBERS ONLY** |
| `address` | TEXT | No | Guest's physical address | Optional, unlimited length |
| `car_make` | TEXT | No | Vehicle manufacturer | Optional (e.g., "Toyota", "N/A") |
| `car_model` | TEXT | No | Vehicle model | Optional (e.g., "Camry", "N/A") |
| `car_color` | TEXT | No | Vehicle color | Optional (e.g., "Blue", "N/A") |
| `loyalty_points` | INTEGER | No | Accumulated loyalty points | Default: 0 |
| `created_at` | TIMESTAMP | No | Record creation timestamp | Default: CURRENT_TIMESTAMP |

---

## Phone Field Specification

### ⚠️ IMPORTANT: Phone Field Usage

**The `phone` field is designated for CELL/MOBILE NUMBERS ONLY.**

### Details:
- **Field Name**: `phone`
- **Type**: TEXT (unlimited length)
- **Purpose**: Store guest's cell/mobile phone number
- **Required**: No (optional/nullable)
- **Format**: No enforced format (flexible for international numbers)

### Usage Guidelines:
✅ **DO** use for:
- Cell phone numbers
- Mobile phone numbers
- Primary contact numbers that are mobile

❌ **DO NOT** use for:
- Home/landline numbers
- Work phone numbers
- Fax numbers
- Other non-mobile contact numbers

### Common Formats Accepted:
- `555-1234` (7 digits)
- `555-123-4567` (10 digits with dashes)
- `(555) 123-4567` (parentheses format)
- `+1-555-123-4567` (international format)
- `555.123.4567` (dot separator)

### Current Database Statistics:
- **56 guests** have phone numbers stored
- **Average length**: ~12 characters
- **No maximum length enforced**

---

## Address Field Specification

### Details:
- **Field Name**: `address`
- **Type**: TEXT (unlimited length)
- **Purpose**: Store guest's physical/mailing address
- **Required**: No (optional/nullable)
- **Format**: Free-form text

### Current Usage:
- **Shortest address**: 10 characters
- **Longest address**: 34 characters
- **Average length**: ~19 characters
- **No maximum length enforced**

### Examples:
```
123 Main St, Anytown, USA
456 Oak Avenue, Springfield, IL
742 Evergreen Terrace, Springfield
1 Paradise Island, Themyscira
```

---

## Car Fields Specification

### Purpose:
Track guest vehicle information for parking, valet service, or identification purposes.

### Fields:

#### `car_make` (Vehicle Manufacturer)
- **Type**: TEXT
- **Optional**: Yes
- **Examples**: "Toyota", "BMW", "Tesla", "N/A"
- **Can be empty**: Yes

#### `car_model` (Vehicle Model)
- **Type**: TEXT
- **Optional**: Yes
- **Examples**: "Camry", "5 Series", "Model S", "N/A"
- **Can be empty**: Yes

#### `car_color` (Vehicle Color)
- **Type**: TEXT
- **Optional**: Yes
- **Examples**: "Blue", "Black", "Silver", "N/A"
- **Can be empty**: Yes

### Usage Patterns:
1. **Complete car info**: All three fields populated
2. **No car**: All fields empty or NULL
3. **N/A car**: All fields set to "N/A"
4. **Partial info**: Some fields populated, others empty

---

## Code Documentation

### database.py
```python
'''CREATE TABLE IF NOT EXISTS guests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT,
    phone TEXT,  -- Cell/mobile number only
    address TEXT,
    car_make TEXT,
    car_model TEXT,
    car_color TEXT,
    loyalty_points INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)'''
```

### hotel_simulator.py - Guest Class
```python
@dataclass
class Guest:
    """Represents a hotel guest
    
    Attributes:
        id: Unique guest identifier
        first_name: Guest's first name
        last_name: Guest's last name
        email: Guest's email address
        phone: Guest's cell/mobile phone number (cell numbers only)
        address: Guest's physical address
        car_make: Vehicle manufacturer (optional, can be N/A)
        car_model: Vehicle model (optional, can be N/A)
        car_color: Vehicle color (optional, can be N/A)
        loyalty_points: Accumulated loyalty points
    """
    id: Optional[int] = None
    first_name: str = ""
    last_name: str = ""
    email: str = ""
    phone: str = ""  # Cell/mobile number only
    address: str = ""
    car_make: str = ""
    car_model: str = ""
    car_color: str = ""
    loyalty_points: int = 0
```

### hotel_simulator.py - create_guest() Method
```python
def create_guest(self, first_name: str, last_name: str, email: str = "", 
                phone: str = "", address: str = "", car_make: str = "",
                car_model: str = "", car_color: str = "") -> Guest:
    """Create a new guest and add to database
    
    Args:
        first_name: Guest's first name
        last_name: Guest's last name
        email: Guest's email
        phone: Guest's cell/mobile phone number (cell numbers only)
        address: Guest's physical address
        car_make: Vehicle manufacturer (optional)
        car_model: Vehicle model (optional)
        car_color: Vehicle color (optional)
        
    Returns:
        Created Guest object with ID
    """
```

---

## Example Usage

### Creating a Guest with Cell Number:
```python
guest = sim.create_guest(
    first_name="John",
    last_name="Doe",
    email="john@example.com",
    phone="555-123-4567",  # Cell number only
    address="123 Main St, Anytown, USA",
    car_make="Toyota",
    car_model="Camry",
    car_color="Blue"
)
```

### Creating a Guest without Phone:
```python
guest = sim.create_guest(
    first_name="Jane",
    last_name="Smith",
    email="jane@example.com",
    address="456 Oak Ave, Springfield, IL"
    # phone omitted - guest doesn't have cell number
)
```

---

## Database Queries

### Find guests with cell numbers:
```sql
SELECT first_name, last_name, phone 
FROM guests 
WHERE phone IS NOT NULL AND phone != '';
```

### Find guests without cell numbers:
```sql
SELECT first_name, last_name, email 
FROM guests 
WHERE phone IS NULL OR phone = '';
```

---

## Summary

✅ **Phone field is for CELL/MOBILE NUMBERS ONLY**
✅ **Address field has unlimited length**
✅ **Car fields are optional and flexible**
✅ **All contact fields (email, phone, address) are optional**
✅ **Documentation updated in code comments and docstrings**

---

**Last Updated**: 2026-02-06
**Documentation Version**: 1.1
