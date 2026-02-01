# Hotel Simulator Specification

## Project Overview
**Name**: Hotel Management Simulator
**Location**: `hotel_sim/`
**Language**: Python 3.x
**Database**: SQLite
**Purpose**: Simulate hotel operations including room management, reservations, transactions, and reporting

## System Architecture

### Database Schema (SQLite)

```sql
-- Hotel Structure
CREATE TABLE hotel (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    address TEXT,
    stars INTEGER,
    total_floors INTEGER,
    total_rooms INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Floors
CREATE TABLE floors (
    id INTEGER PRIMARY KEY,
    hotel_id INTEGER,
    floor_number INTEGER,
    description TEXT,
    FOREIGN KEY (hotel_id) REFERENCES hotel(id)
);

-- Room Types
CREATE TABLE room_types (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    base_price DECIMAL(10,2),
    max_occupancy INTEGER,
    amenities TEXT
);

-- Rooms
CREATE TABLE rooms (
    id INTEGER PRIMARY KEY,
    hotel_id INTEGER,
    floor_id INTEGER,
    room_number TEXT NOT NULL,
    room_type_id INTEGER,
    status TEXT DEFAULT 'available',
    price_per_night DECIMAL(10,2),
    max_occupancy INTEGER,
    FOREIGN KEY (hotel_id) REFERENCES hotel(id),
    FOREIGN KEY (floor_id) REFERENCES floors(id),
    FOREIGN KEY (room_type_id) REFERENCES room_types(id)
);

-- Guests
CREATE TABLE guests (
    id INTEGER PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT,
    phone TEXT,
    address TEXT,
    loyalty_points INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Reservations
CREATE TABLE reservations (
    id INTEGER PRIMARY KEY,
    room_id INTEGER,
    guest_id INTEGER,
    check_in_date TEXT NOT NULL,
    check_out_date TEXT NOT NULL,
    status TEXT DEFAULT 'confirmed',
    total_price DECIMAL(10,2),
    booking_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    payment_status TEXT DEFAULT 'pending',
    FOREIGN KEY (room_id) REFERENCES rooms(id),
    FOREIGN KEY (guest_id) REFERENCES guests(id)
);

-- Transactions
CREATE TABLE transactions (
    id INTEGER PRIMARY KEY,
    reservation_id INTEGER,
    amount DECIMAL(10,2) NOT NULL,
    transaction_type TEXT NOT NULL,
    payment_method TEXT,
    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    description TEXT,
    FOREIGN KEY (reservation_id) REFERENCES reservations(id)
);

-- Housekeeping
CREATE TABLE housekeeping (
    id INTEGER PRIMARY KEY,
    room_id INTEGER,
    status TEXT DEFAULT 'clean',
    last_cleaned TIMESTAMP,
    notes TEXT,
    FOREIGN KEY (room_id) REFERENCES rooms(id)
);
```

## Python Class Structure

### Core Classes

```python
class HotelSimulator:
    def __init__(self, db_path='hotel.db'):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self._initialize_database()

    def create_hotel(self, name, floors, rooms_per_floor, room_types):
        """Create a new hotel with specified structure"""
        # Implementation details

    def _initialize_database(self):
        """Create all tables if they don't exist"""
        # Execute CREATE TABLE statements

class ReservationSystem:
    def __init__(self, db_connection):
        self.conn = db_connection

    def make_reservation(self, guest_id, room_id, check_in, check_out):
        """Create a new reservation"""
        # Validation and creation logic

    def check_in(self, reservation_id):
        """Process guest check-in"""
        # Update statuses

    def check_out(self, reservation_id):
        """Process guest check-out"""
        # Finalize charges

class HotelSimulatorEngine:
    def __init__(self, hotel_id, days_to_simulate=30):
        self.hotel_id = hotel_id
        self.days_to_simulate = days_to_simulate
        self.current_date = datetime.now()

    def run_simulation(self):
        """Run simulation for specified number of days"""
        for day in range(self.days_to_simulate):
            self.current_date += timedelta(days=1)
            self._simulate_daily_operations()
            self._generate_daily_report()

class HotelReporter:
    def __init__(self, db_connection):
        self.conn = db_connection

    def display_hotel_status(self):
        """Show overall hotel occupancy and status"""
        # Display summaries

    def display_room_status(self, floor=None, room_type=None):
        """Show detailed room status"""
        # Filter and display rooms
```

## Simulation Configuration

```python
SIMULATION_CONFIG = {
    # Probability settings
    'new_reservation_probability': 0.3,
    'check_in_probability': 0.4,
    'check_out_probability': 0.35,
    'cancellation_probability': 0.05,
    'housekeeping_delay_probability': 0.02,

    # Guest behavior
    'average_stay_days': (1, 7),
    'guest_types': ['business', 'leisure', 'family', 'group'],

    # Pricing
    'seasonal_price_variation': 0.2,
    'weekend_price_multiplier': 1.15,
}
```

## Implementation Plan

### Phase 1: Database Setup
1. Create SQLite database with all tables
2. Implement database initialization
3. Create data access layer

### Phase 2: Core Classes
1. Implement Hotel, Floor, Room classes
2. Implement Guest and Reservation classes
3. Implement Transaction processing

### Phase 3: Simulation Engine
1. Implement random event generation
2. Create daily operation simulation
3. Implement time advancement

### Phase 4: Reporting System
1. Implement status display functions
2. Create financial reporting
3. Build occupancy analysis

### Phase 5: CLI Interface
1. Create command-line interface
2. Implement interactive mode
3. Add batch simulation mode

## Example Usage

```python
# Initialize simulator
hotel_sim = HotelSimulator('my_hotel.db')

# Create hotel
hotel_sim.create_hotel(
    name="Grand Hotel",
    floors=10,
    rooms_per_floor=20,
    room_types=[
        {"name": "Standard", "base_price": 120.00, "max_occupancy": 2},
        {"name": "Deluxe", "base_price": 180.00, "max_occupancy": 3},
        {"name": "Suite", "base_price": 300.00, "max_occupancy": 4}
    ]
)

# Run simulation
simulator = HotelSimulatorEngine(hotel_id=1, days_to_simulate=30)
simulator.run_simulation()

# Display status
reporter = HotelReporter(hotel_sim.conn)
reporter.display_hotel_status()
```

## Technical Requirements

1. **Python Libraries**: sqlite3, random, datetime, tabulate, faker
2. **Database Features**: Transactions, indexes, foreign keys
3. **Performance**: Batch inserts, efficient queries, memory management

## Error Handling

1. **Data Validation**: Date ranges, room availability, payments
2. **Error Recovery**: Transaction rollback, graceful failures
3. **Logging**: Comprehensive logging for debugging