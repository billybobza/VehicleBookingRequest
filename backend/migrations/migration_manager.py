#!/usr/bin/env python3
"""
Database migration management system for the car booking system
"""

import os
import sqlite3
from datetime import datetime
from typing import List, Dict, Any
from sqlalchemy import text
from sqlalchemy.orm import Session

from models.database import SessionLocal, engine


class MigrationManager:
    """Manages database migrations and versioning"""
    
    def __init__(self):
        self.migrations_dir = os.path.dirname(__file__)
        self.migration_table = "schema_migrations"
    
    def ensure_migration_table(self, db: Session) -> None:
        """Create the migration tracking table if it doesn't exist"""
        create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS {self.migration_table} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            version VARCHAR(50) NOT NULL UNIQUE,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            description TEXT
        )
        """
        db.execute(text(create_table_sql))
        db.commit()
    
    def get_applied_migrations(self, db: Session) -> List[str]:
        """Get list of applied migration versions"""
        self.ensure_migration_table(db)
        
        result = db.execute(text(f"SELECT version FROM {self.migration_table} ORDER BY version"))
        return [row[0] for row in result.fetchall()]
    
    def record_migration(self, db: Session, version: str, description: str = "") -> None:
        """Record that a migration has been applied"""
        insert_sql = f"""
        INSERT INTO {self.migration_table} (version, description, applied_at)
        VALUES (:version, :description, :applied_at)
        """
        db.execute(text(insert_sql), {
            "version": version,
            "description": description,
            "applied_at": datetime.now()
        })
        db.commit()
    
    def get_database_version(self, db: Session) -> str:
        """Get the current database schema version"""
        applied_migrations = self.get_applied_migrations(db)
        return applied_migrations[-1] if applied_migrations else "0.0.0"
    
    def initialize_schema_version(self, db: Session) -> None:
        """Initialize the schema version for existing databases"""
        self.ensure_migration_table(db)
        
        # Check if this is a fresh database or existing one
        applied_migrations = self.get_applied_migrations(db)
        
        if not applied_migrations:
            # Record the initial schema version
            self.record_migration(db, "1.0.0", "Initial schema with vehicles, bookings, and availability")
            print("Database schema version initialized to 1.0.0")
    
    def get_migration_status(self, db: Session) -> Dict[str, Any]:
        """Get detailed migration status information"""
        applied_migrations = self.get_applied_migrations(db)
        current_version = self.get_database_version(db)
        
        return {
            "current_version": current_version,
            "applied_migrations": applied_migrations,
            "migration_count": len(applied_migrations),
            "last_migration_date": self._get_last_migration_date(db)
        }
    
    def _get_last_migration_date(self, db: Session) -> str:
        """Get the date of the last applied migration"""
        result = db.execute(text(f"""
            SELECT applied_at FROM {self.migration_table} 
            ORDER BY applied_at DESC LIMIT 1
        """))
        row = result.fetchone()
        return row[0] if row else "Never"


def get_migration_manager() -> MigrationManager:
    """Get a migration manager instance"""
    return MigrationManager()


if __name__ == "__main__":
    # Example usage
    manager = MigrationManager()
    
    with SessionLocal() as db:
        manager.initialize_schema_version(db)
        status = manager.get_migration_status(db)
        
        print("Migration Status:")
        print(f"  Current Version: {status['current_version']}")
        print(f"  Applied Migrations: {status['migration_count']}")
        print(f"  Last Migration: {status['last_migration_date']}")