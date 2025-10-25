#!/usr/bin/env python3
"""
Database initialization script for FinMDA-Bot.
"""
import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.database import create_tables, engine
from app.models import Base
from app.config import settings

def init_database():
    """Initialize the database with tables."""
    print("🗄️ Initializing database...")
    
    try:
        # Create all tables
        create_tables()
        print("✅ Database tables created successfully")
        
        # For SQLite, just creating tables is enough to verify it's working
        print("✅ Database initialization successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Database initialization failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = init_database()
    sys.exit(0 if success else 1)
