#!/usr/bin/env python3
"""
Hotel Simulator - Reporting System (Phase 4)
Comprehensive reporting functionality for hotel operations
"""

import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import csv
import os
from tabulate import tabulate


class ReportType(Enum):
    """Types of reports available in the system"""
    DAILY_STATUS = "daily_status"
    FINANCIAL_SUMMARY = "financial_summary"
    OCCUPANCY_ANALYSIS = "occupancy_analysis"
    REVENUE_BY_ROOM_TYPE = "revenue_by_room_type"
    GUEST_DEMOGRAPHICS = "guest_demographics"
    HOUSEKEEPING_STATUS = "housekeeping_status"
    CANCELLATION_ANALYSIS = "cancellation_analysis"


class TimePeriod(Enum):
    """Time periods for reporting"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    CUSTOM = "custom"


@dataclass
class ReportConfig:
    """Configuration for report generation"""
    report_type: ReportType
    time_period: TimePeriod
    hotel_id: int
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    output_format: str = "text"  # text, csv, json
    include_details: bool = False
    specific_date: Optional[str] = None  # For daily reports with specific date


@dataclass
class ReportResult:
    """Container for report data"""
    report_type: ReportType
    time_period: TimePeriod
    hotel_id: int
    generated_at: str
    data: Dict[str, Any]
    summary: Dict[str, Any]


class HotelReportingSystem:
    """Comprehensive reporting system for hotel operations"""
    
    def __init__(self, db_path: str = 'hotel.db'):
        """Initialize reporting system with database connection"""
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()
        
    def generate_report(self, config: ReportConfig) -> ReportResult:
        """Generate a report based on configuration"""
        generated_at = datetime.now().isoformat()
        
        # Validate hotel exists
        if not self._hotel_exists(config.hotel_id):
            raise ValueError(f"Hotel ID {config.hotel_id} does not exist")
        
        # Validate date parameters for reports that require them
        if config.report_type in [ReportType.DAILY_STATUS, ReportType.OCCUPANCY_ANALYSIS]:
            self._validate_date_parameters(config)
        
        # Generate the appropriate report
        if config.report_type == ReportType.DAILY_STATUS:
            data, summary = self._generate_daily_status_report(config)
        elif config.report_type == ReportType.FINANCIAL_SUMMARY:
            data, summary = self._generate_financial_summary_report(config)
        elif config.report_type == ReportType.OCCUPANCY_ANALYSIS:
            data, summary = self._generate_occupancy_analysis_report(config)
        elif config.report_type == ReportType.REVENUE_BY_ROOM_TYPE:
            data, summary = self._generate_revenue_by_room_type_report(config)
        elif config.report_type == ReportType.GUEST_DEMOGRAPHICS:
            data, summary = self._generate_guest_demographics_report(config)
        elif config.report_type == ReportType.HOUSEKEEPING_STATUS:
            data, summary = self._generate_housekeeping_status_report(config)
        elif config.report_type == ReportType.CANCELLATION_ANALYSIS:
            data, summary = self._generate_cancellation_analysis_report(config)
        else:
            raise ValueError(f"Unknown report type: {config.report_type}")
        
        return ReportResult(
            report_type=config.report_type,
            time_period=config.time_period,
            hotel_id=config.hotel_id,
            generated_at=generated_at,
            data=data,
            summary=summary
        )
    
    def display_report(self, report: ReportResult, format: str = "text") -> str:
        """Display a report in the specified format"""
        if format == "text":
            return self._display_text_report(report)
        elif format == "csv":
            return self._display_csv_report(report)
        elif format == "json":
            return self._display_json_report(report)
        else:
            raise ValueError(f"Unknown format: {format}")
    
    def export_report(self, report: ReportResult, filename: str, format: str = "csv") -> str:
        """Export report to file"""
        if format == "csv":
            return self._export_csv_report(report, filename)
        elif format == "json":
            return self._export_json_report(report, filename)
        else:
            raise ValueError(f"Unknown export format: {format}")
    
    # Private methods for specific report types
    
    def _generate_daily_status_report(self, config: ReportConfig) -> tuple:
        """Generate daily status report"""
        cursor = self.conn.cursor()
        
        # Get hotel info
        cursor.execute("""
            SELECT name, total_floors, total_rooms 
            FROM hotel 
            WHERE id = ?
        """, (config.hotel_id,))
        hotel_info = cursor.fetchone()
        
        # Get date for daily report (use specific_date if provided, otherwise today)
        current_date = config.specific_date if config.specific_date else datetime.now().strftime('%Y-%m-%d')
        
        # Get room status counts
        cursor.execute("""
            SELECT 
                status, 
                COUNT(*) as count
            FROM rooms 
            WHERE hotel_id = ?
            GROUP BY status
        """, (config.hotel_id,))
        room_status = {row['status']: row['count'] for row in cursor.fetchall()}
        
        # Get reservations for today
        cursor.execute("""
            SELECT 
                COUNT(*) as total_reservations,
                SUM(CASE WHEN status = 'checked_in' THEN 1 ELSE 0 END) as checked_in,
                SUM(CASE WHEN status = 'confirmed' THEN 1 ELSE 0 END) as confirmed,
                SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) as cancelled
            FROM reservations 
            WHERE room_id IN (
                SELECT id FROM rooms WHERE hotel_id = ?
            )
            AND (check_in_date <= ? AND check_out_date >= ?)
        """, (config.hotel_id, current_date, current_date))
        reservation_stats = cursor.fetchone()
        
        # Get housekeeping status
        cursor.execute("""
            SELECT 
                h.status, 
                COUNT(*) as count
            FROM housekeeping h
            JOIN rooms r ON h.room_id = r.id
            WHERE r.hotel_id = ?
            GROUP BY h.status
        """, (config.hotel_id,))
        housekeeping_status = {row['status']: row['count'] for row in cursor.fetchall()}
        
        data = {
            'hotel_info': dict(hotel_info),
            'date': current_date,
            'room_status': room_status,
            'reservation_stats': dict(reservation_stats),
            'housekeeping_status': housekeeping_status
        }
        
        summary = {
            'hotel_id': config.hotel_id,
            'hotel_name': hotel_info['name'],
            'report_date': current_date,
            'total_rooms': hotel_info['total_rooms'],
            'total_floors': hotel_info['total_floors'],
            'occupied_rooms': room_status.get('occupied', 0),
            'available_rooms': room_status.get('available', 0),
            'reserved_rooms': room_status.get('reserved', 0),
            'maintenance_rooms': room_status.get('maintenance', 0),
            'occupancy_rate': (room_status.get('occupied', 0) / hotel_info['total_rooms']) * 100 if hotel_info['total_rooms'] > 0 else 0,
            'current_guests': reservation_stats['checked_in'],
            'check_ins_today': reservation_stats['checked_in'],
            'check_outs_today': reservation_stats['checked_out'],
            'new_reservations': reservation_stats['confirmed'],
            'cancellations': reservation_stats['cancelled']
        }
        
        return data, summary
    
    def _generate_financial_summary_report(self, config: ReportConfig) -> tuple:
        """Generate financial summary report"""
        cursor = self.conn.cursor()
        
        # Determine date range based on time period
        if config.time_period == TimePeriod.DAILY:
            start_date = datetime.now().strftime('%Y-%m-%d')
            end_date = start_date
        elif config.time_period == TimePeriod.WEEKLY:
            start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            end_date = datetime.now().strftime('%Y-%m-%d')
        elif config.time_period == TimePeriod.MONTHLY:
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            end_date = datetime.now().strftime('%Y-%m-%d')
        else:
            start_date = config.start_date or (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            end_date = config.end_date or datetime.now().strftime('%Y-%m-%d')
        
        # Get total revenue
        cursor.execute("""
            SELECT 
                SUM(amount) as total_revenue
            FROM transactions 
            WHERE transaction_type = 'payment'
            AND transaction_date BETWEEN ? AND ?
            AND reservation_id IN (
                SELECT id FROM reservations 
                WHERE room_id IN (
                    SELECT id FROM rooms WHERE hotel_id = ?
                )
            )
        """, (start_date, end_date, config.hotel_id))
        total_revenue = cursor.fetchone()['total_revenue'] or 0.0
        
        # Get revenue by category
        cursor.execute("""
            SELECT 
                transaction_type, 
                SUM(amount) as amount
            FROM transactions 
            WHERE transaction_date BETWEEN ? AND ?
            AND reservation_id IN (
                SELECT id FROM reservations 
                WHERE room_id IN (
                    SELECT id FROM rooms WHERE hotel_id = ?
                )
            )
            GROUP BY transaction_type
        """, (start_date, end_date, config.hotel_id))
        revenue_by_type = {row['transaction_type']: row['amount'] for row in cursor.fetchall()}
        
        # Get payment methods
        cursor.execute("""
            SELECT 
                payment_method, 
                SUM(amount) as amount
            FROM transactions 
            WHERE transaction_date BETWEEN ? AND ?
            AND reservation_id IN (
                SELECT id FROM reservations 
                WHERE room_id IN (
                    SELECT id FROM rooms WHERE hotel_id = ?
                )
            )
            GROUP BY payment_method
        """, (start_date, end_date, config.hotel_id))
        payment_methods = {row['payment_method']: row['amount'] for row in cursor.fetchall()}
        
        # Get average daily rate
        cursor.execute("""
            SELECT 
                AVG(total_price / (julianday(check_out_date) - julianday(check_in_date))) as adr
            FROM reservations 
            WHERE room_id IN (
                SELECT id FROM rooms WHERE hotel_id = ?
            )
            AND check_in_date BETWEEN ? AND ?
            AND status = 'completed'
        """, (config.hotel_id, start_date, end_date))
        adr = cursor.fetchone()['adr'] or 0.0
        
        # Get occupancy rate
        cursor.execute("""
            SELECT 
                COUNT(DISTINCT room_id) as occupied_rooms,
                (SELECT COUNT(*) FROM rooms WHERE hotel_id = ?) as total_rooms
            FROM reservations 
            WHERE room_id IN (
                SELECT id FROM rooms WHERE hotel_id = ?
            )
            AND check_in_date <= ? AND check_out_date >= ?
            AND status = 'checked_in'
        """, (config.hotel_id, config.hotel_id, end_date, end_date))
        result = cursor.fetchone()
        occupied_rooms = result['occupied_rooms']
        total_rooms = result['total_rooms']
        occupancy_rate = (occupied_rooms / total_rooms * 100) if total_rooms > 0 else 0
        
        data = {
            'period': {'start_date': start_date, 'end_date': end_date},
            'total_revenue': total_revenue,
            'revenue_by_type': revenue_by_type,
            'payment_methods': payment_methods,
            'average_daily_rate': adr,
            'occupancy_rate': occupancy_rate,
            'occupied_rooms': occupied_rooms,
            'total_rooms': total_rooms
        }
        
        summary = {
            'total_revenue': total_revenue,
            'occupancy_rate': occupancy_rate,
            'average_daily_rate': adr,
            'period_days': (datetime.strptime(end_date, '%Y-%m-%d') - datetime.strptime(start_date, '%Y-%m-%d')).days + 1
        }
        
        return data, summary
    
    def _generate_occupancy_analysis_report(self, config: ReportConfig) -> tuple:
        """Generate occupancy analysis report"""
        cursor = self.conn.cursor()
        
        # Determine date range based on time period
        if config.time_period == TimePeriod.DAILY:
            # For daily occupancy analysis, use specific_date if provided, otherwise today
            target_date = config.specific_date if config.specific_date else datetime.now().strftime('%Y-%m-%d')
            start_date = target_date
            end_date = target_date
        elif config.time_period == TimePeriod.WEEKLY:
            start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            end_date = datetime.now().strftime('%Y-%m-%d')
        elif config.time_period == TimePeriod.MONTHLY:
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            end_date = datetime.now().strftime('%Y-%m-%d')
        elif config.time_period == TimePeriod.QUARTERLY:
            start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
            end_date = datetime.now().strftime('%Y-%m-%d')
        elif config.time_period == TimePeriod.YEARLY:
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
            end_date = datetime.now().strftime('%Y-%m-%d')
        elif config.time_period == TimePeriod.CUSTOM:
            # Use the validated start_date and end_date from config
            start_date = config.start_date or (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            end_date = config.end_date or datetime.now().strftime('%Y-%m-%d')
        else:
            # Default to monthly
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            end_date = datetime.now().strftime('%Y-%m-%d')
        
        # Get daily occupancy data
        cursor.execute("""
            SELECT 
                date(check_in_date) as date,
                COUNT(*) as check_ins,
                0 as check_outs
            FROM reservations 
            WHERE room_id IN (
                SELECT id FROM rooms WHERE hotel_id = ?
            )
            AND check_in_date BETWEEN ? AND ?
            GROUP BY date(check_in_date)
            
            UNION ALL
            
            SELECT 
                date(check_out_date) as date,
                0 as check_ins,
                COUNT(*) as check_outs
            FROM reservations 
            WHERE room_id IN (
                SELECT id FROM rooms WHERE hotel_id = ?
            )
            AND check_out_date BETWEEN ? AND ?
            GROUP BY date(check_out_date)
            
            ORDER BY date
        """, (config.hotel_id, start_date, end_date, config.hotel_id, start_date, end_date))
        
        daily_data = []
        for row in cursor.fetchall():
            daily_data.append({
                'date': row['date'],
                'check_ins': row['check_ins'],
                'check_outs': row['check_outs']
            })
        
        # Get occupancy by room type
        cursor.execute("""
            SELECT 
                rt.name as room_type,
                COUNT(r.id) as total_rooms,
                COUNT(DISTINCT res.room_id) as occupied_rooms,
                (COUNT(DISTINCT res.room_id) * 100.0 / COUNT(r.id)) as occupancy_rate
            FROM room_types rt
            JOIN rooms r ON rt.id = r.room_type_id
            LEFT JOIN reservations res ON r.id = res.room_id
                AND res.check_in_date <= ?
                AND res.check_out_date >= ?
                AND res.status = 'checked_in'
            WHERE r.hotel_id = ?
            GROUP BY rt.name
        """, (end_date, end_date, config.hotel_id))
        
        occupancy_by_type = []
        for row in cursor.fetchall():
            occupancy_by_type.append({
                'room_type': row['room_type'],
                'total_rooms': row['total_rooms'],
                'occupied_rooms': row['occupied_rooms'],
                'occupancy_rate': row['occupancy_rate']
            })
        
        # Get average stay length
        cursor.execute("""
            SELECT 
                AVG(julianday(check_out_date) - julianday(check_in_date)) as avg_stay_length
            FROM reservations 
            WHERE room_id IN (
                SELECT id FROM rooms WHERE hotel_id = ?
            )
            AND check_in_date BETWEEN ? AND ?
            AND status = 'completed'
        """, (config.hotel_id, start_date, end_date))
        avg_stay_length = cursor.fetchone()['avg_stay_length'] or 0.0
        
        data = {
            'period': {'start_date': start_date, 'end_date': end_date},
            'daily_occupancy': daily_data,
            'occupancy_by_room_type': occupancy_by_type,
            'average_stay_length': avg_stay_length
        }
        
        summary = {
            'hotel_id': config.hotel_id,
            'start_date': start_date,
            'end_date': end_date,
            'period_days': (datetime.strptime(end_date, '%Y-%m-%d') - datetime.strptime(start_date, '%Y-%m-%d')).days + 1,
            'average_stay_length': avg_stay_length,
            'total_room_types': len(occupancy_by_type),
            'average_occupancy_rate': average_occupancy_rate
        }
        
        return data, summary
    
    def _generate_revenue_by_room_type_report(self, config: ReportConfig) -> tuple:
        """Generate revenue by room type report"""
        cursor = self.conn.cursor()
        
        # Determine date range
        if config.time_period == TimePeriod.MONTHLY:
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            end_date = datetime.now().strftime('%Y-%m-%d')
        else:
            start_date = config.start_date or (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            end_date = config.end_date or datetime.now().strftime('%Y-%m-%d')
        
        # Get revenue by room type
        cursor.execute("""
            SELECT 
                rt.name as room_type,
                rt.base_price as base_price,
                COUNT(res.id) as reservations,
                SUM(res.total_price) as total_revenue,
                AVG(res.total_price) as avg_revenue_per_reservation,
                AVG(res.total_price / (julianday(res.check_out_date) - julianday(res.check_in_date))) as avg_daily_rate
            FROM room_types rt
            JOIN rooms r ON rt.id = r.room_type_id
            JOIN reservations res ON r.id = res.room_id
            WHERE r.hotel_id = ?
            AND res.check_in_date BETWEEN ? AND ?
            AND res.status = 'completed'
            GROUP BY rt.name, rt.base_price
            ORDER BY total_revenue DESC
        """, (config.hotel_id, start_date, end_date))
        
        room_type_revenue = []
        total_revenue = 0.0
        for row in cursor.fetchall():
            room_type_revenue.append({
                'room_type': row['room_type'],
                'base_price': row['base_price'],
                'reservations': row['reservations'],
                'total_revenue': row['total_revenue'],
                'avg_revenue_per_reservation': row['avg_revenue_per_reservation'],
                'avg_daily_rate': row['avg_daily_rate']
            })
            total_revenue += row['total_revenue'] or 0.0
        
        data = {
            'period': {'start_date': start_date, 'end_date': end_date},
            'room_type_revenue': room_type_revenue,
            'total_revenue': total_revenue
        }
        
        summary = {
            'period_days': (datetime.strptime(end_date, '%Y-%m-%d') - datetime.strptime(start_date, '%Y-%m-%d')).days + 1,
            'total_revenue': total_revenue,
            'room_types': len(room_type_revenue)
        }
        
        return data, summary
    
    def _generate_guest_demographics_report(self, config: ReportConfig) -> tuple:
        """Generate guest demographics report"""
        cursor = self.conn.cursor()
        
        # Determine date range
        if config.time_period == TimePeriod.MONTHLY:
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            end_date = datetime.now().strftime('%Y-%m-%d')
        else:
            start_date = config.start_date or (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            end_date = config.end_date or datetime.now().strftime('%Y-%m-%d')
        
        # Get guest demographics
        cursor.execute("""
            SELECT 
                g.id as guest_id,
                g.first_name,
                g.last_name,
                g.email,
                g.loyalty_points,
                COUNT(res.id) as total_stays,
                SUM(res.total_price) as total_spent,
                AVG(res.total_price) as avg_spent_per_stay
            FROM guests g
            JOIN reservations res ON g.id = res.guest_id
            WHERE res.room_id IN (
                SELECT id FROM rooms WHERE hotel_id = ?
            )
            AND res.check_in_date BETWEEN ? AND ?
            GROUP BY g.id
            ORDER BY total_spent DESC
        """, (config.hotel_id, start_date, end_date))
        
        guest_data = []
        total_guests = 0
        total_revenue = 0.0
        for row in cursor.fetchall():
            guest_data.append({
                'guest_id': row['guest_id'],
                'name': f"{row['first_name']} {row['last_name']}",
                'email': row['email'],
                'loyalty_points': row['loyalty_points'],
                'total_stays': row['total_stays'],
                'total_spent': row['total_spent'],
                'avg_spent_per_stay': row['avg_spent_per_stay']
            })
            total_guests += 1
            total_revenue += row['total_spent'] or 0.0
        
        # Get loyalty program stats
        cursor.execute("""
            SELECT 
                COUNT(*) as total_guests,
                AVG(loyalty_points) as avg_loyalty_points,
                SUM(loyalty_points) as total_loyalty_points
            FROM guests
            WHERE id IN (
                SELECT DISTINCT guest_id 
                FROM reservations 
                WHERE room_id IN (
                    SELECT id FROM rooms WHERE hotel_id = ?
                )
                AND check_in_date BETWEEN ? AND ?
            )
        """, (config.hotel_id, start_date, end_date))
        loyalty_stats = cursor.fetchone()
        
        data = {
            'period': {'start_date': start_date, 'end_date': end_date},
            'guest_data': guest_data,
            'loyalty_stats': dict(loyalty_stats),
            'total_guests': total_guests,
            'total_revenue': total_revenue
        }
        
        summary = {
            'period_days': (datetime.strptime(end_date, '%Y-%m-%d') - datetime.strptime(start_date, '%Y-%m-%d')).days + 1,
            'total_guests': total_guests,
            'total_revenue': total_revenue,
            'avg_revenue_per_guest': total_revenue / total_guests if total_guests > 0 else 0
        }
        
        return data, summary
    
    def _generate_housekeeping_status_report(self, config: ReportConfig) -> tuple:
        """Generate housekeeping status report"""
        cursor = self.conn.cursor()
        
        # Get overall housekeeping status
        cursor.execute("""
            SELECT 
                h.status,
                COUNT(*) as count,
                COUNT(*) * 100.0 / (SELECT COUNT(*) FROM rooms WHERE hotel_id = ?) as percentage
            FROM housekeeping h
            JOIN rooms r ON h.room_id = r.id
            WHERE r.hotel_id = ?
            GROUP BY h.status
        """, (config.hotel_id, config.hotel_id))
        
        housekeeping_status = []
        for row in cursor.fetchall():
            housekeeping_status.append({
                'status': row['status'],
                'count': row['count'],
                'percentage': row['percentage']
            })
        
        # Get rooms needing attention
        cursor.execute("""
            SELECT 
                r.room_number,
                f.floor_number,
                rt.name as room_type,
                h.status,
                h.last_cleaned,
                h.notes
            FROM housekeeping h
            JOIN rooms r ON h.room_id = r.id
            JOIN floors f ON r.floor_id = f.id
            JOIN room_types rt ON r.room_type_id = rt.id
            WHERE r.hotel_id = ?
            AND h.status != 'clean'
            ORDER BY f.floor_number, r.room_number
        """, (config.hotel_id,))
        
        rooms_needing_attention = []
        for row in cursor.fetchall():
            rooms_needing_attention.append({
                'room_number': row['room_number'],
                'floor_number': row['floor_number'],
                'room_type': row['room_type'],
                'status': row['status'],
                'last_cleaned': row['last_cleaned'],
                'notes': row['notes']
            })
        
        # Get average cleaning time
        cursor.execute("""
            SELECT 
                AVG(julianday(h.last_cleaned) - julianday(res.check_out_date)) as avg_cleaning_time_days
            FROM housekeeping h
            JOIN rooms r ON h.room_id = r.id
            JOIN reservations res ON r.id = res.room_id
            WHERE r.hotel_id = ?
            AND res.status = 'completed'
            AND h.last_cleaned IS NOT NULL
        """, (config.hotel_id,))
        avg_cleaning_time = cursor.fetchone()['avg_cleaning_time_days'] or 0.0
        
        data = {
            'housekeeping_status': housekeeping_status,
            'rooms_needing_attention': rooms_needing_attention,
            'average_cleaning_time_days': avg_cleaning_time
        }
        
        summary = {
            'total_rooms': sum(item['count'] for item in housekeeping_status),
            'clean_rooms': next((item['count'] for item in housekeeping_status if item['status'] == 'clean'), 0),
            'rooms_needing_attention': len(rooms_needing_attention),
            'average_cleaning_time_days': avg_cleaning_time
        }
        
        return data, summary
    
    def _generate_cancellation_analysis_report(self, config: ReportConfig) -> tuple:
        """Generate cancellation analysis report"""
        cursor = self.conn.cursor()
        
        # Determine date range
        if config.time_period == TimePeriod.MONTHLY:
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            end_date = datetime.now().strftime('%Y-%m-%d')
        else:
            start_date = config.start_date or (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            end_date = config.end_date or datetime.now().strftime('%Y-%m-%d')
        
        # Get cancellation statistics
        cursor.execute("""
            SELECT 
                COUNT(*) as total_cancellations,
                SUM(CASE WHEN julianday(cancellation_date) - julianday(booking_date) <= 1 THEN 1 ELSE 0 END) as last_minute_cancellations,
                SUM(CASE WHEN julianday(cancellation_date) - julianday(booking_date) > 1 AND julianday(cancellation_date) - julianday(booking_date) <= 7 THEN 1 ELSE 0 END) as short_notice_cancellations,
                SUM(CASE WHEN julianday(cancellation_date) - julianday(booking_date) > 7 THEN 1 ELSE 0 END) as long_notice_cancellations
            FROM reservations
            WHERE room_id IN (
                SELECT id FROM rooms WHERE hotel_id = ?
            )
            AND status = 'cancelled'
            AND cancellation_date BETWEEN ? AND ?
        """, (config.hotel_id, start_date, end_date))
        
        cancellation_stats = cursor.fetchone()
        
        # Get cancellation reasons (if available in notes)
        cursor.execute("""
            SELECT 
                notes as reason,
                COUNT(*) as count
            FROM reservations
            WHERE room_id IN (
                SELECT id FROM rooms WHERE hotel_id = ?
            )
            AND status = 'cancelled'
            AND cancellation_date BETWEEN ? AND ?
            AND notes IS NOT NULL
            GROUP BY notes
            ORDER BY count DESC
        """, (config.hotel_id, start_date, end_date))
        
        cancellation_reasons = []
        for row in cursor.fetchall():
            cancellation_reasons.append({
                'reason': row['reason'],
                'count': row['count']
            })
        
        # Get cancellation rate
        cursor.execute("""
            SELECT 
                COUNT(*) as total_reservations,
                SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) as total_cancellations
            FROM reservations
            WHERE room_id IN (
                SELECT id FROM rooms WHERE hotel_id = ?
            )
            AND booking_date BETWEEN ? AND ?
        """, (config.hotel_id, start_date, end_date))
        
        rate_data = cursor.fetchone()
        cancellation_rate = (rate_data['total_cancellations'] / rate_data['total_reservations'] * 100) if rate_data['total_reservations'] > 0 else 0
        
        data = {
            'period': {'start_date': start_date, 'end_date': end_date},
            'cancellation_stats': dict(cancellation_stats),
            'cancellation_reasons': cancellation_reasons,
            'cancellation_rate': cancellation_rate,
            'total_reservations': rate_data['total_reservations'],
            'total_cancellations': rate_data['total_cancellations']
        }
        
        summary = {
            'period_days': (datetime.strptime(end_date, '%Y-%m-%d') - datetime.strptime(start_date, '%Y-%m-%d')).days + 1,
            'cancellation_rate': cancellation_rate,
            'total_cancellations': rate_data['total_cancellations'],
            'total_reservations': rate_data['total_reservations']
        }
        
        return data, summary
    
    # Utility methods
    
    def _hotel_exists(self, hotel_id: int) -> bool:
        """Check if hotel exists in database"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM hotel WHERE id = ?", (hotel_id,))
        return cursor.fetchone()[0] > 0
    
    def _validate_date_parameters(self, config: ReportConfig) -> None:
        """Validate date parameters and provide helpful error messages"""
        report_type = config.report_type
        
        # For daily status reports
        if report_type == ReportType.DAILY_STATUS:
            if config.specific_date:
                # Validate specific date format (YYYY-MM-DD)
                if not self._is_valid_date_format(config.specific_date):
                    raise ValueError(
                        f"Invalid date format: {config.specific_date}\"
                        f"Date should be in YYYY-MM-DD format. Example: \"2026-02-01\"
                    )
            # Daily status reports can use specific_date or default to today
            return
        
        # For occupancy analysis reports
        elif report_type == ReportType.OCCUPANCY_ANALYSIS:
            if config.time_period == TimePeriod.CUSTOM:
                if not config.start_date or not config.end_date:
                    raise ValueError(
                        "For CUSTOM time period, both start_date and end_date are required.\n"
                        "Usage: start_date='YYYY-MM-DD', end_date='YYYY-MM-DD'"
                    )
                if not self._is_valid_date_format(config.start_date):
                    raise ValueError(
                        f"Invalid start_date format: {config.start_date}\"
                        f"Date should be in YYYY-MM-DD format. Example: \"2026-02-01\"
                    )
                if not self._is_valid_date_format(config.end_date):
                    raise ValueError(
                        f"Invalid end_date format: {config.end_date}\"
                        f"Date should be in YYYY-MM-DD format. Example: \"2026-02-01\"
                    )
                
                # Validate date range
                start_date = datetime.strptime(config.start_date, '%Y-%m-%d')
                end_date = datetime.strptime(config.end_date, '%Y-%m-%d')
                if start_date > end_date:
                    raise ValueError(
                        f"Invalid date range: start_date ({config.start_date}) "
                        f"cannot be after end_date ({config.end_date})"
                    )
                
                # Validate reasonable date range (max 365 days)
                delta = end_date - start_date
                if delta.days > 365:
                    raise ValueError(
                        f"Date range too large: {delta.days} days. "
                        f"Maximum allowed is 365 days."
                    )
            # Other time periods don't require custom dates
            return
        
        # For other report types, provide helpful guidance
        else:
            if config.specific_date or config.start_date or config.end_date:
                print(f"Note: Date parameters are not typically used for {report_type.value} reports.")
                print(f"For date-specific analysis, consider using:")
                print(f"  - {ReportType.DAILY_STATUS.value} with specific_date parameter")
                print(f"  - {ReportType.OCCUPANCY_ANALYSIS.value} with time_period and date range")
    
    def _is_valid_date_format(self, date_str: str) -> bool:
        """Check if date string is in valid YYYY-MM-DD format"""
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return True
        except ValueError:
            return False
    
    def get_usage_help(self, report_type: ReportType = None) -> str:
        """Get helpful usage information for report generation"""
        help_text = [
            "📊 HOTEL REPORTING SYSTEM - USAGE GUIDE",
            "=" * 60,
            "",
            "📋 REPORT TYPES:",
            "  • daily_status - Daily occupancy and status report",
            "  • financial_summary - Financial performance summary",
            "  • occupancy_analysis - Occupancy trends and analysis",
            "  • revenue_by_room_type - Revenue breakdown by room type",
            "  • guest_demographics - Guest information and statistics",
            "  • housekeeping_status - Housekeeping operations report",
            "  • cancellation_analysis - Cancellation patterns and reasons",
            "",
            "📅 TIME PERIODS:",
            "  • daily - Single day (use with specific_date)",
            "  • weekly - Last 7 days",
            "  • monthly - Last 30 days (default)",
            "  • quarterly - Last 90 days",
            "  • yearly - Last 365 days",
            "  • custom - Custom date range (requires start_date and end_date)",
            "",
            "🗓️ DATE FORMAT: YYYY-MM-DD (Example: 2026-02-01)",
            "",
            "📈 USAGE EXAMPLES:",
        ]
        
        examples = [
            ("Daily Status Report (today)", 
             "ReportConfig(report_type=ReportType.DAILY_STATUS, time_period=TimePeriod.DAILY, hotel_id=1)"),
            
            ("Daily Status Report (specific date)",
             "ReportConfig(report_type=ReportType.DAILY_STATUS, time_period=TimePeriod.DAILY, hotel_id=1, specific_date='2026-02-01')"),
            
            ("Occupancy Analysis (weekly)",
             "ReportConfig(report_type=ReportType.OCCUPANCY_ANALYSIS, time_period=TimePeriod.WEEKLY, hotel_id=1)"),
            
            ("Occupancy Analysis (custom range)",
             "ReportConfig(report_type=ReportType.OCCUPANCY_ANALYSIS, time_period=TimePeriod.CUSTOM, hotel_id=1, start_date='2026-01-01', end_date='2026-01-31')"),
            
            ("Financial Summary (monthly)",
             "ReportConfig(report_type=ReportType.FINANCIAL_SUMMARY, time_period=TimePeriod.MONTHLY, hotel_id=1)"),
        ]
        
        for title, example in examples:
            help_text.append(f"  {title}:")
            help_text.append(f"    {example}")
            help_text.append("")
        
        help_text.extend([
            "💡 TIPS:",
            "  • Use specific_date for daily reports to analyze historical days",
            "  • Use CUSTOM time period with start_date and end_date for date ranges",
            "  • Date format must be YYYY-MM-DD (e.g., 2026-02-01)",
            "  • Maximum date range is 365 days for performance reasons",
            "  • All reports support text, csv, and json output formats",
            "",
            "❌ COMMON ERRORS:",
            "  • Wrong date format: '02/01/2026' → Use '2026-02-01' instead",
            "  • Missing dates for CUSTOM period: Provide both start_date and end_date",
            "  • Invalid date range: start_date cannot be after end_date",
            "  • Date range too large: Maximum 365 days allowed",
            "",
            "=" * 60
        ])
        
        return "\n".join(help_text)
    
    def _display_text_report(self, report: ReportResult) -> str:
        """Display report in text format"""
        output = []
        output.append(f"Hotel Report: {report.report_type.value}")
        output.append(f"Hotel ID: {report.hotel_id}")
        output.append(f"Generated: {report.generated_at}")
        output.append("=" * 50)
        
        if report.report_type == ReportType.DAILY_STATUS:
            output.append("DAILY STATUS REPORT")
            output.append(f"Hotel: {report.data['hotel_info']['name']}")
            output.append(f"Date: {report.data['date']}")
            output.append("\nRoom Status:")
            for status, count in report.data['room_status'].items():
                output.append(f"  {status}: {count}")
            
            output.append("\nReservation Status:")
            for key, value in report.data['reservation_stats'].items():
                output.append(f"  {key}: {value}")
            
            output.append("\nHousekeeping Status:")
            for status, count in report.data['housekeeping_status'].items():
                output.append(f"  {status}: {count}")
                
        elif report.report_type == ReportType.FINANCIAL_SUMMARY:
            output.append("FINANCIAL SUMMARY REPORT")
            output.append(f"Period: {report.data['period']['start_date']} to {report.data['period']['end_date']}")
            output.append(f"Total Revenue: ${report.data['total_revenue']:.2f}")
            output.append(f"Occupancy Rate: {report.data['occupancy_rate']:.1f}%")
            output.append(f"Average Daily Rate: ${report.data['average_daily_rate']:.2f}")
            
        elif report.report_type == ReportType.OCCUPANCY_ANALYSIS:
            output.append("OCCUPANCY ANALYSIS REPORT")
            output.append(f"Period: {report.data['period']['start_date']} to {report.data['period']['end_date']}")
            output.append(f"Average Stay Length: {report.data['average_stay_length']:.1f} days")
            
        # Add summary section
        output.append("\nSUMMARY:")
        for key, value in report.summary.items():
            output.append(f"  {key}: {value}")
            
        return "\n".join(output)
    
    def _display_csv_report(self, report: ReportResult) -> str:
        """Display report in CSV format"""
        import io
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([f"Hotel Report: {report.report_type.value}"])
        writer.writerow([f"Hotel ID: {report.hotel_id}"])
        writer.writerow([f"Generated: {report.generated_at}"])
        writer.writerow([])
        
        # Write data based on report type
        if report.report_type == ReportType.DAILY_STATUS:
            writer.writerow(["DAILY STATUS REPORT"])
            writer.writerow(["Hotel", report.data['hotel_info']['name']])
            writer.writerow(["Date", report.data['date']])
            writer.writerow([])
            writer.writerow(["Room Status"])
            writer.writerow(["Status", "Count"])
            for status, count in report.data['room_status'].items():
                writer.writerow([status, count])
        
        # Add summary
        writer.writerow([])
        writer.writerow(["SUMMARY"])
        for key, value in report.summary.items():
            writer.writerow([key, value])
        
        return output.getvalue()
    
    def _display_json_report(self, report: ReportResult) -> str:
        """Display report in JSON format"""
        import json
        report_dict = {
            'report_type': report.report_type.value,
            'hotel_id': report.hotel_id,
            'generated_at': report.generated_at,
            'data': report.data,
            'summary': report.summary
        }
        return json.dumps(report_dict, indent=2)
    
    def _export_csv_report(self, report: ReportResult, filename: str) -> str:
        """Export report to CSV file"""
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write header
            writer.writerow([f"Hotel Report: {report.report_type.value}"])
            writer.writerow([f"Hotel ID: {report.hotel_id}"])
            writer.writerow([f"Generated: {report.generated_at}"])
            writer.writerow([])
            
            # Write data based on report type
            if report.report_type == ReportType.DAILY_STATUS:
                writer.writerow(["DAILY STATUS REPORT"])
                writer.writerow(["Hotel", report.data['hotel_info']['name']])
                writer.writerow(["Date", report.data['date']])
                writer.writerow([])
                writer.writerow(["Room Status"])
                writer.writerow(["Status", "Count"])
                for status, count in report.data['room_status'].items():
                    writer.writerow([status, count])
            
            # Add summary
            writer.writerow([])
            writer.writerow(["SUMMARY"])
            for key, value in report.summary.items():
                writer.writerow([key, value])
        
        return f"Report exported to {filename}"
    
    def _export_json_report(self, report: ReportResult, filename: str) -> str:
        """Export report to JSON file"""
        import json
        report_dict = {
            'report_type': report.report_type.value,
            'hotel_id': report.hotel_id,
            'generated_at': report.generated_at,
            'data': report.data,
            'summary': report.summary
        }
        
        with open(filename, 'w') as jsonfile:
            json.dump(report_dict, jsonfile, indent=2)
        
        return f"Report exported to {filename}"


