from fastapi import APIRouter
from .endpoints import vehicles, bookings
from routers import admin

# Create main API router
api_router = APIRouter(prefix="/api")

# Include endpoint routers
api_router.include_router(vehicles.router, prefix="/vehicles", tags=["vehicles"])
api_router.include_router(bookings.router, prefix="/bookings", tags=["bookings"])
api_router.include_router(admin.router, tags=["admin"])