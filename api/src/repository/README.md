# Repository Pattern Implementation

This document describes the implementation of the Repository Pattern in the Flights Chatbot Assistant API.

## Overview

The repository pattern has been implemented to separate data access logic from business logic in the API endpoints. This provides several benefits:

1. **Separation of Concerns**: Business logic is separated from data access logic
2. **Testability**: Easy to mock repositories for unit testing
3. **Maintainability**: Database operations are centralized and consistent
4. **Flexibility**: Easy to switch between different data storage implementations

## Structure

The repository module is located at `api/src/repository/` and contains:

```
repository/
├── __init__.py              # Module exports
├── user.py                  # User entity repository
├── flight.py                # Flight entity repository
├── booking.py               # Booking entity repository
└── chatbot_message.py       # ChatbotMessage entity repository
```

## Repository Pattern Components

Each repository file contains:

1. **DB Model Import**: The corresponding SQLAlchemy model
2. **Abstract Repository Class**: Defines the interface with abstract methods
3. **Concrete Repository Class**: SQLite implementation of the abstract class
4. **Dependency Injection Function**: Factory function for FastAPI dependency injection

### Example Structure (User Repository)

```python
# Abstract base class
class UserRepository(ABC):
    @abstractmethod
    def create(self, name: str, email: str, password_hash: str, phone: Optional[str] = None) -> User:
        pass
    
    @abstractmethod
    def find_by_email(self, email: str) -> Optional[User]:
        pass
    # ... more methods

# Concrete implementation
class UserSqliteRepository(UserRepository):
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, name: str, email: str, password_hash: str, phone: Optional[str] = None) -> User:
        # Implementation details
        pass
    
    def find_by_email(self, email: str) -> Optional[User]:
        # Implementation details
        pass
    # ... method implementations

# Dependency injection function
def create_user_repository(db: Session = Depends(get_database_session)) -> UserRepository:
    return UserSqliteRepository(db)
```

## Repository Methods by Entity

### UserRepository

- `create(name, email, password_hash, phone)` - Create a new user
- `find_by_email(email)` - Find user by email address
- `find_by_id(user_id)` - Find user by ID
- `update_token_expiration(user_id, expiration)` - Update user's token expiration
- `exists_by_email(email)` - Check if user exists with given email

### FlightRepository

- `create(origin, destination, departure_time, arrival_time, airline, price, status)` - Create a new flight
- `find_by_id(flight_id)` - Find flight by ID
- `search_flights(origin, destination, departure_date)` - Search flights by criteria
- `list_all()` - Get all flights
- `find_available_by_id(flight_id)` - Find available (scheduled) flight by ID

### BookingRepository

- `create(user_id, flight_id, status)` - Create a new booking
- `find_by_id(booking_id)` - Find booking by ID
- `find_existing_booking(user_id, flight_id)` - Find existing active booking
- `update_status(booking_id, status, cancelled_at)` - Update booking status
- `find_by_user_id(user_id, status_filter)` - Find user bookings with optional filter
- `delete_by_id(booking_id)` - Delete booking by ID

### ChatbotMessageRepository

- `create(user_id, message, response)` - Create a new chat message
- `find_by_user_id(user_id, limit, offset)` - Find user's chat messages with pagination
- `count_by_user_id(user_id)` - Count total chat messages for user
- `delete_by_user_id(user_id)` - Delete all chat messages for user

## Usage in Endpoints

### Before (Direct DB Access)

```python
@router.post("/register", response_model=Token)
def register(user: UserCreate, db: Session = Depends(get_database_session)):
    # Direct SQLAlchemy queries
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_user = User(name=user.name, email=user.email, ...)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
```

### After (Repository Pattern)

```python
@router.post("/register", response_model=Token)
def register(
    user: UserCreate, 
    user_repo: UserRepository = Depends(create_user_repository)
):
    # Clean, abstracted operations
    if user_repo.exists_by_email(user.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_user = user_repo.create(
        name=user.name,
        email=user.email,
        password_hash=hashed_password,
        phone=user.phone
    )
```

## Benefits Demonstrated

### 1. Cleaner Code

- Endpoints focus on business logic rather than database queries
- Consistent naming and interfaces across all repositories
- Reduced code duplication

### 2. Better Error Handling

- Repository methods can raise domain-specific exceptions
- Database errors are handled at the repository level
- Cleaner error propagation to endpoints

### 3. Easier Testing

- Mock repositories can be easily created for unit tests
- Business logic can be tested independently of database
- Integration tests can use test-specific repository implementations

### 4. Future-Proof Design

- Easy to switch from SQLite to PostgreSQL or other databases
- Repository implementations can be swapped without changing endpoints
- Caching layers can be added at the repository level

## Testing Example

```python
# Mock repository for testing
class MockUserRepository(UserRepository):
    def __init__(self):
        self.users = []
    
    def create(self, name: str, email: str, password_hash: str, phone: Optional[str] = None) -> User:
        user = User(id=len(self.users) + 1, name=name, email=email, ...)
        self.users.append(user)
        return user
    
    def find_by_email(self, email: str) -> Optional[User]:
        return next((u for u in self.users if u.email == email), None)

# Test endpoint with mock repository
def test_register_user():
    mock_repo = MockUserRepository()
    app.dependency_overrides[create_user_repository] = lambda: mock_repo
    
    response = client.post("/users/register", json={...})
    assert response.status_code == 200
```

## Migration Guide

To migrate existing code to use repositories:

1. **Identify Database Operations**: Look for `db.query()`, `db.add()`, `db.commit()` calls
2. **Extract to Repository Methods**: Move database logic to appropriate repository methods
3. **Update Endpoint Dependencies**: Replace `db: Session = Depends(get_database_session)` with repository dependencies
4. **Replace Direct Queries**: Use repository methods instead of direct SQLAlchemy queries
5. **Test**: Ensure all functionality works as expected

## Best Practices

1. **Keep Repositories Focused**: Each repository should only handle operations for its entity
2. **Use Abstract Base Classes**: Define clear interfaces for each repository
3. **Handle Errors Appropriately**: Let repositories handle database-specific errors
4. **Maintain Consistency**: Use consistent naming patterns across all repositories
5. **Document Methods**: Clearly document what each repository method does
6. **Transaction Management**: Handle database transactions within repository methods

## Future Enhancements

1. **Caching Layer**: Add Redis caching at the repository level
2. **Read/Write Separation**: Implement separate repositories for read and write operations
3. **Audit Logging**: Add audit trails for data modifications
4. **Bulk Operations**: Add methods for bulk insert/update operations
5. **Query Optimization**: Implement query optimization strategies within repositories
