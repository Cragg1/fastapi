import logging
from fastapi import FastAPI, Response, status, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from random import randrange
import psycopg
from sqlalchemy.orm import Session
from . import models, schemas, utils
from .database import engine, get_db
from .routers import post, user, auth, vote
from .config import settings

# Up to 10:56:30 on below video.
# https://www.youtube.com/watch?v=0sOvCWFmrtA&list=WL&index=78

# uvicorn app.main:app --reload

# https://fastapi.tiangolo.com/tutorial/first-steps/
# FastAPI auto generates docs for you. Go to http://127.0.0.1:8000/docs or http://127.0.0.1:8000/redoc to see the docs for your API!

logging.getLogger('passlib').setLevel(logging.ERROR)

# For sqlalchemy to create the tables using the models from model.py. This cannot modify existing tables, need to use Alembic for this feature.
# Redundant because of alembic.
# models.Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# database = psycopg.connect(host="localhost", dbname="fastapi", user="postgres", password="2Philio<83Ball7")


# First app object encountered when FastAPI runs.
# Looks into post.py going down one by one to see if it is the function being called.
# Then moves on to the next, etc.
app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(vote.router)


# Decorator turns the function into a path operator. HTTP method .get passed in. 
# "/" is the root path. http://127.0.0.1:8000/ takes you to http://127.0.0.1:8000. If "login", then it would need to be http://127.0.0.1:8000/login
@app.get("/")
# Function can have any name. async def <name>() - async can be used as an optional term if the transaction is asynchronous (requires waiting)
def root():
    # FastAPI converts the below message to JSON.
    return {"message": "Welcome to my API"}

# Using sqlalchemy as an ORM to get around having to use SQL ourselves as per commented out code in post.py.
@app.get("/sqlalchemy")
# Have to pass the database in as a function argument as it is a dependency.
def test_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return {"data": posts}

