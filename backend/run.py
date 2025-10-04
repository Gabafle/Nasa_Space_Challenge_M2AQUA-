#!/usr/bin/env python
"""
Space Apps 2025 - Exoplanet AI Platform
Backend Server Runner
"""

import os
import sys
import logging
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_dependencies():
    """Check if required packages are installed"""
    required = [
        'flask',
        'flask_cors',
        'flask_jwt_extended',
        'flask_sqlalchemy',
        'flask_migrate',
        'marshmallow',
        'pandas',
        'numpy'
    ]
    
    missing = []
    for package in required:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print("❌ Missing required packages:")
        for pkg in missing:
            print(f"   - {pkg}")
        print("\n📦 Install them with:")
        print("   pip install -r requirements.txt")
        return False
    return True

def setup_environment():
    """Setup environment variables if .env doesn't exist"""
    env_file = Path('.env')
    
    if not env_file.exists():
        print("📝 Creating .env file with default settings...")
        default_env = """DATABASE_URL=sqlite:///app.db
JWT_SECRET_KEY=blablablajwt
UPLOAD_FOLDER=uploads
ARTIFACT_FOLDER=artifacts
CORS_ORIGINS=http://localhost:5173,http://localhost:5174
FLASK_ENV=development
"""
        env_file.write_text(default_env)
        print("✅ .env file created")

def create_directories():
    """Create necessary directories"""
    dirs = ['uploads', 'artifacts', 'blueprints', 'services', 'migrations']
    for dir_name in dirs:
        Path(dir_name).mkdir(exist_ok=True)
    print("📁 Directories created/verified")

def initialize_database():
    """Initialize database if it doesn't exist"""
    try:
        from app import app, db
        from models import User, Role
        from werkzeug.security import generate_password_hash
        
        db_file = Path('app.db')
        
        with app.app_context():
            if not db_file.exists():
                print("🗄️ Creating database...")
                db.create_all()
                print("✅ Database created")
                
                # Create default admin user (optional)
                admin = User.query.filter_by(email='admin@example.com').first()
                if not admin:
                    admin = User(
                        email='admin@example.com',
                        name='Admin User',
                        role=Role.admin,
                        password_hash=generate_password_hash('admin123')
                    )
                    db.session.add(admin)
                    db.session.commit()
                    print("👤 Default admin user created:")
                    print("   Email: admin@example.com")
                    print("   Password: admin123")
                    print("   ⚠️  Change this password immediately!")
            else:
                print("✅ Database already exists")
    except Exception as e:
        print(f"⚠️ Database initialization warning: {e}")
        print("   The database will be created when the app starts.")

def run_server():
    """Run the Flask development server"""
    try:
        from app import app
        
        print("\n" + "="*50)
        print("🚀 Space Apps 2025 - Exoplanet AI Platform")
        print("="*50)
        print("📍 Backend URL: http://localhost:5000")
        print("📍 Frontend URL: http://localhost:5173")
        print("📚 API Docs: http://localhost:5000/api/health")
        print("\nPress CTRL+C to stop the server")
        print("="*50 + "\n")
        
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True,
            use_reloader=True
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

def main():
    """Main entry point"""
    print("🚀 Starting Space Apps 2025 Backend Setup...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Setup
    setup_environment()
    create_directories()
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Initialize database
    initialize_database()
    
    # Run server
    run_server()

if __name__ == '__main__':
    main()