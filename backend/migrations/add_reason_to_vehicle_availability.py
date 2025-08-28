"""
Migration: Add reason field to vehicle_availability table
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from models.database import engine


def upgrade():
    """Add reason column to vehicle_availability table"""
    with engine.connect() as connection:
        # Add reason column
        connection.execute(text("""
            ALTER TABLE vehicle_availability 
            ADD COLUMN reason VARCHAR(200)
        """))
        connection.commit()
        print("Added reason column to vehicle_availability table")


def downgrade():
    """Remove reason column from vehicle_availability table"""
    with engine.connect() as connection:
        # Remove reason column
        connection.execute(text("""
            ALTER TABLE vehicle_availability 
            DROP COLUMN reason
        """))
        connection.commit()
        print("Removed reason column from vehicle_availability table")


if __name__ == "__main__":
    try:
        upgrade()
        print("Migration completed successfully")
    except Exception as e:
        print(f"Migration failed: {e}")
        print("This might be expected if the column already exists or if using SQLite")