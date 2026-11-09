from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import init_db, using_remote_db
from .routers import attachments, subtasks, tags, tasks
from .storage import using_blob


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Kanban Task Manager API",
    version="1.0.0",
    description="API REST para la gestión de tareas en un tablero Kanban.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tasks.router)
app.include_router(subtasks.router)
app.include_router(attachments.router)
app.include_router(tags.router)


@app.get("/api/health", tags=["health"])
def health_check():
    return {
        "status": "ok",
        "database": "turso" if using_remote_db() else "sqlite",
        "storage": "blob" if using_blob() else "local",
    }
