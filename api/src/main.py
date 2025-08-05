from fastapi import FastAPI
from contextlib import asynccontextmanager
from routers import users_router, flights_router, bookings_router, chat_router, health_check_router
from resources.app_resources import app_resources


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        # Initialize all application resources (logging is initialized first inside)
        app_resources.initialize_all()
        
        # Now we can get the logger since logging is initialized
        logger = app_resources.logging.get_logger("main")
        logger.info("Starting Flights Chatbot Assistant API...")
        
        # Store reference for shutdown
        app.state.app_resources = app_resources
        logger.info("Application startup completed successfully")
        
        yield
        
        # Shutdown cleanup
        logger.info("Starting application shutdown...")
        app_resources.shutdown_all()
        logger.info("Application shutdown completed")
        
    except Exception as e:
        # If we can't get a logger, fall back to print
        try:
            logger = app_resources.logging.get_logger("main") if 'app_resources' in locals() else None
            if logger:
                logger.critical(f"Failed to start application: {e}", exc_info=True)
            else:
                print(f"CRITICAL: Failed to start application: {e}")
        except:
            print(f"CRITICAL: Failed to start application: {e}")
        raise

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
app.include_router(health_check_router)


@app.get("/")
async def root():
    return {"message": "Welcome to the Flights Chatbot Assistant API v2"}

if __name__ == "__main__":
    import uvicorn
    import os
    uvicorn.run(app, host="0.0.0", port=os.getenv("PORT", 8000), log_level="info")