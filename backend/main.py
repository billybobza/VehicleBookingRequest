from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database_init import initialize_database
from api.routes import api_router
from middleware.error_handler import add_error_handlers


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application lifespan events"""
    # Startup
    try:
        initialize_database()
        print("Database initialized successfully on startup")
    except Exception as e:
        print(f"Warning: Database initialization failed: {e}")
    
    yield
    
    # Shutdown (if needed)
    pass


app = FastAPI(
    title="Car Booking System API", 
    version="1.0.0",
    description="API for managing car bookings and vehicle availability",
    lifespan=lifespan
)

# Add error handlers
add_error_handlers(app)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5177"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router)

@app.get("/")
async def root():
    return {"message": "Car Booking System API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)