#!/bin/bash
# Quick reference queries for guest car fields

echo "=========================================="
echo "Guest Car Fields - Quick Reference Queries"
echo "=========================================="
echo ""

echo "1. View updated schema:"
sqlite3 hotel.db ".schema guests"
echo ""

echo "2. Count guests with cars:"
sqlite3 hotel.db "SELECT COUNT(*) as guests_with_cars FROM guests WHERE car_make IS NOT NULL AND car_make != '' AND car_make != 'N/A';"
echo ""

echo "3. Count guests without cars:"
sqlite3 hotel.db "SELECT COUNT(*) as guests_without_cars FROM guests WHERE car_make IS NULL OR car_make = '' OR car_make = 'N/A';"
echo ""

echo "4. List all car makes:"
sqlite3 hotel.db "SELECT DISTINCT car_make, COUNT(*) as count FROM guests WHERE car_make IS NOT NULL AND car_make != '' AND car_make != 'N/A' GROUP BY car_make ORDER BY count DESC;"
echo ""

echo "5. List all car colors:"
sqlite3 hotel.db "SELECT DISTINCT car_color, COUNT(*) as count FROM guests WHERE car_color IS NOT NULL AND car_color != '' AND car_color != 'N/A' GROUP BY car_color ORDER BY count DESC;"
echo ""

echo "6. Recent guests with cars (last 10):"
sqlite3 hotel.db "SELECT first_name, last_name, car_color, car_make, car_model FROM guests WHERE car_make IS NOT NULL AND car_make != '' AND car_make != 'N/A' ORDER BY id DESC LIMIT 10;"
echo ""

echo "7. Find specific car make (example: Toyota):"
sqlite3 hotel.db "SELECT first_name, last_name, email, car_model, car_color FROM guests WHERE car_make = 'Toyota';"
echo ""

echo "8. Sample guest with all fields:"
sqlite3 hotel.db "SELECT * FROM guests WHERE car_make IS NOT NULL AND car_make != '' AND car_make != 'N/A' LIMIT 1;"
echo ""

echo "=========================================="
echo "All queries completed!"
echo "=========================================="
