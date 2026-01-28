import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.routes import router as api_router


# Ensure environment variables (API keys, etc.) are loaded
load_dotenv()


def create_app() -> FastAPI:
    app = FastAPI(
        title="Beacon Backend",
        description="FastAPI backend for the Beacon volunteer opportunity assistant.",
        version="0.1.0",
    )

    # CORS configuration — allow all origins for now
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Mount API routes
    app.include_router(api_router, prefix="/api")

    return app


app = create_app()


if __name__ == "__main__":
    # Local development entrypoint
    import uvicorn

    uvicorn.run(
        "backend.main:app",
        host=os.getenv("BEACON_HOST", "0.0.0.0"),
        port=int(os.getenv("BEACON_PORT", "8000")),
        reload=True,
    )

