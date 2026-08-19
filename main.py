from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from mjt.client import mjt_client
from mjt.router import router as mjt_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Pre-fetch tokens at startup
    try:
        await mjt_client.refresh_tokens()
    except Exception as e:
        print(f"Warning: Failed to pre-fetch MJT tokens on startup: {e}")
    yield
    # Cleanup client on shutdown
    await mjt_client.close()


API_DESCRIPTION = """
## 🚆 Transport for Greater Bandung (TfGB) API

Unified RESTful API service providing public transit data, bus tracking, and route schedules across Greater Bandung.
"""

TAGS_METADATA = [
    {
        "name": "MJT",
        "description": """
### 🚌 Overview
**MJT PIS API** is a high-performance RESTful API wrapper for the **MJT Passenger Information System (PIS)** and transit tracking services.

Source upstream: [mjt.trans.my.id](https://mjt.trans.my.id)

---

### 🔑 Features & Session Management
- **On-Demand Auto-Refresh**: Tokens are automatically renewed when expired upon incoming bus or route requests.
- **Dynamic TTL & Caching**: Token requests are cached in-memory based on upstream `pisNonceTtl` without superfluous upstream traffic.
- **CORS Enabled**: Ready out-of-the-box for modern single-page applications and mobile backends.
""",
    },
    {
        "name": "Health",
        "description": "Service health and metadata discovery endpoints.",
    },
]

app = FastAPI(
    title="TfGB API",
    description=API_DESCRIPTION,
    version="1.0.0",
    openapi_tags=TAGS_METADATA,
    lifespan=lifespan,
    docs_url=None,
    redoc_url="/docs",
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"message": "Validation error", "errors": exc.errors()},
    )


# Mount Service Routers
app.include_router(mjt_router)


@app.get(
    "/",
    tags=["Health"],
    summary="Root Discovery",
    description="Returns metadata about the API service, upstream source, and documentation link.",
    responses={
        200: {
            "description": "API service metadata",
            "content": {
                "application/json": {
                    "example": {
                        "title": "TfGB API",
                        "description": "Transport for Greater Bandung API",
                        "docs": "/docs",
                        "version": "1.0.0",
                    }
                }
            },
        }
    },
)
async def root():
    return {
        "title": "TfGB API",
        "description": "Transport for Greater Bandung API",
        "docs": "/docs",
        "version": "1.0.0",
    }


@app.get(
    "/api/health",
    tags=["Health"],
    summary="Health Check",
    description='Performs a lightweight liveness check returning `{"status": "success"}`.',
    responses={
        200: {
            "description": "Health check status",
            "content": {"application/json": {"example": {"status": "success"}}},
        }
    },
)
async def health_check():
    return {"status": "success"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
