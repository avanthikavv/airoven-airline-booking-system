import random
from datetime import datetime, timedelta
from flask import render_template, redirect, url_for, flash, request, session, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from app import db
from models import User, Flight, Booking
from forms import SignupForm, LoginForm, QuizForm, SearchFlightForm, BookingForm, AddMoneyForm

# Quiz questions
quiz_questions = [
    {
        'question': "Why are passengers required to switch electronic devices to airplane mode during a flight?",
        'options': ["A. To save battery", "B. To avoid interference with aircraft systems", "C. To reduce noise", "D. For entertainment purposes"],
        'correct': "B"
    },
    {
        'question': "What is the purpose of the safety card found in the seat pocket on an airplane?",
        'options': ["A. To advertise travel destinations", "B. To guide passengers on using in-flight entertainment", "C. To provide instructions during an emergency", "D. To offer discount coupons"],
        'correct': "C"
    },
    {
        'question': "When should a passenger wear a seatbelt during a flight?",
        'options': ["A. Only during takeoff", "B. Only when sleeping", "C. Only during turbulence", "D. During takeoff, landing, and whenever the seatbelt sign is on"],
        'correct': "D"
    },
    {
        'question': "What color are the emergency lights that guide passengers to exits during an evacuation?",
        'options': ["A. Blue", "B. Green", "C. Red", "D. White"],
        'correct': "B"
    },
    {
        'question': "Why are cabin lights dimmed during takeoff and landing at night?",
        'options': ["A. To save power", "B. To help passengers sleep", "C. To adjust eyes to darkness in case of emergency", "D. To improve Wi-Fi connection"],
        'correct': "C"
    }
]

# Function to populate database with initial flight data
def populate_flight_data():
    # Check if there are already flights in the database
    if Flight.query.count() > 0:
        return
    
    # List of cities for flight routes
    cities = [
        'Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Kolkata', 
        'Hyderabad', 'Ahmedabad', 'Pune', 'Jaipur', 'Lucknow',
        'London', 'New York', 'Paris', 'Tokyo', 'Dubai', 
        'Singapore', 'Sydney', 'Toronto', 'Berlin', 'Rome'
    ]
    
    # Aircraft types
    aircraft_types = [
        'Boeing 737-800', 'Airbus A320', 'Boeing 777-300ER', 
        'Airbus A330-200', 'Boeing 787-9 Dreamliner'
    ]
    
    # Status options
    status_options = ['On Time', 'Delayed', 'On Time', 'On Time', 'Advance']
    
    # Keep track of used flight numbers to avoid duplicates
    used_flight_numbers = set()
    
    # Create 50 flights
    for i in range(1, 51):
        # Select random origin and destination (ensuring they're different)
        origin = random.choice(cities)
        destination = random.choice([city for city in cities if city != origin])
        
        # Generate random departure time in the next 30 days
        days_ahead = random.randint(1, 30)
        hours = random.randint(0, 23)
        minutes = random.choice([0, 15, 30, 45])
        
        departure_time = datetime.now() + timedelta(days=days_ahead, hours=hours, minutes=minutes)
        
        # Flight duration between 1-12 hours depending on if it's domestic or international
        is_domestic = (origin in cities[:10] and destination in cities[:10])
        if is_domestic:
            flight_duration = random.randint(1, 4)  # 1-4 hours for domestic
            distance = random.randint(500, 2000)  # 500-2000 km
        else:
            flight_duration = random.randint(5, 12)  # 5-12 hours for international
            distance = random.randint(2500, 10000)  # 2500-10000 km
            
        arrival_time = departure_time + timedelta(hours=flight_duration)
        
        # Generate a unique flight number
        while True:
            flight_number = f"AO{random.randint(100, 999)}"
            if flight_number not in used_flight_numbers:
                used_flight_numbers.add(flight_number)
                break
        
        # Pricing (economy, premium, business)
        if is_domestic:
            economy_price = round(random.uniform(3000, 8000), 2)
        else:
            economy_price = round(random.uniform(20000, 80000), 2)
            
        premium_price = round(economy_price * 1.5, 2)
        business_price = round(economy_price * 3, 2)
        
        try:
            flight = Flight(
                flight_number=flight_number,
                origin=origin,
                destination=destination,
                departure_time=departure_time,
                arrival_time=arrival_time,
                status=random.choice(status_options),
                economy_price=economy_price,
                premium_price=premium_price,
                business_price=business_price,
                aircraft_type=random.choice(aircraft_types),
                distance_km=distance
            )
            
            db.session.add(flight)
        except Exception as e:
            print(f"Error adding flight {flight_number}: {str(e)}")
            db.session.rollback()
    
    try:
        db.session.commit()
        print("Successfully populated flight data")
    except Exception as e:
        print(f"Error committing flight data: {str(e)}")
        db.session.rollback()

