#!/usr/bin/env python3
"""
Startup script for Smart Content Moderator API
This script helps you quickly set up and run the application.
"""

import os
import sys
import subprocess
import time
from pathlib import Path
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 11):
        print("❌ Error: Python 3.11 or higher is required.")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import fastapi
        import sqlalchemy
        import google.generativeai
        print("✅ All required dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def check_env_file():
    """Check if .env file exists and has required variables."""
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found")
        print("Please copy env.example to .env and configure your settings")
        return False
    
    # Read .env file
    with open(env_file, 'r') as f:
        content = f.read()
    
    required_vars = [
        "DATABASE_URL",
        "GEMINI_API_KEY"
    ]
    
    missing_vars = []
    for var in required_vars:
        if f"{var}=" not in content or (f"{var}=" in content and "your_" in content):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing or unconfigured environment variables: {', '.join(missing_vars)}")
        print("Please update your .env file with the required values")
        return False
    
    print("✅ Environment file is configured")
    return True

def check_database():
    """Check if database is accessible."""
    try:
        from app.core.config import settings
        from sqlalchemy import create_engine, text

        engine = create_engine(settings.database_url, echo=False)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Database connection successful:", result.fetchall())
        engine.dispose()
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("Please ensure PostgreSQL is running and DATABASE_URL is correct")
        return False

def run_migrations():
    """Run database migrations."""
    try:
        print("🔄 Running database migrations...")
        result = subprocess.run(["alembic", "upgrade", "head"], 
                                capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Database migrations completed")
            return True
        else:
            print(f"❌ Migration failed: {result.stderr}")
            return False
    except FileNotFoundError:
        print("❌ Alembic not found. Please install it: pip install alembic")
        return False

def start_server():
    """Start the FastAPI server."""
    print("🚀 Starting Smart Content Moderator API...")
    print("API will be available at: http://localhost:8000")
    print("API Documentation: http://localhost:8000/docs")
    print("Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        subprocess.run([
            "uvicorn", "app.main:app", 
            "--reload", 
            "--host", "0.0.0.0", 
            "--port", "8000"
        ])
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
    except FileNotFoundError:
        print("❌ Uvicorn not found. Please install it: pip install uvicorn[standard]")

def main():
    """Main startup function."""
    print("🤖 Smart Content Moderator API Startup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        return
    
    # Check dependencies
    if not check_dependencies():
        return
    
    # Check environment file
    if not check_env_file():
        return
    
    # Check database connection
    if not check_database():
        return
    
    # Run migrations
    if not run_migrations():
        return
    
    print("\n✅ All checks passed! Starting server...")
    time.sleep(1)
    
    # Start server
    start_server()

if __name__ == "__main__":
    main()
