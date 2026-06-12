from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import health, uploads, applications, agent_runs, jobs, users, companies

app = FastAPI(title="Talent Intelligence API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, tags=["health"])
app.include_router(uploads.router, prefix="/uploads", tags=["uploads"])
app.include_router(companies.router, prefix="/companies", tags=["companies"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
app.include_router(applications.router, prefix="/applications", tags=["applications"])
app.include_router(agent_runs.router, prefix="/agent_runs", tags=["agent_runs"])