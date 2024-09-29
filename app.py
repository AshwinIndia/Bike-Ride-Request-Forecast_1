from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
import joblib
import pandas as pd
import secrets
from itsdangerous import URLSafeTimedSerializer
from werkzeug.security import generate_password_hash, check_password_hash
import traceback

model = joblib.load('bike_demand_model.pkl')

# Initialize Flask app
app = Flask(__name__)

# Set up the database configuration (SQLite in this case)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = secrets.token_urlsafe(16)

# Initialize SQLAlchemy with the Flask app
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Initialize bcrypt
bcrypt = Bcrypt(app)

# Define User model for registration and login, inheriting from `UserMixin`
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(150), nullable=False)
    is_active = db.Column(db.Boolean, default=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Load user from the database
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Ensure the database is up to date by recreating tables (useful in development)
with app.app_context():
    db.create_all()

# Helper function to generate password reset tokens
def generate_reset_token(user):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return serializer.dumps(user.email, salt='password-reset-salt')

# Helper function to verify reset tokens
def verify_reset_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        email = serializer.loads(token, salt='password-reset-salt', max_age=expiration)
    except:
        return None
    return User.query.filter_by(email=email).first()

# Route: Home
@app.route('/')
def home():
    return "Bike Ride Demand Forecasting API Home Page"

# Route: Registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email address already exists. Please use a different email.', 'danger')
            return redirect(url_for('register'))

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(username=username, email=email, password_hash=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

# Route: Forgot Password
@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        user = User.query.filter_by(email=email).first()
        if user:
            token = generate_reset_token(user)
            reset_url = url_for('reset_password', token=token, _external=True)
            print(f"Reset your password here: {reset_url}")
            flash(f"Password reset link has been sent to {email}. Check your email!", "info")
        else:
            flash("This email is not registered.", "danger")
        return redirect(url_for('login'))
    return render_template('forgot_password.html')

# Route: Reset Password
@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    user = verify_reset_token(token)
    if not user:
        flash('The reset link is invalid or has expired.', 'warning')
        return redirect(url_for('forgot_password'))

    if request.method == 'POST':
        password = request.form['password']
        user.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        db.session.commit()
        flash('Your password has been updated!', 'success')
        return redirect(url_for('login'))
    return render_template('reset_password.html')

# Route: Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('homepage'))
        else:
            flash('Invalid credentials. Please try again.', 'danger')
    return render_template('login.html')

# Route: Logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

day_of_week_mapping = {
    'Monday': 0,
    'Tuesday': 1,
    'Wednesday': 2,
    'Thursday': 3,
    'Friday': 4,
    'Saturday': 5,
    'Sunday': 6
}

# Route: Homepage (Requires Login)
@app.route('/homepage', methods=['GET', 'POST'])
@login_required
def homepage():
    if request.method == 'POST':
        try:
            # Get the input values from the form
            temperature = float(request.form['temperature'])
            humidity = float(request.form['humidity'])
            weather_condition = request.form['weather_condition']
            
            day_of_week = request.form['day_of_week']
            if day_of_week in day_of_week_mapping:
                day_of_week = day_of_week_mapping[day_of_week]
            else:
                day_of_week = int(day_of_week)  

            hour_of_day = int(request.form['hour_of_day'])
            is_weekend = int(request.form['is_weekend'])
            is_holiday = int(request.form['is_holiday'])

            input_data = pd.DataFrame({
                'temperature': [temperature],
                'humidity': [humidity],
                'weather_condition': [weather_condition],
                'hour_of_day': [hour_of_day],
                'day_of_week': [day_of_week],
                'is_weekend': [is_weekend],
                'is_holiday': [is_holiday]
            })

            print(f"Input Data Before Prediction: \n{input_data}")

            prediction = model.predict(input_data)//1
            
            print(f"Prediction: {prediction//1}")

            return render_template('result.html', prediction=prediction[0])

        except Exception as e:
            print(f"Error during prediction: {traceback.format_exc()}")
            return f"Error during prediction. Check your input format. Error details: {e}"

    return render_template('homepage.html')

# Route: Result (Shows the prediction result)
@app.route('/result')
@login_required
def result():
    return render_template('result.html')

# Run the app
if __name__ == '__main__':
    app.run(debug=True, port=5000)
