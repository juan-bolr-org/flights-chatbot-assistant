# Flights Chatbot Assistant

**Objective**: Provide an airline customer assistant platform where users can register, log in, search and book flights, manage and cancel bookings, and quickly get answers to common questions through a chatbot.

**User Stories**: [User Stories](./user-stories.md)

## 🚀 Project Overview

Flights Chatbot Assistant is a full-stack web application that combines modern web technologies with AI-powered assistance to provide a seamless flight booking experience. The platform features a React/Next.js frontend, FastAPI backend, and an intelligent chatbot powered by OpenAI's GPT models with LangGraph agents and LangChain tools for flight operations and FAQ knowledge base.

## 🏗️ Architecture

The project consists of two main components:

```
flights-chatbot-assistant/
├── frontend/          # Next.js React application
├── api/              # FastAPI backend service with integrated chatbot
├── chatbot/          # RAG knowledge base system
└── docker-compose.yml # Container orchestration
```

## 📊 Architecture & Flow Diagrams

Find all tecnical and flow diagrams in [`docs/diagrams`](docs/diagrams)

### Technology Stack

**Frontend:**
- **Framework**: Next.js 15.3.3 with React 19
- **Styling**: Tailwind CSS 4, Radix UI Themes
- **Form Management**: React Hook Form with Zod validation
- **Language**: TypeScript 5
- **Authentication**: JWT token-based with automatic refresh

**Backend:**
- **Framework**: FastAPI with Python 3.12
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: JWT with bcrypt password hashing and token refresh
- **AI Integration**: LangChain with OpenAI GPT-4.1 models
- **Agent Framework**: LangGraph with ReAct agents
- **Memory**: MemorySaver for conversation persistence
- **Vector Store**: In-memory vector store for FAQ retrieval

**AI & Knowledge Base:**
- **Agent Framework**: LangGraph with ReAct agents and tool calling
- **Knowledge Base**: RAG system with Jupyter notebook generation
- **Vector Store**: In-memory vector store with OpenAI embeddings
- **Binary Optimization**: Pickle serialization for knowledge base
- **Voice Processing**: Azure Cognitive Services Speech-to-Text
- **Memory Management**: SQLite chat history with MemorySaver checkpoints

**AI Chatbot:**
- **LLM**: OpenAI GPT-4.1 with temperature 0 for consistent responses
- **Agent Architecture**: LangGraph ReAct agents with tool calling
- **Tools**: Flight search, booking, cancellation, and FAQ retrieval
- **Memory**: Persistent conversation history per user session
- **Knowledge Base**: RAG-powered FAQ system with vector search for airline policies

## 🌟 Features

### User Management
- ✅ User registration with email validation
- ✅ Secure login with JWT authentication
- ✅ Password hashing with bcrypt
- ✅ Session management with automatic token refresh
- ✅ Token expiration warnings (5 minutes before expiry)
- ✅ Automatic session extension via popup interface

### Flight Operations
- ✅ Flight search by origin, destination, and date
- ✅ Real-time flight listing
- ✅ Flight booking system
- ✅ Booking management (view, cancel)
- ✅ Flight status tracking

### Booking System
- **Flight Booking**: One-click flight reservations with instant confirmation
- **Booking Management**: View, filter, and manage all user bookings
- **Advanced Filtering**: Filter bookings by status (booked/cancelled/completed), booking date, departure date
- **Booking Cancellation**: Cancel upcoming bookings with business rule validation
- **Booking History**: Complete travel history with pagination support

### AI-Powered Chatbot
- **Natural Language Processing**: Powered by OpenAI GPT models
- **Flight Assistant**: Search flights, make bookings, check reservations via chat
- **FAQ Integration**: RAG-powered knowledge base with vector search for contextual answers
- **Tool Integration**: Direct API access for booking operations
- **Conversation History**: Persistent chat history with user context
- **Multi-modal Input**: Text and voice input support
- **Knowledge Retrieval**: Semantic search through airline policies and product documentation

### Knowledge Base & RAG System
- **RAG Implementation**: Retrieval-Augmented Generation with vector search
- **Knowledge Generation**: Jupyter notebook-based knowledge base creation
- **Binary Optimization**: Pickle serialization for fast knowledge base loading
- **Vector Search**: OpenAI embeddings with semantic similarity matching
- **Auto-sync**: CI/CD pipeline generates and copies knowledge base during build
- **Fallback Support**: Hardcoded knowledge base when files unavailable

