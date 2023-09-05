from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.staticfiles import StaticFiles

import models
from database import engine
from exceptions import UnicornException
from routers import users, words, categories, feedbacks

# models.Base.metadata.create_all(bind=engine)
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Authorization", "X-Refresh-Token"],  # 设置允许暴露的响应头
)


@app.exception_handler(UnicornException)
async def unicorn_exception_handler(request: Request, exc: UnicornException):
    return JSONResponse(
        status_code=200,
        content=exc.response,
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse({
        "code": 412,
        "message": '验证错误',
        "data": exc.errors(),
    })


#  register routers
app.include_router(users.router)
app.include_router(words.router)
app.include_router(categories.router)
app.include_router(feedbacks.router)
app.mount("/static", StaticFiles(directory="static"), name="static")

# @app.get("/")
# async def root():
#     return schemas.StandardResponse(code=200, message='Hello World', data={'test': 1})


# @app.get("/hello/{name}")
# async def say_hello(name: str):
#     return schemas.StandardResponse(code=200, message=f'Hello {name}', data={'name': name})
