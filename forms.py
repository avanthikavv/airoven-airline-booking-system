from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, SelectField, SubmitField, FloatField, RadioField, HiddenField
from wtforms.validators import DataRequired, Email, Length, EqualTo, NumberRange, ValidationError
import re
from datetime import datetime, timedelta

class SignupForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    age = IntegerField('Age', validators=[DataRequired(), NumberRange(min=1, max=120)])
    gender = SelectField('Gender', choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')], validators=[DataRequired()])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Sign Up')
    
    def validate_password(self, field):
        # Check if password contains at least one uppercase letter, one lowercase, and one number
        if not re.search(r'[A-Z]', field.data):
            raise ValidationError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', field.data):
            raise ValidationError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', field.data):
            raise ValidationError('Password must contain at least one number')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')

class QuizForm(FlaskForm):
    question_1 = RadioField('Question 1', validators=[DataRequired()], choices=[
        ('A', 'To save battery'),
        ('B', 'To avoid interference with aircraft systems'),
        ('C', 'To reduce noise'),
        ('D', 'For entertainment purposes')
    ])
    question_2 = RadioField('Question 2', validators=[DataRequired()], choices=[
        ('A', 'To advertise travel destinations'),
        ('B', 'To guide passengers on using in-flight entertainment'),
        ('C', 'To provide instructions during an emergency'),
        ('D', 'To offer discount coupons')
    ])
    question_3 = RadioField('Question 3', validators=[DataRequired()], choices=[
        ('A', 'Only during takeoff'),
        ('B', 'Only when sleeping'),
        ('C', 'Only during turbulence'),
        ('D', 'During takeoff, landing, and whenever the seatbelt sign is on')
    ])
    question_4 = RadioField('Question 4', validators=[DataRequired()], choices=[
        ('A', 'Blue'),
        ('B', 'Green'),
        ('C', 'Red'),
        ('D', 'White')
    ])
    question_5 = RadioField('Question 5', validators=[DataRequired()], choices=[
        ('A', 'To save power'),
        ('B', 'To help passengers sleep'),
        ('C', 'To adjust eyes to darkness in case of emergency'),
        ('D', 'To improve Wi-Fi connection')
    ])
    submit = SubmitField('Submit Quiz')

class SearchFlightForm(FlaskForm):
    origin = StringField('From', validators=[DataRequired()])
    destination = StringField('To', validators=[DataRequired()])
    submit = SubmitField('Search Flights')

class BookingForm(FlaskForm):
    flight_id = HiddenField('Flight ID', validators=[DataRequired()])
    travel_class = SelectField('Travel Class', choices=[
        ('economy', 'Economy'),
        ('premium', 'Premium'),
        ('business', 'Business')
    ], validators=[DataRequired()])
    passenger_name = StringField('Passenger Name', validators=[DataRequired()])
    passenger_age = IntegerField('Passenger Age', validators=[DataRequired(), NumberRange(min=1, max=120)])
    passenger_gender = SelectField('Passenger Gender', choices=[
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    contact_number = StringField('Contact Number', validators=[DataRequired(), Length(min=10, max=15)])
    submit = SubmitField('Confirm Booking')

class AddMoneyForm(FlaskForm):
    amount = FloatField('Amount (₹)', validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Add to Wallet')

class AddFlightForm(FlaskForm):
    flight_number = StringField('Flight Number', validators=[DataRequired(), Length(min=2, max=10)])
    origin = StringField('Origin City', validators=[DataRequired(), Length(min=2, max=64)])
    destination = StringField('Destination City', validators=[DataRequired(), Length(min=2, max=64)])
    departure_date = StringField('Departure Date (YYYY-MM-DD)', validators=[DataRequired()])
    departure_time = StringField('Departure Time (HH:MM)', validators=[DataRequired()])
    arrival_date = StringField('Arrival Date (YYYY-MM-DD)', validators=[DataRequired()])
    arrival_time = StringField('Arrival Time (HH:MM)', validators=[DataRequired()])
    economy_price = FloatField('Economy Price (₹)', validators=[DataRequired(), NumberRange(min=1)])
    premium_price = FloatField('Premium Price (₹)', validators=[DataRequired(), NumberRange(min=1)])
    business_price = FloatField('Business Price (₹)', validators=[DataRequired(), NumberRange(min=1)])
    aircraft_type = StringField('Aircraft Type', validators=[DataRequired(), Length(min=2, max=50)])
    status = SelectField('Status', choices=[
        ('On Time', 'On Time'),
        ('Delayed', 'Delayed'),
        ('Cancelled', 'Cancelled'),
        ('Advanced', 'Advanced')
    ], validators=[DataRequired()])
    distance_km = IntegerField('Distance (km)', validators=[DataRequired(), NumberRange(min=1)])
    available_seats_economy = IntegerField('Economy Seats', validators=[DataRequired(), NumberRange(min=0)], default=100)
    available_seats_premium = IntegerField('Premium Seats', validators=[DataRequired(), NumberRange(min=0)], default=50)
    available_seats_business = IntegerField('Business Seats', validators=[DataRequired(), NumberRange(min=0)], default=20)
    submit = SubmitField('Add Flight')
