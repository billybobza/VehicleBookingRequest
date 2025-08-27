from sqlalchemy import create_engine, Column, Integer, String, DateTime, Date, Boolean, ForeignKey, Text
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func
from datetime import datetime, date
from typing import Optional

from config import settings

# Create database engine
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()


class Vehicle(Base):
    """Vehicle model representing company vehicles"""
    __tablename__ = "vehicles"
    
    id = Column(Integer, primary_key=True, index=True)
    registration = Column(String(20), unique=True, nullable=False, index=True)
    make = Column(String(50), nullable=False)
    color = Column(String(30), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    bookings = relationship("Booking", back_populates="vehicle")
    availability_records = relationship("VehicleAvailability", back_populates="vehicle")
    
    def __repr__(self):
        return f"<Vehicle(id={self.id}, registration='{self.registration}', make='{self.make}', color='{self.color}')>"


class Booking(Base):
    """Booking model representing vehicle reservations"""
    __tablename__ = "bookings"
    
    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False)
    start_datetime = Column(DateTime(timezone=True), nullable=False)
    end_datetime = Column(DateTime(timezone=True), nullable=False)
    return_datetime = Column(DateTime(timezone=True), nullable=False)
    reason = Column(Text, nullable=False)
    estimated_mileage = Column(Integer, nullable=False)
    status = Column(String(20), default="confirmed", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    vehicle = relationship("Vehicle", back_populates="bookings")
    
    def __repr__(self):
        return f"<Booking(id={self.id}, vehicle_id={self.vehicle_id}, start='{self.start_datetime}', status='{self.status}')>"


class VehicleAvailability(Base):
    """Vehicle availability model for tracking when vehicles are available"""
    __tablename__ = "vehicle_availability"
    
    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    is_available = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    vehicle = relationship("Vehicle", back_populates="availability_records")
    
    def __repr__(self):
        return f"<VehicleAvailability(id={self.id}, vehicle_id={self.vehicle_id}, start='{self.start_date}', end='{self.end_date}', available={self.is_available})>"


# Database dependency function
def get_db():
    """Dependency function to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Function to create all tables
def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)


# Function to drop all tables (useful for testing)
def drop_tables():
    """Drop all database tables"""
    Base.metadata.drop_all(bind=engine)