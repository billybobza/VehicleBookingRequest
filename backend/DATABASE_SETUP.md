# Database Setup and Migration Guide

This document provides comprehensive instructions for setting up, initializing, and managing the car booking system database.

## Overview

The car booking system uses SQLite as the default database with SQLAlchemy ORM for data modeling and management. The system includes:

- **Vehicle Management**: Store and manage company vehicle information
- **Booking System**: Handle vehicle reservations and scheduling
- **Availability Tracking**: Monitor vehicle availability periods
- **Migration System**: Track database schema changes and versions

## Database Schema

### Tables

1. **vehicles**: Company vehicle information
   - `id`: Primary key
   - `registration`: Unique vehicle registration number
   - `make`: Vehicle manufacturer
   - `color`: Vehicle color
   - `created_at`, `updated_at`: Timestamps

2. **bookings**: Vehicle reservation records
   - `id`: Primary key
   - `vehicle_id`: Foreign key to vehicles table
   - `start_datetime`, `end_datetime`: Booking period
   - `return_datetime`: Expected return time
   - `reason`: Booking purpose
   - `estimated_mileage`: Expected mileage
   - `status`: Booking status (confirmed, cancelled, etc.)
   - `created_at`: Creation timestamp

3. **vehicle_availability**: Vehicle availability periods
   - `id`: Primary key
   - `vehicle_id`: Foreign key to vehicles table
   - `start_date`, `end_date`: Availability period
   - `is_available`: Availability status

4. **schema_migrations**: Migration tracking (auto-created)
   - `id`: Primary key
   - `version`: Migration version
   - `applied_at`: Application timestamp
   - `description`: Migration description

## Quick Start

### 1. Environment Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment configuration
cp .env.example .env
```

### 2. Database Initialization

The database is automatically initialized when you start the application:

```bash
# Start the development server (auto-initializes database)
python run_dev.py

# Or run the main application
python main.py
```

### 3. Manual Database Operations

```bash
# Initialize database manually
python database_init.py

# Reset database (drops all data and recreates)
python -c "from database_init import reset_database; reset_database()"

# Check migration status
python -c "from migrations.migration_manager import get_migration_manager; from models.database import SessionLocal; manager = get_migration_manager(); db = SessionLocal(); status = manager.get_migration_status(db); print(f'Version: {status[\"current_version\"]}, Migrations: {status[\"migration_count\"]}'); db.close()"
```

## Database Configuration

### Environment Variables

Configure database settings in `.env` file:

```env
# Database URL (SQLite by default)
DATABASE_URL=sqlite:///./car_booking.db

# For PostgreSQL (example)
# DATABASE_URL=postgresql://user:password@localhost/car_booking

# For MySQL (example)
# DATABASE_URL=mysql://user:password@localhost/car_booking
```

### Database Files

- **Production**: `car_booking.db`
- **Testing**: `test_vehicles.db`, `test_bookings.db`

## Seeded Data

The system automatically seeds the database with:

### 11 Company Vehicles

| Registration | Make | Color |
|-------------|------|-------|
| ABC123 | Toyota | White |
| DEF456 | Honda | Silver |
| GHI789 | Ford | Blue |
| JKL012 | Volkswagen | Black |
| MNO345 | Nissan | Red |
| PQR678 | Hyundai | Gray |
| STU901 | Mazda | White |
| VWX234 | Subaru | Blue |
| YZA567 | Kia | Silver |
| BCD890 | Mitsubishi | Black |
| EFG123 | Suzuki | Green |

### Availability Data

- **Period**: Next 3 months from current date
- **Pattern**: Random availability periods (1-7 days each)
- **Availability Rate**: 80% available, 20% unavailable
- **Purpose**: Realistic testing and demonstration data

## Migration System

### Overview

The migration system tracks database schema changes and versions:

- **Version Tracking**: Each schema change gets a version number
- **Applied Migrations**: System tracks which migrations have been applied
- **Rollback Support**: Future enhancement for rolling back changes

### Migration Commands

```python
from migrations.migration_manager import get_migration_manager
from models.database import SessionLocal

# Get migration manager
manager = get_migration_manager()

# Check current status
with SessionLocal() as db:
    status = manager.get_migration_status(db)
    print(f"Current version: {status['current_version']}")
    print(f"Applied migrations: {status['applied_migrations']}")
```

### Adding New Migrations

1. Create migration file in `migrations/` directory
2. Update migration manager to include new migration
3. Test migration on development database
4. Apply to production database

## Database Utilities

### Available Utilities (`db_utils.py`)

- `get_all_vehicles()`: Retrieve all vehicles
- `get_vehicle_by_id()`: Find vehicle by ID
- `check_vehicle_availability()`: Check if vehicle is available for date range
- `get_available_vehicles()`: Get all available vehicles for period
- `create_booking()`: Create new booking
- `calculate_return_date()`: Calculate return date with business rules

### Usage Example

```python
from db_utils import DatabaseSession, get_available_vehicles
from datetime import date, timedelta

# Use context manager for database operations
with DatabaseSession() as db:
    today = date.today()
    tomorrow = today + timedelta(days=1)
    
    available_vehicles = get_available_vehicles(db, today, tomorrow)
    print(f"Available vehicles: {len(available_vehicles)}")
```

## Troubleshooting

### Common Issues

1. **Database locked error**
   - Ensure no other processes are using the database
   - Check for unclosed database connections

2. **Migration table not found**
   - Run database initialization: `python database_init.py`

3. **Seeding fails**
   - Check if data already exists (seeding skips existing data)
   - Verify database permissions

4. **Connection errors**
   - Verify DATABASE_URL in `.env` file
   - Check database file permissions

### Reset Database

```bash
# Complete reset (WARNING: Deletes all data)
python -c "from database_init import reset_database; reset_database()"
```

### Backup and Restore

```bash
# Backup SQLite database
cp car_booking.db car_booking_backup.db

# Restore from backup
cp car_booking_backup.db car_booking.db
```

## Testing

### Test Database

Tests use separate database files to avoid affecting development data:

```bash
# Run all tests
pytest

# Run database-specific tests
pytest tests/test_database.py

# Run with verbose output
pytest -v
```

### Test Data

Test databases are automatically created and seeded during test runs. Test data is isolated from development and production databases.

## Performance Considerations

### Indexing

Current indexes:
- `vehicles.registration` (unique)
- `vehicles.id` (primary key)
- `bookings.vehicle_id` (foreign key)
- `vehicle_availability.vehicle_id` (foreign key)

### Query Optimization

- Use `get_available_vehicles()` for efficient availability queries
- Leverage database indexes for filtering operations
- Consider connection pooling for high-traffic scenarios

## Security

### Best Practices

- Use environment variables for database credentials
- Implement proper input validation
- Use parameterized queries (SQLAlchemy handles this)
- Regular database backups
- Monitor for SQL injection attempts

### Access Control

- Database access through application layer only
- No direct database access for end users
- API-level authentication and authorization

## Monitoring

### Health Checks

The application includes database health checks:

```bash
# Check API health (includes database connectivity)
curl http://localhost:8000/health
```

### Logging

Database operations are logged through the application logging system. Check application logs for database-related issues.