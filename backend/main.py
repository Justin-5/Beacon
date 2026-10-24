import os
import logging

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .api.routes import router as api_router


# Ensure environment variables (API keys, etc.) are loaded
load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
log = logging.getLogger("beacon")


def create_app() -> FastAPI:
    app = FastAPI(
        title="Beacon Backend",
        description="FastAPI backend for the Beacon volunteer opportunity assistant.",
        version="0.2.0",
    )

    # A middleware (not an exception_handler) so the 500 still passes through
    # CORSMiddleware below and the browser can read the message.
    @app.middleware("http")
    async def unhandled_error(request: Request, call_next):
        try:
            return await call_next(request)
        except Exception:
            # Log the real error server-side; never leak internals to the client.
            log.exception("Unhandled error on %s %s", request.method, request.url.path)
            return JSONResponse(
                status_code=500,
                content={"detail": "Something went wrong on our side. Please try again."},
            )

    # Comma-separated list, e.g. "http://localhost:3000,https://beacon.example.com"
    app.add_middleware(
        CORSMiddleware,
        allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","),
        allow_methods=["*"],
        allow_headers=["*"],
    )

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
