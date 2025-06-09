from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .routes import router, add_422_handler
from fastapi.responses import FileResponse
import os

app = FastAPI(title="FashionReps Scraper Web Config")

# Register global 422 handler for user-friendly validation errors
add_422_handler(app)

# Mount static files (frontend)
app.mount("/static", StaticFiles(directory="src/web_config/static"), name="static")

# Include API routes
app.include_router(router)

@app.get("/")
def root():
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    return FileResponse(os.path.join(static_dir, "index.html"))

@app.get("/health")
def health():
    return {"status": "ok"} 