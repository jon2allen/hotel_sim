# Hotel Simulator Reporting CLI Documentation

## Overview

This document describes the comprehensive reporting functionality that has been integrated into the Hotel Simulator system. The system now includes:

1. **Interactive CLI Reporting**: Daily status and occupancy reports accessible from the interactive shell
2. **Standalone Reporting CLI**: Separate command-line utility for generating reports
3. **Multiple Output Formats**: Text, CSV, and JSON report formats

## 1. Interactive CLI Reporting

The main `hotel_cli.py` interactive shell now includes two new commands:

### Daily Status Report

**Command**: `daily_report <hotel_id> [YYYY-MM-DD]`

**Usage**:
```
hotel> daily_report 1
# Generates report for today
hotel> daily_report 1 2026-02-01
# Generates report for specific date
```

**Example Output**:
```
==================================================
DAILY STATUS REPORT
Hotel: Grand Hotel
Date: 2026-02-01

Room Status:
  available: 20
  occupied: 75
  reserved: 3
  maintenance: 2

Reservation Status:
  total_reservations: 85
  checked_in: 12
  checked_out: 8
  confirmed: 15
  cancelled: 2

SUMMARY:
  Occupancy Rate: 75.0%
  Current Guests: 75
  Check-ins Today: 12
  Check-outs Today: 8
```

### Occupancy Analysis Report

**Command**: `occupancy_report <hotel_id> [time_period] [start_date] [end_date]`

**Usage**:
```
hotel> occupancy_report 1
# Monthly report (default)
hotel> occupancy_report 1 weekly
# Weekly report
hotel> occupancy_report 1 custom 2026-01-01 2026-01-31
# Custom date range report
```

**Time Periods**:
- `daily` - Single day
- `weekly` - Last 7 days
- `monthly` - Last 30 days (default)
- `quarterly` - Last 90 days
- `yearly` - Last 365 days
- `custom` - Custom date range (requires start and end dates)

**Example Output**:
```
==================================================
OCCUPANCY ANALYSIS REPORT
Period: 2026-01-01 to 2026-01-31
Average Stay Length: 3.2 days

Daily Occupancy:
  2026-01-01: 65% (65/100 rooms)
  2026-01-02: 72% (72/100 rooms)
  ...

SUMMARY:
  Period: 31 days
  Average Occupancy: 72.5%
  Total Room Types: 4
```

## 2. Standalone Reporting CLI

A separate command-line utility `reporting_cli.py` provides comprehensive reporting capabilities:

### Installation

```bash
chmod +x reporting_cli.py
./reporting_cli.py --help
```

### Command Structure

```bash
python3 reporting_cli.py <report_type> <hotel_id> [options]
```

### Report Types

#### Daily Status Report

**Command**: `python3 reporting_cli.py daily <hotel_id> [--date YYYY-MM-DD] [--format text|csv|json]`

**Examples**:
```bash
# Today's report
python3 reporting_cli.py daily 1

# Specific date report
python3 reporting_cli.py daily 1 --date 2026-02-01

# CSV format
python3 reporting_cli.py daily 1 --date 2026-02-01 --format csv

# JSON format
python3 reporting_cli.py daily 1 --date 2026-02-01 --format json
```

#### Occupancy Analysis Report

**Command**: `python3 reporting_cli.py occupancy <hotel_id> [--period daily|weekly|monthly|quarterly|yearly|custom] [--start YYYY-MM-DD] [--end YYYY-MM-DD] [--format text|csv|json]`

**Examples**:
```bash
# Monthly report (default)
python3 reporting_cli.py occupancy 1

# Weekly report
python3 reporting_cli.py occupancy 1 --period weekly

# Custom date range
python3 reporting_cli.py occupancy 1 --period custom --start 2026-01-01 --end 2026-01-31

# JSON format
python3 reporting_cli.py occupancy 1 --period weekly --format json
```

#### Transaction Tracker Report

**Command**: `python3 reporting_cli.py transactions <hotel_id> [--date YYYY-MM-DD] [--format text|csv|json]`

**Examples**:
```bash
# Today's transactions
python3 reporting_cli.py transactions 1

# Specific date
python3 reporting_cli.py transactions 1 --date 2026-02-01

# CSV format
python3 reporting_cli.py transactions 1 --date 2026-02-01 --format csv
```

### Complete Help

```bash
python3 reporting_cli.py --help
```

Shows all available commands with examples:

```
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
```

## 3. Date Format Requirements

All date parameters must use the **YYYY-MM-DD** format:

✅ **Valid**: `2026-02-01`, `2026-12-31`
❌ **Invalid**: `02/01/2026`, `2026-2-1`, `01-02-2026`

### Error Handling

The system provides helpful error messages for invalid dates:

```bash
python3 reporting_cli.py daily 1 --date 02/01/2026
# Output: ❌ Error: Invalid date format: 02/01/2026. Use YYYY-MM-DD
```

## 4. Output Formats

All reports support three output formats:

### Text Format (Default)
Human-readable text output with emojis and formatting:
```
==================================================
DAILY STATUS REPORT
Hotel: Grand Hotel
Date: 2026-02-01

📊 SUMMARY
----------------------------------------
Total Rooms: 100
Occupied: 75 | Available: 20
```

### CSV Format
Comma-separated values for spreadsheet import:
```bash
python3 reporting_cli.py daily 1 --format csv
```
```csv
Daily Status Report
Hotel: Grand Hotel
Date: 2026-02-01

Summary,,,
Total Rooms,100,,
Occupied,75,,
Available,20,,
```

