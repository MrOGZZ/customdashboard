from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user
from sqlalchemy.orm import relationship
import os


app = Flask(__name__)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port)
    
app.config['SECRET_KEY'] = 'your_secret_key'  # Replace with a secure secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'  # SQLite database file
db = SQLAlchemy(app)
login_manager = LoginManager(app)

class Dashboard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    website_link_count = db.Column(db.Integer, default=0)
    dmca_takedowns_sent = db.Column(db.Integer, default=0)
    dmca_takedowns_successful = db.Column(db.Integer, default=0)
    money_saved = db.Column(db.Float, default=0.0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    dashboard = relationship('Dashboard', backref='user', uselist=False, foreign_keys='Dashboard.user_id')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/user_ids')
def user_ids():
    users = User.query.all()
    user_ids = [user.id for user in users]
    return render_template('user_ids.html', user_ids=user_ids)

@app.route('/update_links')
@login_required
def update_links():
    # Check if the current user is the admin
    if current_user.username == 'admin':
        # Fetch all user IDs from the database
        user_ids = [user.id for user in User.query.all()]

        return render_template('update_links.html', user_ids=user_ids)

    return "Unauthorized access!"

@app.route('/update_dashboard/<int:user_id>', methods=['GET', 'POST'])
@login_required
def update_dashboard(user_id):
    # Check if the current user is the admin
    if current_user.username == 'admin':
        user_to_update = User.query.get(user_id)

        if request.method == 'POST':
            # Check if the user has a dashboard, create a new one if None
            if user_to_update.dashboard is None:
                user_to_update.dashboard = Dashboard()

            try:
                # Update dashboard values
                user_to_update.dashboard.website_link_count = int(request.form.get('website_link_count', 0))
                user_to_update.dashboard.dmca_takedowns_sent = int(request.form.get('dmca_takedowns_sent', 0))
                user_to_update.dashboard.dmca_takedowns_successful = int(request.form.get('dmca_takedowns_successful', 0))

                # Handle money_saved conversion
                money_saved_str = request.form.get('money_saved', '')
                user_to_update.dashboard.money_saved = float(money_saved_str) if money_saved_str else 0.0

                db.session.commit()
                flash('Dashboard updated successfully!', 'success')
                return redirect(url_for('admin_panel'))
            except Exception as e:
                db.session.rollback()
                flash(f'Error updating dashboard: {str(e)}', 'error')

        return render_template('update_dashboard.html', user=user_to_update)

    return "Unauthorized access!"

@app.route('/user_dashboard')
@login_required
def user_dashboard():
    dashboard = current_user.dashboard
    return render_template('user_dashboard.html', dashboard=dashboard)

@app.route('/register', methods=['POST'])
@login_required
def register_user():
    if current_user.username == 'admin':
        username = request.form.get('username')
        password = request.form.get('password')

        # Create a new user with a linked dashboard
        new_dashboard = Dashboard()
        new_user = User(username=username, password=password, dashboard=new_dashboard)
        db.session.add_all([new_dashboard, new_user])
        db.session.commit()

        return f"User {username} registered successfully!"

    return "Unauthorized access!"

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username, password=password).first()

        if user:
            login_user(user)
            return "Login successful!"

        return "Login failed!"

    # If it's a GET request, render the login form
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return "Logout successful!"

@app.route('/admin')
@login_required
def admin_panel():
    if current_user.username == 'admin':  # Change this to your admin username
        users = User.query.all()
        return render_template('admin_panel.html', users=users)
    return "Unauthorized access!"

if __name__ == '__main__':
    app.run(debug=True)
