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
└── docker-compose.yml # Container orchestration
```

### Technology Stack

**Frontend:**
- **Framework**: Next.js 15.3.3 with React 19
- **Styling**: Tailwind CSS 4, Radix UI Themes
- **Form Management**: React Hook Form with Zod validation
- **Language**: TypeScript 5
- **Authentication**: JWT token-based authentication

**Backend:**
- **Framework**: FastAPI with Python 3.12
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: JWT with bcrypt password hashing
- **AI Integration**: LangChain with OpenAI GPT-4.1 models
- **Agent Framework**: LangGraph with ReAct agents
- **Memory**: MemorySaver for conversation persistence
- **Vector Store**: In-memory vector store for FAQ retrieval

**AI Chatbot:**
- **LLM**: OpenAI GPT-4.1 with temperature 0 for consistent responses
- **Agent Architecture**: LangGraph ReAct agents with tool calling
- **Tools**: Flight search, booking, cancellation, and FAQ retrieval
- **Memory**: Persistent conversation history per user session
- **Knowledge Base**: Embedded FAQ system for airline policies

## 🌟 Features

### User Management
- ✅ User registration with email validation
- ✅ Secure login with JWT authentication
- ✅ Password hashing with bcrypt
- ✅ Session management

### Flight Operations
- ✅ Flight search by origin, destination, and date
- ✅ Real-time flight listing
- ✅ Flight booking system
- ✅ Booking management (view, cancel)
- ✅ Flight status tracking

### AI-Powered Chatbot
- ✅ LangGraph ReAct agent with tool calling capabilities
- ✅ Flight search and booking through conversation
- ✅ Booking management and cancellation via chat
- ✅ FAQ retrieval for airline policies and procedures
- ✅ Authentication-required chat access
- ✅ Persistent conversation memory per user
- ✅ Floating chat interface with message counter

### UI/UX Features
- ✅ Responsive design with modern UI components
- ✅ Dark theme with gradient animations
- ✅ Real-time chat interface
- ✅ Flight cards with detailed information
- ✅ User-friendly navigation and forms

## 🚀 Quick Start

### Prerequisites

- **Node.js** 24.0.2 or higher
- **Python** 3.12 or higher
- **Docker** and Docker Compose (optional)
- **OpenAI API Key**

### Environment Variables

Create a `.env` file in the root directory:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# API Configuration (for Docker)
API_URL=http://api:8000

# Frontend Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
PORT=3000
```

### Development Setup

#### Option 1: Docker Compose (Recommended)

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

#### Option 2: Manual Setup

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
│   └── layout.tsx         # Root layout with providers
├── components/            # Reusable UI components
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
│   ├── types/           # TypeScript type definitions
│   └── utils/           # Helper functions
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
│   │   └── chatbot_tools.py # LangChain tools for flight operations
│   ├── models.py         # SQLAlchemy database models
│   ├── db.py             # Database configuration
│   └── main.py           # FastAPI application entry point
├── Dockerfile            # Container configuration
├── requirements.txt      # Python dependencies
└── README.md            # API documentation
```

## 🛠️ API Endpoints

### Authentication
- `POST /users/register` - User registration
- `POST /users/login` - User login

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
- **`flight_faqs`**: Search FAQ knowledge base for airline policies

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

## 🧪 Testing

Use the provided test script to verify API functionality:

```bash
# Run the test script
bash curls.sh
```

This script tests user registration, login, flight creation, and booking operations.

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
