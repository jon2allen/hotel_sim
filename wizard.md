# Hotel Creation Wizard Specification

## Overview
The Hotel Creation Wizard is an interactive interface that guides users through the complete process of creating a new hotel in the Hotel Simulator system. It handles all aspects of hotel setup including basic information, room type selection, room distribution, pricing, and automatic creation of floors and rooms.

## Requirements

### Functional Requirements

#### 1. Basic Hotel Information Collection
- **Hotel Name**: Must be non-empty string
- **Hotel Address**: Must be non-empty string  
- **Star Rating**: Integer between 1-5 (inclusive)
- **Number of Floors**: Positive integer (≥1)
- **Total Rooms**: Positive integer (≥1)

#### 2. Room Type Selection
- Display all available room types from database
- Allow selection of multiple room types
- Input validation for valid room type selections
- Minimum 1 room type must be selected

#### 3. Room Distribution Options
- **Manual Distribution**:
  - User specifies exact count for each selected room type
  - Validate that total doesn't exceed specified room count
  - Handle remaining rooms automatically
  
- **Random Distribution**:
  - System distributes rooms randomly among selected types
  - Ensure all rooms are assigned
  - Provide visual feedback during distribution

#### 4. Room Pricing Configuration
- Set custom price for each selected room type
- Price must be positive decimal number
- Display pricing prompts with examples
- Validate all price inputs

#### 5. Automatic Room Creation
- Create all specified floors automatically
- Generate systematic room numbers (e.g., 101, 102, 201, 202)
- Distribute rooms across floors evenly
- Assign correct room types and pricing
- Provide progress feedback during creation

### Non-Functional Requirements

#### User Experience
- Clear section headers and progress indicators
- Helpful prompts with examples
- Real-time validation and error messages
- Visual feedback (checkmarks, completion indicators)
- Summary of created hotel and rooms

#### Error Handling
- Comprehensive input validation
- Clear, actionable error messages
- Database transaction rollback on failure
- Graceful handling of edge cases
- User-friendly error recovery

#### Performance
- Efficient database operations
- Minimal user waiting time
- Progress feedback for long operations
- Optimized room creation process

## Technical Specification

### Command Interface

#### Command Line Access
```bash
python3 hotel_cli.py wizard
```

#### Interactive Mode Access
```
hotel> create_hotel_interactive
```

#### Help Text
```
Interactive hotel creation wizard - guides you through creating a complete hotel with rooms, floors, and pricing
```

### Implementation Details

#### Database Operations
1. **Hotel Creation**: Insert record into `hotel` table
2. **Floor Creation**: Insert records into `floors` table
3. **Room Creation**: Insert records into `rooms` table with proper foreign keys
4. **Transaction Management**: Use database transactions with rollback on error

#### Input Validation Rules
- **Strings**: Non-empty, reasonable length
- **Numbers**: Positive integers, within reasonable bounds
- **Prices**: Positive decimals, reasonable values
- **Selections**: Valid room type IDs, proper format

#### Room Numbering Algorithm
- Format: `{floor_number}{sequential_number}`
- Example: Floor 1, Room 1 → "101"
- Sequential numbering across all floors
- Zero-padded for consistency

#### Distribution Algorithms
- **Manual**: User-specified counts with validation
- **Random**: Weighted random distribution ensuring all rooms assigned

### Error Handling Strategy

#### Validation Errors
- Immediate feedback with clear messages
- Allow retry without losing progress
- Specific guidance on correction

#### Database Errors
- Transaction rollback on failure
- User-friendly error messages
- Log technical details internally

#### Edge Cases
- Handle remaining rooms in manual distribution
- Ensure minimum 1 room per type in random distribution
- Validate total rooms match specification

## User Interface Flow

```
Start Wizard
  ↓
Basic Hotel Information
  ↓
Room Type Selection  
  ↓
Room Distribution Choice
  ↓
  ├── Manual Distribution → Room Counts per Type
  │                         ↓
  └── Random Distribution → Auto-distribute
  ↓
Room Pricing Configuration
  ↓
Room Creation Process
  ↓
Completion Summary
  ↓
End Wizard
```

