from app.routers import bugs, comments, projects, users
from fastapi import FastAPI

app = FastAPI(title="DevBug API")

app.include_router(projects.router)
app.include_router(bugs.router)
app.include_router(comments.router)
app.include_router(users.router)


@app.get("/")
def root():
    return {"service": "DevBug", "status": "ok"}
