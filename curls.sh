# Shell script to test the flight booking API
set -e

# Register user1
curl -X POST "http://localhost:8000/users/register" \
  -H "Content-Type: application/json" \
  -d '{"name": "Alice", "email": "alice1@example.com", "password": "alicepass", "phone": "1234567890"}'

# Register user2
curl -X POST "http://localhost:8000/users/register" \
  -H "Content-Type: application/json" \
  -d '{"name": "Bob", "email": "bob1@example.com", "password": "bobpass", "phone": "0987654321"}'

# Login as user1 and store token
export TOKEN1=$(curl -s -X POST "http://localhost:8000/users/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "alice1@example.com", "password": "alicepass"}' | jq -r .token.access_token)
echo "User1 token: $TOKEN1"

# Login as user2 and store token
export TOKEN2=$(curl -s -X POST "http://localhost:8000/users/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "bob1@example.com", "password": "bobpass"}' | jq -r .token.access_token)
echo "User2 token: $TOKEN2"

# Create random flights (as user1)
curl -X POST "http://localhost:8000/flights" \
  -H "Authorization: Bearer $TOKEN1" \
  -H "Content-Type: application/json" \
  -d '{"origin": "NYC", "destination": "LAX", "departure_time": "2024-12-01T08:00:00", "arrival_time": "2024-12-01T11:00:00", "airline": "AirTest"}'
curl -X POST "http://localhost:8000/flights" \
  -H "Authorization: Bearer $TOKEN1" \
  -H "Content-Type: application/json" \
  -d '{"origin": "NYC", "destination": "LAX", "departure_time": "2024-12-01T15:00:00", "arrival_time": "2024-12-01T18:00:00", "airline": "JetMock"}'
curl -X POST "http://localhost:8000/flights" \
  -H "Authorization: Bearer $TOKEN1" \
  -H "Content-Type: application/json" \
  -d '{"origin": "NYC", "destination": "SFO", "departure_time": "2024-12-01T09:00:00", "arrival_time": "2024-12-01T12:00:00", "airline": "FlyDemo"}'

# Optionally, create a booking for user2 (flight id 2)
export BOOKING2_ID=$(curl -s -X POST "http://localhost:8000/bookings" \
  -H "Authorization: Bearer $TOKEN2" \
  -H "Content-Type: application/json" \
  -d '{"flight_id": 2}' | jq -r .id)
echo "User2 Booking ID: $BOOKING2_ID"

# Search for flights (as user1)
curl -X GET "http://localhost:8000/flights/search?origin=NYC&destination=LAX&departure_date=2024-12-01" \
  -H "Authorization: Bearer $TOKEN1"

# Book a flight (as user1, assuming flight id 1)
export BOOKING_ID=$(curl -s -X POST "http://localhost:8000/bookings" \
  -H "Authorization: Bearer $TOKEN1" \
  -H "Content-Type: application/json" \
  -d '{"flight_id": 1}' | jq -r .id)
echo "Booking ID: $BOOKING_ID"

# View user1 bookings
curl -X GET "http://localhost:8000/bookings/user/1" \
  -H "Authorization: Bearer $TOKEN1"

# Cancel the booking (as user1)
curl -X PATCH "http://localhost:8000/bookings/$BOOKING_ID" \
  -H "Authorization: Bearer $TOKEN1" \
  -H "Content-Type: application/json" \
  -d '{"status": "cancelled"}'
