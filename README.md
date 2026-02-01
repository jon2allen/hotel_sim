# Hotel Management Simulator

A comprehensive hotel management simulation system with database backend, simulation engine, reporting system, and CLI interface.

## 🏨 Project Overview

The Hotel Management Simulator is a Python-based application that simulates hotel operations including room management, reservations, transactions, housekeeping, and financial reporting. It provides a complete hotel management ecosystem with:

- **Database System**: SQLite backend with comprehensive schema
- **Simulation Engine**: Realistic hotel operations simulation
- **Reporting System**: Detailed analytics and status reports
- **CLI Interface**: Interactive and batch mode operations
- **Hotel Creation Wizard**: Guided hotel setup process

## 🚀 Features

### ✅ Phase 1: Database Setup - COMPLETE
- SQLite database with 8 tables (hotel, floors, rooms, guests, reservations, transactions, housekeeping, room_types)
- Comprehensive data access layer
- Transaction management and error handling

### ✅ Phase 2: Core Classes - COMPLETE
- Hotel, Floor, and Room management
- Guest and Reservation system
- Transaction processing
- Housekeeping operations

### ✅ Phase 3: Simulation Engine - COMPLETE
- Random event generation (reservations, check-ins, check-outs)
- Daily operations simulation
- Time advancement and date handling
- Realistic guest behavior patterns

### ✅ Phase 4: Reporting System - COMPLETE
- Hotel status reports
- Financial summaries
- Occupancy analysis
- Detailed room status displays

### ✅ Phase 5: CLI Interface - COMPLETE
- Command-line argument parsing
- Interactive REPL mode with auto-completion
- Batch simulation mode
- Comprehensive command set

### ✅ Hotel Creation Wizard - COMPLETE
- Interactive guided hotel creation
- Room type selection and distribution
- Automatic floor and room generation
- Pricing configuration
- Progress feedback and validation

## 📁 Project Structure

```
hotel_sim/
├── database.py                  # Database operations and schema
├── hotel.db                     # SQLite database
├── hotel_cli.py                 # CLI interface
├── hotel_simulator.py           # Core simulation logic
├── simulation_engine.py         # Simulation engine
├── reporting_system.py          # Reporting functions
├── test_hotel.db                # Test database
├── test_reporting.py            # Reporting tests
├── test_phase5.py               # CLI tests
├── spec.md                      # Project specification
├── PHASE5_COMPLETE.md           # Phase 5 completion report
├── wizard.md                    # Hotel wizard specification
├── README.md                    # This file
└── [other documentation files]
```

## 🛠️ Installation

### Prerequisites
- Python 3.6+
- SQLite 3

### Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/hotel-simulator.git
cd hotel-simulator

# Install dependencies
pip install -r requirements.txt
```

### Dependencies
- `sqlite3` (included with Python)
- `tabulate` (for pretty printing)
- `faker` (for test data generation)

## 🎯 Usage

### Basic CLI Commands

```bash
# Create a new hotel
python3 hotel_cli.py create --name "Grand Hotel" --address "123 Main St" --stars 5 --floors 10 --rooms 100

# List all hotels
python3 hotel_cli.py list

# Get hotel information
python3 hotel_cli.py info --hotel-id 1

# Run batch simulation
python3 hotel_cli.py batch --hotel-id 1 --days 30

