#!/usr/bin/env python3
"""
Script to update documentation for phone field (cell numbers only)
"""

# Update database.py
with open('database.py', 'r') as f:
    content = f.read()

# Add comment to guests table schema
old_schema = """                '''CREATE TABLE IF NOT EXISTS guests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    first_name TEXT NOT NULL,
                    last_name TEXT NOT NULL,
                    email TEXT,
                    phone TEXT,
                    address TEXT,
                    car_make TEXT,
                    car_model TEXT,
                    car_color TEXT,
                    loyalty_points INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )'''"""

new_schema = """                '''CREATE TABLE IF NOT EXISTS guests (
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
                )'''"""

content = content.replace(old_schema, new_schema)

with open('database.py', 'w') as f:
    f.write(content)

print("✓ Updated database.py")

# Update hotel_simulator.py
with open('hotel_simulator.py', 'r') as f:
    content = f.read()

# Update create_guest docstring
old_docstring = """    def create_guest(self, first_name: str, last_name: str, email: str = "", 
                    phone: str = "", address: str = "", car_make: str = "",
                    car_model: str = "", car_color: str = "") -> Guest:
        \"\"\"Create a new guest and add to database
        
        Args:
            first_name: Guest's first name
            last_name: Guest's last name
            email: Guest's email
            phone: Guest's phone number
            address: Guest's address"""

new_docstring = """    def create_guest(self, first_name: str, last_name: str, email: str = "", 
                    phone: str = "", address: str = "", car_make: str = "",
                    car_model: str = "", car_color: str = "") -> Guest:
        \"\"\"Create a new guest and add to database
        
        Args:
            first_name: Guest's first name
            last_name: Guest's last name
            email: Guest's email
            phone: Guest's cell/mobile phone number (cell numbers only)
            address: Guest's physical address"""

content = content.replace(old_docstring, new_docstring)

# Update Guest class docstring
old_guest_doc = """@dataclass
class Guest:
    \"\"\"Represents a hotel guest\"\"\"
    id: Optional[int] = None
    first_name: str = ""
    last_name: str = ""
    email: str = ""
    phone: str = ""
    address: str = ""
    car_make: str = ""
    car_model: str = ""
    car_color: str = ""
    loyalty_points: int = 0"""

new_guest_doc = """@dataclass
class Guest:
    \"\"\"Represents a hotel guest
    
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
    \"\"\"
    id: Optional[int] = None
    first_name: str = ""
    last_name: str = ""
    email: str = ""
    phone: str = ""  # Cell/mobile number only
    address: str = ""
    car_make: str = ""
    car_model: str = ""
    car_color: str = ""
    loyalty_points: int = 0"""

content = content.replace(old_guest_doc, new_guest_doc)

with open('hotel_simulator.py', 'w') as f:
    f.write(content)

print("✓ Updated hotel_simulator.py")
print("\nAll documentation updated successfully!")