### Audio & Voice Features
- **Speech-to-Text**: Azure Cognitive Services integration
- **Audio Upload**: Support for WAV, MP3, M4A, WEBM formats
- **Real-time Processing**: Fast voice-to-text conversion in chat interface
- **Audio Transcription**: Automatic transcription with chat message integration

### Memory & State Management
- **Conversation Persistence**: SQLite-based chat history storage
- **User Context**: Per-user conversation memory with session isolation
- **Memory Checkpoints**: LangGraph MemorySaver for agent state persistence
- **Session Management**: Chat history retrieval and clearing capabilities

### Developer Experience
- **Comprehensive Testing**: 80%+ test coverage across all layers
- **API Documentation**: Interactive Swagger/OpenAPI documentation
- **Development Tools**: Helper scripts for environment management
- **Error Handling**: Structured error responses with detailed information
- **Logging**: Comprehensive logging with Azure Application Insights integration

#### Generating Coverage Report
To verify the test coverage percentage:

```bash
# Navigate to the API directory
cd api

# Run tests with coverage tracking
coverage run -m pytest tests

# Generate coverage report
coverage report

# Optional: Generate HTML coverage report
coverage html
```

## 🚀 Quick Start

### Prerequisites

- **Node.js** 24.0.2 or higher
- **Python** 3.12 or higher
- **Docker** and Docker Compose (optional)
- **OpenAI API Key**

#### Installing System Dependencies

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
```bash
# Using chocolatey
choco install ffmpeg

# Or download from https://ffmpeg.org/download.html
```

## 🛠️ Development Tools

### Helper Tool (Recommended)

The API includes a comprehensive helper tool that automates development tasks, manages virtual environments, dependencies, and environment variables.

**Unix-like systems (Linux, macOS):**
```bash
cd api
./helper
```

**Windows:**
```bash
cd api
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
cd api
./helper run          # Start the API server
./helper test         # Run tests
./helper install      # Install dependencies
./helper env          # Configure environment variables
./helper shell        # Open venv shell

# Windows
cd api
python helper run     # Start the API server
python helper test    # Run tests
python helper install # Install dependencies
python helper env     # Configure environment variables
python helper shell   # Open venv shell
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
# OpenAI Configuration (Required)
OPENAI_API_KEY=your_openai_api_key_here

# API Configuration
PORT=8000
SECRET_KEY=your_secret_key_here

# Azure Services (Optional)
APPINSIGHTS_CONNECTION_STRING=your_azure_insights_connection
AZURE_SPEECH_KEY=your_azure_speech_key
AZURE_SPEECH_REGION=your_azure_speech_region
AZURE_SPEECH_ENDPOINT=your_azure_speech_endpoint

# Frontend Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
API_URL=http://api:8000  # For Docker

# Database (Optional)
DATABASE_URL=sqlite:///./flights.db  # Default SQLite

# Logging (Optional)
LOG_LEVEL=INFO
```

### Setting Environment Variables

**Option 1: Using Helper Tool (Interactive)**
```bash
cd api
./helper env  # Interactive environment variable setup
```

**Option 2: Manual Setup**

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

### Knowledge Base Setup

Before using the chatbot, generate the knowledge base files:

```bash
# Navigate to chatbot directory
cd chatbot

# Install knowledge base requirements
pip install -r requirements.txt

# Generate knowledge base files using Jupyter notebook
jupyter notebook RAG.ipynb

# Execute all cells to create:
# - knowledge_base/airline_faqs.json
# - knowledge_base/product_docs.yaml
```

### Development Setup

#### Option 1: Using Helper Tool (Recommended for API)

```bash
# Clone the repository
git clone <repository-url>
cd flights-chatbot-assistant

# Setup and run API with helper
cd api
./helper run          # Automatically sets up environment and starts server

# Setup frontend (separate terminal)
cd frontend
npm install
npm run dev
```

#### Option 2: Docker Compose

