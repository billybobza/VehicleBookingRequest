# Car Booking System

A web application for booking company vehicles built with Svelte 5 frontend and FastAPI backend.

## Project Structure

```
├── frontend/          # Svelte 5 frontend application
│   ├── src/          # Source code
│   ├── package.json  # Frontend dependencies
│   └── vite.config.ts # Vite configuration
├── backend/          # FastAPI backend application
│   ├── models/       # Database models
│   ├── api/          # API routes
│   ├── services/     # Business logic
│   ├── tests/        # Test files
│   ├── main.py       # FastAPI application
│   └── requirements.txt # Backend dependencies
└── README.md         # This file
```

## Development Setup

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Copy environment file:
   ```bash
   cp .env.example .env
   ```

5. Run the development server:
   ```bash
   python run_dev.py
   ```

The API will be available at http://localhost:8000

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Run the development server:
   ```bash
   npm run dev
   ```

The frontend will be available at http://localhost:5173

## Database Setup

The database is automatically initialized when you start the backend server. For manual database management:

```bash
cd backend

# Check database status
python manage_db.py status

# Initialize database manually
python manage_db.py init

# List all vehicles
python manage_db.py vehicles

# Check vehicle availability for date range
python manage_db.py availability 2024-01-15 2024-01-17

# Seed database with initial data
python manage_db.py seed
```

For detailed database setup and migration information, see [backend/DATABASE_SETUP.md](backend/DATABASE_SETUP.md).

## API Documentation

Once the backend is running, visit http://localhost:8000/docs for interactive API documentation.

## Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```