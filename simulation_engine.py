#!/usr/bin/env python3
"""
Hotel Simulator - Simulation Engine
Implements time-based simulation with random events and statistical analysis
"""

import random
import datetime
import time
import sys
import os
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict
import statistics

# Add the parent directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from hotel_simulator import HotelSimulator, ReservationSystem, HotelReporter, Guest, Room
from database import HotelDatabase


@dataclass
class SimulationConfig:
    """Configuration for hotel simulation"""
    # Probability settings (0.0 - 1.0)
    new_reservation_probability: float = 0.5  # Increased from 0.3
    check_in_probability: float = 0.6  # Increased from 0.4
    check_out_probability: float = 0.5  # Increased from 0.35
    cancellation_probability: float = 0.08  # Increased from 0.05
    early_checkout_probability: float = 0.15  # Increased from 0.1
    late_checkout_probability: float = 0.2  # Increased from 0.15
    housekeeping_delay_probability: float = 0.05  # Increased from 0.02
    maintenance_issue_probability: float = 0.03  # Increased from 0.01
    walk_in_guest_probability: float = 0.2  # New: Walk-in guests
    group_booking_probability: float = 0.15  # New: Group bookings
    extended_stay_probability: float = 0.2  # New: Extended stays
    loyalty_member_probability: float = 0.3  # New: Loyalty members
    special_request_probability: float = 0.25  # New: Special requests
    
    # Guest behavior
    average_stay_days: Tuple[int, int] = (1, 7)  # min, max
    guest_types: List[str] = None
    payment_methods: List[str] = None
    
    # Pricing
    seasonal_price_variation: float = 0.2  # ±20%
    weekend_price_multiplier: float = 1.15
    loyalty_discount: float = 0.1
    
    # Operational
    check_in_time_range: Tuple[str, str] = ('14:00', '23:00')
    check_out_time_range: Tuple[str, str] = ('07:00', '12:00')
    
    def __post_init__(self):
        """Initialize mutable fields"""
        if self.guest_types is None:
            self.guest_types = ['business', 'leisure', 'family', 'group']
        if self.payment_methods is None:
            self.payment_methods = ['credit_card', 'cash', 'bank_transfer']


@dataclass
class SimulationEvent:
    """Represents a simulation event"""
    day: int
    time: str
    event_type: str
    description: str
    amount: float = 0.0
    guest_id: Optional[int] = None
    room_number: Optional[str] = None
    reservation_id: Optional[int] = None


@dataclass
class SimulationResults:
    """Stores simulation results and statistics"""
    total_days: int = 0
    total_guests: int = 0
    total_reservations: int = 0
    total_revenue: float = 0.0
    total_cancellations: int = 0
    total_walk_ins: int = 0
    total_group_bookings: int = 0
    total_extended_stays: int = 0
    total_loyalty_bookings: int = 0
    total_special_requests: int = 0
    occupancy_rate: float = 0.0
    events: List[SimulationEvent] = None
    
    def __init__(self):
        self.events = []


