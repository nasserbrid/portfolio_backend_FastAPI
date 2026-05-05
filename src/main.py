from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.contacts.router import router as contacts_router
from src.projects.router import router as projects_router

app = FastAPI(title="Portfolio API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(projects_router)
app.include_router(contacts_router)