### JSON Format
Structured data for programmatic processing:
```bash
python3 reporting_cli.py daily 1 --format json
```
```json
{
  "report_type": "daily_status",
  "hotel": {"id": 1, "name": "Grand Hotel"},
  "date": "2026-02-01",
  "summary": {
    "room_status": {"occupied": 75, "available": 20},
    "occupancy_rate": 75.0
  }
}
```

## 5. Integration Examples

### Python API Usage

```python
from reporting_system import HotelReportingSystem, ReportConfig, ReportType, TimePeriod

# Create reporter
reporter = HotelReportingSystem()

# Daily report
config = ReportConfig(
    report_type=ReportType.DAILY_STATUS,
    time_period=TimePeriod.DAILY,
    hotel_id=1,
    specific_date='2026-02-01'
)
report = reporter.generate_report(config)
print(reporter.display_report(report, 'text'))

# Occupancy report
config = ReportConfig(
    report_type=ReportType.OCCUPANCY_ANALYSIS,
    time_period=TimePeriod.WEEKLY,
    hotel_id=1
)
report = reporter.generate_report(config)
print(reporter.display_report(report, 'json'))
```

### Transaction Tracker Usage

```python
from daily_transaction_tracker import DailyTransactionTracker

# Create tracker
tracker = DailyTransactionTracker()

# Get daily summary
summary = tracker.get_daily_summary(hotel_id=1, date='2026-02-01')
print(f"Occupancy: {summary.occupancy_rate:.1f}%")
print(f"Expected Revenue: ${summary.expected_end_of_day_revenue:.2f}")

# Get room details
rooms = tracker.get_room_details(hotel_id=1, date='2026-02-01')
for room in rooms:
    print(f"Room {room.room_number}: {room.status}")
```

## 6. Common Use Cases

### Daily Operations Check
```bash
# Check today's status
python3 reporting_cli.py daily 1

# Check yesterday's status
python3 reporting_cli.py daily 1 --date $(date -d "yesterday" +%Y-%m-%d)
```

### Weekly Performance Review
```bash
# Weekly occupancy analysis
python3 reporting_cli.py occupancy 1 --period weekly

# Export to CSV for analysis
python3 reporting_cli.py occupancy 1 --period weekly --format csv > weekly_report.csv
```

### Monthly Financial Reporting
```bash
# Monthly occupancy and revenue
python3 reporting_cli.py occupancy 1 --period monthly
python3 reporting_cli.py transactions 1 --format json > monthly_transactions.json
```

### Historical Analysis
```bash
# Compare two periods
python3 reporting_cli.py occupancy 1 --period custom --start 2026-01-01 --end 2026-01-31
python3 reporting_cli.py occupancy 1 --period custom --start 2026-02-01 --end 2026-02-28
```

## 7. Error Handling & Troubleshooting

### Common Errors and Solutions

**Error**: `Invalid date format: 02/01/2026`
**Solution**: Use `YYYY-MM-DD` format: `2026-02-01`

**Error**: `Hotel ID 999 does not exist`
**Solution**: Check available hotels with `list_hotels` command

**Error**: `Custom period requires both start_date and end_date`
**Solution**: Provide both dates for custom periods

**Error**: `Invalid date range: start_date cannot be after end_date`
**Solution**: Ensure start date ≤ end date

### Debugging Tips

1. **Check hotel exists**: `list_hotels` in interactive mode
2. **Validate dates**: Use `date +%Y-%m-%d` for current date
3. **Test with small ranges**: Start with daily reports before complex ranges
4. **Check database**: Ensure data exists for the date range

## 8. Performance Considerations

### Query Optimization
- Uses indexed database queries
- Efficient date-based filtering
- Maximum 365-day range for custom periods
- Minimal performance impact on existing functionality

### Caching Recommendations
- Cache frequent reports (e.g., daily reports)
- Pre-compute weekly/monthly summaries
- Store historical reports for quick access

## 9. Future Enhancements

### Potential Features
- **Scheduled Reports**: Cron-based report generation
- **Email Notifications**: Automated report delivery
- **Web Dashboard**: Visualization interface
- **Comparative Analysis**: Period-over-period comparisons
- **Export Enhancements**: PDF, Excel formats

### Advanced Analytics
- **Predictive Modeling**: Forecast future occupancy
- **Anomaly Detection**: Identify unusual patterns
- **Seasonal Analysis**: Year-over-year trends
- **Competitive Benchmarking**: Industry comparisons

## 10. Summary

The Hotel Simulator now provides comprehensive reporting capabilities through:

✅ **Interactive CLI**: Integrated reporting commands
✅ **Standalone CLI**: Separate reporting utility
✅ **Date Parameters**: Full date and range support
✅ **Multiple Formats**: Text, CSV, JSON outputs
✅ **Error Handling**: Helpful validation and messages
✅ **Documentation**: Complete usage guide

### Quick Reference

```bash
# Interactive mode
python3 hotel_cli.py interactive
hotel> daily_report 1 2026-02-01
hotel> occupancy_report 1 weekly

# Standalone CLI
python3 reporting_cli.py daily 1 --date 2026-02-01
python3 reporting_cli.py occupancy 1 --period monthly
python3 reporting_cli.py transactions 1 --format json

# Help
python3 reporting_cli.py --help
python3 reporting_cli.py daily --help
```

This comprehensive reporting system provides hotel managers with powerful tools to analyze occupancy, revenue, and operations with flexible date ranges and multiple output formats.