def create_sample_reports():
    """Create sample reports for demonstration"""
    with HotelReportingSystem() as reporter:
        # Create daily status report
        daily_config = ReportConfig(
            report_type=ReportType.DAILY_STATUS,
            time_period=TimePeriod.DAILY,
            hotel_id=1
        )
        daily_report = reporter.generate_report(daily_config)
        print("=== DAILY STATUS REPORT ===")
        print(reporter.display_report(daily_report, "text"))
        print()
        
        # Create financial summary report
        financial_config = ReportConfig(
            report_type=ReportType.FINANCIAL_SUMMARY,
            time_period=TimePeriod.MONTHLY,
            hotel_id=1
        )
        financial_report = reporter.generate_report(financial_config)
        print("=== FINANCIAL SUMMARY REPORT ===")
        print(reporter.display_report(financial_report, "text"))
        print()
        
        # Create occupancy analysis report
        occupancy_config = ReportConfig(
            report_type=ReportType.OCCUPANCY_ANALYSIS,
            time_period=TimePeriod.MONTHLY,
            hotel_id=1
        )
        occupancy_report = reporter.generate_report(occupancy_config)
        print("=== OCCUPANCY ANALYSIS REPORT ===")
        print(reporter.display_report(occupancy_report, "text"))
        print()


if __name__ == "__main__":
    print("Hotel Reporting System - Phase 4 Implementation")
    print("=" * 50)
    
    # Create sample reports
    create_sample_reports()
    
    print("Phase 4 Implementation Complete!")
    print("Reporting system includes:")
    print("- Daily Status Reports")
    print("- Financial Summary Reports")
    print("- Occupancy Analysis Reports")
    print("- Revenue by Room Type Reports")
    print("- Guest Demographics Reports")
    print("- Housekeeping Status Reports")
    print("- Cancellation Analysis Reports")
    print("- Multiple output formats (text, CSV, JSON)")
    print("- Export functionality")