import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from src.contacts.router import router as contacts_router
from src.core.logging import get_logger, setup_logging
from src.projects.router import router as projects_router

setup_logging()
logger = get_logger(__name__)

app = FastAPI(title="Portfolio API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = (time.perf_counter() - start) * 1000
    logger.info(
        "%s %s → %d [%.0fms]",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response


app.include_router(projects_router)
app.include_router(contacts_router)