# Start interactive mode
python3 hotel_cli.py interactive
```

### Interactive Mode

```bash
python3 hotel_cli.py interactive
```

Then use commands like:
- `create_hotel <name> <address> <stars> <floors> <rooms>`
- `list_hotels`
- `hotel_info <hotel_id>`
- `create_room <hotel_id> <floor> <room_number> <room_type>`
- `book_room <hotel_id> <room_id> <guest_name> <check_in> <check_out>`
- `run_simulation <hotel_id> <days>`
- `hotel_status <hotel_id>`
- `financial_report <hotel_id>`
- `occupancy_report <hotel_id>`
- `exit` or `quit`

### Hotel Creation Wizard

```bash
# Start the interactive wizard
python3 hotel_cli.py wizard
```

The wizard guides you through:
1. Basic hotel information (name, address, stars, floors, rooms)
2. Room type selection
3. Room distribution (manual or random)
4. Room pricing configuration
5. Automatic room creation with progress feedback

## 📊 Database Schema

The system uses a comprehensive SQLite database with these tables:

- **hotel**: Hotel information (name, address, stars, floors, rooms)
- **floors**: Floor information for each hotel
- **room_types**: Room type definitions (Standard, Deluxe, Suite, etc.)
- **rooms**: Individual room details (number, type, status, pricing)
- **guests**: Guest information
- **reservations**: Reservation records
- **transactions**: Financial transactions
- **housekeeping**: Housekeeping status

## 🧪 Testing

The project includes comprehensive test suites:

```bash
# Run reporting tests
python3 test_reporting.py

# Run CLI tests
python3 test_phase5.py

# Run wizard tests
python3 test_wizard.py
```

## 📈 Simulation Features

- **Random Event Generation**: Reservations, check-ins, check-outs, cancellations
- **Realistic Guest Behavior**: Different guest types with varying stay patterns
- **Seasonal Variations**: Price adjustments based on season and weekends
- **Housekeeping Operations**: Room cleaning and maintenance simulation
- **Financial Transactions**: Payment processing and revenue tracking

## 📊 Reporting Capabilities

- **Hotel Status**: Overall occupancy and operational status
- **Financial Reports**: Revenue, expenses, and profitability
- **Occupancy Analysis**: Room utilization and availability
- **Room Status**: Detailed room-by-room information
- **Guest Reports**: Guest information and loyalty programs

## 🎮 Example Usage

### Create and Simulate a Hotel

```bash
# Create a hotel using the wizard
python3 hotel_cli.py wizard

# Or create manually
python3 hotel_cli.py create --name "Grand Hotel" --address "123 Main St" --stars 5 --floors 10 --rooms 100

# Add some rooms
python3 hotel_cli.py room --hotel-id 1 --floor 1 --room-number "101" --room-type "Standard"
python3 hotel_cli.py room --hotel-id 1 --floor 1 --room-number "102" --room-type "Deluxe"

# Run a 30-day simulation
python3 hotel_cli.py batch --hotel-id 1 --days 30

# Check the results
python3 hotel_cli.py interactive
hotel> hotel_status 1
hotel> financial_report 1
hotel> exit
```

## 🔧 Configuration

The simulation uses configurable parameters:

```python
SIMULATION_CONFIG = {
    'new_reservation_probability': 0.3,
    'check_in_probability': 0.4,
    'check_out_probability': 0.35,
    'cancellation_probability': 0.05,
    'housekeeping_delay_probability': 0.02,
    'average_stay_days': (1, 7),
    'guest_types': ['business', 'leisure', 'family', 'group'],
    'seasonal_price_variation': 0.2,
    'weekend_price_multiplier': 1.15,
}
```

## 📋 Project Status

- **Phase 1 (Database)**: ✅ Complete
- **Phase 2 (Core Classes)**: ✅ Complete  
- **Phase 3 (Simulation Engine)**: ✅ Complete
- **Phase 4 (Reporting System)**: ✅ Complete
- **Phase 5 (CLI Interface)**: ✅ Complete
- **Hotel Wizard**: ✅ Complete

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m 'Add some feature'`
4. Push to the branch: `git push origin feature/your-feature`
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📬 Contact

For questions or support, please contact:
- Project Maintainer: [Your Name]
- Email: [your.email@example.com]
- GitHub Issues: [https://github.com/yourusername/hotel-simulator/issues](https://github.com/yourusername/hotel-simulator/issues)

## 🎯 Future Enhancements

- Web interface using Flask/Django
- Mobile app integration
- Advanced analytics dashboard
- Multi-hotel management
- Staff scheduling simulation
- Restaurant and amenities management
- Loyalty program enhancements

---

**Hotel Management Simulator** - Your complete hotel simulation solution! 🏨💻