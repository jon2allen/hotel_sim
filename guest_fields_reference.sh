#!/bin/bash
# Quick reference for guest field specifications

echo "=========================================="
echo "GUEST TABLE FIELD SPECIFICATIONS"
echo "=========================================="
echo ""

echo "📱 PHONE FIELD:"
echo "  Field: phone"
echo "  Type: TEXT"
echo "  Purpose: CELL/MOBILE NUMBERS ONLY"
echo "  Required: No (optional)"
echo ""

echo "📍 ADDRESS FIELD:"
echo "  Field: address"
echo "  Type: TEXT (unlimited length)"
echo "  Purpose: Physical/mailing address"
echo "  Required: No (optional)"
echo ""

echo "🚗 CAR FIELDS:"
echo "  Fields: car_make, car_model, car_color"
echo "  Type: TEXT (all optional)"
echo "  Purpose: Vehicle information"
echo "  Can be: Empty, N/A, or specific values"
echo ""

echo "=========================================="
echo "CURRENT DATABASE STATISTICS"
echo "=========================================="
echo ""

echo "Guests with phone numbers:"
sqlite3 hotel.db "SELECT COUNT(*) FROM guests WHERE phone IS NOT NULL AND phone != '';"

echo ""
echo "Guests with addresses:"
sqlite3 hotel.db "SELECT COUNT(*) FROM guests WHERE address IS NOT NULL AND address != '';"

echo ""
echo "Guests with car info:"
sqlite3 hotel.db "SELECT COUNT(*) FROM guests WHERE car_make IS NOT NULL AND car_make != '' AND car_make != 'N/A';"

echo ""
echo "=========================================="
echo "SAMPLE GUEST RECORD"
echo "=========================================="
sqlite3 -line hotel.db "SELECT first_name, last_name, email, phone, address, car_make, car_model, car_color FROM guests WHERE phone IS NOT NULL AND phone != '' AND car_make IS NOT NULL AND car_make != '' AND car_make != 'N/A' LIMIT 1;"

echo ""
echo "=========================================="
echo "For full documentation, see:"
echo "  GUEST_FIELDS_DOCUMENTATION.md"
echo "=========================================="
