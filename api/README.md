# Flights Chatbot Assistant API

This is the API for the Flights Chatbot Assistant project. It provides endpoints for user management, flight information, and chatbot interactions.

## Requirements

- Python 3.12 or higher
- ffmpeg (required for audio processing in speech-to-text feature)

### Installing System Dependencies

**Ubuntu/Debian:**

```bash
sudo apt update
sudo apt install ffmpeg
```

**macOS:**

```bash
brew install ffmpeg
```

**Windows:**

Download from <https://ffmpeg.org/download.html> or use chocolatey:

```cmd
choco install ffmpeg
```

## Quick Start with Helper Tool

This project includes a comprehensive helper tool that automates development tasks. The helper automatically manages virtual environments, dependencies, and environment variables.

### Using the Helper

**Unix-like systems (Linux, macOS):**

```bash
./helper
```

**Windows:**

```bash
python helper
```

### Helper Features

The helper provides an interactive menu with the following options:

- **Run API server** - Starts the FastAPI development server with configured environment variables
- **Run tests** - Executes the test suite
- **Install/Check dependencies** - Automatically installs missing dependencies
- **Configure environment variables** - Interactive environment variable management
- **Open shell in virtual environment** - Opens a shell with the project environment activated
- **Create/recreate virtual environment** - Sets up a fresh virtual environment

### Helper Commands

You can also run specific commands directly:

```bash
# Unix-like systems
./helper run          # Start the API server
./helper test         # Run tests
./helper install      # Install dependencies
./helper env          # Configure environment variables
./helper shell        # Open venv shell

# Windows
python helper run     # Start the API server
python helper test    # Run tests
python helper install # Install dependencies
python helper env     # Configure environment variables
python helper shell   # Open venv shell
```

## Manual Setup (Alternative)

If you prefer to set up the project manually without using the helper:

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Start the Server

```bash
uvicorn --app-dir src main:app --reload --port YOUR_PORT
```

## Environment Variables

The following environment variables are required or recommended:

### Required

- **OPENAI_API_KEY** - Your OpenAI API key for chatbot functionality

### Optional

- **PORT** - Server port (default: 8000)
- **SECRET_KEY** - JWT secret key for authentication
- **APPINSIGHTS_CONNECTION_STRING** - Azure Application Insights connection string
- **LOG_LEVEL** - Logging level (default: INFO)
- **DATABASE_URL** - Database connection URL (default: sqlite:///./flights.db)

### Setting Environment Variables

The helper tool provides an interactive way to manage environment variables, or you can set them manually:

**Unix-like systems:**

```bash
export OPENAI_API_KEY="your_openai_api_key"
export SECRET_KEY="your_secret_key"
```

**Windows:**

```cmd
set OPENAI_API_KEY=your_openai_api_key
set SECRET_KEY=your_secret_key
```

## Endpoints

| Method | Endpoint                           | Description                       |
|--------|------------------------------------|-----------------------------------|
| POST   | /users/register                    | Register a new user               |
| POST   | /users/login                       | User login                        |
| GET    | /users/me                          | Get current user information      |
| POST   | /users/refresh                     | Refresh JWT token (30 min)        |
| POST   | /users/logout                      | User logout                       |
| GET    | /flights/search                    | Search for flights                |
| GET    | /flights/list                      | List all flights                  |
| POST   | /flights                           | Create a new flight               |
| POST   | /bookings                          | Book a flight                     |
| GET    | /bookings/user                     | View user bookings (with filters) |
| PATCH  | /bookings/{bookingId}              | Update/cancel a booking           |
| DELETE | /bookings/{bookingId}              | Cancel a booking                  |
| POST   | /chat                              | Chatbot interaction (FAQs)        |
| GET    | /chat/history                      | Get chat history                  |
| DELETE | /chat/history                      | Clear chat history                |
| POST   | /speech/transcribe                 | Speech-to-text transcription      |
