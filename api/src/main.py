from fastapi import FastAPI
from contextlib import asynccontextmanager
from db import init_db
from routers import users_router, flights_router, bookings_router, chat_router
from utils import init_data
from routers.chat import init_chat


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    init_data()
    init_chat()
    yield

app = FastAPI(
    title="Flights Chatbot Assistant API",
    description="An airline customer assistant platform where users can register, log in, search and book flights, manage and cancel bookings.",
    version="1.0.0",
    lifespan=lifespan
)

# Include routers
app.include_router(users_router)
app.include_router(flights_router)
app.include_router(bookings_router)
app.include_router(chat_router)

@app.get("/")
async def root():
    return {"message": "Welcome to the Flights Chatbot Assistant API"}