## Data Flow

```
User Input → Validation → Database Operations → Feedback → Next Step
```

## Success Criteria

### Functional Success
- Hotel record created with correct details
- All floors created successfully
- All rooms created with correct types and pricing
- Total room count matches specification
- No database errors or inconsistencies

### User Experience Success
- Clear, intuitive interface
- Minimal user confusion
- Helpful error messages
- Satisfying completion feedback
- Reasonable completion time

## Testing Requirements

### Test Cases
1. **Basic Functionality**: Complete wizard with valid inputs
2. **Manual Distribution**: Test exact room count specification
3. **Random Distribution**: Test automatic room distribution
4. **Input Validation**: Test all validation scenarios
5. **Error Handling**: Test error recovery and rollback
6. **Edge Cases**: Test boundary conditions

### Test Coverage
- All room types supported
- Various hotel sizes (small, medium, large)
- Different distribution patterns
- Error conditions and recovery
- Both CLI access methods

## Documentation Requirements

### User Documentation
- Step-by-step usage guide
- Examples of complete sessions
- Troubleshooting guide
- Frequently asked questions

### Technical Documentation
- Implementation details
- Database schema interactions
- Error handling strategy
- Performance considerations

## Compliance

### Database Schema Compliance
- Maintain referential integrity
- Respect foreign key constraints
- Follow existing naming conventions
- Preserve data consistency

### Code Standards Compliance
- Follow existing code style
- Maintain consistent error handling
- Use appropriate logging
- Include comprehensive documentation

## Future Enhancements

### Potential Features
- Room amenity configuration
- Floor-specific features
- Advanced pricing rules
- Template-based hotel creation
- Import/export functionality

### Performance Improvements
- Batch room creation
- Progress indicators
- Parallel processing where possible
- Caching of common data

## Appendix

### Example Session

```
=== Hotel Creation Wizard ===

--- Basic Hotel Information ---
Enter hotel name: Grand Hotel
Enter hotel address: 123 Main Street
Enter star rating (1-5): 5
Enter number of floors: 10
Enter total number of rooms: 50

--- Room Types Setup ---
Available room types:
1. Basic
2. Deluxe
3. King
4. Standard
5. Suite

Enter room type numbers to include (1-5, comma-separated): 2,3,5

--- Room Distribution (Total: 50 rooms) ---
How would you like to distribute rooms?
1. Define exact numbers for each type
2. Use random distribution
Enter choice (1-2): 1

Number of Deluxe rooms (remaining: 50): 25
Number of King rooms (remaining: 25): 15
Number of Suite rooms (remaining: 10): 10

--- Room Pricing ---
Enter base price for Deluxe rooms (e.g., 150.00): $250.00
Enter base price for King rooms (e.g., 150.00): $350.00
Enter base price for Suite rooms (e.g., 150.00): $500.00

--- Creating Rooms ---
✓ Created 50 rooms for hotel 'Grand Hotel'

🎉 Hotel creation complete!
Hotel ID: 16
Name: Grand Hotel
Address: 123 Main Street
Stars: ★★★★★
Floors: 10
Rooms: 50

Room Type Summary:
  • Deluxe: 25 rooms at $250.00/night
  • King: 15 rooms at $350.00/night
  • Suite: 10 rooms at $500.00/night
```

### Error Handling Examples

```
# Invalid star rating
Enter star rating (1-5): 6
Error: Star rating must be between 1 and 5

# Invalid room count
Number of Deluxe rooms (remaining: 50): 51
Error: Cannot have more than 50 rooms

# Invalid price
Enter base price for Deluxe rooms (e.g., 150.00): -100
Error: Price must be positive
```

## Revision History

- **1.0**: Initial specification
- **1.1**: Added detailed error handling requirements
- **1.2**: Enhanced user interface flow diagram
- **1.3**: Added compliance section
- **1.4**: Added future enhancements section