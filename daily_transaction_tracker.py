#!/usr/bin/env python3
"""
Daily Transaction Tracker for Hotel Simulator
Provides functionality to track all transactions by date and analyze room occupancy and revenue
"""

import sqlite3
import datetime
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import sys
import os

# Add the parent directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from database import HotelDatabase


@dataclass
class DailyTransactionSummary:
    """Summary of transactions and occupancy for a specific date"""
    date: str
    hotel_id: int
    hotel_name: str = ""
    total_rooms: int = 0
    occupied_rooms: int = 0
    available_rooms: int = 0
    reserved_rooms: int = 0
    maintenance_rooms: int = 0
    check_ins: int = 0
    check_outs: int = 0
    new_reservations: int = 0
    cancellations: int = 0
    total_revenue: float = 0.0
    room_revenue: float = 0.0
    additional_revenue: float = 0.0
    expected_end_of_day_revenue: float = 0.0
    occupancy_rate: float = 0.0
    average_daily_rate: float = 0.0
    revenue_per_available_room: float = 0.0


@dataclass
class RoomTransactionDetail:
    """Detailed transaction information for a specific room on a specific date"""
    room_number: str
    room_type: str
    status: str
    guest_name: Optional[str] = None
    reservation_id: Optional[int] = None
    check_in_date: Optional[str] = None
    check_out_date: Optional[str] = None
    daily_rate: float = 0.0
    transactions: List[Dict[str, Any]] = None
    
    def __init__(self):
        self.transactions = []


