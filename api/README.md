# Flights Chatbot Assistant API

This is the API for the Flights Chatbot Assistant project. It provides endpoints for user management, flight information, and chatbot interactions.

## Requirements

- Python 3.12 or higher

## How to run

- Install the required dependencies:

```bash
pip install -r requirements.txt
```

- Start the FastAPI server:

```bash
uvicorn --app-dir src main:app --reload --port YOUR_PORT
```

## Environment Variables

You need the following environment variables:

- OPENAI_API_KEY=your_openai_api_key

## Endpoints

| Method | Endpoint                           | Description                       |
|--------|------------------------------------|-----------------------------------|
| POST   | /users/register                    | Register a new user               |
| POST   | /users/login                       | User login                        |
| GET    | /flights/search                    | Search for flights                |
| GET    | /flights/list                      | List all flights                  |
| POST   | /flights                           | Create a new flight               |
| POST   | /bookings                          | Book a flight                     |
| GET    | /bookings/users/{userId}/bookings  | View user bookings                |
| PATCH  | /bookings/{bookingId}              | Update/cancel a booking           |
| DELETE | /bookings/{bookingId}              | Cancel a booking                  |
| POST   | /chat                              | Chatbot interaction (FAQs)        |
