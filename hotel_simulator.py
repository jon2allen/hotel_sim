#!/usr/bin/env python3
"""
Hotel Simulator - Core Simulation Classes
Implements the main hotel simulation functionality including reservations, transactions, and reporting
"""

import sqlite3
import random
import datetime
import sys
import os
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# Add the parent directory to Python path so we can import hotel_sim.database
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from database import HotelDatabase


# Enums for status values
class RoomStatus(Enum):
    AVAILABLE = "available"
    OCCUPIED = "occupied"
    RESERVED = "reserved"
    MAINTENANCE = "maintenance"


class ReservationStatus(Enum):
    CONFIRMED = "confirmed"
    CHECKED_IN = "checked_in"
    CHECKED_OUT = "checked_out"
    CANCELLED = "cancelled"


class PaymentStatus(Enum):
    PENDING = "pending"
    PAID = "paid"
    PARTIALLY_PAID = "partially_paid"
    REFUNDED = "refunded"


class TransactionType(Enum):
    PAYMENT = "payment"
    REFUND = "refund"
    CHARGE = "charge"
    ADJUSTMENT = "adjustment"


@dataclass
class Guest:
    """Represents a hotel guest"""
    id: Optional[int] = None
    first_name: str = ""
    last_name: str = ""
    email: str = ""
    phone: str = ""
    address: str = ""
    loyalty_points: int = 0


@dataclass
class Room:
    """Represents a hotel room"""
    id: int
    hotel_id: int
    floor_id: int
    room_number: str
    room_type: str
    status: RoomStatus
    price_per_night: float
    max_occupancy: int
    current_guest: Optional[Guest] = None
    current_reservation: Optional[Dict] = None


@dataclass
class Reservation:
    """Represents a hotel reservation"""
    id: Optional[int] = None
    room_id: int = 0
    guest_id: int = 0
    check_in_date: str = ""
    check_out_date: str = ""
    status: ReservationStatus = ReservationStatus.CONFIRMED
    total_price: float = 0.0
    booking_date: str = ""
    payment_status: PaymentStatus = PaymentStatus.PENDING


