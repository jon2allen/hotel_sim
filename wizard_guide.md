# Hotel Creation Wizard Guide

The interactive hotel creation wizard guides you through the complete process of setting up a new hotel in the system.

## How to Use

### From Command Line
```bash
python3 hotel_cli.py wizard
```

### From Interactive Mode
```
hotel> create_hotel_interactive
```

## Wizard Steps

### 1. Basic Hotel Information
- **Hotel Name**: The name of your hotel
- **Address**: Full address of the hotel
- **Star Rating**: Rating from 1-5 stars
- **Number of Floors**: How many floors the hotel has
- **Total Rooms**: Total number of rooms in the hotel

### 2. Room Types Selection
- Choose from available room types (Basic, Deluxe, King, Standard, Suite)
- Select multiple types by entering comma-separated numbers

### 3. Room Distribution
Choose one of two options:
- **Manual Distribution**: Specify exact number of rooms for each type
- **Random Distribution**: Let the system distribute rooms randomly

### 4. Room Pricing
- Set base price for each selected room type
- Prices should be positive numbers (e.g., 150.00)

### 5. Room Creation
- The wizard automatically creates all floors and rooms
- Rooms are distributed across floors
- Each room gets the appropriate pricing

## Example Session

```
=== Hotel Creation Wizard ===

--- Basic Hotel Information ---
Enter hotel name: Grand Plaza Hotel
Enter hotel address: 123 Downtown Avenue, New York
Enter star rating (1-5): 5
Enter number of floors: 15
Enter total number of rooms: 100

--- Room Types Setup ---
Available room types:
1. Basic
2. Deluxe  
3. King
4. Standard
5. Suite

Enter room type numbers to include (1-5, comma-separated): 2,3,5

--- Room Distribution (Total: 100 rooms) ---
How would you like to distribute rooms?
1. Define exact numbers for each type
2. Use random distribution
Enter choice (1-2): 1

Number of Deluxe rooms (remaining: 100): 50
Number of King rooms (remaining: 50): 30
Number of Suite rooms (remaining: 20): 20

--- Room Pricing ---
Enter base price for Deluxe rooms (e.g., 150.00): $250.00
Enter base price for King rooms (e.g., 150.00): $350.00
Enter base price for Suite rooms (e.g., 150.00): $500.00

--- Creating Rooms ---
✓ Created 100 rooms for hotel 'Grand Plaza Hotel'

🎉 Hotel creation complete!
Hotel ID: 16
Name: Grand Plaza Hotel
Address: 123 Downtown Avenue, New York
Stars: ★★★★★
Floors: 15
Rooms: 100

Room Type Summary:
  • Deluxe: 50 rooms at $250.00/night
  • King: 30 rooms at $350.00/night
  • Suite: 20 rooms at $500.00/night
```

## Features

- **Complete Hotel Setup**: Creates hotel, floors, and rooms in one process
- **Flexible Room Distribution**: Choose manual or random distribution
- **Custom Pricing**: Set different prices for each room type
- **Automatic Floor Creation**: All floors are created automatically
- **Room Numbering**: Rooms are numbered systematically (e.g., 101, 102, 201, 202)
- **Validation**: Input validation at every step
- **Error Handling**: Graceful error handling with rollback on failure

## Benefits

- **Time Saving**: Creates a complete hotel setup in minutes
- **User Friendly**: Step-by-step guidance with clear prompts
- **Flexible**: Supports both precise control and quick random setup
- **Comprehensive**: Handles all aspects of hotel creation automatically