#!/usr/bin/env python3
"""
Hotel Simulator - Database Initialization
Handles all database operations and schema creation
"""

import sqlite3
import os
from typing import Optional, List, Dict, Any

class HotelDatabase:
    """Handles all database operations for the hotel simulator"""
    
    def __init__(self, db_path: str = 'hotel.db', create_dir: bool = True):
        """Initialize database connection
        
        Args:
            db_path: Path to SQLite database file
            create_dir: Whether to create parent directories if they don't exist
        """
        self.db_path = db_path
        self.conn = None
        
        # Create parent directories if needed
        if create_dir:
            import os
            db_dir = os.path.dirname(db_path)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir)
                print(f"Created directory: {db_dir}")
        
        self._connect()
        self._initialize_schema()
    
    def _connect(self):
        """Create database connection"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.execute("PRAGMA foreign_keys = ON")  # Enable foreign key constraints
            print(f"Connected to database: {self.db_path}")
        except sqlite3.Error as e:
            print(f"Database connection error: {e}")
            raise
    
    def _initialize_schema(self):
        """Create all tables if they don't exist"""
        try:
            cursor = self.conn.cursor()
            
            # Enable foreign key support
            cursor.execute("PRAGMA foreign_keys = ON")
            
            # Create tables
            tables = [
                # Hotel structure
                '''CREATE TABLE IF NOT EXISTS hotel (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    address TEXT,
                    stars INTEGER DEFAULT 3,
                    total_floors INTEGER,
                    total_rooms INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )''',
                
                # Floors
                '''CREATE TABLE IF NOT EXISTS floors (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    hotel_id INTEGER NOT NULL,
                    floor_number INTEGER NOT NULL,
                    description TEXT,
                    FOREIGN KEY (hotel_id) REFERENCES hotel(id) ON DELETE CASCADE,
                    UNIQUE(hotel_id, floor_number)
                )''',
                
                # Room Types
                '''CREATE TABLE IF NOT EXISTS room_types (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    description TEXT,
                    base_price DECIMAL(10,2) NOT NULL,
                    max_occupancy INTEGER NOT NULL,
                    amenities TEXT
                )''',
                
                # Rooms
                '''CREATE TABLE IF NOT EXISTS rooms (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    hotel_id INTEGER NOT NULL,
                    floor_id INTEGER NOT NULL,
                    room_number TEXT NOT NULL,
                    room_type_id INTEGER NOT NULL,
                    status TEXT DEFAULT 'available',
                    price_per_night DECIMAL(10,2),
                    max_occupancy INTEGER,
                    FOREIGN KEY (hotel_id) REFERENCES hotel(id) ON DELETE CASCADE,
                    FOREIGN KEY (floor_id) REFERENCES floors(id) ON DELETE CASCADE,
                    FOREIGN KEY (room_type_id) REFERENCES room_types(id),
                    UNIQUE(hotel_id, room_number)
                )''',
                
                # Guests
                '''CREATE TABLE IF NOT EXISTS guests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    first_name TEXT NOT NULL,
                    last_name TEXT NOT NULL,
                    email TEXT,
                    phone TEXT,
                    address TEXT,
                    loyalty_points INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )''',
                
                # Reservations
                '''CREATE TABLE IF NOT EXISTS reservations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    room_id INTEGER NOT NULL,
                    guest_id INTEGER NOT NULL,
                    check_in_date TEXT NOT NULL,
                    check_out_date TEXT NOT NULL,
                    status TEXT DEFAULT 'confirmed',
                    total_price DECIMAL(10,2),
                    booking_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    payment_status TEXT DEFAULT 'pending',
                    FOREIGN KEY (room_id) REFERENCES rooms(id) ON DELETE CASCADE,
                    FOREIGN KEY (guest_id) REFERENCES guests(id) ON DELETE CASCADE
                )''',
                
                # Transactions
                '''CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    reservation_id INTEGER NOT NULL,
                    amount DECIMAL(10,2) NOT NULL,
                    transaction_type TEXT NOT NULL,
                    payment_method TEXT,
                    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    description TEXT,
                    FOREIGN KEY (reservation_id) REFERENCES reservations(id) ON DELETE CASCADE
                )''',
                
                # Housekeeping
                '''CREATE TABLE IF NOT EXISTS housekeeping (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    room_id INTEGER NOT NULL,
                    status TEXT DEFAULT 'clean',
                    last_cleaned TIMESTAMP,
                    notes TEXT,
                    FOREIGN KEY (room_id) REFERENCES rooms(id) ON DELETE CASCADE,
                    UNIQUE(room_id)
                )''',
                
                # Indexes for performance
                '''CREATE INDEX IF NOT EXISTS idx_hotel_name ON hotel(name)''',
                '''CREATE INDEX IF NOT EXISTS idx_rooms_status ON rooms(status)''',
                '''CREATE INDEX IF NOT EXISTS idx_rooms_hotel ON rooms(hotel_id)''',
                '''CREATE INDEX IF NOT EXISTS idx_reservations_room ON reservations(room_id)''',
                '''CREATE INDEX IF NOT EXISTS idx_reservations_guest ON reservations(guest_id)''',
                '''CREATE INDEX IF NOT EXISTS idx_reservations_dates ON reservations(check_in_date, check_out_date)''',
                '''CREATE INDEX IF NOT EXISTS idx_transactions_reservation ON transactions(reservation_id)'''
            ]
            
            for table_sql in tables:
                cursor.execute(table_sql)
            
            self.conn.commit()
            print("Database schema initialized successfully")
            
        except sqlite3.Error as e:
            print(f"Error initializing database schema: {e}")
            if self.conn:
                self.conn.rollback()
            raise
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            print("Database connection closed")
    
    def execute_query(self, query: str, params: tuple = None, fetch: bool = False) -> Optional[List[Dict[str, Any]]]:
        """Execute a SQL query with optional parameters"""
        try:
            cursor = self.conn.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            if fetch:
                # Get column names
                columns = [column[0] for column in cursor.description]
                # Fetch all results and convert to list of dictionaries
                results = cursor.fetchall()
                return [dict(zip(columns, row)) for row in results]
            else:
                self.conn.commit()
                return None
                
        except sqlite3.Error as e:
            print(f"Query execution error: {e}")
            self.conn.rollback()
            raise
    
    def execute_many(self, query: str, params_list: List[tuple]):
        """Execute a query with multiple parameter sets"""
        try:
            cursor = self.conn.cursor()
            cursor.executemany(query, params_list)
            self.conn.commit()
            return cursor.rowcount
        except sqlite3.Error as e:
            print(f"Bulk execution error: {e}")
            self.conn.rollback()
            raise
    
    def create_hotel(self, name: str, address: str, stars: int, total_floors: int, total_rooms: int) -> int:
        """Create a new hotel and return its ID
        
        Args:
            name: Hotel name (must not be empty)
            address: Hotel address
            stars: Star rating (1-5)
            total_floors: Number of floors (must be positive)
            total_rooms: Total number of rooms (must be positive)
            
        Returns:
            ID of the created hotel
            
        Raises:
            ValueError: If validation fails
            sqlite3.Error: If database operation fails
        """
        # Input validation
        if not name or not name.strip():
            raise ValueError("Hotel name cannot be empty")
        
        if stars < 1 or stars > 5:
            raise ValueError("Star rating must be between 1 and 5")
        
        if total_floors <= 0:
            raise ValueError("Total floors must be positive")
        
        if total_rooms <= 0:
            raise ValueError("Total rooms must be positive")
        
        try:
            query = """
                INSERT INTO hotel (name, address, stars, total_floors, total_rooms)
                VALUES (?, ?, ?, ?, ?)
            """
            cursor = self.conn.cursor()
            cursor.execute(query, (name.strip(), address.strip(), stars, total_floors, total_rooms))
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Error creating hotel: {e}")
            self.conn.rollback()
            raise
    
    def create_floors(self, hotel_id: int, floor_count: int) -> List[int]:
        """Create multiple floors for a hotel"""
        try:
            floor_data = [(hotel_id, i, f"Floor {i}") for i in range(1, floor_count + 1)]
            query = "INSERT INTO floors (hotel_id, floor_number, description) VALUES (?, ?, ?)"
            self.execute_many(query, floor_data)
            
            # Return list of created floor IDs
            cursor = self.conn.cursor()
            cursor.execute("SELECT id FROM floors WHERE hotel_id = ? ORDER BY floor_number", (hotel_id,))
            return [row[0] for row in cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"Error creating floors: {e}")
            self.conn.rollback()
            raise
    
    def create_room_types(self, room_types: List[Dict[str, Any]]) -> Dict[str, int]:
        """Create room types and return their IDs
        
        Args:
            room_types: List of room type dictionaries with name, base_price, max_occupancy
            
        Returns:
            Dictionary mapping room type names to their IDs
            
        Note:
            If room types already exist, returns IDs of existing types
        """
        try:
            # First check which room types already exist
            cursor = self.conn.cursor()
            cursor.execute("SELECT id, name FROM room_types")
            existing_types = {row[1]: row[0] for row in cursor.fetchall()}
            
            # Only create room types that don't exist
            new_room_types = []
            for rt in room_types:
                if rt['name'] not in existing_types:
                    new_room_types.append(rt)
            
            if new_room_types:
                type_data = [(rt['name'], rt.get('description', ''), rt['base_price'], 
                             rt['max_occupancy'], rt.get('amenities', '')) 
                            for rt in new_room_types]
                query = """
                    INSERT INTO room_types (name, description, base_price, max_occupancy, amenities)
                    VALUES (?, ?, ?, ?, ?)
                """
                self.execute_many(query, type_data)
                print(f"✓ Created {len(new_room_types)} new room types")
            else:
                print("✓ All room types already exist")
            
            # Return complete mapping including existing types
            cursor.execute("SELECT id, name FROM room_types")
            return {row[1]: row[0] for row in cursor.fetchall()}
        except sqlite3.Error as e:
            print(f"Error creating room types: {e}")
            self.conn.rollback()
            raise
    
    def create_rooms(self, hotel_id: int, floor_ids: List[int], room_types: Dict[str, int], 
                    rooms_per_floor: int, room_number_format: str = "{floor}{room}") -> int:
        """Create rooms for all floors and return count of rooms created"""
        try:
            rooms_data = []
            room_number = 1
            
            for floor_id in floor_ids:
                # Get floor number for room numbering
                cursor = self.conn.cursor()
                cursor.execute("SELECT floor_number FROM floors WHERE id = ?", (floor_id,))
                floor_number = cursor.fetchone()[0]
                
                for i in range(rooms_per_floor):
                    # Alternate room types (this could be made more sophisticated)
                    room_type_name = "Standard"
                    if i % 5 == 0:
                        room_type_name = "Suite"
                    elif i % 3 == 0:
                        room_type_name = "Deluxe"
                    
                    room_type_id = room_types[room_type_name]
                    
                    # Generate room number
                    generated_room_number = room_number_format.format(floor=floor_number, room=room_number)
                    
                    # Get base price and occupancy from room type
                    cursor.execute("SELECT base_price, max_occupancy FROM room_types WHERE id = ?", (room_type_id,))
                    result = cursor.fetchone()
                    if result is None:
                        raise ValueError(f"Room type ID {room_type_id} not found")
                    base_price, max_occupancy = result
                    
                    rooms_data.append((
                        hotel_id, floor_id, generated_room_number, room_type_id,
                        'available', base_price, max_occupancy
                    ))
                    
                    room_number += 1
            
            query = """
                INSERT INTO rooms (hotel_id, floor_id, room_number, room_type_id, status, price_per_night, max_occupancy)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            count = self.execute_many(query, rooms_data)
            return count
        except sqlite3.Error as e:
            print(f"Error creating rooms: {e}")
            self.conn.rollback()
            raise
    
    def get_hotel_info(self, hotel_id: int) -> Optional[Dict[str, Any]]:
        """Get hotel information by ID"""
        query = "SELECT * FROM hotel WHERE id = ?"
        results = self.execute_query(query, (hotel_id,), fetch=True)
        return results[0] if results else None
    def delete_hotel(self, hotel_id: int) -> bool:
        """Delete a hotel and all its associated data (floors, rooms, etc.)
        
        Args:
            hotel_id: ID of the hotel to delete
            
        Returns:
            True if deletion was successful, False otherwise
            
        Note:
            Due to ON DELETE CASCADE constraints, this will automatically delete:
            - All floors belonging to the hotel
            - All rooms belonging to the hotel
            - All reservations for those rooms
            - All transactions for those reservations
            - All housekeeping records for those rooms
        """
        try:
            # First check if hotel exists
            hotel_info = self.get_hotel_info(hotel_id)
            if not hotel_info:
                print(f"Hotel with ID {hotel_id} not found")
                return False
                
            # Get hotel name for confirmation message
            hotel_name = hotel_info['name']
            
            # Delete the hotel (CASCADE will handle related records)
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM hotel WHERE id = ?", (hotel_id,))
            
            if cursor.rowcount == 0:
                print(f"Hotel with ID {hotel_id} not found")
                return False
                
            self.conn.commit()
            print(f"Successfully deleted hotel '{hotel_name}' (ID: {hotel_id}) and all associated data")
            return True
        except sqlite3.Error as e:
            print(f"Error deleting hotel: {e}")
            self.conn.rollback()
            return False    
    def get_room_status(self, hotel_id: int, floor: int = None, room_type: str = None) -> List[Dict[str, Any]]:
        """Get room status with optional filtering"""
        query = """
            SELECT r.id, r.hotel_id, r.room_number, r.status, r.price_per_night, r.max_occupancy,
                   rt.name as room_type, f.floor_number,
                   g.first_name, g.last_name, res.check_in_date, res.check_out_date
            FROM rooms r
            JOIN room_types rt ON r.room_type_id = rt.id
            JOIN floors f ON r.floor_id = f.id
            LEFT JOIN reservations res ON r.id = res.room_id 
                AND res.status IN ('confirmed', 'checked_in')
                AND strftime('%Y-%m-%d', res.check_in_date) <= strftime('%Y-%m-%d', 'now')
                AND strftime('%Y-%m-%d', res.check_out_date) >= strftime('%Y-%m-%d', 'now')
            LEFT JOIN guests g ON res.guest_id = g.id
            WHERE r.hotel_id = ?
        """
        
        params = [hotel_id]
        
        if floor:
            query += " AND f.floor_number = ?"
            params.append(floor)
        
        if room_type:
            query += " AND rt.name = ?"
            params.append(room_type)
        
        query += " ORDER BY f.floor_number, r.room_number"
        
        return self.execute_query(query, tuple(params), fetch=True)
    
    def create_room(self, hotel_id: int, floor_number: int, room_number: str, room_type_name: str, price_per_night: float = 100.00, max_occupancy: int = 2) -> int:
        """Create a single room with the specified parameters
        
        Args:
            hotel_id: ID of the hotel
            floor_number: Floor number
            room_number: Room number
            room_type_name: Name of room type
            price_per_night: Price per night (default: 100.00)
            max_occupancy: Maximum occupancy (default: 2)
            
        Returns:
            ID of the created room
        """
        try:
            # Get floor ID
            cursor = self.conn.cursor()
            cursor.execute("SELECT id FROM floors WHERE hotel_id = ? AND floor_number = ?", (hotel_id, floor_number))
            floor_result = cursor.fetchone()
            
            if not floor_result:
                # Create floor if it doesn't exist
                cursor.execute("INSERT INTO floors (hotel_id, floor_number, description) VALUES (?, ?, ?)", 
                              (hotel_id, floor_number, f"Floor {floor_number}"))
                floor_id = cursor.lastrowid
            else:
                floor_id = floor_result[0]
            
            # Get room type ID
            cursor.execute("SELECT id FROM room_types WHERE name = ?", (room_type_name,))
            room_type_result = cursor.fetchone()
            
            if not room_type_result:
                # Create room type if it doesn't exist (with default values)
                cursor.execute("INSERT INTO room_types (name, base_price, max_occupancy) VALUES (?, ?, ?)", 
                              (room_type_name, 100.00, 2))
                room_type_id = cursor.lastrowid
            else:
                room_type_id = room_type_result[0]
            
            # Create the room
            cursor.execute(
                "INSERT INTO rooms (hotel_id, floor_id, room_number, room_type_id, status, price_per_night, max_occupancy) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (hotel_id, floor_id, room_number, room_type_id, 'available', price_per_night, max_occupancy)
            )
            
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Error creating room: {e}")
            self.conn.rollback()
            raise

    def update_room_price(self, room_id: int, new_price: float) -> bool:
        """Update the price of a specific room
        
        Args:
            room_id: ID of the room to update
            new_price: New price per night
            
        Returns:
            True if update was successful, False otherwise
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "UPDATE rooms SET price_per_night = ? WHERE id = ?",
                (new_price, room_id)
            )
            
            if cursor.rowcount == 0:
                print(f"Room with ID {room_id} not found")
                return False
                
            self.conn.commit()
            print(f"Updated room {room_id} price to ${new_price:.2f}")
            return True
        except sqlite3.Error as e:
            print(f"Error updating room price: {e}")
            self.conn.rollback()
            return False

    def update_prices_by_type(self, hotel_id: int, room_type_name: str, new_price: float) -> int:
        """Update prices for all rooms of a specific type in a hotel
        
        Args:
            hotel_id: ID of the hotel
            room_type_name: Name of the room type to update
            new_price: New price per night
            
        Returns:
            Number of rooms updated
        """
        try:
            cursor = self.conn.cursor()
            
            # Get room type ID
            cursor.execute("SELECT id FROM room_types WHERE name = ?", (room_type_name,))
            room_type_result = cursor.fetchone()
            
            if not room_type_result:
                print(f"Room type '{room_type_name}' not found")
                return 0
                
            room_type_id = room_type_result[0]
            
            # Update all rooms of this type in the specified hotel
            cursor.execute(
                "UPDATE rooms SET price_per_night = ? "
                "WHERE hotel_id = ? AND room_type_id = ?",
                (new_price, hotel_id, room_type_id)
            )
            
            self.conn.commit()
            updated_count = cursor.rowcount
            print(f"Updated {updated_count} rooms of type '{room_type_name}' to ${new_price:.2f}")
            return updated_count
        except sqlite3.Error as e:
            print(f"Error updating prices by type: {e}")
            self.conn.rollback()
            return 0

    def increase_prices_by_percentage(self, hotel_id: int, percentage: float) -> int:
        """Increase all room prices in a hotel by a specified percentage
        
        Args:
            hotel_id: ID of the hotel
            percentage: Percentage increase (e.g., 10.0 for 10%)
            
        Returns:
            Number of rooms updated
        """
        try:
            cursor = self.conn.cursor()
            
            # Get all rooms in the hotel
            cursor.execute(
                "SELECT id, price_per_night FROM rooms WHERE hotel_id = ?",
                (hotel_id,)
            )
            rooms = cursor.fetchall()
            
            if not rooms:
                print(f"No rooms found for hotel ID {hotel_id}")
                return 0
                
            # Calculate new prices and update each room
            updated_count = 0
            for room_id, current_price in rooms:
                new_price = current_price * (1 + percentage / 100.0)
                cursor.execute(
                    "UPDATE rooms SET price_per_night = ? WHERE id = ?",
                    (new_price, room_id)
                )
                updated_count += cursor.rowcount
                
            self.conn.commit()
            print(f"Increased prices for {updated_count} rooms by {percentage}%")
            return updated_count
        except sqlite3.Error as e:
            print(f"Error increasing prices by percentage: {e}")
            self.conn.rollback()
            return 0

    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensure connection is closed"""
        self.close()

if __name__ == "__main__":
    # Example usage and testing
    print("Hotel Database Initialization")
    print("=" * 50)
    
    try:
        # Test 1: Basic functionality with default database location
        print("\n[TEST 1] Basic Hotel Creation")
        print("-" * 30)
        
        with HotelDatabase() as db:
            # Test creating a hotel
            hotel_id = db.create_hotel(
                name="Grand Hotel",
                address="123 Main Street, Cityville",
                stars=4,
                total_floors=5,
                total_rooms=100
            )
            print(f"✓ Created hotel with ID: {hotel_id}")
            
            # Create floors
            floor_ids = db.create_floors(hotel_id, 5)
            print(f"✓ Created {len(floor_ids)} floors")
            
            # Create room types
            room_types = [
                {"name": "Standard", "base_price": 120.00, "max_occupancy": 2, "description": "Standard room with queen bed"},
                {"name": "Deluxe", "base_price": 180.00, "max_occupancy": 3, "description": "Deluxe room with king bed and view"},
                {"name": "Suite", "base_price": 300.00, "max_occupancy": 4, "description": "Luxury suite with separate living area"}
            ]
            room_type_ids = db.create_room_types(room_types)
            print(f"✓ Created room types: {room_type_ids}")
            
            # Create rooms (20 per floor)
            rooms_created = db.create_rooms(hotel_id, floor_ids, room_type_ids, 20)
            print(f"✓ Created {rooms_created} rooms")
            
            # Test getting hotel info
            hotel_info = db.get_hotel_info(hotel_id)
            print(f"✓ Hotel info retrieved: {hotel_info['name']} ({hotel_info['stars']} stars)")
            
            # Test getting room status
            room_status = db.get_room_status(hotel_id, floor=1)
            print(f"✓ Room status for floor 1: {len(room_status)} rooms")
            for room in room_status[:3]:  # Show first 3 rooms
                print(f"  • Room {room['room_number']}: {room['status']} ({room['room_type']}) - ${room['price_per_night']}/night")
        
        # Test 2: Database in specific directory
        print("\n[TEST 2] Database in Specific Directory")
        print("-" * 30)
        
        with HotelDatabase(db_path="hotel_sim/test_hotel.db") as db:
            hotel_id2 = db.create_hotel(
                name="Beach Resort",
                address="456 Ocean Avenue, Seaside",
                stars=5,
                total_floors=3,
                total_rooms=50
            )
            print(f"✓ Created resort hotel with ID: {hotel_id2}")
            
            floor_ids2 = db.create_floors(hotel_id2, 3)
            
            # Create room types for this database too
            room_type_ids2 = db.create_room_types(room_types)
            rooms_created2 = db.create_rooms(hotel_id2, floor_ids2, room_type_ids2, 16)
            print(f"✓ Created {rooms_created2} rooms in resort")
        
        # Test 3: Validation
        print("\n[TEST 3] Input Validation")
        print("-" * 30)
        
        with HotelDatabase(db_path=":memory:") as db:  # In-memory database for testing
            try:
                db.create_hotel("", "", 0, 0, 0)
                print("✗ Validation failed - should have raised ValueError")
            except ValueError as ve:
                print(f"✓ Validation working: {ve}")
            
            try:
                db.create_hotel("Test", "Address", 6, 10, 100)  # 6 stars should fail
                print("✗ Validation failed - should have rejected 6 stars")
            except ValueError as ve:
                print(f"✓ Star validation working: {ve}")
        
        # Test 4: Query capabilities
        print("\n[TEST 4] Advanced Queries")
        print("-" * 30)
        
        with HotelDatabase() as db:
            # Get all suites on floor 2
            suites_floor2 = db.get_room_status(hotel_id, floor=2, room_type="Suite")
            print(f"✓ Found {len(suites_floor2)} suites on floor 2")
            
            # Get occupancy summary
            query = """
                SELECT 
                    status, 
                    COUNT(*) as count,
                    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM rooms WHERE hotel_id = ?), 2) as percentage
                FROM rooms 
                WHERE hotel_id = ?
                GROUP BY status
            """
            occupancy = db.execute_query(query, (hotel_id, hotel_id), fetch=True)
            print("✓ Occupancy summary:")
            for status in occupancy:
                print(f"  • {status['status']}: {status['count']} rooms ({status['percentage']}%)")
        
        print("\n" + "=" * 50)
        print("✓ ALL TESTS COMPLETED SUCCESSFULLY")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n✗ Error during database operations: {e}")
        import traceback
        traceback.print_exc()