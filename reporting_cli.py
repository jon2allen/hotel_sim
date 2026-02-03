#!/usr/bin/env python3
"""
Hotel Simulator - Reporting CLI
Standalone command-line interface for generating hotel reports
"""

import argparse
import sys
from datetime import datetime, timedelta
from reporting_system import HotelReportingSystem, ReportConfig, ReportType, TimePeriod
from daily_transaction_tracker import DailyTransactionTracker
from database import HotelDatabase
from hotel_simulator import ReservationSystem


def parse_date(date_str):
    """Parse and validate date string in YYYY-MM-DD format"""
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').strftime('%Y-%m-%d')
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid date format: {date_str}. Use YYYY-MM-DD")


def main():
    """Main function for reporting CLI"""
    parser = argparse.ArgumentParser(
        description='Hotel Simulator Reporting CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Daily status report for today
  python3 reporting_cli.py daily 1

  # Daily status report for specific date
  python3 reporting_cli.py daily 1 --date 2026-02-01

  # Occupancy analysis (monthly - default)
  python3 reporting_cli.py occupancy 1

  # Occupancy analysis (weekly)
  python3 reporting_cli.py occupancy 1 --period weekly

  # Occupancy analysis (custom date range)
  python3 reporting_cli.py occupancy 1 --period custom --start 2026-01-01 --end 2026-01-31

  # Transaction tracker daily summary
  python3 reporting_cli.py transactions 1 --date 2026-02-01

  # Show help for specific report type
  python3 reporting_cli.py daily --help
        """)

    # Create subparsers for different report types
    subparsers = parser.add_subparsers(dest='report_type', help='Type of report to generate')

    # Daily status report parser
    daily_parser = subparsers.add_parser('daily', help='Generate daily status report')
    daily_parser.add_argument('hotel_id', type=int, help='Hotel ID')
    daily_parser.add_argument('--date', type=parse_date, help='Specific date (YYYY-MM-DD), defaults to today')
    daily_parser.add_argument('--format', choices=['text', 'csv', 'json'], default='text', help='Output format')

    # Occupancy analysis report parser
    occupancy_parser = subparsers.add_parser('occupancy', help='Generate occupancy analysis report')
    occupancy_parser.add_argument('hotel_id', type=int, help='Hotel ID')
    occupancy_parser.add_argument('--period', choices=['daily', 'weekly', 'monthly', 'quarterly', 'yearly', 'custom'],
                                  default='monthly', help='Time period for analysis')
    occupancy_parser.add_argument('--start', type=parse_date, help='Start date for custom period (YYYY-MM-DD)')
    occupancy_parser.add_argument('--end', type=parse_date, help='End date for custom period (YYYY-MM-DD)')
    occupancy_parser.add_argument('--format', choices=['text', 'csv', 'json'], default='text', help='Output format')

    # Transactions report parser
    transactions_parser = subparsers.add_parser('transactions', help='Generate transaction tracker report')
    transactions_parser.add_argument('hotel_id', type=int, help='Hotel ID')
    transactions_parser.add_argument('--date', type=parse_date, help='Specific date (YYYY-MM-DD), defaults to today')
    transactions_parser.add_argument('--format', choices=['text', 'csv', 'json'], default='text', help='Output format')

    # Room-specific report parser
    room_parser = subparsers.add_parser('room', help='Generate room-specific report')
    room_parser.add_argument('hotel_id', type=int, help='Hotel ID')
    room_parser.add_argument('room_number', help='Room number (e.g., 101)')
    room_parser.add_argument('--start', type=parse_date, help='Start date (YYYY-MM-DD)')
    room_parser.add_argument('--end', type=parse_date, help='End date (YYYY-MM-DD)')
    room_parser.add_argument('--format', choices=['text', 'csv', 'json'], default='text', help='Output format')

    # Check-in parser
    checkin_parser = subparsers.add_parser('checkin', help='Process guest check-in')
    checkin_parser.add_argument('reservation_id', type=int, help='Reservation ID')

    # Check-out parser
    checkout_parser = subparsers.add_parser('checkout', help='Process guest check-out')
    checkout_parser.add_argument('reservation_id', type=int, help='Reservation ID')

    # List reservations parser
    list_reservations_parser = subparsers.add_parser('reservations', help='List all reservations')
    list_reservations_parser.add_argument('--hotel-id', type=int, help='Filter by hotel ID')
    list_reservations_parser.add_argument('--format', choices=['text', 'csv', 'json'], default='text', help='Output format')

    # Help command parser
    help_parser = subparsers.add_parser('help', help='Show help and usage examples')

    # Parse arguments
    args = parser.parse_args()

    if not args.report_type:
        parser.print_help()
        return

    if args.report_type == 'help':
        print(parser.format_help())
        return

    try:
        if args.report_type == 'daily':
            generate_daily_report(args)
        elif args.report_type == 'occupancy':
            generate_occupancy_report(args)
        elif args.report_type == 'transactions':
            generate_transactions_report(args)
        elif args.report_type == 'room':
            generate_room_report(args)
        elif args.report_type == 'checkin':
            process_checkin(args)
        elif args.report_type == 'checkout':
            process_checkout(args)
        elif args.report_type == 'reservations':
            list_reservations(args)
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


def generate_daily_report(args):
    """Generate daily status report"""
    reporter = HotelReportingSystem()
    
    config = ReportConfig(
        report_type=ReportType.DAILY_STATUS,
        time_period=TimePeriod.DAILY,
        hotel_id=args.hotel_id,
        specific_date=args.date
    )
    
    report = reporter.generate_report(config)
    result = reporter.display_report(report, args.format)
    print(result)


def generate_occupancy_report(args):
    """Generate occupancy analysis report"""
    reporter = HotelReportingSystem()
    
    # Parse time period
    time_period = TimePeriod[args.period.upper()]
    
    # Validate custom period dates
    if time_period == TimePeriod.CUSTOM:
        if not args.start or not args.end:
            print("❌ Custom period requires both --start and --end dates", file=sys.stderr)
            sys.exit(1)
    
    config = ReportConfig(
        report_type=ReportType.OCCUPANCY_ANALYSIS,
        time_period=time_period,
        hotel_id=args.hotel_id,
        start_date=args.start,
        end_date=args.end
    )
    
    report = reporter.generate_report(config)
    result = reporter.display_report(report, args.format)
    print(result)


def generate_transactions_report(args):
    """Generate transaction tracker report"""
    tracker = DailyTransactionTracker()
    
    date = args.date if args.date else datetime.now().strftime('%Y-%m-%d')
    
    if args.format == 'text':
        result = tracker.generate_daily_report(args.hotel_id, date, 'text')
    elif args.format == 'csv':
        result = tracker.generate_daily_report(args.hotel_id, date, 'csv')
    elif args.format == 'json':
        result = tracker.generate_daily_report(args.hotel_id, date, 'json')
    
    print(result)


def generate_room_report(args):
    """Generate room-specific report"""
    reporter = HotelReportingSystem()
    
    # Determine time period
    if args.start and args.end:
        time_period = TimePeriod.CUSTOM
    elif args.start:
        time_period = TimePeriod.DAILY
    else:
        time_period = TimePeriod.CUSTOM
        # Default to last 30 days
        args.start = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        args.end = datetime.now().strftime('%Y-%m-%d')
    
    # Create report configuration
    config = ReportConfig(
        report_type=ReportType.ROOM_SPECIFIC_REPORT,
        time_period=time_period,
        hotel_id=args.hotel_id,
        room_number=args.room_number,
        start_date=args.start,
        end_date=args.end,
        specific_date=args.start if time_period == TimePeriod.DAILY else None
    )
    
    # Generate and display report
    report = reporter.generate_report(config)
    result = reporter.display_report(report, args.format)
    print(result)


def process_checkin(args):
    """Process guest check-in"""
    db = HotelDatabase()
    res_system = ReservationSystem(db)
    
    try:
        success = res_system.check_in(args.reservation_id)
        if success:
            print(f"✅ Checked in reservation #{args.reservation_id}")
        else:
            print(f"❌ Check-in failed for reservation #{args.reservation_id}")
    except Exception as e:
        print(f"❌ Error during check-in: {e}")
        sys.exit(1)


def process_checkout(args):
    """Process guest check-out"""
    db = HotelDatabase()
    res_system = ReservationSystem(db)
    
    try:
        success, final_amount = res_system.check_out(args.reservation_id)
        if success:
            print(f"✅ Checked out reservation #{args.reservation_id}")
            print(f"💰 Final charges: ${final_amount:.2f}")
        else:
            print(f"❌ Check-out failed for reservation #{args.reservation_id}")
    except Exception as e:
        print(f"❌ Error during check-out: {e}")
        sys.exit(1)


def list_reservations(args):
    """List all reservations"""
    db = HotelDatabase()
    
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
        if args.hotel_id:
            query += " WHERE h.id = ?"
            params.append(args.hotel_id)
        
        query += " ORDER BY r.id DESC"
        
        reservations = db.execute_query(query, tuple(params) if params else None, fetch=True)
        
        if not reservations:
            print("No reservations found.")
            return
        
        # Format output based on format type
        if args.format == 'text':
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
        
        elif args.format == 'csv':
            # CSV format
            print("ID,Hotel ID,Hotel Name,Guest Name,Room Number,Check-in Date,Check-out Date,Status")
            for res in reservations:
                print(f"{res['id']},{res['hotel_id']},\"{res['hotel_name']}\",\"{res['guest_name']}\",{res['room_number']},{res['check_in_date']},{res['check_out_date']},{res['status']}")
        
        elif args.format == 'json':
            # JSON format
            import json
            result = []
            for res in reservations:
                result.append({
                    'id': res['id'],
                    'hotel_id': res['hotel_id'],
                    'hotel_name': res['hotel_name'],
                    'guest_name': res['guest_name'],
                    'room_number': res['room_number'],
                    'check_in_date': res['check_in_date'],
                    'check_out_date': res['check_out_date'],
                    'status': res['status']
                })
            print(json.dumps(result, indent=2))
            
    except Exception as e:
        print(f"❌ Error listing reservations: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()