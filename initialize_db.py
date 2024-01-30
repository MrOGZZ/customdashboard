# initialize_db.py

from app import app, db, User, Dashboard

with app.app_context():
    db.create_all()
    print("Database tables created successfully.")