class HotelSimulationEngine:
    """Main simulation engine that generates hotel operations over time"""
    
    def __init__(self, hotel_id: int, db_path: str = 'hotel.db'):
        """Initialize simulation engine"""
        self.hotel_id = hotel_id
        self.db = HotelDatabase(db_path)
        self.simulator = HotelSimulator(db_path)
        self.reservation_system = ReservationSystem(self.db)
        self.reporter = HotelReporter(self.db)
        self.config = SimulationConfig()
        self.current_date = datetime.datetime.now()
        self.guest_counter = 1
        self.results = None
        
        # Load hotel data
        if not self.simulator.load_hotel(hotel_id):
            raise ValueError(f"Failed to load hotel {hotel_id}")
    
    def run_simulation(self, days: int = 30, verbose: bool = True) -> SimulationResults:
        """Run simulation for specified number of days
        
        Args:
            days: Number of days to simulate
            verbose: Whether to print progress
            
        Returns:
            SimulationResults object with statistics
        """
        if verbose:
            print(f"Starting Hotel Simulation: {days} days")
            print("=" * 60)
        
        self.results = SimulationResults()
        self.results.total_days = days
        
        # Generate guest names for simulation - expanded list
        first_names = [
            'John', 'Jane', 'Michael', 'Sarah', 'David', 'Emily', 'Robert', 'Jennifer',
            'William', 'Lisa', 'Thomas', 'Jessica', 'Daniel', 'Amanda', 'Christopher', 'Melissa',
            'Matthew', 'Nicole', 'Andrew', 'Stephanie', 'James', 'Rebecca', 'Joshua', 'Laura',
            'Kevin', 'Heather', 'Brian', 'Michelle', 'Timothy', 'Christina', 'Jason', 'Elizabeth',
            'Ryan', 'Katherine', 'Jacob', 'Samantha', 'Gary', 'Ashley', 'Nicholas', 'Megan'
        ]
        last_names = [
            'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Miller', 'Davis', 'Wilson',
            'Taylor', 'Anderson', 'Thomas', 'Jackson', 'White', 'Harris', 'Martin', 'Thompson',
            'Garcia', 'Martinez', 'Robinson', 'Clark', 'Rodriguez', 'Lewis', 'Lee', 'Walker',
            'Hall', 'Allen', 'Young', 'Hernandez', 'King', 'Wright', 'Lopez', 'Hill'
        ]
        
        # Add some international names for diversity
        international_first_names = [
            'Carlos', 'Maria', 'Wei', 'Li', 'Pierre', 'Sophie', 'Hans', 'Anna',
            'Yuki', 'Hiro', 'Aisha', 'Mohammed', 'Luca', 'Giovanna', 'Ivan', 'Olga'
        ]
        international_last_names = [
            'Gonzalez', 'Rodriguez', 'Wang', 'Zhang', 'Dubois', 'Muller', 'Tanaka', 'Ivanov',
            'Khan', 'Rossi', 'Silva', 'Kim', 'Patel', 'Nguyen', 'Chen', 'Wong'
        ]
        
        # Combine all names
        all_first_names = first_names + international_first_names
        all_last_names = last_names + international_last_names
        
        for day in range(1, days + 1):
            self.current_date += datetime.timedelta(days=1)
            day_name = self.current_date.strftime("%A")
            date_str = self.current_date.strftime("%Y-%m-%d")
            
            if verbose:
                print(f"\n📅 Day {day} ({day_name}, {date_str})")
                print("-" * 50)
            
            # Track daily metrics
            daily_revenue = 0.0
            daily_guests = 0
            
            # 1. Process scheduled check-ins
            check_ins = self._get_scheduled_check_ins(date_str)
            for res_id, guest_id, room_num in check_ins:
                if self.reservation_system.check_in(res_id):
                    daily_guests += 1
                    event = SimulationEvent(
                        day=day,
                        time=self._random_time(*self.config.check_in_time_range),
                        event_type="check_in",
                        description=f"Guest checked into room {room_num}",
                        guest_id=guest_id,
                        room_number=room_num,
                        reservation_id=res_id
                    )
                    self.results.events.append(event)
                    if verbose:
                        print(f"✅ Check-in: Guest {guest_id} → Room {room_num}")
            
            # 2. Process scheduled check-outs
            check_outs = self._get_scheduled_check_outs(date_str)
            for res_id, guest_id, room_num in check_outs:
                success, amount = self.reservation_system.check_out(res_id)
                if success:
                    daily_revenue += amount
                    self.results.total_revenue += amount
                    event = SimulationEvent(
                        day=day,
                        time=self._random_time(*self.config.check_out_time_range),
                        event_type="check_out",
                        description=f"Guest checked out of room {room_num}",
                        amount=amount,
                        guest_id=guest_id,
                        room_number=room_num,
                        reservation_id=res_id
                    )
                    self.results.events.append(event)
                    if verbose:
                        print(f"💰 Check-out: Guest {guest_id} ← Room {room_num} (${amount})")
            
            # 3. Generate new reservations (random events)
            if random.random() < self.config.new_reservation_probability:
                available_rooms = self.simulator.find_available_rooms(check_in=date_str)
                if available_rooms:
                    room = random.choice(available_rooms)
                    stay_days = random.randint(*self.config.average_stay_days)
                    check_out = (self.current_date + datetime.timedelta(days=stay_days)).strftime("%Y-%m-%d")
                    
                    # Create guest with expanded name pool
                    guest = self.simulator.create_guest(
                        first_name=random.choice(all_first_names),
                        last_name=random.choice(all_last_names),
                        email=f"guest{self.guest_counter}@example.com"
                    )
                    self.guest_counter += 1
                    self.results.total_guests += 1
                    
                    # Create reservation
                    reservation = self.reservation_system.create_reservation(
                        self.simulator, guest, room, date_str, check_out
                    )
                    self.results.total_reservations += 1
                    
                    event = SimulationEvent(
                        day=day,
                        time=self._random_time('09:00', '18:00'),
                        event_type="new_reservation",
                        description=f"New reservation: {guest.first_name} {guest.last_name} → Room {room.room_number}",
                        amount=reservation.total_price,
                        guest_id=guest.id,
                        room_number=room.room_number,
                        reservation_id=reservation.id
                    )
                    self.results.events.append(event)
                    if verbose:
                        print(f"📝 New Reservation: {guest.first_name} {guest.last_name} → Room {room.room_number} (${reservation.total_price})")
            
            # 4. Walk-in guests (same-day bookings)
            if random.random() < self.config.walk_in_guest_probability:
                available_rooms = self.simulator.find_available_rooms(check_in=date_str)
                if available_rooms:
                    room = random.choice(available_rooms)
                    stay_days = random.randint(1, 3)  # Shorter stays for walk-ins
                    check_out = (self.current_date + datetime.timedelta(days=stay_days)).strftime("%Y-%m-%d")
                     
                    # Create guest
                    guest = self.simulator.create_guest(
                        first_name=random.choice(all_first_names),
                        last_name=random.choice(all_last_names),
                        email=f"walkin{self.guest_counter}@example.com"
                    )
                    self.guest_counter += 1
                    self.results.total_guests += 1
                    
                    # Create reservation
                    reservation = self.reservation_system.create_reservation(
                        self.simulator, guest, room, date_str, check_out
                    )
                    self.results.total_reservations += 1
                    
                    event = SimulationEvent(
                        day=day,
                        time=self._random_time('14:00', '20:00'),
                        event_type="walk_in_booking",
                        description=f"Walk-in booking: {guest.first_name} {guest.last_name} → Room {room.room_number}",
                        amount=reservation.total_price,
                        guest_id=guest.id,
                        room_number=room.room_number,
                        reservation_id=reservation.id
                    )
                    self.results.events.append(event)
                    self.results.total_walk_ins += 1
                    if verbose:
                        print(f"🚶 Walk-in Booking: {guest.first_name} {guest.last_name} → Room {room.room_number} (${reservation.total_price})")
            
            # 5. Group bookings (multiple rooms)
            if random.random() < self.config.group_booking_probability:
                available_rooms = self.simulator.find_available_rooms(check_in=date_str)
                if len(available_rooms) >= 3:  # Need at least 3 rooms for a group
                    group_size = random.randint(3, min(6, len(available_rooms)))  # 3-6 rooms
                    selected_rooms = random.sample(available_rooms, group_size)
                    stay_days = random.randint(2, 5)
                    check_out = (self.current_date + datetime.timedelta(days=stay_days)).strftime("%Y-%m-%d")
                    
                    # Create group leader
                    group_leader = self.simulator.create_guest(
                        first_name=random.choice(all_first_names),
                        last_name=random.choice(all_last_names),
                        email=f"group{self.guest_counter}@example.com"
                    )
                    self.guest_counter += 1
                    self.results.total_guests += group_size
                    
                    total_group_price = 0
                    group_rooms = []
                    
                    # Create reservations for each room in the group
                    for room in selected_rooms:
                        reservation = self.reservation_system.create_reservation(
                            self.simulator, group_leader, room, date_str, check_out
                        )
                        total_group_price += reservation.total_price
                        self.results.total_reservations += 1
                        group_rooms.append(room.room_number)
                    
                    event = SimulationEvent(
                        day=day,
                        time=self._random_time('10:00', '16:00'),
                        event_type="group_booking",
                        description=f"Group booking: {group_leader.first_name} {group_leader.last_name} → {group_size} rooms",
                        amount=total_group_price,
                        guest_id=group_leader.id,
                        room_number=", ".join(group_rooms),
                        reservation_id=None
                    )
                    self.results.events.append(event)
                    self.results.total_group_bookings += 1
                    if verbose:
                        print(f"👥 Group Booking: {group_leader.first_name} {group_leader.last_name} → {group_size} rooms (${total_group_price})")
            
            # 6. Extended stays (longer reservations)
            if random.random() < self.config.extended_stay_probability:
                available_rooms = self.simulator.find_available_rooms(check_in=date_str)
                if available_rooms:
                    room = random.choice(available_rooms)
                    stay_days = random.randint(7, 14)  # 1-2 weeks
                    check_out = (self.current_date + datetime.timedelta(days=stay_days)).strftime("%Y-%m-%d")
                    
                    # Create guest
                    guest = self.simulator.create_guest(
                        first_name=random.choice(all_first_names),
                        last_name=random.choice(all_last_names),
                        email=f"extended{self.guest_counter}@example.com"
                    )
                    self.guest_counter += 1
                    self.results.total_guests += 1
                    
                    # Create reservation
                    reservation = self.reservation_system.create_reservation(
                        self.simulator, guest, room, date_str, check_out
                    )
                    self.results.total_reservations += 1
                    
                    event = SimulationEvent(
                        day=day,
                        time=self._random_time('09:00', '17:00'),
                        event_type="extended_stay",
                        description=f"Extended stay: {guest.first_name} {guest.last_name} → Room {room.room_number} ({stay_days} nights)",
                        amount=reservation.total_price,
                        guest_id=guest.id,
                        room_number=room.room_number,
                        reservation_id=reservation.id
                    )
                    self.results.events.append(event)
                    self.results.total_extended_stays += 1
                    if verbose:
                        print(f"🏖️ Extended Stay: {guest.first_name} {guest.last_name} → Room {room.room_number} ({stay_days} nights, ${reservation.total_price})")
            
            # 7. Loyalty member bookings (higher probability, discounts)
            if random.random() < self.config.loyalty_member_probability:
                available_rooms = self.simulator.find_available_rooms(check_in=date_str)
                if available_rooms:
                    room = random.choice(available_rooms)
                    stay_days = random.randint(2, 5)
                    check_out = (self.current_date + datetime.timedelta(days=stay_days)).strftime("%Y-%m-%d")
                    
                    # Create loyalty member guest
                    guest = self.simulator.create_guest(
                        first_name=random.choice(all_first_names),
                        last_name=random.choice(all_last_names),
                        email=f"loyalty{self.guest_counter}@example.com"
                    )
                    self.guest_counter += 1
                    self.results.total_guests += 1
                    
                    # Create reservation with loyalty discount
                    reservation = self.reservation_system.create_reservation(
                        self.simulator, guest, room, date_str, check_out
                    )
                    # Apply loyalty discount
                    discount_amount = reservation.total_price * self.config.loyalty_discount
                    discounted_price = reservation.total_price - discount_amount
                    
                    self.results.total_reservations += 1
                    
                    event = SimulationEvent(
                        day=day,
                        time=self._random_time('09:00', '17:00'),
                        event_type="loyalty_booking",
                        description=f"Loyalty booking: {guest.first_name} {guest.last_name} → Room {room.room_number} (${discounted_price:.2f} with discount)",
                        amount=discounted_price,
                        guest_id=guest.id,
                        room_number=room.room_number,
                        reservation_id=reservation.id
                    )
                    self.results.events.append(event)
                    self.results.total_loyalty_bookings += 1
                    if verbose:
                        print(f"💎 Loyalty Booking: {guest.first_name} {guest.last_name} → Room {room.room_number} (${discounted_price:.2f} with discount)")
            
            # 8. Special requests (room upgrades, late checkouts, etc.)
            if random.random() < self.config.special_request_probability:
                # Find guests who are currently checked in
                checked_in_guests = self._get_checked_in_guests(date_str)
                if checked_in_guests:
                    guest_id, room_num, res_id = random.choice(checked_in_guests)
                    
                    # Randomly select type of special request
                    request_type = random.choice(['upgrade', 'late_checkout', 'extra_amenities', 'room_service'])
                    
                    if request_type == 'upgrade':
                        # Room upgrade request
                        event = SimulationEvent(
                            day=day,
                            time=self._random_time('10:00', '18:00'),
                            event_type="special_request",
                            description=f"Room upgrade request: Guest {guest_id} in Room {room_num}",
                            amount=50.00,  # Upgrade fee
                            guest_id=guest_id,
                            room_number=room_num,
                            reservation_id=res_id
                        )
                        if verbose:
                            print(f"📈 Special Request: Guest {guest_id} requested room upgrade (Room {room_num})")
                    
                    elif request_type == 'late_checkout':
                        # Late checkout request
                        event = SimulationEvent(
                            day=day,
                            time=self._random_time('08:00', '12:00'),
                            event_type="special_request",
                            description=f"Late checkout request: Guest {guest_id} in Room {room_num}",
                            amount=25.00,  # Late checkout fee
                            guest_id=guest_id,
                            room_number=room_num,
                            reservation_id=res_id
                        )
                        if verbose:
                            print(f"⏰ Special Request: Guest {guest_id} requested late checkout (Room {room_num})")
                    
                    elif request_type == 'extra_amenities':
                        # Extra amenities request
                        event = SimulationEvent(
                            day=day,
                            time=self._random_time('09:00', '20:00'),
                            event_type="special_request",
                            description=f"Extra amenities request: Guest {guest_id} in Room {room_num}",
                            amount=35.00,  # Amenities fee
                            guest_id=guest_id,
                            room_number=room_num,
                            reservation_id=res_id
                        )
                        if verbose:
                            print(f"🛎️ Special Request: Guest {guest_id} requested extra amenities (Room {room_num})")
                    
                    else:  # room_service
                        # Room service request
                        event = SimulationEvent(
                            day=day,
                            time=self._random_time('18:00', '22:00'),
                            event_type="special_request",
                            description=f"Room service request: Guest {guest_id} in Room {room_num}",
                            amount=45.00,  # Room service fee
                            guest_id=guest_id,
                            room_number=room_num,
                            reservation_id=res_id
                        )
                        if verbose:
                            print(f"🍽️ Special Request: Guest {guest_id} ordered room service (Room {room_num})")
                    
                    self.results.events.append(event)
                    self.results.total_special_requests += 1
            
            # 9. Random cancellations
            active_reservations = self._get_active_reservations(date_str)
            for res_id, guest_id, room_num in active_reservations:
                if random.random() < self.config.cancellation_probability:
                    if self.reservation_system.cancel_reservation(res_id):
                        self.results.total_cancellations += 1
                        event = SimulationEvent(
                            day=day,
                            time=self._random_time('09:00', '17:00'),
                            event_type="cancellation",
                            description=f"Reservation cancelled: Room {room_num}",
                            guest_id=guest_id,
                            room_number=room_num,
                            reservation_id=res_id
                        )
                        self.results.events.append(event)
                        if verbose:
                            print(f"❌ Cancellation: Room {room_num}")
            
            # 5. Update daily metrics
            self.results.total_revenue += daily_revenue
            
            # 6. Get daily status
            status = self.reporter.get_hotel_status(self.hotel_id)
            if status:
                daily_occupancy = status.get('occupancy_rate', 0)
                self.results.occupancy_rate += daily_occupancy
                if verbose:
                    print(f"📊 Daily Stats: {daily_occupancy}% occupancy, ${daily_revenue} revenue, {daily_guests} check-ins")
        
        # Calculate average occupancy
        if days > 0:
            self.results.occupancy_rate /= days
        
        if verbose:
            print(f"\n" + "=" * 60)
            print("🎉 SIMULATION COMPLETED")
            print("=" * 60)
        
        return self.results
    
    def _get_scheduled_check_ins(self, date: str) -> List[Tuple[int, int, str]]:
        """Get reservations scheduled for check-in on given date"""
        try:
            query = """
                SELECT r.id, r.guest_id, rm.room_number
                FROM reservations r
                JOIN rooms rm ON r.room_id = rm.id
                WHERE r.check_in_date = ?
                AND r.status = 'confirmed'
                AND rm.hotel_id = ?
            """
            results = self.db.execute_query(query, (date, self.hotel_id), fetch=True)
            return [(row['id'], row['guest_id'], row['room_number']) for row in results]
        except Exception as e:
            print(f"Error getting check-ins: {e}")
            return []
    
    def _get_scheduled_check_outs(self, date: str) -> List[Tuple[int, int, str]]:
        """Get reservations scheduled for check-out on given date"""
        try:
            query = """
                SELECT r.id, r.guest_id, rm.room_number
                FROM reservations r
                JOIN rooms rm ON r.room_id = rm.id
                WHERE r.check_out_date = ?
                AND r.status = 'checked_in'
                AND rm.hotel_id = ?
            """
            results = self.db.execute_query(query, (date, self.hotel_id), fetch=True)
            return [(row['id'], row['guest_id'], row['room_number']) for row in results]
        except Exception as e:
            print(f"Error getting check-outs: {e}")
            return []
    
    def _get_active_reservations(self, date: str) -> List[Tuple[int, int, str]]:
        """Get active reservations that could be cancelled"""
        try:
            query = """
                SELECT r.id, r.guest_id, rm.room_number
                FROM reservations r
                JOIN rooms rm ON r.room_id = rm.id
                WHERE r.check_in_date > ?
                AND r.status = 'confirmed'
                AND rm.hotel_id = ?
            """
            results = self.db.execute_query(query, (date, self.hotel_id), fetch=True)
            return [(row['id'], row['guest_id'], row['room_number']) for row in results]
        except Exception as e:
            print(f"Error getting active reservations: {e}")
            return []
    
    def _get_checked_in_guests(self, date: str) -> List[Tuple[int, str, int]]:
        """Get guests who are currently checked in"""
        try:
            query = """
                SELECT r.id, r.guest_id, rm.room_number
                FROM reservations r
                JOIN rooms rm ON r.room_id = rm.id
                WHERE r.status = 'checked_in'
                AND r.check_out_date >= ?
                AND rm.hotel_id = ?
            """
            results = self.db.execute_query(query, (date, self.hotel_id), fetch=True)
            return [(row['guest_id'], row['room_number'], row['id']) for row in results]
        except Exception as e:
            print(f"Error getting checked-in guests: {e}")
            return []
    
    def _random_time(self, start: str, end: str) -> str:
        """Generate random time between start and end"""
        start_h, start_m = map(int, start.split(':'))
        end_h, end_m = map(int, end.split(':'))
        
        start_minutes = start_h * 60 + start_m
        end_minutes = end_h * 60 + end_m
        
        random_minutes = random.randint(start_minutes, end_minutes)
        return f"{random_minutes // 60:02d}:{random_minutes % 60:02d}"
    
    def generate_detailed_report(self, results: SimulationResults) -> Dict[str, Any]:
        """Generate comprehensive report from simulation results"""
        if not results:
            return {}
        
        # Calculate statistics
        revenue_per_day = results.total_revenue / results.total_days if results.total_days > 0 else 0
        guests_per_day = results.total_guests / results.total_days if results.total_days > 0 else 0
        reservations_per_day = results.total_reservations / results.total_days if results.total_days > 0 else 0
        cancellation_rate = results.total_cancellations / results.total_reservations if results.total_reservations > 0 else 0
        walk_in_rate = results.total_walk_ins / results.total_reservations if results.total_reservations > 0 else 0
        group_booking_rate = results.total_group_bookings / results.total_reservations if results.total_reservations > 0 else 0
        extended_stay_rate = results.total_extended_stays / results.total_reservations if results.total_reservations > 0 else 0
        loyalty_booking_rate = results.total_loyalty_bookings / results.total_reservations if results.total_reservations > 0 else 0
        special_requests_per_guest = results.total_special_requests / results.total_guests if results.total_guests > 0 else 0
        
        # Event type breakdown
        event_types = defaultdict(int)
        revenue_by_type = defaultdict(float)
        
        for event in results.events:
            event_types[event.event_type] += 1
            if event.amount > 0:
                revenue_by_type[event.event_type] += event.amount
        
        return {
            'simulation_period': f"{results.total_days} days",
            'total_revenue': round(results.total_revenue, 2),
            'revenue_per_day': round(revenue_per_day, 2),
            'total_guests': results.total_guests,
            'guests_per_day': round(guests_per_day, 2),
            'total_reservations': results.total_reservations,
            'reservations_per_day': round(reservations_per_day, 2),
            'total_cancellations': results.total_cancellations,
            'cancellation_rate': round(cancellation_rate * 100, 2),
            'walk_in_rate': round(walk_in_rate * 100, 2),
            'group_booking_rate': round(group_booking_rate * 100, 2),
            'extended_stay_rate': round(extended_stay_rate * 100, 2),
            'loyalty_booking_rate': round(loyalty_booking_rate * 100, 2),
            'special_requests_per_guest': round(special_requests_per_guest, 2),
            'total_walk_ins': results.total_walk_ins,
            'total_group_bookings': results.total_group_bookings,
            'total_extended_stays': results.total_extended_stays,
            'total_loyalty_bookings': results.total_loyalty_bookings,
            'total_special_requests': results.total_special_requests,
            'average_occupancy': round(results.occupancy_rate, 2),
            'event_breakdown': dict(event_types),
            'revenue_breakdown': {k: round(v, 2) for k, v in revenue_by_type.items()},
            'busy_days': self._find_busy_days(results),
            'slow_days': self._find_slow_days(results)
        }
    
    def _find_busy_days(self, results: SimulationResults) -> List[str]:
        """Find days with high occupancy"""
        if not results.events:
            return []
        
        # Group events by day
        daily_events = defaultdict(list)
        for event in results.events:
            daily_events[event.day].append(event)
        
        # Find days with many check-ins
        busy_days = []
        for day, events in daily_events.items():
            check_ins = sum(1 for e in events if e.event_type == 'check_in')
            if check_ins >= 3:  # Arbitrary threshold
                busy_days.append(f"Day {day}")
        
        return busy_days
    
    def _find_slow_days(self, results: SimulationResults) -> List[str]:
        """Find days with low activity"""
        if not results.events:
            return []
        
        # Group events by day
        daily_events = defaultdict(list)
        for event in results.events:
            daily_events[event.day].append(event)
        
        # Find days with few events
        slow_days = []
        for day, events in daily_events.items():
            if len(events) <= 2:  # Arbitrary threshold
                slow_days.append(f"Day {day}")
        
        return slow_days
    
    def export_events_to_csv(self, results: SimulationResults, filename: str = "simulation_events.csv"):
        """Export simulation events to CSV file"""
        try:
            with open(filename, 'w') as f:
                f.write("Day,Time,Event Type,Description,Amount,Guest ID,Room,Reservation ID\n")
                for event in results.events:
                    f.write(f"{event.day},{event.time},{event.event_type},{event.description},"
                           f"{event.amount},{event.guest_id or ''},{event.room_number or ''},{event.reservation_id or ''}\n")
            print(f"✓ Exported events to {filename}")
        except Exception as e:
            print(f"Error exporting events: {e}")
    
    def run_benchmark(self, days: int = 30) -> Dict[str, float]:
        """Run performance benchmark"""
        print(f"Running benchmark for {days} days...")
        
        start_time = time.time()
        results = self.run_simulation(days, verbose=False)
        end_time = time.time()
        
        elapsed = end_time - start_time
        
        return {
            'total_time_seconds': round(elapsed, 2),
            'days_per_second': round(days / elapsed, 2),
            'events_per_second': round(len(results.events) / elapsed, 2) if results.events else 0,
            'memory_usage_mb': self._get_memory_usage()
        }
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage (simplified)"""
        try:
            import psutil
            import os
            process = psutil.Process(os.getpid())
            return round(process.memory_info().rss / 1024 / 1024, 2)
        except ImportError:
            return 0.0  # psutil not available


class AdvancedSimulationEngine(HotelSimulationEngine):
    """Extended simulation engine with more sophisticated features"""
    
    def __init__(self, hotel_id: int, db_path: str = 'hotel.db'):
        super().__init__(hotel_id, db_path)
        # Extend config with additional parameters
        self.config.seasonal_variation = True
        self.config.weekend_effect = True
    
    def run_simulation(self, days: int = 30, verbose: bool = True) -> SimulationResults:
        """Run advanced simulation with seasonal and weekend effects"""
        print(f"Starting Advanced Hotel Simulation: {days} days")
        print("=" * 60)
        
        self.results = SimulationResults()
        self.results.total_days = days
        
        # Generate guest names
        first_names = ['John', 'Jane', 'Michael', 'Sarah', 'David', 'Emily', 'Robert', 'Jennifer']
        last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Miller', 'Davis', 'Wilson']
        
        for day in range(1, days + 1):
            self.current_date += datetime.timedelta(days=1)
            day_name = self.current_date.strftime("%A")
            date_str = self.current_date.strftime("%Y-%m-%d")
            is_weekend = day_name in ['Saturday', 'Sunday']
            
            if verbose:
                print(f"\n📅 Day {day} ({day_name}, {date_str}) {'🎉 Weekend' if is_weekend else ''}")
                print("-" * 50)
            
            # Apply weekend effects
            if is_weekend:
                self.config.new_reservation_probability *= 1.5  # More weekend bookings
                self.config.average_stay_days = (1, 3)  # Shorter weekend stays
            else:
                self.config.new_reservation_probability = 0.3  # Reset to default
                self.config.average_stay_days = (1, 7)  # Normal stays
            
            # Run standard simulation day
            super().run_simulation(1, verbose=verbose)
            
            # Add seasonal pricing variation (simplified)
            if self.config.seasonal_variation:
                month = self.current_date.month
                if month in [6, 7, 8]:  # Summer season
                    self._apply_seasonal_pricing(1.2)  # 20% premium
                elif month in [12, 1, 2]:  # Winter season
                    self._apply_seasonal_pricing(0.9)  # 10% discount
                else:
                    self._apply_seasonal_pricing(1.0)  # Normal pricing
        
        return self.results
    
    def _apply_seasonal_pricing(self, multiplier: float):
        """Apply seasonal pricing multiplier to available rooms"""
        try:
            # This would update room prices in a real implementation
            # For simulation, we'll just log it
            if multiplier != 1.0:
                print(f"🌞 Seasonal pricing: {multiplier:.0%}")
        except Exception as e:
            print(f"Error applying seasonal pricing: {e}")


if __name__ == "__main__":
    # Test the simulation engine
    print("Hotel Simulation Engine Test")
    print("=" * 60)
    
    try:
        # Test 1: Basic simulation
        print("\n[TEST 1] Basic Simulation (7 days)")
        print("-" * 50)
        
        engine = HotelSimulationEngine(hotel_id=5)
        results = engine.run_simulation(days=7, verbose=True)
        
        print(f"\n📊 Simulation Results:")
        print(f"  Total Days: {results.total_days}")
        print(f"  Total Guests: {results.total_guests}")
        print(f"  Total Reservations: {results.total_reservations}")
        print(f"  Total Revenue: ${results.total_revenue:.2f}")
        print(f"  Total Cancellations: {results.total_cancellations}")
        print(f"  Average Occupancy: {results.occupancy_rate:.2f}%")
        print(f"  Total Events: {len(results.events)}")
        
        # Generate detailed report
        report = engine.generate_detailed_report(results)
        print(f"\n📈 Detailed Report:")
        print(f"  Revenue per Day: ${report['revenue_per_day']:.2f}")
        print(f"  Guests per Day: {report['guests_per_day']:.2f}")
        print(f"  Cancellation Rate: {report['cancellation_rate']:.2f}%")
        print(f"  Event Types: {report['event_breakdown']}")
        
        # Export events
        engine.export_events_to_csv(results, "test_simulation_events.csv")
        
        # Test 2: Performance benchmark
        print("\n[TEST 2] Performance Benchmark (30 days)")
        print("-" * 50)
        
        benchmark = engine.run_benchmark(days=30)
        print(f"🚀 Benchmark Results:")
        print(f"  Total Time: {benchmark['total_time_seconds']} seconds")
        print(f"  Days per Second: {benchmark['days_per_second']}")
        print(f"  Events per Second: {benchmark['events_per_second']}")
        print(f"  Memory Usage: {benchmark['memory_usage_mb']} MB")
        
        # Test 3: Advanced simulation with seasonal effects
        print("\n[TEST 3] Advanced Simulation (14 days with seasonal effects)")
        print("-" * 50)
        
        advanced_engine = AdvancedSimulationEngine(hotel_id=5)
        advanced_results = advanced_engine.run_simulation(days=14, verbose=True)
        
        print(f"\n📊 Advanced Simulation Results:")
        print(f"  Total Days: {advanced_results.total_days}")
        print(f"  Total Guests: {advanced_results.total_guests}")
        print(f"  Total Revenue: ${advanced_results.total_revenue:.2f}")
        print(f"  Average Occupancy: {advanced_results.occupancy_rate:.2f}%")
        
        print("\n" + "=" * 60)
        print("✅ ALL SIMULATION TESTS COMPLETED SUCCESSFULLY")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error during simulation testing: {e}")
        import traceback
        traceback.print_exc()