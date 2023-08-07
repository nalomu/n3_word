from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

import models
import schemas
from database import engine
from exceptions import UnicornException
from routers import users, words

models.Base.metadata.create_all(bind=engine)
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(UnicornException)
async def unicorn_exception_handler(request: Request, exc: UnicornException):
    return JSONResponse(
        status_code=400,
        content=exc.response,
    )


#  register routers
app.include_router(users.router)
app.include_router(words.router)


@app.get("/")
async def root():
    return schemas.StandardResponse(code=200, message='Hello World', data={'test': 1})


@app.get("/hello/{name}")
async def say_hello(name: str):
    return schemas.StandardResponse(code=200, message=f'Hello {name}', data={'name': name})
