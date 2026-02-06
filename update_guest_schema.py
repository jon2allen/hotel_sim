#!/usr/bin/env python3
"""
Script to update database.py and hotel_simulator.py with car fields
"""

# Update database.py
with open('database.py', 'r') as f:
    content = f.read()

# Replace the guests table schema
old_schema = """                '''CREATE TABLE IF NOT EXISTS guests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    first_name TEXT NOT NULL,
                    last_name TEXT NOT NULL,
                    email TEXT,
                    phone TEXT,
                    address TEXT,
                    loyalty_points INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )'''"""

new_schema = """                '''CREATE TABLE IF NOT EXISTS guests (
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

content = content.replace(old_schema, new_schema)

with open('database.py', 'w') as f:
    f.write(content)

print("✓ Updated database.py schema")

# Update hotel_simulator.py - Guest class
with open('hotel_simulator.py', 'r') as f:
    content = f.read()

# Update Guest dataclass
old_guest_class = """@dataclass
class Guest:
    \"\"\"Represents a hotel guest\"\"\"
    id: Optional[int] = None
    first_name: str = \"\"
    last_name: str = \"\"
    email: str = \"\"
    phone: str = \"\"
    address: str = \"\"
    loyalty_points: int = 0"""

new_guest_class = """@dataclass
class Guest:
    \"\"\"Represents a hotel guest\"\"\"
    id: Optional[int] = None
    first_name: str = \"\"
    last_name: str = \"\"
    email: str = \"\"
    phone: str = \"\"
    address: str = \"\"
    car_make: str = \"\"
    car_model: str = \"\"
    car_color: str = \"\"
    loyalty_points: int = 0"""

content = content.replace(old_guest_class, new_guest_class)

# Update create_guest method signature
old_signature = """    def create_guest(self, first_name: str, last_name: str, email: str = "", 
                    phone: str = "", address: str = "") -> Guest:"""

new_signature = """    def create_guest(self, first_name: str, last_name: str, email: str = "", 
                    phone: str = "", address: str = "", car_make: str = "",
                    car_model: str = "", car_color: str = "") -> Guest:"""

content = content.replace(old_signature, new_signature)

# Update create_guest INSERT query
old_insert = """            query = \"\"\"
                INSERT INTO guests (first_name, last_name, email, phone, address)
                VALUES (?, ?, ?, ?, ?)
            \"\"\"
            cursor = self.db.conn.cursor()
            cursor.execute(query, (first_name, last_name, email, phone, address))"""

new_insert = """            query = \"\"\"
                INSERT INTO guests (first_name, last_name, email, phone, address, car_make, car_model, car_color)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            \"\"\"
            cursor = self.db.conn.cursor()
            cursor.execute(query, (first_name, last_name, email, phone, address, car_make, car_model, car_color))"""

content = content.replace(old_insert, new_insert)

# Update Guest object creation in create_guest
old_guest_obj = """            guest = Guest(
                id=guest_id,
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                address=address
            )"""

new_guest_obj = """            guest = Guest(
                id=guest_id,
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                address=address,
                car_make=car_make,
                car_model=car_model,
                car_color=car_color
            )"""

content = content.replace(old_guest_obj, new_guest_obj)

with open('hotel_simulator.py', 'w') as f:
    f.write(content)

print("✓ Updated hotel_simulator.py")
print("\nAll files updated successfully!")
