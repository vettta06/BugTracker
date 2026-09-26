from app.routers import bugs, comments, projects, users
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="DevBug API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(projects.router)
app.include_router(bugs.router)
app.include_router(comments.router)
app.include_router(users.router)


@app.get("/")
def root():
    return {"service": "DevBug", "status": "ok"}
