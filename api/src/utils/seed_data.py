from sqlalchemy.orm import Session
from db import SessionLocal, init_db
from models import User, Flight, Booking
from utils import get_password_hash

def create_fake_users(db, fake, n=10):
    users = []
    for _ in range(n):
        user = User(
            name=fake.name(),
            email=fake.unique.email(),
            password_hash=get_password_hash("password123"),
            phone=fake.phone_number()
        )
        db.add(user)
        users.append(user)
    db.commit()
    for user in users:
        db.refresh(user)
    return users

def create_fake_flights(db, fake, n=20):
    import random, datetime
    flights = []
    for _ in range(n):
        origin = fake.city()[:3].upper()
        destination = fake.city()[:3].upper()
        while destination == origin:
            destination = fake.city()[:3].upper()
        departure = fake.date_time_between(start_date="+1d", end_date="+30d")
        arrival = departure + datetime.timedelta(hours=random.randint(2, 12))
        flight = Flight(
            origin=origin,
            destination=destination,
            departure_time=departure,
            arrival_time=arrival,
            airline=fake.company(),
            status="scheduled",
            price=random.uniform(100, 1000)
        )
        db.add(flight)
        flights.append(flight)
    db.commit()
    for flight in flights:
        db.refresh(flight)
    return flights

def create_fake_bookings(db, users, flights, n=30):
    import random
    for _ in range(n):
        user = random.choice(users)
        flight = random.choice(flights)
        exists = db.query(Booking).filter_by(user_id=user.id, flight_id=flight.id).first()
        if not exists:
            booking = Booking(
                user_id=user.id,
                flight_id=flight.id,
                status="booked"
            )
            db.add(booking)
    db.commit()

def create_default_user(db):
    from sqlalchemy.exc import IntegrityError
    user = User(
        name="default@default.com",
        email="default@default.com",
        password_hash=get_password_hash("default@default.com"),
        phone="000-000-0000"
    )
    db.add(user)
    try:
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        user = db.query(User).filter_by(email="default@default.com").first()
    return user

def init_data():
    from faker import Faker
    fake = Faker()
    db: Session = SessionLocal()
    try:
        create_default_user(db)
        users = create_fake_users(db, fake, 10)
        flights = create_fake_flights(db, fake, 20)
        create_fake_bookings(db, users, flights, 30)
    finally:
        db.close()