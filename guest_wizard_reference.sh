#!/bin/bash
# Guest Wizard Quick Reference

cat << 'EOF'
╔══════════════════════════════════════════════════════════════╗
║          GUEST MANAGEMENT WIZARDS - QUICK REFERENCE          ║
╚══════════════════════════════════════════════════════════════╝

📋 COMMANDS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Interactive Menu (Recommended):
    python3 guest_wizard.py

  Add Guest:
    python3 guest_wizard.py add

  Search Guests:
    python3 guest_wizard.py search

  Demo Mode:
    python3 demo_guest_wizard.py

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✨ ADD GUEST WIZARD
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Required Fields:
    • First Name
    • Last Name

  Optional Fields:
    • Email
    • Cell Phone (10-digit: 555-123-4567)
    • Address (Street, City, State ZIP)
    • Car Make, Model, Color

  Features:
    ✓ Phone validation (10-digit check)
    ✓ Summary confirmation
    ✓ Success feedback with Guest ID

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔍 SEARCH GUEST WIZARD
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Search By:
    • First Name (partial)
    • Last Name (partial)
    • Email (partial)
    • Phone (partial)
    • Address (partial)
    • Car Make (partial)
    • Car Model (partial)
    • Car Color (partial)

  Features:
    ✓ Partial matching (contains logic)
    ✓ Multiple criteria (AND logic)
    ✓ Detailed results
    ✓ 50 result limit

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 SEARCH EXAMPLES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Find by last name:
    Last Name: Johnson

  Find by car:
    Car Make: Toyota

  Find by location:
    Address: CA

  Find by phone area:
    Phone: 555-123

  Combined search:
    First Name: John
    Car Make: Tesla

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📚 DOCUMENTATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Full Guide:
    GUEST_WIZARD_GUIDE.md

  Implementation Details:
    GUEST_WIZARD_IMPLEMENTATION.md

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

EOF

echo ""
echo "Current Guest Statistics:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

sqlite3 hotel.db << 'SQL'
.mode column
.headers on
SELECT 
    'Total Guests' as Metric,
    COUNT(*) as Count
FROM guests
UNION ALL
SELECT 
    'With Phone',
    COUNT(*)
FROM guests WHERE phone IS NOT NULL AND phone != ''
UNION ALL
SELECT 
    'With Address',
    COUNT(*)
FROM guests WHERE address IS NOT NULL AND address != ''
UNION ALL
SELECT 
    'With Vehicle',
    COUNT(*)
FROM guests WHERE car_make IS NOT NULL AND car_make != '' AND car_make != 'N/A';
SQL

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