def register_routes(app):
    # Initialize data when the app starts
    with app.app_context():
        populate_flight_data()
    
    @app.route('/')
    def index():
        if current_user.is_authenticated:
            # If user has not completed the quiz, redirect to quiz
            if not current_user.quiz_completed:
                return redirect(url_for('quiz'))
            return redirect(url_for('home'))
        return redirect(url_for('login'))
    
    @app.route('/signup', methods=['GET', 'POST'])
    def signup():
        if current_user.is_authenticated:
            return redirect(url_for('home'))
        
        form = SignupForm()
        if form.validate_on_submit():
            # Check if email already exists
            existing_user = User.query.filter_by(email=form.email.data).first()
            if existing_user:
                flash('Email already registered. Please log in instead.', 'danger')
                return redirect(url_for('login'))
            
            # Create new user
            user = User(
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                email=form.email.data,
                age=form.age.data,
                gender=form.gender.data,
                wallet_balance=0.0,
                quiz_completed=False
            )
            user.set_password(form.password.data)
            
            db.session.add(user)
            db.session.commit()
            
            flash('Account created successfully! Please sign in.', 'success')
            return redirect(url_for('login'))
        
        return render_template('signup.html', form=form)
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('home'))
        
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            
            if user and user.check_password(form.password.data):
                login_user(user)
                next_page = request.args.get('next')
                
                # If user has not completed the quiz, redirect to quiz
                if not user.quiz_completed:
                    return redirect(url_for('quiz'))
                
                flash('Logged in successfully!', 'success')
                return redirect(next_page or url_for('home'))
            else:
                flash('Invalid email or password. Please try again.', 'danger')
        
        return render_template('login.html', form=form)
    
    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash('You have been logged out.', 'info')
        return redirect(url_for('login'))
    
    @app.route('/quiz', methods=['GET', 'POST'])
    @login_required
    def quiz():
        # If user has already completed the quiz, redirect to home
        if current_user.quiz_completed:
            flash('You have already completed the quiz.', 'info')
            return redirect(url_for('home'))
        
        form = QuizForm()
        
        if form.validate_on_submit():
            # Calculate score
            score = 0
            if form.question_1.data == quiz_questions[0]['correct']: score += 1
            if form.question_2.data == quiz_questions[1]['correct']: score += 1
            if form.question_3.data == quiz_questions[2]['correct']: score += 1
            if form.question_4.data == quiz_questions[3]['correct']: score += 1
            if form.question_5.data == quiz_questions[4]['correct']: score += 1
            
            # Add bonus to wallet (Rs. 100 per correct answer)
            bonus_amount = score * 100
            current_user.add_to_wallet(bonus_amount)
            current_user.quiz_completed = True
            
            db.session.commit()
            
            # Show results
            flash(f'Quiz completed! You scored {score}/5 and earned ₹{bonus_amount} bonus in your wallet.', 'success')
            return redirect(url_for('home'))
        
        return render_template('quiz.html', form=form, questions=quiz_questions)
    
    @app.route('/home')
    @login_required
    def home():
        return render_template('home.html')
    
    @app.route('/flight_schedules')
    @login_required
    def flight_schedules():
        # Get all flights
        flights = Flight.query.all()
        
        # Create a JSON-serializable list of flight data
        serializable_flights = []
        for flight in flights:
            serializable_flights.append({
                'id': flight.id,
                'flight_number': flight.flight_number,
                'origin': flight.origin,
                'destination': flight.destination,
                'departure_time_str': flight.departure_time.strftime('%d-%b-%Y %H:%M'),
                'arrival_time_str': flight.arrival_time.strftime('%d-%b-%Y %H:%M'),
                'duration_hours': ((flight.arrival_time - flight.departure_time).total_seconds() / 3600),
                'status': flight.status,
                'economy_price': flight.economy_price,
                'premium_price': flight.premium_price,
                'business_price': flight.business_price,
                'aircraft_type': flight.aircraft_type
            })
        
        return render_template('flight_schedules.html', flights=flights, flight_data=serializable_flights)
    
    @app.route('/search_flights', methods=['GET', 'POST'])
    @login_required
    def search_flights():
        form = SearchFlightForm()
        
        if form.validate_on_submit():
            origin = form.origin.data
            destination = form.destination.data
            
            # Search for direct flights
            direct_flights = Flight.query.filter_by(origin=origin, destination=destination).all()
            
            # If direct flights are found
            if direct_flights:
                return render_template('search_flights.html', form=form, direct_flights=direct_flights, 
                                      origin=origin, destination=destination)
            
            # If no direct flights, find connecting flights
            connecting_flights = []
            
            # Find flights from origin to any city
            first_leg_flights = Flight.query.filter_by(origin=origin).all()
            
            for first_leg in first_leg_flights:
                # Find flights from the connection city to the destination
                connection_city = first_leg.destination
                second_leg_flights = Flight.query.filter_by(origin=connection_city, destination=destination).all()
                
                for second_leg in second_leg_flights:
                    # Ensure there's enough connection time (at least 2 hours)
                    if second_leg.departure_time > (first_leg.arrival_time + timedelta(hours=2)):
                        connecting_flights.append({
                            'first_leg': first_leg,
                            'second_leg': second_leg,
                            'total_duration': (second_leg.arrival_time - first_leg.departure_time).total_seconds() / 3600,
                            'connection_time': (second_leg.departure_time - first_leg.arrival_time).total_seconds() / 3600,
                            'total_price_economy': first_leg.economy_price + second_leg.economy_price,
                            'total_price_premium': first_leg.premium_price + second_leg.premium_price,
                            'total_price_business': first_leg.business_price + second_leg.business_price
                        })
            
            return render_template('search_flights.html', form=form, connecting_flights=connecting_flights,
                                  direct_flights=direct_flights, origin=origin, destination=destination)
        
        return render_template('search_flights.html', form=form)
    
    @app.route('/flight_details/<int:flight_id>')
    @login_required
    def flight_details(flight_id):
        flight = Flight.query.get_or_404(flight_id)
        return render_template('flight_details.html', flight=flight)
    
    @app.route('/book_flight/<int:flight_id>', methods=['GET', 'POST'])
    @login_required
    def book_flight(flight_id):
        flight = Flight.query.get_or_404(flight_id)
        form = BookingForm(flight_id=flight_id)
        
        if form.validate_on_submit():
            travel_class = form.travel_class.data
            
            # Get price based on travel class
            price = flight.get_price(travel_class)
            
            # Check if user has enough balance
            if current_user.wallet_balance < price:
                flash(f'Insufficient balance. You need ₹{price} to book this flight. Please add money to your wallet.', 'danger')
                return redirect(url_for('wallet'))
            
            # Check if seats are available
            if not flight.book_seat(travel_class):
                flash(f'No seats available in {travel_class.capitalize()} class.', 'danger')
                return redirect(url_for('flight_details', flight_id=flight_id))
            
            # Generate seat number
            seat_prefix = {'economy': 'E', 'premium': 'P', 'business': 'B'}
            seat_number = f"{seat_prefix[travel_class]}{random.randint(1, 50)}"
            
            # Create booking
            booking = Booking(
                user_id=current_user.id,
                flight_id=flight_id,
                travel_class=travel_class,
                seat_number=seat_number,
                price_paid=price,
                passenger_name=form.passenger_name.data,
                passenger_age=form.passenger_age.data,
                passenger_gender=form.passenger_gender.data,
                contact_number=form.contact_number.data,
                status="Confirmed"
            )
            
            # Deduct amount from wallet
            current_user.deduct_from_wallet(price)
            
            db.session.add(booking)
            db.session.commit()
            
            flash(f'Flight booked successfully! Your seat number is {seat_number}.', 'success')
            return redirect(url_for('home'))
        
        return render_template('booking.html', form=form, flight=flight)
    
    @app.route('/my_bookings')
    @login_required
    def my_bookings():
        bookings = Booking.query.filter_by(user_id=current_user.id).all()
        return render_template('my_bookings.html', bookings=bookings)
    
    @app.route('/cancel_booking/<int:booking_id>', methods=['POST'])
    @login_required
    def cancel_booking(booking_id):
        booking = Booking.query.get_or_404(booking_id)
        
        # Ensure the booking belongs to the current user
        if booking.user_id != current_user.id:
            flash('Unauthorized access.', 'danger')
            return redirect(url_for('my_bookings'))
        
        # Calculate refund amount (50% of the ticket price)
        refund_amount = booking.price_paid * 0.5
        
        # Add refund to wallet
        current_user.add_to_wallet(refund_amount)
        
        # Release the seat
        flight = Flight.query.get(booking.flight_id)
        flight.release_seat(booking.travel_class)
        
        # Delete the booking
        db.session.delete(booking)
        db.session.commit()
        
        flash(f'Booking cancelled successfully. ₹{refund_amount} has been refunded to your wallet.', 'success')
        return redirect(url_for('my_bookings'))
    
    @app.route('/wallet', methods=['GET', 'POST'])
    @login_required
    def wallet():
        form = AddMoneyForm()
        
        if request.method == 'POST':
            print(f"Form submitted: {request.form}")
            
            # Direct processing for preset amount buttons
            if 'preset_amount' in request.form:
                try:
                    amount = float(request.form['preset_amount'])
                    if amount > 0:
                        # Add amount to wallet
                        current_user.add_to_wallet(amount)
                        db.session.commit()
                        flash(f'₹{amount} added to your wallet successfully.', 'success')
                    else:
                        flash('Amount must be greater than 0.', 'danger')
                except (ValueError, TypeError):
                    flash('Invalid amount format.', 'danger')
                return redirect(url_for('wallet'))
            
            # Standard form processing
            if form.validate_on_submit():
                amount = form.amount.data
                print(f"Amount to be added: {amount}")
                
                # Add amount to wallet
                current_user.add_to_wallet(amount)
                db.session.commit()
                
                flash(f'₹{amount} added to your wallet successfully.', 'success')
                return redirect(url_for('wallet'))
            else:
                print(f"Form validation failed: {form.errors}")
        
        return render_template('wallet.html', form=form)
    
    @app.route('/get_flight_path/<int:flight_id>')
    @login_required
    def get_flight_path(flight_id):
        flight = Flight.query.get_or_404(flight_id)
        
        # This is a simplified version - in a real application, you would use a geocoding API
        # to get actual coordinates for origin and destination cities
        # For now, we'll use a static mapping for demonstration
        city_coords = {
            'Mumbai': [19.0760, 72.8777],
            'Delhi': [28.7041, 77.1025],
            'Bangalore': [12.9716, 77.5946],
            'Chennai': [13.0827, 80.2707],
            'Kolkata': [22.5726, 88.3639],
            'Hyderabad': [17.3850, 78.4867],
            'Ahmedabad': [23.0225, 72.5714],
            'Pune': [18.5204, 73.8567],
            'Jaipur': [26.9124, 75.7873],
            'Lucknow': [26.8467, 80.9462],
            'London': [51.5074, -0.1278],
            'New York': [40.7128, -74.0060],
            'Paris': [48.8566, 2.3522],
            'Tokyo': [35.6762, 139.6503],
            'Dubai': [25.2048, 55.2708],
            'Singapore': [1.3521, 103.8198],
            'Sydney': [-33.8688, 151.2093],
            'Toronto': [43.6532, -79.3832],
            'Berlin': [52.5200, 13.4050],
            'Rome': [41.9028, 12.4964]
        }
        
        # Default coordinates if city not found
        origin_coords = city_coords.get(flight.origin, [0, 0])
        dest_coords = city_coords.get(flight.destination, [0, 0])
        
        flight_data = {
            'origin': {
                'name': flight.origin,
                'coords': origin_coords
            },
            'destination': {
                'name': flight.destination,
                'coords': dest_coords
            },
            'flight_number': flight.flight_number,
            'distance_km': flight.distance_km,
            'duration_hours': (flight.arrival_time - flight.departure_time).total_seconds() / 3600
        }
        
        return jsonify(flight_data)
    
    @app.route('/get_connecting_flight_path/<int:first_leg_id>/<int:second_leg_id>')
    @login_required
    def get_connecting_flight_path(first_leg_id, second_leg_id):
        first_leg = Flight.query.get_or_404(first_leg_id)
        second_leg = Flight.query.get_or_404(second_leg_id)
        
        # City coordinates mapping (simplified version)
        city_coords = {
            'Mumbai': [19.0760, 72.8777],
            'Delhi': [28.7041, 77.1025],
            'Bangalore': [12.9716, 77.5946],
            'Chennai': [13.0827, 80.2707],
            'Kolkata': [22.5726, 88.3639],
            'Hyderabad': [17.3850, 78.4867],
            'Ahmedabad': [23.0225, 72.5714],
            'Pune': [18.5204, 73.8567],
            'Jaipur': [26.9124, 75.7873],
            'Lucknow': [26.8467, 80.9462],
            'London': [51.5074, -0.1278],
            'New York': [40.7128, -74.0060],
            'Paris': [48.8566, 2.3522],
            'Tokyo': [35.6762, 139.6503],
            'Dubai': [25.2048, 55.2708],
            'Singapore': [1.3521, 103.8198],
            'Sydney': [-33.8688, 151.2093],
            'Toronto': [43.6532, -79.3832],
            'Berlin': [52.5200, 13.4050],
            'Rome': [41.9028, 12.4964]
        }
        
        # Get coordinates for all three cities
        origin_coords = city_coords.get(first_leg.origin, [0, 0])
        connection_coords = city_coords.get(first_leg.destination, [0, 0])
        destination_coords = city_coords.get(second_leg.destination, [0, 0])
        
        connection_data = {
            'origin': {
                'name': first_leg.origin,
                'coords': origin_coords
            },
            'connection': {
                'name': first_leg.destination,
                'coords': connection_coords
            },
            'destination': {
                'name': second_leg.destination,
                'coords': destination_coords
            },
            'first_leg': {
                'flight_number': first_leg.flight_number,
                'distance_km': first_leg.distance_km,
                'duration_hours': (first_leg.arrival_time - first_leg.departure_time).total_seconds() / 3600
            },
            'second_leg': {
                'flight_number': second_leg.flight_number,
                'distance_km': second_leg.distance_km,
                'duration_hours': (second_leg.arrival_time - second_leg.departure_time).total_seconds() / 3600
            },
            'connection_time_hours': (second_leg.departure_time - first_leg.arrival_time).total_seconds() / 3600
        }
        
        return jsonify(connection_data)