class DailyTransactionTracker:
    """Main class for tracking daily transactions and generating reports"""
    
    def __init__(self, db_path: str = 'hotel.db'):
        """Initialize the transaction tracker with database connection"""
        self.db = HotelDatabase(db_path)
        self.conn = self.db.conn
    
    def get_daily_summary(self, hotel_id: int, date: str) -> DailyTransactionSummary:
        """Get comprehensive daily summary for a specific hotel and date
        
        Args:
            hotel_id: ID of the hotel
            date: Date in YYYY-MM-DD format
            
        Returns:
            DailyTransactionSummary object with all metrics
        """
        summary = DailyTransactionSummary(date=date, hotel_id=hotel_id)
        
        # Get hotel information
        hotel_info = self._get_hotel_info(hotel_id)
        if hotel_info:
            summary.hotel_name = hotel_info['name']
            summary.total_rooms = hotel_info['total_rooms']
        
        # Get room status counts
        room_status = self._get_room_status_counts(hotel_id, date)
        summary.occupied_rooms = room_status.get('occupied', 0)
        summary.available_rooms = room_status.get('available', 0)
        summary.reserved_rooms = room_status.get('reserved', 0)
        summary.maintenance_rooms = room_status.get('maintenance', 0)
        
        # Calculate occupancy rate
        if summary.total_rooms > 0:
            summary.occupancy_rate = (summary.occupied_rooms / summary.total_rooms) * 100
        
        # Get transaction counts for the day
        transaction_counts = self._get_transaction_counts(hotel_id, date)
        summary.check_ins = transaction_counts.get('check_ins', 0)
        summary.check_outs = transaction_counts.get('check_outs', 0)
        summary.new_reservations = transaction_counts.get('new_reservations', 0)
        summary.cancellations = transaction_counts.get('cancellations', 0)
        
        # Get revenue information
        revenue_data = self._get_daily_revenue(hotel_id, date)
        summary.total_revenue = revenue_data.get('total_revenue', 0.0)
        summary.room_revenue = revenue_data.get('room_revenue', 0.0)
        summary.additional_revenue = revenue_data.get('additional_revenue', 0.0)
        
        # Calculate expected end-of-day revenue
        summary.expected_end_of_day_revenue = self._calculate_expected_revenue(hotel_id, date)
        
        # Calculate ADR (Average Daily Rate)
        if summary.occupied_rooms > 0:
            summary.average_daily_rate = summary.room_revenue / summary.occupied_rooms
        
        # Calculate RevPAR (Revenue Per Available Room)
        if summary.total_rooms > 0:
            summary.revenue_per_available_room = summary.room_revenue / summary.total_rooms
        
        return summary
    
    def get_room_details(self, hotel_id: int, date: str) -> List[RoomTransactionDetail]:
        """Get detailed transaction information for each room on a specific date
        
        Args:
            hotel_id: ID of the hotel
            date: Date in YYYY-MM-DD format
            
        Returns:
            List of RoomTransactionDetail objects
        """
        details = []
        
        # Get all rooms for the hotel
        rooms = self._get_hotel_rooms(hotel_id)
        
        for room in rooms:
            room_detail = RoomTransactionDetail()
            room_detail.room_number = room['room_number']
            room_detail.room_type = room['room_type']
            room_detail.daily_rate = room['price_per_night']
            
            # Get current guest information to determine actual status
            guest_info = self._get_current_guest_for_room(room['id'], date)
            
            if guest_info:
                # Room is actually occupied if there's a checked-in guest
                room_detail.status = 'occupied'
                room_detail.guest_name = f"{guest_info['first_name']} {guest_info['last_name']}"
                room_detail.reservation_id = guest_info['reservation_id']
                room_detail.check_in_date = guest_info['check_in_date']
                room_detail.check_out_date = guest_info['check_out_date']
            else:
                # Check if room is reserved for this date
                is_reserved = self._is_room_reserved_for_date(room['id'], date)
                if is_reserved:
                    room_detail.status = 'reserved'
                else:
                    # Check if room had any activity today (check-ins/outs)
                    had_activity = self._room_had_activity_today(room['id'], date)
                    if had_activity:
                        room_detail.status = 'occupied'  # Room was occupied during the day
                        # Try to get checkout guest information for rooms that checked out today
                        checkout_guest = self._get_checkout_guest_for_room(room['id'], date)
                        if checkout_guest:
                            room_detail.guest_name = f"{checkout_guest['first_name']} {checkout_guest['last_name']}"
                            room_detail.reservation_id = checkout_guest['reservation_id']
                            room_detail.check_in_date = checkout_guest['check_in_date']
                            room_detail.check_out_date = checkout_guest['check_out_date']
                            # Calculate daily rate
                            try:
                                check_in = datetime.datetime.strptime(checkout_guest['check_in_date'], '%Y-%m-%d')
                                check_out = datetime.datetime.strptime(checkout_guest['check_out_date'], '%Y-%m-%d')
                                nights = (check_out - check_in).days
                                if nights > 0:
                                    # This is a simplified rate calculation - in a real system you'd get the actual room rate
                                    room_detail.daily_rate = 220.00  # Default standard room rate
                            except:
                                room_detail.daily_rate = 220.00  # Fallback rate
                    else:
                        # Use database status for other cases (maintenance, etc.)
                        room_detail.status = room['status']
            
            # Get transactions for this room on this date
            transactions = self._get_room_transactions(room['id'], date)
            room_detail.transactions = transactions
            
            details.append(room_detail)
        
        return details
    
    def get_date_range_summary(self, hotel_id: int, start_date: str, end_date: str) -> List[DailyTransactionSummary]:
        """Get daily summaries for a date range
        
        Args:
            hotel_id: ID of the hotel
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            
        Returns:
            List of DailyTransactionSummary objects for each day in range
        """
        summaries = []
        
        # Parse dates
        start = datetime.datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.datetime.strptime(end_date, '%Y-%m-%d')
        
        # Generate summary for each day in range
        current_date = start
        while current_date <= end:
            date_str = current_date.strftime('%Y-%m-%d')
            summary = self.get_daily_summary(hotel_id, date_str)
            summaries.append(summary)
            current_date += datetime.timedelta(days=1)
        
        return summaries
    
    def generate_daily_report(self, hotel_id: int, date: str, format: str = 'text') -> str:
        """Generate a formatted daily report
        
        Args:
            hotel_id: ID of the hotel
            date: Date in YYYY-MM-DD format
            format: Output format ('text', 'csv', 'json')
            
        Returns:
            Formatted report string
        """
        summary = self.get_daily_summary(hotel_id, date)
        room_details = self.get_room_details(hotel_id, date)
        
        if format == 'text':
            return self._format_text_report(summary, room_details)
        elif format == 'csv':
            return self._format_csv_report(summary, room_details)
        elif format == 'json':
            return self._format_json_report(summary, room_details)
        else:
            raise ValueError(f"Unknown format: {format}")
    
    def _get_hotel_info(self, hotel_id: int) -> Optional[Dict]:
        """Get basic hotel information"""
        try:
            query = "SELECT name, total_rooms FROM hotel WHERE id = ?"
            return self.db.execute_query(query, (hotel_id,), fetch=True)[0]
        except Exception as e:
            print(f"Error getting hotel info: {e}")
            return None
    
    def _get_room_status_counts(self, hotel_id: int, date: str) -> Dict[str, int]:
        """Get counts of rooms by status for a specific date"""
        try:
            # Get actual room statuses from database
            query = """
                SELECT 
                    status, 
                    COUNT(*) as count
                FROM rooms 
                WHERE hotel_id = ?
                GROUP BY status
            """
            results = self.db.execute_query(query, (hotel_id,), fetch=True)
            status_counts = {row['status']: row['count'] for row in results}
            
            # Get count of actually occupied rooms (with checked-in guests OR today's activity)
            # For transaction reports, we want to show rooms that were occupied during the day
            occupied_query = """
                SELECT COUNT(DISTINCT rm.id) as occupied
                FROM rooms rm
                LEFT JOIN reservations r ON rm.id = r.room_id
                WHERE rm.hotel_id = ?
                AND (
                    -- Currently checked-in guests
                    (r.status = 'checked_in' AND r.check_in_date <= ? AND r.check_out_date >= ?)
                    OR
                    -- Rooms with check-in/out activity today
                    (r.status IN ('checked_in', 'checked_out') AND (r.check_in_date = ? OR r.check_out_date = ?))
                    OR
                    -- Multi-day stays (checked in before, checking out after)
                    (r.status = 'checked_in' AND r.check_in_date < ? AND r.check_out_date > ?)
                )
            """
            occupied_result = self.db.execute_query(occupied_query, (hotel_id, date, date, date, date, date, date), fetch=True)
            actual_occupied = occupied_result[0]['occupied'] if occupied_result else 0
            
            # Override the occupied count with the actual count
            status_counts['occupied'] = actual_occupied
            
            return status_counts
        except Exception as e:
            print(f"Error getting room status counts: {e}")
            return {}
    
    def _get_transaction_counts(self, hotel_id: int, date: str) -> Dict[str, int]:
        """Get counts of different transaction types for a specific date"""
        try:
            # Check-ins (reservations that transitioned to checked_in status on this date)
            check_in_query = """
                SELECT COUNT(*) as count
                FROM reservations 
                WHERE room_id IN (
                    SELECT id FROM rooms WHERE hotel_id = ?
                )
                AND check_in_date = ?
                AND status = 'checked_in'
            """
            check_ins = self.db.execute_query(check_in_query, (hotel_id, date), fetch=True)[0]['count']
            
            # Check-outs (reservations that ended on this date)
            check_out_query = """
                SELECT COUNT(*) as count
                FROM reservations 
                WHERE room_id IN (
                    SELECT id FROM rooms WHERE hotel_id = ?
                )
                AND check_out_date = ?
                AND status = 'checked_out'
            """
            check_outs = self.db.execute_query(check_out_query, (hotel_id, date), fetch=True)[0]['count']
            
            # New reservations (created on this date)
            new_res_query = """
                SELECT COUNT(*) as count
                FROM reservations 
                WHERE room_id IN (
                    SELECT id FROM rooms WHERE hotel_id = ?
                )
                AND booking_date LIKE ?
                AND status IN ('confirmed', 'checked_in')
            """
            new_reservations = self.db.execute_query(new_res_query, (hotel_id, f"{date}%"), fetch=True)[0]['count']
            
            # Cancellations (cancelled on this date)
            cancel_query = """
                SELECT COUNT(*) as count
                FROM reservations 
                WHERE room_id IN (
                    SELECT id FROM rooms WHERE hotel_id = ?
                )
                AND status = 'cancelled'
                AND booking_date LIKE ?
            """
            cancellations = self.db.execute_query(cancel_query, (hotel_id, f"{date}%"), fetch=True)[0]['count']
            
            return {
                'check_ins': check_ins,
                'check_outs': check_outs,
                'new_reservations': new_reservations,
                'cancellations': cancellations
            }
        except Exception as e:
            print(f"Error getting transaction counts: {e}")
            return {}
    
    def _get_daily_revenue(self, hotel_id: int, date: str) -> Dict[str, float]:
        """Get revenue breakdown for a specific date"""
        try:
            # Total revenue from all transactions on this date
            total_query = """
                SELECT 
                    SUM(amount) as total_revenue
                FROM transactions 
                WHERE transaction_date LIKE ?
                AND reservation_id IN (
                    SELECT id FROM reservations 
                    WHERE room_id IN (
                        SELECT id FROM rooms WHERE hotel_id = ?
                    )
                )
            """
            total_revenue = self.db.execute_query(total_query, (f"{date}%", hotel_id), fetch=True)[0]['total_revenue'] or 0.0
            
            # Room revenue (from room charges)
            room_query = """
                SELECT 
                    SUM(amount) as room_revenue
                FROM transactions 
                WHERE transaction_date LIKE ?
                AND transaction_type = 'payment'
                AND description LIKE '%room%'
                AND reservation_id IN (
                    SELECT id FROM reservations 
                    WHERE room_id IN (
                        SELECT id FROM rooms WHERE hotel_id = ?
                    )
                )
            """
            room_revenue = self.db.execute_query(room_query, (f"{date}%", hotel_id), fetch=True)[0]['room_revenue'] or 0.0
            
            # Additional revenue (from other services)
            additional_query = """
                SELECT 
                    SUM(amount) as additional_revenue
                FROM transactions 
                WHERE transaction_date LIKE ?
                AND transaction_type IN ('charge', 'payment')
                AND description NOT LIKE '%room%'
                AND reservation_id IN (
                    SELECT id FROM reservations 
                    WHERE room_id IN (
                        SELECT id FROM rooms WHERE hotel_id = ?
                    )
                )
            """
            additional_revenue = self.db.execute_query(additional_query, (f"{date}%", hotel_id), fetch=True)[0]['additional_revenue'] or 0.0
            
            return {
                'total_revenue': total_revenue,
                'room_revenue': room_revenue,
                'additional_revenue': additional_revenue
            }
        except Exception as e:
            print(f"Error getting daily revenue: {e}")
            return {}
    
    def _calculate_expected_revenue(self, hotel_id: int, date: str) -> float:
        """Calculate expected end-of-day revenue based on current reservations"""
        try:
            # Get all active reservations for this date
            query = """
                SELECT 
                    r.id as reservation_id,
                    r.total_price,
                    r.check_out_date,
                    rm.price_per_night
                FROM reservations r
                JOIN rooms rm ON r.room_id = rm.id
                WHERE rm.hotel_id = ?
                AND r.status IN ('checked_in', 'confirmed')
                AND r.check_in_date <= ?
                AND r.check_out_date >= ?
            """
            reservations = self.db.execute_query(query, (hotel_id, date, date), fetch=True)
            
            expected_revenue = 0.0
            
            for res in reservations:
                # For reservations that end today, add the full amount
                if res['check_out_date'] == date:
                    expected_revenue += res['total_price']
                # For ongoing reservations, add the daily rate
                else:
                    expected_revenue += res['price_per_night']
            
            # Add expected additional revenue (average from past days)
            avg_additional = self._get_average_additional_revenue(hotel_id)
            expected_revenue += avg_additional
            
            return expected_revenue
        except Exception as e:
            print(f"Error calculating expected revenue: {e}")
            return 0.0
    
    def _get_average_additional_revenue(self, hotel_id: int) -> float:
        """Get average additional revenue from past 7 days"""
        try:
            # Get additional revenue from past 7 days
            seven_days_ago = (datetime.datetime.now() - datetime.timedelta(days=7)).strftime('%Y-%m-%d')
            today = datetime.datetime.now().strftime('%Y-%m-%d')
            
            query = """
                SELECT 
                    AVG(amount) as avg_additional
                FROM transactions 
                WHERE transaction_date BETWEEN ? AND ?
                AND transaction_type IN ('charge', 'payment')
                AND description NOT LIKE '%room%'
                AND reservation_id IN (
                    SELECT id FROM reservations 
                    WHERE room_id IN (
                        SELECT id FROM rooms WHERE hotel_id = ?
                    )
                )
            """
            result = self.db.execute_query(query, (seven_days_ago, today, hotel_id), fetch=True)[0]['avg_additional']
            return result or 0.0
        except Exception as e:
            print(f"Error getting average additional revenue: {e}")
            return 0.0
    
    def _get_hotel_rooms(self, hotel_id: int) -> List[Dict]:
        """Get all rooms for a hotel"""
        try:
            # Try with room_type first, fall back to simpler query if needed
            query = """
                SELECT 
                    id, room_number, status, price_per_night
                FROM rooms 
                WHERE hotel_id = ?
                ORDER BY room_number
            """
            rooms = self.db.execute_query(query, (hotel_id,), fetch=True)
            
            # If we need room_type, we can get it from room_types table
            # For now, use a default value if not available
            for room in rooms:
                if 'room_type' not in room:
                    room['room_type'] = 'Standard'  # Default room type
            
            return rooms
        except Exception as e:
            print(f"Error getting hotel rooms: {e}")
            return []
    
    def _is_room_reserved_for_date(self, room_id: int, date: str) -> bool:
        """Check if a room is reserved for a specific date"""
        try:
            query = """
                SELECT COUNT(*) as count
                FROM reservations r
                WHERE r.room_id = ?
                AND r.status IN ('confirmed', 'reserved')
                AND r.check_in_date <= ?
                AND r.check_out_date >= ?
            """
            results = self.db.execute_query(query, (room_id, date, date), fetch=True)
            return results[0]['count'] > 0 if results else False
        except Exception as e:
            print(f"Error checking room reservation: {e}")
            return False

    def _room_had_activity_today(self, room_id: int, date: str) -> bool:
        """Check if a room had activity today (check-in/out) or is occupied by multi-day stay"""
        try:
            # Check for check-in/out activity today
            activity_query = """
                SELECT COUNT(*) as count
                FROM reservations 
                WHERE room_id = ? 
                AND (check_in_date = ? OR check_out_date = ?)
                AND status IN ('checked_in', 'checked_out')
            """
            activity_result = self.db.execute_query(activity_query, (room_id, date, date), fetch=True)
            
            if activity_result[0]['count'] > 0:
                return True
            
            # Check for multi-day stays (checked in before, checking out after)
            multi_day_query = """
                SELECT COUNT(*) as count
                FROM reservations 
                WHERE room_id = ? 
                AND status = 'checked_in'
                AND check_in_date < ?
                AND check_out_date > ?
            """
            multi_day_result = self.db.execute_query(multi_day_query, (room_id, date, date), fetch=True)
            
            return multi_day_result[0]['count'] > 0
            
        except Exception as e:
            print(f"Error checking room activity: {e}")
            return False

    def _get_current_guest_for_room(self, room_id: int, date: str) -> Optional[Dict]:
        """Get current guest information for a room"""
        try:
            query = """
                SELECT 
                    g.first_name, g.last_name, r.id as reservation_id,
                    r.check_in_date, r.check_out_date
                FROM guests g
                JOIN reservations r ON g.id = r.guest_id
                WHERE r.room_id = ?
                AND r.status = 'checked_in'
                AND r.check_in_date <= ?
                AND r.check_out_date >= ?
            """
            results = self.db.execute_query(query, (room_id, date, date), fetch=True)
            return results[0] if results else None
        except Exception as e:
            print(f"Error getting current guest: {e}")
            return None

    def _get_checkout_guest_for_room(self, room_id: int, date: str) -> Optional[Dict]:
        """Get guest information for rooms that checked out today"""
        try:
            query = """
                SELECT 
                    g.first_name, g.last_name, r.id as reservation_id,
                    r.check_in_date, r.check_out_date
                FROM guests g
                JOIN reservations r ON g.id = r.guest_id
                WHERE r.room_id = ?
                AND r.check_out_date = ?
                AND r.status = 'checked_out'
                ORDER BY r.id DESC
                LIMIT 1
            """
            results = self.db.execute_query(query, (room_id, date), fetch=True)
            return results[0] if results else None
        except Exception as e:
            print(f"Error getting checkout guest: {e}")
            return None

    def _get_room_transactions(self, room_id: int, date: str) -> List[Dict]:
        """Get all transactions for a room on a specific date"""
        try:
            query = """
                SELECT 
                    t.id, t.amount, t.transaction_type, t.payment_method,
                    t.transaction_date, t.description
                FROM transactions t
                JOIN reservations r ON t.reservation_id = r.id
                WHERE r.room_id = ?
                AND t.transaction_date LIKE ?
                ORDER BY t.transaction_date
            """
            return self.db.execute_query(query, (room_id, f"{date}%"), fetch=True)
        except Exception as e:
            print(f"Error getting room transactions: {e}")
            return []
    
    def _format_text_report(self, summary: DailyTransactionSummary, room_details: List[RoomTransactionDetail]) -> str:
        """Format report as text"""
        report = []
        report.append("=" * 80)
        report.append(f"DAILY TRANSACTION REPORT - {summary.hotel_name}")
        report.append(f"Date: {summary.date}")
        report.append("=" * 80)
        report.append("")
        
        # Summary section
        report.append("📊 SUMMARY")
        report.append("-" * 40)
        report.append(f"Total Rooms: {summary.total_rooms}")
        report.append(f"Occupied: {summary.occupied_rooms} | Available: {summary.available_rooms}")
        report.append(f"Reserved: {summary.reserved_rooms} | Maintenance: {summary.maintenance_rooms}")
        report.append(f"Occupancy Rate: {summary.occupancy_rate:.1f}%")
        report.append(f"Average Daily Rate: ${summary.average_daily_rate:.2f}")
        report.append(f"RevPAR: ${summary.revenue_per_available_room:.2f}")
        report.append("")
        
        # Activity section
        report.append("📈 ACTIVITY")
        report.append("-" * 40)
        report.append(f"Check-ins: {summary.check_ins}")
        report.append(f"Check-outs: {summary.check_outs}")
        report.append(f"New Reservations: {summary.new_reservations}")
        report.append(f"Cancellations: {summary.cancellations}")
        report.append("")
        
        # Revenue section
        report.append("💰 REVENUE")
        report.append("-" * 40)
        report.append(f"Total Revenue (Today): ${summary.total_revenue:.2f}")
        report.append(f"  Room Revenue: ${summary.room_revenue:.2f}")
        report.append(f"  Additional Revenue: ${summary.additional_revenue:.2f}")
        report.append(f"Expected End-of-Day Revenue: ${summary.expected_end_of_day_revenue:.2f}")
        report.append("")
        
        # Room details section
        report.append("🏨 ROOM DETAILS")
        report.append("-" * 40)
        
        for room in room_details:
            status_icon = "🟢" if room.status == "available" else "🔴"
            report.append(f"Room {room.room_number} ({room.room_type}): {status_icon} {room.status}")
            
            if room.guest_name:
                report.append(f"  Guest: {room.guest_name}")
                report.append(f"  Rate: ${room.daily_rate:.2f}/night")
                report.append(f"  Stay: {room.check_in_date} → {room.check_out_date}")
            
            if room.transactions:
                report.append(f"  Transactions ({len(room.transactions)}):")
                for tx in room.transactions:
                    report.append(f"    {tx['transaction_date']}: {tx['description']} - ${tx['amount']:.2f}")
        
        report.append("")
        report.append("=" * 80)
        
        return "\n".join(report)
    
    def _format_csv_report(self, summary: DailyTransactionSummary, room_details: List[RoomTransactionDetail]) -> str:
        """Format report as CSV"""
        lines = []
        
        # Header
        lines.append("Daily Transaction Report")
        lines.append(f"Hotel: {summary.hotel_name}")
        lines.append(f"Date: {summary.date}")
        lines.append("")
        
        # Summary
        lines.append("Summary,,,")
        lines.append(f"Total Rooms,{summary.total_rooms},,")
        lines.append(f"Occupied,{summary.occupied_rooms},,")
        lines.append(f"Available,{summary.available_rooms},,")
        lines.append(f"Reserved,{summary.reserved_rooms},,")
        lines.append(f"Maintenance,{summary.maintenance_rooms},,")
        lines.append(f"Occupancy Rate,{summary.occupancy_rate:.1f}%,,")
        lines.append(f"ADR,${summary.average_daily_rate:.2f},,")
        lines.append(f"RevPAR,${summary.revenue_per_available_room:.2f},,")
        lines.append("")
        
        # Activity
        lines.append("Activity,,,")
        lines.append(f"Check-ins,{summary.check_ins},,")
        lines.append(f"Check-outs,{summary.check_outs},,")
        lines.append(f"New Reservations,{summary.new_reservations},,")
        lines.append(f"Cancellations,{summary.cancellations},,")
        lines.append("")
        
        # Revenue
        lines.append("Revenue,,,")
        lines.append(f"Total Revenue,${summary.total_revenue:.2f},,")
        lines.append(f"Room Revenue,${summary.room_revenue:.2f},,")
        lines.append(f"Additional Revenue,${summary.additional_revenue:.2f},,")
        lines.append(f"Expected EOD Revenue,${summary.expected_end_of_day_revenue:.2f},,")
        lines.append("")
        
        # Room details header
        lines.append("Room Details,,,,")
        lines.append("Room Number,Room Type,Status,Guest,Rate,Check-in,Check-out,Transactions")
        
        # Room details
        for room in room_details:
            guest_info = room.guest_name or ""
            check_in = room.check_in_date or ""
            check_out = room.check_out_date or ""
            tx_count = len(room.transactions)
            
            lines.append(f"{room.room_number},{room.room_type},{room.status},{guest_info},${room.daily_rate:.2f},{check_in},{check_out},{tx_count}")
        
        return "\n".join(lines)
    
    def _format_json_report(self, summary: DailyTransactionSummary, room_details: List[RoomTransactionDetail]) -> str:
        """Format report as JSON"""
        import json
        
        report_data = {
            "report_type": "daily_transaction_report",
            "hotel": {
                "id": summary.hotel_id,
                "name": summary.hotel_name,
                "total_rooms": summary.total_rooms
            },
            "date": summary.date,
            "summary": {
                "room_status": {
                    "occupied": summary.occupied_rooms,
                    "available": summary.available_rooms,
                    "reserved": summary.reserved_rooms,
                    "maintenance": summary.maintenance_rooms
                },
                "occupancy_rate": summary.occupancy_rate,
                "average_daily_rate": summary.average_daily_rate,
                "revpar": summary.revenue_per_available_room,
                "activity": {
                    "check_ins": summary.check_ins,
                    "check_outs": summary.check_outs,
                    "new_reservations": summary.new_reservations,
                    "cancellations": summary.cancellations
                },
                "revenue": {
                    "total": summary.total_revenue,
                    "room_revenue": summary.room_revenue,
                    "additional_revenue": summary.additional_revenue,
                    "expected_end_of_day": summary.expected_end_of_day_revenue
                }
            },
            "rooms": []
        }
        
        # Add room details
        for room in room_details:
            room_data = {
                "room_number": room.room_number,
                "room_type": room.room_type,
                "status": room.status,
                "daily_rate": room.daily_rate,
                "transactions": room.transactions
            }
            
            if room.guest_name:
                room_data["guest"] = room.guest_name
                room_data["reservation_id"] = room.reservation_id
                room_data["check_in_date"] = room.check_in_date
                room_data["check_out_date"] = room.check_out_date
            
            report_data["rooms"].append(room_data)
        
        return json.dumps(report_data, indent=2)


