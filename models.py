from datetime import datetime
from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    wallet_balance = db.Column(db.Float, default=0.0)
    quiz_completed = db.Column(db.Boolean, default=False)
    date_registered = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with Booking
    bookings = db.relationship('Booking', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def add_to_wallet(self, amount):
        self.wallet_balance += amount
        
    def deduct_from_wallet(self, amount):
        if self.wallet_balance >= amount:
            self.wallet_balance -= amount
            return True
        return False
    
    def _repr_(self):
        return f'<User {self.email}>'

class Flight(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    flight_number = db.Column(db.String(10), unique=True, nullable=False)
    origin = db.Column(db.String(64), nullable=False)
    destination = db.Column(db.String(64), nullable=False)
    departure_time = db.Column(db.DateTime, nullable=False)
    arrival_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default="On Time")
    economy_price = db.Column(db.Float, nullable=False)
    premium_price = db.Column(db.Float, nullable=False)
    business_price = db.Column(db.Float, nullable=False)
    available_seats_economy = db.Column(db.Integer, default=100)
    available_seats_premium = db.Column(db.Integer, default=50)
    available_seats_business = db.Column(db.Integer, default=20)
    aircraft_type = db.Column(db.String(50), nullable=False)
    distance_km = db.Column(db.Integer)

    # Relationship with Booking
    bookings = db.relationship('Booking', backref='flight', lazy=True, cascade='all, delete-orphan')

    def get_price(self, travel_class):
        travel_class = travel_class.lower()
        if travel_class == 'economy':
            return self.economy_price
        elif travel_class == 'premium':
            return self.premium_price
        elif travel_class == 'business':
            return self.business_price
        return 0

    def book_seat(self, travel_class):
        travel_class = travel_class.lower()
        if travel_class == 'economy' and self.available_seats_economy > 0:
            self.available_seats_economy -= 1
            return True
        elif travel_class == 'premium' and self.available_seats_premium > 0:
            self.available_seats_premium -= 1
            return True
        elif travel_class == 'business' and self.available_seats_business > 0:
            self.available_seats_business -= 1
            return True
        return False

    def release_seat(self, travel_class):
        travel_class = travel_class.lower()
        if travel_class == 'economy':
            self.available_seats_economy += 1
        elif travel_class == 'premium':
            self.available_seats_premium += 1
        elif travel_class == 'business':
            self.available_seats_business += 1

    def to_dict(self):
        return {
            'id': self.id,
            'flight_number': self.flight_number,
            'origin': self.origin,
            'destination': self.destination,
            'departure_time': self.departure_time.strftime('%Y-%m-%d %H:%M'),
            'arrival_time': self.arrival_time.strftime('%Y-%m-%d %H:%M'),
            'status': self.status,
            'economy_price': self.economy_price,
            'premium_price': self.premium_price,
            'business_price': self.business_price,
            'aircraft_type': self.aircraft_type,
            'distance_km': self.distance_km
        }

    def _repr_(self):
        return f'<Flight {self.flight_number}>'

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    flight_id = db.Column(db.Integer, db.ForeignKey('flight.id'), nullable=False)
    booking_date = db.Column(db.DateTime, default=datetime.utcnow)
    travel_class = db.Column(db.String(20), nullable=False)
    seat_number = db.Column(db.String(5), nullable=False)
    price_paid = db.Column(db.Float, nullable=False)
    passenger_name = db.Column(db.String(128), nullable=False)
    passenger_age = db.Column(db.Integer, nullable=False)
    passenger_gender = db.Column(db.String(10), nullable=False)
    contact_number = db.Column(db.String(15))
    status = db.Column(db.String(20), default="Confirmed")

    def _repr_(self):
        return f'<Booking {self.id}>'