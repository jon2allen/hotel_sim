import argparse
import sys
import cmd
import readline
from datetime import datetime, timedelta
from hotel_simulator import HotelSimulator, ReservationSystem
from database import HotelDatabase
from simulation_engine import HotelSimulationEngine
from reporting_system import HotelReportingSystem, ReportConfig, ReportType, TimePeriod
class HotelCLI(cmd.Cmd):
    """Interactive command-line interface for Hotel Simulator"""
    
    intro = "Welcome to Hotel Simulator CLI. Type 'help' or '?' to list commands.\n"
    prompt = 'hotel> '
    
    def __init__(self):
        super().__init__()
        self.db = HotelDatabase()
        self.simulator = HotelSimulator()
        self.reporter = HotelReportingSystem()
        self.res_system = ReservationSystem(self.db)
        
    def do_create_hotel(self, arg):
        """Create a new hotel: create_hotel <name> <address> <stars> <floors> <rooms>"""
        try:
            args = arg.split()
            if len(args) != 5:
                print("Usage: create_hotel <name> <address> <stars> <floors> <rooms>")
                return
            
            name, address, stars, floors, rooms = args
            hotel_id = self.db.create_hotel(name, address, int(stars), int(floors), int(rooms))
            print(f"Hotel created with ID: {hotel_id}")
        except Exception as e:
            print(f"Error: {e}")
    
    def do_list_hotels(self, arg):
        """List all hotels"""
        try:
            hotels = self.db.execute_query('SELECT * FROM hotel', fetch=True)
            if hotels:
                for hotel in hotels:
                    print(f"ID: {hotel['id']}, Name: {hotel['name']}, Address: {hotel['address']}")
            else:
                print("No hotels found.")
        except Exception as e:
            print(f"Error: {e}")
    
    def do_daily_report(self, arg):
        """Generate daily status report: daily_report <hotel_id> [YYYY-MM-DD]"""
        try:
            args = arg.split()
            if len(args) < 1:
                print("Usage: daily_report <hotel_id> [YYYY-MM-DD]")
                print("Example: daily_report 1 2026-02-01")
                return
            
            hotel_id = int(args[0])
            date = args[1] if len(args) > 1 else None
            
            # Validate date format if provided
            if date:
                try:
                    datetime.strptime(date, '%Y-%m-%d')
                except ValueError:
                    print(f"❌ Invalid date format: {date}")
                    print("📅 Date should be in YYYY-MM-DD format. Example: 2026-02-01")
                    return
            
            # Create report configuration
            config = ReportConfig(
                report_type=ReportType.DAILY_STATUS,
                time_period=TimePeriod.DAILY,
                hotel_id=hotel_id,
                specific_date=date
            )
            
            # Generate report
            report = self.reporter.generate_report(config)
            result = self.reporter.display_report(report, "text")
            print(result)
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def do_occupancy_report(self, arg):
        """Generate occupancy analysis report: occupancy_report <hotel_id> [time_period] [start_date] [end_date]"""
        try:
            # Improved argument parsing to handle various formats
            parts = arg.split()
            if len(parts) < 1:
                print("Usage: occupancy_report <hotel_id> [time_period] [start_date] [end_date]")
                print("Example: occupancy_report 1 weekly")
                print("Example: occupancy_report 1 custom 2026-01-01 2026-01-31")
                return
            
            # Extract hotel_id (first argument)
            try:
                hotel_id = int(parts[0])
            except ValueError:
                print(f"❌ Invalid hotel ID: {parts[0]}")
                return
            
            # Parse remaining arguments
            remaining_args = parts[1:]
            
            # Parse time period (default: monthly)
            time_period = TimePeriod.MONTHLY
            start_date = None
            end_date = None
            
            if remaining_args:
                # Check if first remaining arg is a time period
                period_arg = remaining_args[0].upper()
                if period_arg in ['DAILY', 'WEEKLY', 'MONTHLY', 'QUARTERLY', 'YEARLY', 'CUSTOM']:
                    time_period = TimePeriod[period_arg]
                    remaining_args = remaining_args[1:]  # Remove time period from args
                else:
                    # First arg might be a date, default to daily period
                    time_period = TimePeriod.DAILY
            
            # Parse dates for custom period
            if time_period == TimePeriod.CUSTOM:
                if len(remaining_args) < 2:
                    print("❌ Custom period requires start_date and end_date")
                    print("Usage: occupancy_report <hotel_id> custom YYYY-MM-DD YYYY-MM-DD")
                    return
                
                try:
                    start_date = remaining_args[0]
                    end_date = remaining_args[1]
                    datetime.strptime(start_date, '%Y-%m-%d')
                    datetime.strptime(end_date, '%Y-%m-%d')
                except ValueError as e:
                    print(f"❌ Invalid date format: {e}")
                    print("📅 Date should be in YYYY-MM-DD format. Example: 2026-02-01")
                    return
            elif remaining_args:
                # For non-custom periods, remaining args might be dates for daily period
                if time_period == TimePeriod.DAILY and len(remaining_args) >= 1:
                    try:
                        # Treat as specific date for daily report
                        specific_date = remaining_args[0]
                        datetime.strptime(specific_date, '%Y-%m-%d')
                        # For daily occupancy, we can use a single day range
                        start_date = specific_date
                        end_date = specific_date
                        time_period = TimePeriod.CUSTOM
                    except ValueError as e:
                        print(f"❌ Invalid date format: {e}")
                        print("📅 Date should be in YYYY-MM-DD format. Example: 2026-02-01")
                        return
            
            # Create report configuration
            config = ReportConfig(
                report_type=ReportType.OCCUPANCY_ANALYSIS,
                time_period=time_period,
                hotel_id=hotel_id,
                start_date=start_date,
                end_date=end_date
            )
            
            # Generate report
            report = self.reporter.generate_report(config)
            result = self.reporter.display_report(report, "text")
            print(result)
            
        except Exception as e:
            print(f"❌ Error: {e}")
            
            # Create report configuration
            config = ReportConfig(
                report_type=ReportType.OCCUPANCY_ANALYSIS,
                time_period=time_period,
                hotel_id=hotel_id,
                start_date=start_date,
                end_date=end_date
            )
            
            # Generate report
            report = self.reporter.generate_report(config)
            result = self.reporter.display_report(report, "text")
            print(result)
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def do_hotel_info(self, arg):
        """Get hotel information: hotel_info <hotel_id>"""
        try:
            hotel_id = int(arg.strip())
            hotel_info = self.db.get_hotel_info(hotel_id)
            if hotel_info:
                print(f"Hotel ID: {hotel_info['id']}")
                print(f"Name: {hotel_info['name']}")
                print(f"Address: {hotel_info['address']}")
                print(f"Stars: {hotel_info['stars']}")
                print(f"Floors: {hotel_info['total_floors']}")
                print(f"Rooms: {hotel_info['total_rooms']}")
            else:
                print("Hotel not found.")
        except Exception as e:
            print(f"Error: {e}")
    
    def do_create_room(self, arg):
        """Create a new room: create_room <hotel_id> <floor> <room_number> <room_type> [price] [occupancy]"""
        try:
            args = arg.split()
            if len(args) < 4:
                print("Usage: create_room <hotel_id> <floor> <room_number> <room_type> [price] [occupancy]")
                return
            
            hotel_id, floor, room_number, room_type = args[:4]
            
            # Parse optional price and occupancy parameters
            price = 100.00
            occupancy = 2
            
            if len(args) >= 5:
                price = float(args[4])
            if len(args) >= 6:
                occupancy = int(args[5])
            
            room_id = self.db.create_room(int(hotel_id), int(floor), room_number, room_type, price, occupancy)
            print(f"Room created with ID: {room_id}")
        except Exception as e:
            print(f"Error: {e}")
    
    def do_list_room_types(self, arg):
        """List all room types"""
        try:
            room_types = self.db.execute_query(
                'SELECT id, name, description, base_price, max_occupancy FROM room_types', fetch=True)
            if room_types:
                print(f"Found {len(room_types)} room types:")
                for rt in room_types:
                    print(f"ID: {rt['id']}, Name: {rt['name']}, Price: ${rt['base_price']}, Occupancy: {rt['max_occupancy']}")
                    if rt['description']:
                        print(f"  Description: {rt['description']}")
            else:
                print("No room types found.")
        except Exception as e:
            print(f"Error: {e}")

    def do_list_rooms(self, arg):
        """List rooms in a hotel: list_rooms <hotel_id>"""
        try:
            hotel_id = int(arg.strip())
            rooms = self.db.execute_query(
                'SELECT r.id, r.room_number, r.status, rt.name as room_type, r.price_per_night ' 
                'FROM rooms r JOIN room_types rt ON r.room_type_id = rt.id ' 
                'WHERE r.hotel_id = ?', (hotel_id,), fetch=True)
            if rooms:
                for room in rooms:
                    print(f"ID: {room['id']}, Room: {room['room_number']}, Type: {room['room_type']}, Status: {room['status']}, Price: ${room['price_per_night']}/night")
            else:
                print("No rooms found.")
        except Exception as e:
            print(f"Error: {e}")
    
    def do_book_room(self, arg):
        """Book a room: book_room <hotel_id> <room_id> <guest_name> <check_in> <check_out>"""
        try:
            args = arg.split()
            if len(args) != 5:
                print("Usage: book_room <hotel_id> <room_id> <guest_name> <check_in> <check_out>")
                return
            
            hotel_id, room_id, guest_name, check_in, check_out = args
            booking_id = self.db.book_room(int(hotel_id), int(room_id), guest_name, check_in, check_out)
            print(f"Booking created with ID: {booking_id}")
        except Exception as e:
            print(f"Error: {e}")

    def do_check_in(self, arg):
        """Process guest check-in: check_in <reservation_id>"""
        try:
            if not arg:
                print("Usage: check_in <reservation_id>")
                return
            
            res_id = int(arg)
            if self.res_system.check_in(res_id):
                print(f"✅ Checked in reservation #{res_id}")
            else:
                print(f"❌ Check-in failed for reservation #{res_id}")
                
        except ValueError:
            print("❌ Invalid reservation ID. Please provide a numeric ID.")
        except Exception as e:
            print(f"❌ Error during check-in: {e}")

    def do_check_out(self, arg):
        """Process guest check-out: check_out <reservation_id>"""
        try:
            if not arg:
                print("Usage: check_out <reservation_id>")
                return
            
            res_id = int(arg)
            success, final_amount = self.res_system.check_out(res_id)
            
            if success:
                print(f"✅ Checked out reservation #{res_id}")
                print(f"💰 Final charges: ${final_amount:.2f}")
            else:
                print(f"❌ Check-out failed for reservation #{res_id}")
                
        except ValueError:
            print("❌ Invalid reservation ID. Please provide a numeric ID.")
        except Exception as e:
            print(f"❌ Error during check-out: {e}")
    
    def do_run_simulation(self, arg):
        """Run simulation: run_simulation <hotel_id> <days>"""
        try:
            args = arg.split()
            if len(args) != 2:
                print("Usage: run_simulation <hotel_id> <days>")
                return
            
            hotel_id, days = args
            engine = HotelSimulationEngine(int(hotel_id))
            results = engine.run_simulation(int(days))
            print(f"Simulation completed. Days: {days}, Results: {results}")
        except Exception as e:
            print(f"Error: {e}")
    
    def do_hotel_status(self, arg):
        """Get hotel status: hotel_status <hotel_id>"""
        try:
            hotel_id = int(arg.strip())
            from reporting_system import ReportConfig, ReportType, TimePeriod
            config = ReportConfig(
                report_type=ReportType.DAILY_STATUS,
                time_period=TimePeriod.DAILY,
                hotel_id=hotel_id
            )
            report = self.reporter.generate_report(config)
            print(self.reporter.display_report(report))
        except Exception as e:
            print(f"Error: {e}")
    
    def do_financial_report(self, arg):
        """Get financial report: financial_report <hotel_id> [time_period] [start_date] [end_date]"""
        try:
            # Import at the beginning of the method
            from reporting_system import ReportConfig, ReportType, TimePeriod
            from datetime import datetime
            
            # Parse arguments similar to occupancy_report
            parts = arg.split()
            if len(parts) < 1:
                print("Usage: financial_report <hotel_id> [time_period] [start_date] [end_date]")
                print("Example: financial_report 1 weekly")
                print("Example: financial_report 1 custom 2026-01-01 2026-01-31")
                return
            
            # Extract hotel_id (first argument)
            try:
                hotel_id = int(parts[0])
            except ValueError:
                print(f"❌ Invalid hotel ID: {parts[0]}")
                return
            
            # Parse time period (default: monthly)
            time_period = TimePeriod.MONTHLY
            start_date = None
            end_date = None
            
            if len(parts) > 1:
                # Check if first remaining arg is a time period
                period_arg = parts[1].upper()
                if period_arg in ['DAILY', 'WEEKLY', 'MONTHLY', 'QUARTERLY', 'YEARLY', 'CUSTOM']:
                    time_period = TimePeriod[period_arg]
                    if time_period == TimePeriod.CUSTOM and len(parts) < 4:
                        print("❌ Custom period requires start_date and end_date")
                        print("Usage: financial_report <hotel_id> custom YYYY-MM-DD YYYY-MM-DD")
                        return
                    
                    # Parse dates for custom period
                    if time_period == TimePeriod.CUSTOM:
                        try:
                            start_date = parts[2]
                            end_date = parts[3]
                            datetime.strptime(start_date, '%Y-%m-%d')
                            datetime.strptime(end_date, '%Y-%m-%d')
                        except ValueError as e:
                            print(f"❌ Invalid date format: {e}")
                            print("📅 Date should be in YYYY-MM-DD format. Example: 2026-02-01")
                            return
            config = ReportConfig(
                report_type=ReportType.FINANCIAL_SUMMARY,
                time_period=time_period,
                hotel_id=hotel_id,
                start_date=start_date,
                end_date=end_date
            )
            report = self.reporter.generate_report(config)
            print(self.reporter.display_report(report))
        except Exception as e:
            print(f"Error: {e}")
    
    def do_room_report(self, arg):
        """Generate room-specific report: room_report <hotel_id> <room_number> [YYYY-MM-DD] [YYYY-MM-DD]"""
        try:
            args = arg.split()
            if len(args) < 2:
                print("Usage: room_report <hotel_id> <room_number> [start_date] [end_date]")
                print("Example: room_report 1 101 2026-01-01 2026-01-31")
                print("Example: room_report 1 101 2026-01-15  # Single date")
                return
             
            hotel_id = int(args[0])
            room_number = args[1]  # Use room number instead of room ID
             
            # Parse date parameters
            start_date = None
            end_date = None
             
            if len(args) >= 3:
                # Check if third argument is a date or 'today'
                if args[2].lower() in ['today', 'current']:
                    start_date = datetime.now().strftime('%Y-%m-%d')
                    end_date = start_date
                else:
                    try:
                        datetime.strptime(args[2], '%Y-%m-%d')
                        start_date = args[2]
                        end_date = args[2]  # Single date
                    except ValueError:
                        print(f"❌ Invalid date format: {args[2]}")
                        print("📅 Date should be in YYYY-MM-DD format. Example: 2026-02-01")
                        return
             
            if len(args) >= 4:
                try:
                    datetime.strptime(args[3], '%Y-%m-%d')
                    end_date = args[3]
                except ValueError:
                    print(f"❌ Invalid date format: {args[3]}")
                    print("📅 Date should be in YYYY-MM-DD format. Example: 2026-02-01")
                    return
             
            # Validate dates
            if start_date and end_date and start_date > end_date:
                print("❌ Start date cannot be after end date")
                return
             
            # Create report configuration
            time_period = TimePeriod.CUSTOM if (start_date and end_date and start_date != end_date) else TimePeriod.DAILY
             
            config = ReportConfig(
                report_type=ReportType.ROOM_SPECIFIC_REPORT,
                time_period=time_period,
                hotel_id=hotel_id,
                room_number=room_number,
                start_date=start_date,
                end_date=end_date,
                specific_date=start_date if time_period == TimePeriod.DAILY else None
            )
             
            # Generate report
            report = self.reporter.generate_report(config)
            result = self.reporter.display_report(report, "text")
            print(result)
             
        except Exception as e:
            print(f"❌ Error: {e}")

    def do_list_reservations(self, arg):
        """List all reservations: list_reservations [hotel_id]"""
        try:
            # Query joining reservations, rooms, hotel, and guests
            query = """
                SELECT 
                    r.id, 
                    h.id as hotel_id, 
                    h.name as hotel_name, 
                    g.first_name || ' ' || g.last_name as guest_name,
                    rm.room_number,
                    r.check_in_date,
                    r.check_out_date,
                    r.status
                FROM reservations r
                JOIN rooms rm ON r.room_id = rm.id
                JOIN hotel h ON rm.hotel_id = h.id
                JOIN guests g ON r.guest_id = g.id
            """
            params = []
            
            # Optional: Filter by hotel_id if provided as an argument
            if arg:
                try:
                    query += " WHERE h.id = ?"
                    params.append(int(arg))
                except ValueError:
                    print("❌ Invalid hotel ID. Please provide a numeric ID.")
                    return
            
            query += " ORDER BY r.id DESC"
            
            reservations = self.db.execute_query(query, tuple(params) if params else None, fetch=True)
            
            if not reservations:
                print("No reservations found.")
                return
            # Print Header
            print(f"\n{'ID':<5} {'Hotel (ID)':<25} {'Guest':<20} {'Room':<10} {'Dates':<23} {'Status':<10}")
            print("-" * 95)
            
            # Print Rows
            for res in reservations:
                hotel_display = f"{res['hotel_name']} ({res['hotel_id']})"
                dates_display = f"{res['check_in_date']} -> {res['check_out_date']}"
                
                # Apply simple status indicator
                status = res['status'].upper()
                if status == 'CHECKED_IN':
                    status = f"🟢 {status}"
                elif status == 'CHECKED_OUT':
                    status = f"⚪ {status}"
                elif status == 'CANCELLED':
                    status = f"🔴 {status}"
                else:
                    status = f"🔵 {status}"
                print(f"{res['id']:<5} {hotel_display[:24]:<25} {res['guest_name'][:19]:<20} {res['room_number']:<10} {dates_display:<23} {status}")
                
        except Exception as e:
            print(f"❌ Error listing reservations: {e}")
    
    def do_create_hotel_interactive(self, arg):
        """Interactive hotel creation wizard - guides you through creating a complete hotel with rooms, floors, and pricing"""
        try:
            print("\n=== Hotel Creation Wizard ===")
            
            # Get basic hotel information
            print("\n--- Basic Hotel Information ---")
            name = input("Enter hotel name: ").strip()
            if not name:
                print("Error: Hotel name cannot be empty")
                return
                
            address = input("Enter hotel address: ").strip()
            if not address:
                print("Error: Hotel address cannot be empty")
                return
                
            stars = input("Enter star rating (1-5): ").strip()
            try:
                stars = int(stars)
                if stars < 1 or stars > 5:
                    print("Error: Star rating must be between 1 and 5")
                    return
            except ValueError:
                print("Error: Star rating must be a number")
                return
                
            floors = input("Enter number of floors: ").strip()
            try:
                floors = int(floors)
                if floors < 1:
                    print("Error: Number of floors must be at least 1")
                    return
            except ValueError:
                print("Error: Number of floors must be a number")
                return
                
            rooms = input("Enter total number of rooms: ").strip()
            try:
                rooms = int(rooms)
                if rooms < 1:
                    print("Error: Number of rooms must be at least 1")
                    return
            except ValueError:
                print("Error: Number of rooms must be a number")
                return
            
            # Create the hotel
            hotel_id = self.db.create_hotel(name, address, stars, floors, rooms)
            print(f"\n✓ Hotel '{name}' created successfully with ID: {hotel_id}")
            
            # Get room type information
            print("\n--- Room Types Setup ---")
            print("Let's set up the room types for your hotel.")
            
            # Get available room types from database
            room_types = self.db.execute_query("SELECT id, name FROM room_types", fetch=True)
            if not room_types:
                print("No room types found in database. Let's create some standard room types first.")
                
                # Create standard room types if none exist
                standard_room_types = [
                    {"name": "Standard", "base_price": 120.00, "max_occupancy": 2, "description": "Standard room with queen bed"},
                    {"name": "Deluxe", "base_price": 180.00, "max_occupancy": 3, "description": "Deluxe room with king bed and view"},
                    {"name": "Suite", "base_price": 300.00, "max_occupancy": 4, "description": "Luxury suite with separate living area"},
                    {"name": "King", "base_price": 150.00, "max_occupancy": 2, "description": "Room with king-sized bed"},
                    {"name": "Basic", "base_price": 80.00, "max_occupancy": 2, "description": "Basic room with essential amenities"}
                ]
                
                # Create the room types
                for room_type in standard_room_types:
                    try:
                        self.db.execute_query(
                            "INSERT INTO room_types (name, description, base_price, max_occupancy) VALUES (?, ?, ?, ?)",
                            (room_type["name"], room_type["description"], room_type["base_price"], room_type["max_occupancy"])
                        )
                    except Exception as e:
                        # Room type might already exist, that's okay
                        pass
                
                # Refresh room types list
                room_types = self.db.execute_query("SELECT id, name FROM room_types", fetch=True)
                print(f"✓ Created {len(room_types)} standard room types")
            
            # Ask if user wants to add custom room types
            add_custom = input(f"\nWould you like to add custom room types? (y/n): ").strip().lower()
            if add_custom in ['y', 'yes']:
                while True:
                    print("\n--- Add Custom Room Type ---")
                    
                    # Get room type details
                    room_type_name = input("Enter room type name (or 'done' to finish): ").strip()
                    if room_type_name.lower() in ['done', 'finish', 'exit', 'quit']:
                        break
                    
                    if not room_type_name:
                        print("Error: Room type name cannot be empty")
                        continue
                    
                    # Check if room type already exists
                    existing_check = self.db.execute_query(
                        "SELECT id FROM room_types WHERE name = ?", 
                        (room_type_name,), 
                        fetch=True
                    )
                    
                    if existing_check:
                        print(f"Room type '{room_type_name}' already exists")
                        continue
                    
                    # Get description (optional)
                    description = input("Enter description (optional): ").strip()
                    
                    # Get base price
                    while True:
                        base_price_input = input("Enter base price per night (e.g., 150.00): $").strip()
                        try:
                            base_price = float(base_price_input)
                            if base_price <= 0:
                                print("Error: Price must be positive")
                                continue
                            break
                        except ValueError:
                            print("Error: Please enter a valid price")
                    
                    # Get max occupancy
                    while True:
                        occupancy_input = input("Enter maximum occupancy (1-6): ").strip()
                        try:
                            max_occupancy = int(occupancy_input)
                            if max_occupancy < 1 or max_occupancy > 6:
                                print("Error: Occupancy must be between 1 and 6")
                                continue
                            break
                        except ValueError:
                            print("Error: Please enter a valid number")
                    
                    # Create the custom room type
                    try:
                        self.db.execute_query(
                            "INSERT INTO room_types (name, description, base_price, max_occupancy) VALUES (?, ?, ?, ?)",
                            (room_type_name, description, base_price, max_occupancy)
                        )
                        print(f"✓ Created custom room type: {room_type_name}")
                        
                        # Refresh room types list
                        room_types = self.db.execute_query("SELECT id, name FROM room_types", fetch=True)
                        
                    except Exception as e:
                        print(f"Error creating room type: {e}")
                
            print("\nAvailable room types:")
            for i, rt in enumerate(room_types, 1):
                print(f"{i}. {rt['name']}")
            
            # Ask user to select room types
            selected_types = []
            while True:
                choice = input(f"\nEnter room type numbers to include (1-{len(room_types)}, comma-separated): ").strip()
                if not choice:
                    print("Error: Please select at least one room type")
                    continue
                    
                try:
                    choices = [int(c.strip()) for c in choice.split(',')]
                    if any(c < 1 or c > len(room_types) for c in choices):
                        print(f"Error: Please enter numbers between 1 and {len(room_types)}")
                        continue
                    
                    selected_types = [room_types[c-1] for c in choices]
                    break
                except ValueError:
                    print("Error: Please enter valid numbers separated by commas")
            
            # Ask about room distribution
            print(f"\n--- Room Distribution (Total: {rooms} rooms) ---")
            distribution_choice = input("How would you like to distribute rooms?\n1. Define exact numbers for each type\n2. Use random distribution\nEnter choice (1-2): ").strip()
            
            room_distribution = {}
            if distribution_choice == '1':
                # Manual distribution
                remaining_rooms = rooms
                for rt in selected_types:
                    while True:
                        count = input(f"Number of {rt['name']} rooms (remaining: {remaining_rooms}): ").strip()
                        try:
                            count = int(count)
                            if count < 0:
                                print("Error: Cannot have negative rooms")
                                continue
                            if count > remaining_rooms:
                                print(f"Error: Cannot have more than {remaining_rooms} rooms")
                                continue
                            
                            room_distribution[rt['id']] = count
                            remaining_rooms -= count
                            break
                        except ValueError:
                            print("Error: Please enter a valid number")
                
                if remaining_rooms > 0:
                    print(f"Warning: {remaining_rooms} rooms not assigned. They will be distributed randomly.")
                    # Add remaining rooms to random distribution
                    for rt in selected_types:
                        room_distribution[rt['id']] = room_distribution.get(rt['id'], 0) + remaining_rooms // len(selected_types)
                    
            elif distribution_choice == '2':
                # Random distribution
                print("Using random distribution...")
                import random
                remaining_rooms = rooms
                
                # Distribute most rooms randomly
                for i, rt in enumerate(selected_types):
                    if i == len(selected_types) - 1:
                        # Last type gets remaining rooms
                        room_distribution[rt['id']] = remaining_rooms
                    else:
                        # Random portion for this type
                        portion = random.randint(1, remaining_rooms - (len(selected_types) - i - 1))
                        room_distribution[rt['id']] = portion
                        remaining_rooms -= portion
            else:
                print("Error: Invalid choice")
                return
            
            # Get pricing information
            print("\n--- Room Pricing ---")
            room_prices = {}
            for rt in selected_types:
                while True:
                    price = input(f"Enter base price for {rt['name']} rooms (e.g., 150.00): $").strip()
                    try:
                        price = float(price)
                        if price <= 0:
                            print("Error: Price must be positive")
                            continue
                        room_prices[rt['id']] = price
                        break
                    except ValueError:
                        print("Error: Please enter a valid price")
            
            # Create rooms
            print(f"\n--- Creating Rooms ---")
            rooms_created = 0
            
            # Create floors first
            for floor_num in range(1, floors + 1):
                self.db.execute_query(
                    "INSERT INTO floors (hotel_id, floor_number, description) VALUES (?, ?, ?)",
                    (hotel_id, floor_num, f"Floor {floor_num}")
                )
            
            # Get floor IDs
            floor_data = self.db.execute_query(
                "SELECT id, floor_number FROM floors WHERE hotel_id = ? ORDER BY floor_number",
                (hotel_id,), fetch=True
            )
            
            # Create rooms
            room_number = 1
            for rt in selected_types:
                rt_id = rt['id']
                count = room_distribution.get(rt_id, 0)
                price = room_prices.get(rt_id, 100.00)
                
                for i in range(count):
                    # Distribute rooms across floors
                    floor_idx = i % len(floor_data)
                    floor_id = floor_data[floor_idx]['id']
                    floor_num = floor_data[floor_idx]['floor_number']
                    
                    room_num = f"{floor_num}{room_number:02d}"
                    
                    # Create the room
                    self.db.create_room(hotel_id, floor_num, room_num, rt['name'], price)
                    rooms_created += 1
                    room_number += 1
            
            print(f"✓ Created {rooms_created} rooms for hotel '{name}'")
            print(f"\n🎉 Hotel creation complete!")
            print(f"Hotel ID: {hotel_id}")
            print(f"Name: {name}")
            print(f"Address: {address}")
            print(f"Stars: {'★' * stars}")
            print(f"Floors: {floors}")
            print(f"Rooms: {rooms_created}")
            
            # Show room type summary
            print(f"\nRoom Type Summary:")
            for rt in selected_types:
                count = room_distribution.get(rt['id'], 0)
                price = room_prices.get(rt['id'], 100.00)
                if count > 0:
                    print(f"  • {rt['name']}: {count} rooms at ${price:.2f}/night")
                    
        except Exception as e:
            print(f"Error during hotel creation: {e}")
            self.db.conn.rollback()
    
    def do_add_guest(self, arg):
        """Add a new guest using interactive wizard: add_guest"""
        try:
            from guest_wizard import GuestWizard
            wizard = GuestWizard()
            wizard.add_guest_wizard()
        except ImportError:
            print("❌ Guest wizard not available. Please ensure guest_wizard.py is in the same directory.")
        except Exception as e:
            print(f"❌ Error in guest wizard: {e}")
    
    def do_search_guests(self, arg):
        """Search for guests using interactive wizard: search_guests"""
        try:
            from guest_wizard import GuestWizard
            wizard = GuestWizard()
            wizard.search_guest_wizard()
        except ImportError:
            print("❌ Guest wizard not available. Please ensure guest_wizard.py is in the same directory.")
        except Exception as e:
            print(f"❌ Error in guest wizard: {e}")
    
    def do_guest_menu(self, arg):
        """Open guest management menu: guest_menu"""
        try:
            from guest_wizard import GuestWizard
            wizard = GuestWizard()
            wizard.main_menu()
        except ImportError:
            print("❌ Guest wizard not available. Please ensure guest_wizard.py is in the same directory.")
        except Exception as e:
            print(f"❌ Error in guest wizard: {e}")
    
    def do_search_checkins(self, arg):
        """Search for reservations to check in: search_checkins"""
        try:
            from checkin_wizard import CheckinWizard
            wizard = CheckinWizard()
            wizard.search_reservations_wizard()
        except ImportError:
            print("❌ Check-in wizard not available. Please ensure checkin_wizard.py is in the same directory.")
        except Exception as e:
            print(f"❌ Error in check-in wizard: {e}")
    
    def do_interactive_checkin(self, arg):
        """Interactive check-in process: interactive_checkin"""
        try:
            from checkin_wizard import CheckinWizard
            wizard = CheckinWizard()
            wizard.interactive_check_in()
        except ImportError:
            print("❌ Check-in wizard not available. Please ensure checkin_wizard.py is in the same directory.")
        except Exception as e:
            print(f"❌ Error in check-in wizard: {e}")
    
    def do_checkin_menu(self, arg):
        """Open check-in management menu: checkin_menu"""
        try:
            from checkin_wizard import CheckinWizard
            wizard = CheckinWizard()
            wizard.main_menu()
        except ImportError:
            print("❌ Check-in wizard not available. Please ensure checkin_wizard.py is in the same directory.")
        except Exception as e:
            print(f"❌ Error in check-in wizard: {e}")
    
    def do_exit(self, arg):
        """Exit the CLI"""
        print("Goodbye!")
        return True
    
    def do_quit(self, arg):
        """Exit the CLI"""
        return self.do_exit(arg)
    
    def do_EOF(self, arg):
        """Handle EOF (Ctrl+D)"""
        print("\nGoodbye!")
        return True
    def do_update_room_price(self, arg):
        """Update price for a specific room: update_room_price <room_id> <new_price>"""
        try:
            args = arg.split()
            if len(args) != 2:
                print("Usage: update_room_price <room_id> <new_price>")
                return
                
            room_id = int(args[0])
            new_price = float(args[1])
            success = self.db.update_room_price(room_id, new_price)
            if success:
                print(f"Room {room_id} price updated to ${new_price:.2f}")
        except Exception as e:
            print(f"Error: {e}")

    def do_update_prices_by_type(self, arg):
        """Update prices for all rooms of a specific type: update_prices_by_type <hotel_id> <room_type> <new_price>"""
        try:
            args = arg.split()
            if len(args) != 3:
                print("Usage: update_prices_by_type <hotel_id> <room_type> <new_price>")
                return
                
            hotel_id = int(args[0])
            room_type = args[1]
            new_price = float(args[2])
            updated_count = self.db.update_prices_by_type(hotel_id, room_type, new_price)
            print(f"Updated {updated_count} rooms of type '{room_type}' to ${new_price:.2f}")
        except Exception as e:
            print(f"Error: {e}")

    def do_increase_prices(self, arg):
        """Increase all room prices by percentage: increase_prices <hotel_id> <percentage>"""
        try:
            args = arg.split()
            if len(args) != 2:
                print("Usage: increase_prices <hotel_id> <percentage>")
                return
                
            hotel_id = int(args[0])
            percentage = float(args[1])
            updated_count = self.db.increase_prices_by_percentage(hotel_id, percentage)
            print(f"Increased prices for {updated_count} rooms by {percentage}%")
        except Exception as e:
            print(f"Error: {e}")


    def do_delete_hotel(self, arg):
        """Delete a hotel: delete_hotel <hotel_id> [--force]"""
        try:
            args = arg.split()
            if len(args) < 1:
                print("Usage: delete_hotel <hotel_id> [--force]")
                return
                
            hotel_id = int(args[0])
            force_delete = len(args) >= 2 and args[1] == '--force'
            
            # Get hotel info for confirmation
            hotel_info = self.db.get_hotel_info(hotel_id)
            if not hotel_info:
                print(f"Hotel with ID {hotel_id} not found")
                return
                
            hotel_name = hotel_info['name']
            
            # Confirmation prompt unless --force is used
            if not force_delete:
                confirmation = input(f"WARNING: This will permanently delete hotel '{hotel_name}' (ID: {hotel_id}) and ALL associated data (floors, rooms, reservations, etc.). This action cannot be undone.\n\nAre you sure you want to delete this hotel? (y/n): ")
                
                if confirmation.lower() not in ['y', 'yes']:
                    print("Hotel deletion cancelled.")
                    return
            
            # Perform the deletion
            success = self.db.delete_hotel(hotel_id)
            if success:
                print(f"Hotel '{hotel_name}' deleted successfully.")
        except Exception as e:
            print(f"Error: {e}")

