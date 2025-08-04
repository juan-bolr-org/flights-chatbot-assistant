from sqlalchemy.orm import Session
from models import User, Flight, Booking
from .crypto import crypto_manager
from faker import Faker
import random
import datetime
from sqlalchemy.exc import IntegrityError
from typing import List, TYPE_CHECKING
from pydantic import BaseModel, Field
from .logging import get_logger

if TYPE_CHECKING:
    from .database import DatabaseManager

logger = get_logger("seed_data")


class SeedDataConfig(BaseModel):
    """Configuration for database seeding."""
    num_fake_users: int = Field(default=10, ge=1, le=100, description="Number of fake users to create")
    num_fake_flights: int = Field(default=20, ge=1, le=200, description="Number of fake flights to create")
    num_fake_bookings: int = Field(default=30, ge=1, le=300, description="Number of fake bookings to create")
    default_password: str = Field(default="password123", description="Default password for fake users")
    create_default_user: bool = Field(default=True, description="Create default test user")
    default_user_email: str = Field(default="default@default.com", description="Default user email")
    default_user_phone: str = Field(default="000-000-0000", description="Default user phone")


class DataSeeder:
    """Handles database seeding operations."""
    
    def __init__(self, db_manager: "DatabaseManager", config: SeedDataConfig = None) -> None:
        self.db_manager: "DatabaseManager" = db_manager
        self.config: SeedDataConfig = config or SeedDataConfig()
        self.fake: Faker = Faker()
    
    def create_default_user(self, db: Session) -> User:
        """Create a default user for testing purposes."""
        user = User(
            name=self.config.default_user_email,
            email=self.config.default_user_email,
            password_hash=crypto_manager.get_password_hash(self.config.default_user_email),
            phone=self.config.default_user_phone
        )
        db.add(user)
        try:
            db.commit()
            db.refresh(user)
        except IntegrityError:
            db.rollback()
            user = db.query(User).filter_by(email=self.config.default_user_email).first()
        return user
    
    def create_fake_users(self, db: Session, n: int = None) -> List[User]:
        """Create fake users for testing."""
        if n is None:
            n = self.config.num_fake_users
        users: List[User] = []
        for _ in range(n):
            user = User(
                name=self.fake.name(),
                email=self.fake.unique.email(),
                password_hash=crypto_manager.get_password_hash(self.config.default_password),
                phone=self.fake.phone_number()
            )
            db.add(user)
            users.append(user)
        db.commit()
        for user in users:
            db.refresh(user)
        return users
    
    def create_fake_flights(self, db: Session, n: int = None) -> List[Flight]:
        """Create fake flights for testing."""
        if n is None:
            n = self.config.num_fake_flights
        flights: List[Flight] = []
        for _ in range(n):
            origin = self.fake.city()[:3].upper()
            destination = self.fake.city()[:3].upper()
            while destination == origin:
                destination = self.fake.city()[:3].upper()
            
            departure = self.fake.date_time_between(start_date="+1d", end_date="+30d")
            arrival = departure + datetime.timedelta(hours=random.randint(2, 12))
            
            flight = Flight(
                origin=origin,
                destination=destination,
                departure_time=departure,
                arrival_time=arrival,
                airline=self.fake.company(),
                status="scheduled",
                price=random.uniform(100, 1000)
            )
            db.add(flight)
            flights.append(flight)
        db.commit()
        for flight in flights:
            db.refresh(flight)
        return flights
    
    def create_fake_bookings(self, db: Session, users: List[User], flights: List[Flight], n: int = None) -> None:
        """Create fake bookings for testing."""
        if n is None:
            n = self.config.num_fake_bookings
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
    
    def seed_all(self) -> None:
        """Seed the database with all test data."""
        db = self.db_manager.get_session()
        try:
            logger.info("Starting database seeding...")
            
            # Create default user first
            if self.config.create_default_user:
                logger.debug("Creating default user...")
                self.create_default_user(db)
            
            # Create fake data
            logger.debug(f"Creating {self.config.num_fake_users} fake users...")
            users = self.create_fake_users(db)
            
            logger.debug(f"Creating {self.config.num_fake_flights} fake flights...")
            flights = self.create_fake_flights(db)
            
            logger.debug(f"Creating {self.config.num_fake_bookings} fake bookings...")
            self.create_fake_bookings(db, users, flights)
            
            # Log results
            if self.config.create_default_user:
                logger.info("Created default user")
            logger.info(f"Created {len(users)} fake users")
            logger.info(f"Created {len(flights)} fake flights")
            logger.info("Created fake bookings")
            logger.info("Database seeding completed successfully")
            
        except Exception as e:
            logger.error(f"Error during database seeding: {e}", exc_info=True)
            raise
        finally:
            db.close()
