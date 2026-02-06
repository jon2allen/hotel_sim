#!/bin/bash
# Quick reference showing American-style test data

echo "=========================================="
echo "AMERICAN-STYLE TEST DATA EXAMPLES"
echo "=========================================="
echo ""

echo "📍 ADDRESS FORMAT:"
echo "  Format: [Street Number] [Street Name], [City], [State] [ZIP]"
echo "  Example: 123 Main Street, Anytown, CA 90210"
echo ""

echo "📱 PHONE FORMAT:"
echo "  Format: XXX-XXX-XXXX (10 digits)"
echo "  Example: 555-123-4567"
echo ""

echo "=========================================="
echo "SAMPLE TEST GUESTS"
echo "=========================================="
echo ""

sqlite3 -header -column hotel.db "
SELECT 
    first_name || ' ' || last_name as Name,
    phone as Phone,
    address as Address,
    car_make || ' ' || car_model as Vehicle
FROM guests 
WHERE id >= 2786 AND id <= 2797
ORDER BY id
LIMIT 8;
"

echo ""
echo "=========================================="
echo "PHONE NUMBER VALIDATION"
echo "=========================================="
echo ""

echo "Verifying 10-digit format:"
sqlite3 hotel.db "
SELECT 
    first_name || ' ' || last_name as Guest,
    phone as Phone,
    LENGTH(REPLACE(REPLACE(phone, '-', ''), ' ', '')) as Digits
FROM guests 
WHERE id >= 2790 AND id <= 2797
ORDER BY id;
"

echo ""
echo "=========================================="
echo "ADDRESS COMPONENTS"
echo "=========================================="
echo ""

echo "States represented in test data:"
sqlite3 hotel.db "
SELECT DISTINCT 
    SUBSTR(address, -10, 2) as State,
    COUNT(*) as Count
FROM guests 
WHERE id >= 2786 
  AND address LIKE '%,%'
GROUP BY State
ORDER BY Count DESC
LIMIT 10;
"

echo ""
echo "=========================================="
echo "For full documentation, see:"
echo "  TEST_UPDATE_AMERICAN_FORMAT.md"
echo "=========================================="