def main():
    parser = argparse.ArgumentParser(description='Hotel Simulator CLI')
    subparsers = parser.add_subparsers(dest='command')
    
    # Create hotel
    create_parser = subparsers.add_parser('create', help='Create a new hotel')
    create_parser.add_argument('--name', required=True, help='Hotel name')
    create_parser.add_argument('--address', required=True, help='Hotel address')
    create_parser.add_argument('--stars', type=int, required=True, help='Hotel star rating')
    create_parser.add_argument('--floors', type=int, required=True, help='Number of floors')
    create_parser.add_argument('--rooms', type=int, required=True, help='Number of rooms')
    
    # List hotels
    list_parser = subparsers.add_parser('list', help='List all hotels')
    
    # Get hotel info
    info_parser = subparsers.add_parser('info', help='Get information about a hotel')
    info_parser.add_argument('--hotel-id', type=int, required=True, help='Hotel ID')
    
    # Create room
    room_parser = subparsers.add_parser('room', help='Create a new room')
    room_parser.add_argument('--hotel-id', type=int, required=True, help='Hotel ID')
    room_parser.add_argument('--floor', type=int, required=True, help='Floor number')
    room_parser.add_argument('--room-number', required=True, help='Room number')
    room_parser.add_argument('--room-type', required=True, help='Room type')
    room_parser.add_argument('--price', type=float, default=100.00, help='Price per night (default: 100.00)')
    room_parser.add_argument('--occupancy', type=int, default=2, help='Maximum occupancy (default: 2)')
    
    # List room types
    list_room_types_parser = subparsers.add_parser('list-room-types', help='List all room types')
    
    # List rooms
    list_rooms_parser = subparsers.add_parser('list-rooms', help='List all rooms in a hotel')
    list_rooms_parser.add_argument('--hotel-id', type=int, required=True, help='Hotel ID')
    
    # Book room
    book_parser = subparsers.add_parser('book', help='Book a room')
    book_parser.add_argument('--hotel-id', type=int, required=True, help='Hotel ID')
    book_parser.add_argument('--room-id', type=int, required=True, help='Room ID')
    book_parser.add_argument('--guest-name', required=True, help='Guest name')
    book_parser.add_argument('--check-in', required=True, help='Check-in date')
    book_parser.add_argument('--check-out', required=True, help='Check-out date')
    
    # Interactive hotel creation
    wizard_parser = subparsers.add_parser('wizard', help='Interactive hotel creation wizard')
    
    # Interactive mode
    interactive_parser = subparsers.add_parser('interactive', help='Start interactive CLI mode')
    
    # Batch simulation mode
    batch_parser = subparsers.add_parser('batch', help='Run batch simulation')
    batch_parser.add_argument('--hotel-id', type=int, required=True, help='Hotel ID')
    batch_parser.add_argument('--days', type=int, required=True, help='Number of days to simulate')
    
    # Update room price
    update_room_parser = subparsers.add_parser('update-room', help='Update price for a specific room')
    update_room_parser.add_argument('--room-id', type=int, required=True, help='Room ID')
    update_room_parser.add_argument('--price', type=float, required=True, help='New price per night')

    # Update prices by room type
    update_type_parser = subparsers.add_parser('update-type', help='Update prices for all rooms of a specific type')
    update_type_parser.add_argument('--hotel-id', type=int, required=True, help='Hotel ID')
    update_type_parser.add_argument('--room-type', required=True, help='Room type name')
    update_type_parser.add_argument('--price', type=float, required=True, help='New price per night')

    # Increase all prices by percentage
    increase_parser = subparsers.add_parser('increase-prices', help='Increase all room prices by percentage')
    increase_parser.add_argument('--hotel-id', type=int, required=True, help='Hotel ID')
    # Room-specific report
    room_report_parser = subparsers.add_parser('room-report', help='Generate room-specific report')
    room_report_parser.add_argument('--hotel-id', type=int, required=True, help='Hotel ID')
    room_report_parser.add_argument('--room-number', required=True, help='Room number (e.g., 101)')
    room_report_parser.add_argument('--start-date', help='Start date (YYYY-MM-DD)')
    room_report_parser.add_argument('--end-date', help='End date (YYYY-MM-DD)')
    
    # Delete hotel
    delete_parser = subparsers.add_parser('delete', help='Delete a hotel')
    delete_parser.add_argument('--hotel-id', type=int, required=True, help='Hotel ID to delete')
    delete_parser.add_argument('--force', action='store_true', help='Force deletion without confirmation')
    
    increase_parser.add_argument('--percentage', type=float, required=True, help='Percentage increase')
    args = parser.parse_args()
    
    if args.command == 'create':
        with HotelDatabase() as db:
            hotel_id = db.create_hotel(args.name, args.address, args.stars, args.floors, args.rooms)
            print(f'Hotel created with ID: {hotel_id}')
    elif args.command == 'list':
        with HotelDatabase() as db:
            hotels = db.execute_query('SELECT * FROM hotel', fetch=True)
            for hotel in hotels:
                print(f'ID: {hotel["id"]}, Name: {hotel["name"]}, Address: {hotel["address"]}')
    elif args.command == 'info':
        with HotelDatabase() as db:
            hotel_info = db.get_hotel_info(args.hotel_id)
            if hotel_info:
                print(f'Hotel ID: {hotel_info["id"]}, Name: {hotel_info["name"]}, Address: {hotel_info["address"]}')
                print(f'Stars: {hotel_info["stars"]}, Floors: {hotel_info["total_floors"]}, Rooms: {hotel_info["total_rooms"]}')
            else:
                print('Hotel not found')
    elif args.command == 'room':
        with HotelDatabase() as db:
            room_id = db.create_room(args.hotel_id, args.floor, args.room_number, args.room_type, args.price, args.occupancy)
            print(f'Room created with ID: {room_id}')
    elif args.command == 'list-room-types':
        with HotelDatabase() as db:
            room_types = db.execute_query(
                'SELECT id, name, description, base_price, max_occupancy FROM room_types', fetch=True)
            if room_types:
                print(f'Found {len(room_types)} room types:')
                for rt in room_types:
                    print(f'ID: {rt["id"]}, Name: {rt["name"]}, Price: ${rt["base_price"]}, Occupancy: {rt["max_occupancy"]}')
                    if rt['description']:
                        print(f'  Description: {rt["description"]}')
            else:
                print('No room types found.')
    
    elif args.command == 'list-rooms':
        with HotelDatabase() as db:
            rooms = db.execute_query(
                'SELECT r.id, r.room_number, r.status, rt.name as room_type, r.price_per_night ' 
                'FROM rooms r JOIN room_types rt ON r.room_type_id = rt.id ' 
                'WHERE r.hotel_id = ?', (args.hotel_id,), fetch=True)
            for room in rooms:
                print(f'ID: {room["id"]}, Room: {room["room_number"]}, Type: {room["room_type"]}, Status: {room["status"]}, Price: ${room["price_per_night"]}/night')
    elif args.command == 'book':
        with HotelDatabase() as db:
            booking_id = db.book_room(args.hotel_id, args.room_id, args.guest_name, args.check_in, args.check_out)
            print(f'Booking created with ID: {booking_id}')
    elif args.command == 'wizard':
        # Interactive hotel creation wizard
        cli = HotelCLI()
        cli.do_create_hotel_interactive('')
    elif args.command == 'interactive':
        # Start interactive mode
        cli = HotelCLI()
        cli.cmdloop()
    elif args.command == 'batch':
        # Batch simulation mode
        if not hasattr(args, 'hotel_id') or not hasattr(args, 'days'):
            print("Error: --hotel-id and --days are required for batch mode")
            return
        
        try:
            engine = HotelSimulationEngine(args.hotel_id)
            results = engine.run_simulation(args.days, verbose=True)
            print(f"\nBatch simulation completed successfully!")
            print(f"Hotel ID: {args.hotel_id}")
            print(f"Days simulated: {args.days}")
            print(f"Total reservations: {results.total_reservations}")
            print(f"Total revenue: ${results.total_revenue:.2f}")
            print(f"Occupancy rate: {results.occupancy_rate:.1f}%")
        except Exception as e:
            print(f"Error running batch simulation: {e}")
    elif args.command == 'update-room':
        # Update room price
        with HotelDatabase() as db:
            success = db.update_room_price(args.room_id, args.price)
            if success:
                print(f'Room {args.room_id} price updated to ${args.price:.2f}')
    elif args.command == 'update-type':
        # Update prices by room type
        with HotelDatabase() as db:
            updated_count = db.update_prices_by_type(args.hotel_id, args.room_type, args.price)
            print(f'Updated {updated_count} rooms of type "{args.room_type}" to ${args.price:.2f}')
    elif args.command == 'increase-prices':
        # Increase all prices by percentage
        with HotelDatabase() as db:
            updated_count = db.increase_prices_by_percentage(args.hotel_id, args.percentage)
            print(f'Increased prices for {updated_count} rooms by {args.percentage}%')
    elif args.command == 'room-report':
        # Room-specific report
        with HotelDatabase() as db:
            # Validate hotel and room exist
            room_info = db.execute_query(
                "SELECT r.id, r.room_number, r.hotel_id FROM rooms r WHERE r.room_number = ? AND r.hotel_id = ?",
                (args.room_number, args.hotel_id),
                fetch=True
            )
            
            if not room_info:
                print(f'Room {args.room_number} not found in hotel {args.hotel_id}')
                return
            
            # Create reporting system
            reporter = HotelReportingSystem()
            
            # Determine time period
            if args.start_date and args.end_date:
                time_period = TimePeriod.CUSTOM
            elif args.start_date:
                time_period = TimePeriod.DAILY
            else:
                time_period = TimePeriod.CUSTOM
                # Default to last 30 days
                args.start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
                args.end_date = datetime.now().strftime('%Y-%m-%d')
            
            # Create report configuration
            config = ReportConfig(
                report_type=ReportType.ROOM_SPECIFIC_REPORT,
                time_period=time_period,
                hotel_id=args.hotel_id,
                room_number=args.room_number,
                start_date=args.start_date,
                end_date=args.end_date,
                specific_date=args.start_date if time_period == TimePeriod.DAILY else None
            )
            
            # Generate and display report
            report = reporter.generate_report(config)
            result = reporter.display_report(report, "text")
            print(result)
    
    elif args.command == 'delete':
        # Delete hotel
        with HotelDatabase() as db:
            # Get hotel info for confirmation
            hotel_info = db.get_hotel_info(args.hotel_id)
            if not hotel_info:
                print(f'Hotel with ID {args.hotel_id} not found')
                return
            
            hotel_name = hotel_info['name']
            
            # Confirmation prompt unless --force is used
            if not args.force:
                confirmation = input(f"WARNING: This will permanently delete hotel \"{hotel_name}\" (ID: {args.hotel_id}) and ALL associated data (floors, rooms, reservations, etc.). This action cannot be undone.\n\nAre you sure you want to delete this hotel? (y/n): ")
                
                if confirmation.lower() not in ['y', 'yes']:
                    print('Hotel deletion cancelled.')
                    return
            
            # Perform the deletion
            success = db.delete_hotel(args.hotel_id)
            if success:
                print(f"Hotel \"{hotel_name}\" deleted successfully.")
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
