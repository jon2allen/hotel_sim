#!/bin/bash
# Complete validation showing addresses are included

echo "=========================================="
echo "COMPLETE GUEST RECORD VALIDATION"
echo "=========================================="
echo ""

echo "1. Sample Complete Guest Record:"
echo "-----------------------------------"
sqlite3 -line hotel.db "SELECT * FROM guests WHERE first_name='Alice' AND last_name='Johnson' ORDER BY id DESC LIMIT 1;"
echo ""

echo "2. All Test Guests with Addresses:"
echo "-----------------------------------"
sqlite3 -header -column hotel.db "SELECT first_name, last_name, address FROM guests WHERE id >= 2754 AND id <= 2757;"
echo ""

echo "3. Guests with Complete Info (Name, Address, Car):"
echo "---------------------------------------------------"
sqlite3 -header -column hotel.db "SELECT first_name, last_name, address, car_make, car_model, car_color FROM guests WHERE car_make IS NOT NULL AND car_make != '' AND car_make != 'N/A' ORDER BY id DESC LIMIT 5;"
echo ""

echo "4. Verify Address Field is Populated:"
echo "--------------------------------------"
sqlite3 hotel.db "SELECT COUNT(*) as 'Guests with Address' FROM guests WHERE address IS NOT NULL AND address != '';"
echo ""

echo "=========================================="
echo "VALIDATION COMPLETE"
echo "=========================================="