class HotelSimulator:
    """Main hotel simulation class that orchestrates all operations"""
    
    def __init__(self, db_path: str = 'hotel.db'):
        """Initialize the hotel simulator with database connection"""
        self.db = HotelDatabase(db_path)
        self.hotel_id = None
        self.room_types = {}
        self.rooms = []
        self.guests = {}
        
    def load_hotel(self, hotel_id: int) -> bool:
        """Load hotel data from database
        
        Args:
            hotel_id: ID of the hotel to load
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get hotel info
            hotel_info = self.db.get_hotel_info(hotel_id)
            if not hotel_info:
                print(f"Hotel ID {hotel_id} not found")
                return False
            
            self.hotel_id = hotel_id
            
            # Load room types
            query = "SELECT id, name, base_price, max_occupancy FROM room_types"
            room_types_data = self.db.execute_query(query, fetch=True)
            self.room_types = {rt['name']: rt for rt in room_types_data}
            
            # Load rooms
            rooms_data = self.db.get_room_status(hotel_id)
            self.rooms = []
            for room_data in rooms_data:
                room = Room(
                    id=room_data['id'],
                    hotel_id=room_data['hotel_id'],
                    floor_id=room_data['floor_number'],
                    room_number=room_data['room_number'],
                    room_type=room_data['room_type'],
                    status=RoomStatus(room_data['status']),
                    price_per_night=room_data['price_per_night'],
                    max_occupancy=room_data['max_occupancy']
                )
                
                # Add guest info if room is occupied
                if room_data['first_name']:
                    room.current_guest = Guest(
                        first_name=room_data['first_name'],
                        last_name=room_data['last_name']
                    )
                
                self.rooms.append(room)
            
            print(f"✓ Loaded hotel: {hotel_info['name']} ({len(self.rooms)} rooms)")
            return True
            
        except Exception as e:
            print(f"Error loading hotel: {e}")
            return False
    
    def create_guest(self, first_name: str, last_name: str, email: str = "", 
                    phone: str = "", address: str = "") -> Guest:
        """Create a new guest and add to database
        
        Args:
            first_name: Guest's first name
            last_name: Guest's last name
            email: Guest's email
            phone: Guest's phone number
            address: Guest's address
            
        Returns:
            Created Guest object with ID
        """
        try:
            query = """
                INSERT INTO guests (first_name, last_name, email, phone, address)
                VALUES (?, ?, ?, ?, ?)
            """
            cursor = self.db.conn.cursor()
            cursor.execute(query, (first_name, last_name, email, phone, address))
            self.db.conn.commit()
            guest_id = cursor.lastrowid
            
            guest = Guest(
                id=guest_id,
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                address=address
            )
            
            self.guests[guest_id] = guest
            print(f"✓ Created guest: {first_name} {last_name} (ID: {guest_id})")
            return guest
            
        except sqlite3.Error as e:
            print(f"Error creating guest: {e}")
            self.db.conn.rollback()
            raise
    
    def find_available_rooms(self, room_type: str = None, floor: int = None, 
                           check_in: str = None, check_out: str = None) -> List[Room]:
        """Find available rooms with optional filtering
        
        Args:
            room_type: Filter by room type
            floor: Filter by floor number
            check_in: Check-in date (YYYY-MM-DD)
            check_out: Check-out date (YYYY-MM-DD)
            
        Returns:
            List of available Room objects
        """
        available_rooms = []
        
        for room in self.rooms:
            # Filter by room type
            if room_type and room.room_type != room_type:
                continue
            
            # Filter by floor
            if floor and room.floor_id != floor:
                continue
            
            # Filter by status
            if room.status != RoomStatus.AVAILABLE:
                continue
            
            # Check for existing reservations during the requested period
            if check_in and check_out:
                query = """
                    SELECT COUNT(*) 
                    FROM reservations 
                    WHERE room_id = ? 
                    AND status IN ('confirmed', 'checked_in')
                    AND NOT (
                        check_out_date <= ? OR 
                        check_in_date >= ?
                    )
                """
                count = self.db.execute_query(
                    query, 
                    (room.id, check_in, check_out),
                    fetch=True
                )[0]['COUNT(*)']
                
                if count > 0:
                    continue  # Room is booked during this period
            
            available_rooms.append(room)
        
        return available_rooms
    
    def calculate_reservation_price(self, room: Room, check_in: str, check_out: str) -> float:
        """Calculate total price for a reservation
        
        Args:
            room: Room object
            check_in: Check-in date (YYYY-MM-DD)
            check_out: Check-out date (YYYY-MM-DD)
            
        Returns:
            Total price for the stay
        """
        try:
            # Parse dates
            in_date = datetime.datetime.strptime(check_in, "%Y-%m-%d")
            out_date = datetime.datetime.strptime(check_out, "%Y-%m-%d")
            
            # Calculate number of nights
            nights = (out_date - in_date).days
            
            # Base price
            total_price = nights * room.price_per_night
            
            # Add 10% tax
            total_price *= 1.10
            
            return round(total_price, 2)
            
        except ValueError as e:
            print(f"Invalid date format: {e}")
            raise


class ReservationSystem:
    """Handles all reservation-related operations"""
    
    def __init__(self, db: HotelDatabase):
        """Initialize reservation system with database connection"""
        self.db = db
    
    def create_reservation(self, hotel_sim: HotelSimulator, guest: Guest, 
                          room: Room, check_in: str, check_out: str) -> Reservation:
        """Create a new reservation
        
        Args:
            hotel_sim: HotelSimulator instance
            guest: Guest object
            room: Room object
            check_in: Check-in date (YYYY-MM-DD)
            check_out: Check-out date (YYYY-MM-DD)
            
        Returns:
            Created Reservation object
        """
        try:
            # Calculate total price
            total_price = hotel_sim.calculate_reservation_price(room, check_in, check_out)
            
            # Create reservation
            query = """
                INSERT INTO reservations 
                (room_id, guest_id, check_in_date, check_out_date, status, total_price)
                VALUES (?, ?, ?, ?, ?, ?)
            """
            cursor = self.db.conn.cursor()
            cursor.execute(query, (
                room.id, 
                guest.id, 
                check_in, 
                check_out, 
                ReservationStatus.CONFIRMED.value, 
                total_price
            ))
            self.db.conn.commit()
            reservation_id = cursor.lastrowid
            
            # Update room status
            self._update_room_status(room.id, RoomStatus.RESERVED)
            
            # Create reservation object
            reservation = Reservation(
                id=reservation_id,
                room_id=room.id,
                guest_id=guest.id,
                check_in_date=check_in,
                check_out_date=check_out,
                status=ReservationStatus.CONFIRMED,
                total_price=total_price,
                booking_date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
            
            print(f"✓ Created reservation #{reservation_id} for {guest.first_name} {guest.last_name}")
            print(f"  Room: {room.room_number}, Dates: {check_in} to {check_out}, Price: ${total_price}")
            
            return reservation
            
        except Exception as e:
            print(f"Error creating reservation: {e}")
            self.db.conn.rollback()
            raise
    
    def _update_room_status(self, room_id: int, status: RoomStatus):
        """Update room status in database"""
        try:
            query = "UPDATE rooms SET status = ? WHERE id = ?"
            self.db.execute_query(query, (status.value, room_id))
        except sqlite3.Error as e:
            print(f"Error updating room status: {e}")
            raise
    
    def check_in(self, reservation_id: int) -> bool:
        """Process guest check-in
        
        Args:
            reservation_id: ID of the reservation
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get reservation
            query = "SELECT * FROM reservations WHERE id = ?"
            reservation_data = self.db.execute_query(query, (reservation_id,), fetch=True)
            
            if not reservation_data:
                print(f"Reservation #{reservation_id} not found")
                return False
            
            reservation = reservation_data[0]
            
            # Check if already checked in
            if reservation['status'] == ReservationStatus.CHECKED_IN.value:
                print(f"Guest already checked in for reservation #{reservation_id}")
                return False
            
            # Update reservation status
            query = "UPDATE reservations SET status = ? WHERE id = ?"
            self.db.execute_query(query, (ReservationStatus.CHECKED_IN.value, reservation_id))
            
            # Update room status
            self._update_room_status(reservation['room_id'], RoomStatus.OCCUPIED)
            
            print(f"✓ Checked in reservation #{reservation_id}")
            return True
            
        except Exception as e:
            print(f"Error during check-in: {e}")
            self.db.conn.rollback()
            return False
    
    def check_out(self, reservation_id: int) -> Tuple[bool, float]:
        """Process guest check-out and calculate final charges
        
        Args:
            reservation_id: ID of the reservation
            
        Returns:
            Tuple of (success: bool, final_amount: float)
        """
        try:
            # Get reservation
            query = "SELECT * FROM reservations WHERE id = ?"
            reservation_data = self.db.execute_query(query, (reservation_id,), fetch=True)
            
            if not reservation_data:
                print(f"Reservation #{reservation_id} not found")
                return False, 0.0
            
            reservation = reservation_data[0]
            
            # Check if already checked out
            if reservation['status'] == ReservationStatus.CHECKED_OUT.value:
                print(f"Guest already checked out for reservation #{reservation_id}")
                return False, 0.0
            
            # Calculate any additional charges (simplified for now)
            final_amount = reservation['total_price']
            
            # Update reservation status
            query = "UPDATE reservations SET status = ?, payment_status = ? WHERE id = ?"
            self.db.execute_query(query, (
                ReservationStatus.CHECKED_OUT.value, 
                PaymentStatus.PAID.value, 
                reservation_id
            ))
            
            # Update room status
            self._update_room_status(reservation['room_id'], RoomStatus.AVAILABLE)
            
            # Create payment transaction
            self._create_transaction(
                reservation_id, 
                final_amount, 
                TransactionType.PAYMENT,
                "Final payment for stay"
            )
            
            print(f"✓ Checked out reservation #{reservation_id}")
            print(f"  Final amount: ${final_amount}")
            
            return True, final_amount
            
        except Exception as e:
            print(f"Error during check-out: {e}")
            self.db.conn.rollback()
            return False, 0.0
    
    def _create_transaction(self, reservation_id: int, amount: float, 
                           transaction_type: TransactionType, description: str):
        """Create a financial transaction"""
        try:
            query = """
                INSERT INTO transactions 
                (reservation_id, amount, transaction_type, description)
                VALUES (?, ?, ?, ?)
            """
            self.db.execute_query(query, (
                reservation_id,
                amount,
                transaction_type.value,
                description
            ))
        except sqlite3.Error as e:
            print(f"Error creating transaction: {e}")
            raise
    
    def cancel_reservation(self, reservation_id: int) -> bool:
        """Cancel a reservation
        
        Args:
            reservation_id: ID of the reservation to cancel
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get reservation
            query = "SELECT * FROM reservations WHERE id = ?"
            reservation_data = self.db.execute_query(query, (reservation_id,), fetch=True)
            
            if not reservation_data:
                print(f"Reservation #{reservation_id} not found")
                return False
            
            reservation = reservation_data[0]
            
            # Check if already cancelled or checked in
            if reservation['status'] in (ReservationStatus.CANCELLED.value, ReservationStatus.CHECKED_IN.value):
                print(f"Cannot cancel reservation #{reservation_id} (status: {reservation['status']})")
                return False
            
            # Update reservation status
            query = "UPDATE reservations SET status = ? WHERE id = ?"
            self.db.execute_query(query, (ReservationStatus.CANCELLED.value, reservation_id))
            
            # Update room status
            self._update_room_status(reservation['room_id'], RoomStatus.AVAILABLE)
            
            print(f"✓ Cancelled reservation #{reservation_id}")
            return True
            
        except Exception as e:
            print(f"Error cancelling reservation: {e}")
            self.db.conn.rollback()
            return False


class HotelReporter:
    """Handles reporting and analytics for the hotel"""
    
    def __init__(self, db: HotelDatabase):
        """Initialize reporter with database connection"""
        self.db = db
    
    def get_hotel_status(self, hotel_id: int) -> Dict[str, Any]:
        """Get overall hotel status and occupancy
        
        Args:
            hotel_id: ID of the hotel
            
        Returns:
            Dictionary with hotel status information
        """
        try:
            # Get basic hotel info
            hotel_info = self.db.get_hotel_info(hotel_id)
            if not hotel_info:
                return {}
            
            # Get room counts by status
            query = """
                SELECT 
                    status,
                    COUNT(*) as count
                FROM rooms 
                WHERE hotel_id = ?
                GROUP BY status
            """
            room_status = self.db.execute_query(query, (hotel_id,), fetch=True)
            
            # Calculate occupancy
            total_rooms = sum(status['count'] for status in room_status)
            occupied = sum(status['count'] for status in room_status 
                          if status['status'] in ('occupied', 'reserved'))
            
            occupancy_rate = (occupied / total_rooms * 100) if total_rooms > 0 else 0
            
            # Get upcoming reservations
            today = datetime.datetime.now().strftime("%Y-%m-%d")
            query = """
                SELECT COUNT(*) as upcoming
                FROM reservations r
                JOIN rooms rm ON r.room_id = rm.id
                WHERE rm.hotel_id = ? 
                AND r.check_in_date >= ?
                AND r.status = 'confirmed'
            """
            upcoming = self.db.execute_query(query, (hotel_id, today), fetch=True)[0]['upcoming']
            
            return {
                'hotel_name': hotel_info['name'],
                'stars': hotel_info['stars'],
                'total_rooms': total_rooms,
                'occupied_rooms': occupied,
                'available_rooms': total_rooms - occupied,
                'occupancy_rate': round(occupancy_rate, 2),
                'upcoming_reservations': upcoming,
                'room_status': {status['status']: status['count'] for status in room_status}
            }
            
        except Exception as e:
            print(f"Error getting hotel status: {e}")
            return {}
    
    def get_financial_summary(self, hotel_id: int, days: int = 30) -> Dict[str, Any]:
        """Get financial summary for the hotel
        
        Args:
            hotel_id: ID of the hotel
            days: Number of days to look back
            
        Returns:
            Dictionary with financial information
        """
        try:
            # Calculate date range
            end_date = datetime.datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.datetime.now() - datetime.timedelta(days=days)).strftime("%Y-%m-%d")
            
            # Get revenue by transaction type
            query = """
                SELECT 
                    t.transaction_type,
                    SUM(t.amount) as total_amount,
                    COUNT(*) as transaction_count
                FROM transactions t
                JOIN reservations r ON t.reservation_id = r.id
                JOIN rooms rm ON r.room_id = rm.id
                WHERE rm.hotel_id = ?
                AND t.transaction_date >= ?
                GROUP BY t.transaction_type
            """
            revenue_data = self.db.execute_query(query, (hotel_id, start_date), fetch=True)
            
            # Calculate totals
            total_revenue = sum(item['total_amount'] for item in revenue_data)
            
            # Get upcoming revenue
            query = """
                SELECT SUM(r.total_price) as upcoming_revenue
                FROM reservations r
                JOIN rooms rm ON r.room_id = rm.id
                WHERE rm.hotel_id = ? 
                AND r.check_in_date >= ?
                AND r.status = 'confirmed'
            """
            upcoming_revenue = self.db.execute_query(query, (hotel_id, end_date), fetch=True)[0]['upcoming_revenue'] or 0
            
            return {
                'period': f"Last {days} days",
                'start_date': start_date,
                'end_date': end_date,
                'total_revenue': round(total_revenue, 2),
                'upcoming_revenue': round(upcoming_revenue, 2),
                'revenue_by_type': {item['transaction_type']: item['total_amount'] for item in revenue_data},
                'transaction_counts': {item['transaction_type']: item['transaction_count'] for item in revenue_data}
            }
            
        except Exception as e:
            print(f"Error getting financial summary: {e}")
            return {}
    
    def get_occupancy_forecast(self, hotel_id: int, days: int = 7) -> List[Dict[str, Any]]:
        """Get occupancy forecast for the next N days
        
        Args:
            hotel_id: ID of the hotel
            days: Number of days to forecast
            
        Returns:
            List of daily occupancy forecasts
        """
        try:
            forecast = []
            today = datetime.datetime.now()
            
            for i in range(days):
                date = (today + datetime.timedelta(days=i)).strftime("%Y-%m-%d")
                
                # Get check-ins and check-outs for this date
                query = """
                    SELECT 
                        SUM(CASE WHEN check_in_date = ? THEN 1 ELSE 0 END) as check_ins,
                        SUM(CASE WHEN check_out_date = ? THEN 1 ELSE 0 END) as check_outs
                    FROM reservations r
                    JOIN rooms rm ON r.room_id = rm.id
                    WHERE rm.hotel_id = ?
                    AND r.status IN ('confirmed', 'checked_in')
                """
                
                result = self.db.execute_query(query, (date, date, hotel_id), fetch=True)[0]
                
                # Get current occupancy (guests staying over)
                query = """
                    SELECT COUNT(*) as occupied
                    FROM reservations r
                    JOIN rooms rm ON r.room_id = rm.id
                    WHERE rm.hotel_id = ?
                    AND r.status = 'checked_in'
                    AND r.check_in_date <= ?
                    AND r.check_out_date > ?
                """
                
                occupied = self.db.execute_query(query, (hotel_id, date, date), fetch=True)[0]['occupied']
                
                forecast.append({
                    'date': date,
                    'day_of_week': (today + datetime.timedelta(days=i)).strftime("%A"),
                    'check_ins': result['check_ins'] or 0,
                    'check_outs': result['check_outs'] or 0,
                    'occupied_rooms': occupied or 0
                })
            
            return forecast
            
        except Exception as e:
            print(f"Error getting occupancy forecast: {e}")
            return []


if __name__ == "__main__":
    # Test the core classes
    print("Hotel Simulator - Core Classes Test")
    print("=" * 50)
    
    try:
        # Initialize simulator
        print("\n[TEST 1] Initialization and Hotel Loading")
        print("-" * 40)
        
        simulator = HotelSimulator()
        
        # Use the latest hotel ID (should be 5 from previous tests)
        if simulator.load_hotel(5):
            print(f"✓ Hotel loaded: {len(simulator.rooms)} rooms")
            
            # Show room types
            print(f"✓ Room types available: {list(simulator.room_types.keys())}")
        else:
            print("✗ Failed to load hotel")
            exit(1)
        
        # Test guest creation
        print("\n[TEST 2] Guest Management")
        print("-" * 40)
        
        guest1 = simulator.create_guest(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            phone="555-123-4567"
        )
        
        guest2 = simulator.create_guest(
            first_name="Jane",
            last_name="Smith",
            email="jane.smith@example.com"
        )
        
        print(f"✓ Created 2 guests")
        
        # Test finding available rooms
        print("\n[TEST 3] Room Availability")
        print("-" * 40)
        
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        tomorrow = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        next_week = (datetime.datetime.now() + datetime.timedelta(days=7)).strftime("%Y-%m-%d")
        
        available_rooms = simulator.find_available_rooms(
            room_type="Suite",
            check_in=today,
            check_out=next_week
        )
        
        print(f"✓ Found {len(available_rooms)} available suites for next week")
        if available_rooms:
            print(f"  First available: Room {available_rooms[0].room_number} (${available_rooms[0].price_per_night}/night)")
        
        # Test reservation system
        print("\n[TEST 4] Reservation System")
        print("-" * 40)
        
        reservation_system = ReservationSystem(simulator.db)
        
        if available_rooms:
            # Create a reservation
            reservation = reservation_system.create_reservation(
                simulator, 
                guest1, 
                available_rooms[0], 
                today, 
                tomorrow
            )
            
            print(f"✓ Created reservation for {guest1.first_name} {guest1.last_name}")
            print(f"  Reservation #{reservation.id}: ${reservation.total_price}")
            
            # Test check-in
            if reservation_system.check_in(reservation.id):
                print("✓ Guest checked in successfully")
            
            # Test check-out
            success, amount = reservation_system.check_out(reservation.id)
            if success:
                print(f"✓ Guest checked out, final amount: ${amount}")
        else:
            print("⚠ No available rooms for reservation test")
        
        # Test reporting
        print("\n[TEST 5] Reporting System")
        print("-" * 40)
        
        reporter = HotelReporter(simulator.db)
        
        # Get hotel status
        status = reporter.get_hotel_status(5)
        if status:
            print(f"✓ Hotel Status:")
            print(f"  Name: {status['hotel_name']}")
            print(f"  Occupancy: {status['occupancy_rate']}%")
            print(f"  Upcoming reservations: {status['upcoming_reservations']}")
        
        # Get financial summary
        financial = reporter.get_financial_summary(5, 7)
        if financial:
            print(f"✓ Financial Summary (last 7 days):")
            print(f"  Total Revenue: ${financial['total_revenue']}")
            print(f"  Upcoming Revenue: ${financial['upcoming_revenue']}")
        
        # Get occupancy forecast
        forecast = reporter.get_occupancy_forecast(5, 3)
        if forecast:
            print(f"✓ Occupancy Forecast (next 3 days):")
            for day in forecast:
                print(f"  {day['date']} ({day['day_of_week']}): "
                      f"{day['occupied_rooms']} occupied, "
                      f"{day['check_ins']} check-ins, "
                      f"{day['check_outs']} check-outs")
        
        print("\n" + "=" * 50)
        print("✓ ALL CORE CLASS TESTS COMPLETED SUCCESSFULLY")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n✗ Error during core class testing: {e}")
        import traceback
        traceback.print_exc()