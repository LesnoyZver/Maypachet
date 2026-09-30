from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
import uvicorn
from starlette.staticfiles import StaticFiles
from database import init_db
from router import router


BASE_DIR = Path(__file__).resolve().parent.parent

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(title="Учет компьютерной техники", lifespan=lifespan)

app.include_router(router)

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/static/login.html")


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)