```bash
# Clone the repository
git clone <repository-url>
cd flights-chatbot-assistant

# Start all services
docker-compose up --build

# Access the application
# Frontend: http://localhost:3000
# API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

#### Option 3: Manual Setup

**Backend Setup:**
```bash
cd api
pip install -r requirements.txt
cd src
uvicorn main:app --reload --port 8000
```

**Frontend Setup:**
```bash
cd frontend
npm install
npm run dev
```

### Production Deployment

The application is configured for deployment on Azure Web Apps with automated CI/CD pipelines:

- **Backend**: Deployed as a container on Azure Web App
- **Frontend**: Deployed as a container on Azure Web App
- **Registry**: Azure Container Registry (ACR)

## 📁 Project Structure

### Frontend (`/frontend`)

```
frontend/
├── app/                    # Next.js app directory
│   ├── (auth)/            # Authentication routes
│   │   ├── login/         # Login page
│   │   └── register/      # Registration and success pages
│   ├── flights/           # Flight listing page
│   ├── bookings/          # Bookings management page
│   └── layout.tsx         # Root layout with providers
├── components/            # Reusable UI components
│   ├── auth/             # Authentication components
│   │   ├── TokenManager.tsx      # Token monitoring and refresh
│   │   ├── TokenRefreshPopup.tsx # Session extension popup
│   │   └── TokenDebugInfo.tsx    # Development token info
│   ├── chat/             # Chat-related components
│   │   ├── ChatPanel.tsx  # Main chat interface
│   │   └── FloatingChatButton.tsx # Floating chat button
│   ├── flights/          # Flight display components
│   └── layout/           # Layout components (Header, Footer)
├── context/              # React context providers
├── lib/                  # Utility libraries
│   ├── api/             # API client functions
│   │   ├── auth.ts      # Authentication API calls
│   │   ├── booking.ts   # Booking API calls
│   │   ├── chat.ts      # Chat API calls
│   │   └── flights.ts   # Flights API calls
│   ├── hooks/           # Custom React hooks
│   │   └── useTokenExpiration.ts # Token monitoring hook
│   ├── types/           # TypeScript type definitions
│   └── utils/           # Helper functions
│       └── jwt.ts       # JWT parsing and validation
└── styles/              # Global CSS styles
```

### Backend (`/api`)

```
api/
├── src/
│   ├── routers/          # FastAPI route handlers
│   │   ├── users.py      # User authentication endpoints
│   │   ├── flights.py    # Flight management endpoints
│   │   ├── bookings.py   # Booking management endpoints
│   │   └── chat.py       # Chatbot interaction endpoints
│   ├── resources/        # Application resources and configuration
│   │   ├── app_resources.py # Resource management
│   │   ├── chat.py       # Chat manager and configuration
│   │   ├── dependencies.py # FastAPI dependencies
│   │   └── logging.py    # Logging configuration
│   ├── schemas/          # Pydantic models for request/response
│   ├── utils/            # Utility functions and tools
│   │   └── chatbot_tools.py # LangChain tools for flight operations and RAG retrieval
│   ├── models.py         # SQLAlchemy database models
│   ├── db.py             # Database configuration
│   └── main.py           # FastAPI application entry point
├── docs/                 # API documentation
│   └── token_refresh_endpoint.md # Token refresh endpoint docs
├── Dockerfile            # Container configuration
├── requirements.txt      # Python dependencies
└── README.md            # API documentation
```

### Knowledge Base (`/chatbot`)

```
chatbot/
├── RAG.ipynb              # Knowledge base generation notebook
├── knowledge_base/        # Generated knowledge base files
│   ├── airline_faqs.json  # FAQ entries (19 entries)
│   ├── product_docs.yaml  # Product docs (9 entries)
│   └── knowledge_base.pkl # Binary optimized knowledge base
├── requirements.txt       # Knowledge base dependencies
└── .ipynb_checkpoints/   # Jupyter notebook checkpoints
```

## 🛠️ API Endpoints

### Authentication
- `POST /users/register` - User registration
- `POST /users/login` - User login
- `POST /users/refresh` - Refresh JWT token (30-minute duration)
- `POST /users/logout` - User logout
- `GET /users/me` - Get current user information

### Flights
- `GET /flights/list` - List all available flights
- `GET /flights/search` - Search flights by criteria
- `POST /flights` - Create new flight (admin)

### Bookings
- `POST /bookings` - Book a flight
- `GET /bookings/user/{user_id}` - Get user bookings
- `PATCH /bookings/{booking_id}` - Update booking status
- `DELETE /bookings/{booking_id}` - Cancel booking

### Chatbot
- `POST /chat` - Send message to AI assistant (requires authentication)

### Health Check
- `GET /health` - Service health status

### Knowledge Base & Voice
- `POST /chat/voice` - Process voice messages with transcription
- `GET /chat/history` - Retrieve user chat history
- `DELETE /chat/history` - Clear user chat history

## 🔐 Authentication & Session Management

### Token System
- **Login/Register**: Returns 30-minute tokens for initial authentication
- **Token Refresh**: Returns new 30-minute tokens via `/users/refresh` endpoint
- **Automatic Monitoring**: Frontend checks token expiration every 30 seconds
- **Session Extension**: Popup appears 5 minutes before token expiry

### Security Features
- HTTP-only cookies for token storage (30-minute lifetime)
- Automatic token refresh without page reload
- Client-side token validation for UX (server-side validation for security)
- Secure logout with token cleanup
- Expired token automatic redirect to login

### Token Refresh Flow
1. User receives initial 30-minute token on login/register
2. Frontend monitors token expiration continuously (every 30 seconds)
3. Popup appears 5 minutes before expiry offering session extension
4. User can extend session (new 30-minute token) or dismiss popup
5. Automatic redirect to login if token expires without refresh

### Session Management Strategy
- **Short-lived tokens** (30 minutes) minimize security risk if compromised
- **Proactive refresh** via popup prevents session interruption
- **User choice** to extend or let session expire naturally
- **Seamless UX** with background monitoring and non-intrusive popups

## 🤖 AI Chatbot Implementation

The chatbot uses a sophisticated LangGraph ReAct agent architecture with specialized tools:

### Agent Architecture
1. **LangGraph ReAct Agent**: Reasoning and acting cycle for complex interactions
2. **Tool Integration**: Specialized tools for flight operations and FAQ retrieval
3. **Memory Management**: Persistent conversation history using MemorySaver
4. **Authentication**: User-specific sessions and tool access

### Available Tools
- **`search_flights`**: Search for flights by origin, destination, and date
- **`list_all_flights`**: List all available flights
- **`book_flight`**: Create flight bookings for users
- **`get_my_bookings`**: Retrieve user's current bookings
- **`cancel_booking`**: Cancel existing bookings
- **`flight_faqs`**: Vector-based search through RAG knowledge base for airline policies and procedures

### RAG Knowledge Base System
- **Document Generation**: Jupyter notebook-based creation of FAQ and product documentation
- **Vector Search**: Semantic similarity search using OpenAI embeddings
- **Contextual Retrieval**: Relevant information retrieval for query augmentation
- **Automatic Integration**: Knowledge base files automatically loaded by chatbot tools
- **Fallback Support**: Hardcoded FAQs as fallback if knowledge base files unavailable

### Knowledge Base Content:
- **Airline FAQs** (19 entries): Baggage policies, check-in procedures, booking changes, prohibited items, chatbot capabilities, booking management
- **Product Documentation** (9 entries): API documentation, booking management, authentication, system features, security, customer support

### Key Features:
- **Conversation Memory**: Maintains chat history per user session
- **Tool Calling**: Direct integration with flight booking system
- **Cost Optimization**: Efficient memory management and context handling
- **Error Handling**: Graceful handling of API failures and tool errors
- **Authentication**: Secure access requiring user login

## 🔧 Configuration

### Frontend Configuration

The frontend uses environment variables for API communication:

```typescript
// next.config.ts
const nextConfig: NextConfig = {
  env: {
    API_URL: process.env.API_URL || "http://localhost:3000",
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${process.env.API_URL}/:path*`,
      },
    ];
  },
};
```

### Backend Configuration

```python
# Chat Configuration
class ChatConfig(BaseModel):
    model_name: str = "openai:gpt-4.1"
    temperature: float = 0.0
    system_context: str = "You are a helpful flight booking assistant..."

# Database
DATABASE_URL = "sqlite:///./flights.db"

# JWT Authentication
SECRET_KEY = "your-secret-key"  # Change in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
```

## 📊 Knowledge Base Management

### Generating Knowledge Base

The chatbot uses a RAG system that requires knowledge base generation:

```bash
# Navigate to chatbot directory
cd chatbot

# Install dependencies
pip install -r requirements.txt

# Generate knowledge base using Jupyter
jupyter nbconvert --to notebook --execute RAG.ipynb --output RAG_executed.ipynb

# Verify files generated
ls -la knowledge_base/
# Expected output:
# - airline_faqs.json (FAQ entries)  
# - product_docs.yaml (Product documentation)
# - knowledge_base.pkl (Binary optimized version)
```

### CI/CD Knowledge Base Integration

The GitHub Actions workflow automatically generates and copies the knowledge base:

```yaml
# In .github/workflows/backend-api-ci.yml
- name: Generate and copy knowledge base
  run: |
    pip install jupyter nbconvert pyyaml
    cd chatbot
    jupyter nbconvert --to notebook --execute RAG.ipynb --output RAG_executed.ipynb
    cd ..
    mkdir -p api/chatbot/knowledge_base
    cp chatbot/knowledge_base/* api/chatbot/knowledge_base/
```

### Knowledge Base Content
- **Airline FAQs** (19 entries): Baggage policies, check-in procedures, booking management
- **Product Documentation** (9 entries): API features, booking system, authentication flows
- **Binary Optimization**: Pickle files for 10x faster loading in production

## 🚀 Deployment

### Azure Deployment

The project includes GitHub Actions workflows for automated deployment:

- **API**: `.github/workflows/flights-assistant-container-api.yml`
- **Frontend**: `.github/workflows/flights-assistant-frontend.yml`
- **Main**: `.github/workflows/main_flights-assistant.yml`

### Docker Configuration

Both frontend and backend include optimized Dockerfiles:

```dockerfile
# Frontend Dockerfile
FROM node:24.0.2-bookworm
# Environment variables set before build
ENV NODE_ENV=production
ENV PORT=3000
RUN npm run build
CMD ["npm", "start"]
```

```dockerfile
# Backend Dockerfile  
FROM python:3.12-slim
WORKDIR /api
RUN pip install -r requirements.txt
CMD uvicorn --app-dir src main:app --host 0.0.0.0 --port $PORT
```

### Docker Configuration

Updated docker-compose.yml with proper build contexts:

```yaml
version: '3.8'
services:
  api:
    build:
      context: ./api  # API-specific context
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - AZURE_SPEECH_KEY=${AZURE_SPEECH_KEY}
      - AZURE_SPEECH_REGION=${AZURE_SPEECH_REGION}
      # ... other environment variables

  front:
    build:
      context: ./frontend
    depends_on:
      - api
```

Knowledge base files are copied during CI/CD build process to ensure availability in containers.

## 🧪 Testing

Use the provided test script to verify API functionality:

```bash
# Run the test script
bash curls.sh
```

This script tests user registration, login, flight creation, and booking operations.

## 🔄 CI/CD Pipeline

### GitHub Actions Workflows

The project includes automated deployment workflows:

- **Backend API CI**: `.github/workflows/backend-api-ci.yml`
  - Runs tests and builds Docker images
  - Generates knowledge base during build
  - Copies knowledge base to API directory

- **Container API Deployment**: `.github/workflows/flights-assistant-container-api.yml`
  - Deploys API to Azure Web App
  - Uses Azure Container Registry

- **Frontend Deployment**: `.github/workflows/flights-assistant-frontend.yml`
  - Deploys frontend to Azure Web App
  - Environment-specific configuration

### Build Process

```bash
# Local build with knowledge base
cd chatbot
jupyter nbconvert --to notebook --execute RAG.ipynb --output RAG_executed.ipynb
cd ..

# Docker build (includes knowledge base copy)
docker-compose up --build
```

## 📚 Documentation

### API Documentation
- [Token Refresh Endpoint](./api/docs/token_refresh_endpoint.md) - Detailed endpoint documentation
- [API README](./api/README.md) - Backend API documentation

### Frontend Documentation
- [Token Refresh Popup Implementation](./frontend/docs/token-refresh-popup.md) - Frontend authentication features
- [Authentication Flow](./frontend/docs/authentication.md) - User authentication documentation

### Project Documentation
- [User Stories](./user-stories.md) - Project requirements and user stories
- [Chatbot Knowledge Base](./chatbot/README.md) - RAG system documentation

## 🧪 Advanced Testing

### API Testing Script

Use the comprehensive test script:

```bash
# Test full chat workflow
bash curls.sh

# Tests include:
# - User authentication with token
# - Chat message sending
# - Chat history retrieval  
# - Conversation memory
# - Chat history clearing
```

### Voice Feature Testing

```bash
# Test voice message endpoint
curl -X POST "http://localhost:8000/chat/voice" \
  -H "Authorization: Bearer $TOKEN" \
  -F "audio=@test_audio.wav"
```

### Knowledge Base Testing

```bash
# Test FAQ retrieval
curl -X POST "http://localhost:8000/chat" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content": "What is the baggage allowance?"}'
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is part of an educational assignment and is not intended for commercial use.

## 🆘 Support

For support and questions:
1. Review the user stories in [`user-stories.md`](./user-stories.md)
2. Examine the test scripts in [`curls.sh`](./curls.sh)
3. Check the documentation in respective `/docs` folders