def create_daily_transaction_report(hotel_id: int, date: str, format: str = 'text'):
    """Convenience function to create a daily transaction report"""
    tracker = DailyTransactionTracker()
    return tracker.generate_daily_report(hotel_id, date, format)


if __name__ == "__main__":
    # Example usage
    print("Daily Transaction Tracker - Example Usage")
    print("=" * 60)
    
    try:
        # Create tracker instance
        tracker = DailyTransactionTracker()
        
        # Get today's date
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        
        # Generate report for hotel ID 1
        print(f"\n📊 Generating daily report for Hotel ID 1 - {today}")
        report = tracker.generate_daily_report(1, today, 'text')
        print(report)
        
        # Get daily summary
        print(f"\n📈 Getting daily summary for Hotel ID 1 - {today}")
        summary = tracker.get_daily_summary(1, today)
        print(f"Occupancy: {summary.occupancy_rate:.1f}%")
        print(f"Expected Revenue: ${summary.expected_end_of_day_revenue:.2f}")
        print(f"ADR: ${summary.average_daily_rate:.2f}")
        print(f"RevPAR: ${summary.revenue_per_available_room:.2f}")
        
        # Get room details
        print(f"\n🏨 Getting room details for Hotel ID 1 - {today}")
        rooms = tracker.get_room_details(1, today)
        print(f"Found {len(rooms)} rooms")
        occupied = sum(1 for r in rooms if r.status == 'occupied')
        print(f"Occupied rooms: {occupied}")
        
        # Generate CSV report
        print(f"\n📄 Generating CSV report")
        csv_report = tracker.generate_daily_report(1, today, 'csv')
        print("CSV report generated (first few lines shown):")
        print('\n'.join(csv_report.split('\n')[:10]) + "...")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()