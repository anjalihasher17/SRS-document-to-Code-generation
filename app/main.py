import os
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="SRS to FastAPI Generator",
    description="A system that takes SRS documents as input and generates FastAPI projects",
    version="1.0.0",
    docs_url="/swagger",
    openapi_url="/openapi.json"
)

# Import routers
from api.routes import srs

# Register routers
app.include_router(srs.router, prefix="/api", tags=["SRS Processing"])

# Startup event
@app.on_event("startup")
async def startup_event():
    # Initialize database connection
    from app.services.database import init_db
    await init_db()
    
    # Initialize LangSmith logging if configured
    if os.getenv("LANGCHAIN_API_KEY"):
        import langsmith
        langsmith.setup_tracing(
            project_name=os.getenv("LANGCHAIN_PROJECT", "srs-to-fastapi")
        )


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    # Close database connection
    from app.services.database import close_db
    await close_db()

# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "Welcome to SRS to FastAPI Generator API",
        "docs": "/docs",
        "version": app.version,
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)