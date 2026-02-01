#!/usr/bin/env python3
"""
Hotel Simulator - Reporting CLI
Standalone command-line interface for generating hotel reports
"""

import argparse
import sys
from datetime import datetime
from reporting_system import HotelReportingSystem, ReportConfig, ReportType, TimePeriod
from daily_transaction_tracker import DailyTransactionTracker


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


if __name__ == '__main__':
    main()