from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .routes import router, add_422_handler

app = FastAPI(title="FashionReps Scraper Web Config")

# Register global 422 handler for user-friendly validation errors
add_422_handler(app)

# Mount static files (frontend)
app.mount("/static", StaticFiles(directory="src/web_config/static"), name="static")

# Include API routes
app.include_router(router)

@app.get("/health")
def health():
    return {"status": "ok"} 