from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import declarative_base, relationship
import datetime

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc))
    token_expiration = Column(DateTime, nullable=True)
    bookings = relationship('Booking', back_populates='user')
    chatbot_messages = relationship('ChatbotMessage', back_populates='user')
    chat_sessions = relationship('ChatSession', back_populates='user')


class Flight(Base):
    __tablename__ = 'flights'
    id = Column(Integer, primary_key=True, index=True)
    origin = Column(String, nullable=False)
    destination = Column(String, nullable=False)
    departure_time = Column(DateTime, nullable=False)
    arrival_time = Column(DateTime, nullable=False)
    airline = Column(String, nullable=False)
    status = Column(String, default='scheduled')
    bookings = relationship('Booking', back_populates='flight')
    price = Column(Integer, nullable=False)


class Booking(Base):
    __tablename__ = 'bookings'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    flight_id = Column(Integer, ForeignKey('flights.id'), nullable=False)
    status = Column(String, default='booked')  # booked, cancelled
    booked_at = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc))
    cancelled_at = Column(DateTime, nullable=True)
    user = relationship('User', back_populates='bookings')
    flight = relationship('Flight', back_populates='bookings')


class ChatSession(Base):
    __tablename__ = 'chat_sessions'
    id = Column(String, primary_key=True, index=True)  # This will be the session_id
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    alias = Column(String, nullable=False)  # User-friendly name
    created_at = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc))
    updated_at = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc), onupdate=datetime.datetime.now(datetime.timezone.utc))
    user = relationship('User', back_populates='chat_sessions')
    messages = relationship('ChatbotMessage', back_populates='session')


class ChatbotMessage(Base):
    __tablename__ = 'chatbot_messages'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    session_id = Column(String, ForeignKey('chat_sessions.id'), nullable=False)
    user_message = Column(Text, nullable=False)
    bot_response = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc))
    user = relationship('User', back_populates='chatbot_messages')
    session = relationship('ChatSession', back_populates='messages')
