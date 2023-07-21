import uvicorn
from fastapi import FastAPI, Body, Depends
from sqlalchemy.orm import sessionmaker

from backend.auth.model import PostSchema, UserSchema, UserLoginSchema
from backend.auth.auth_bearer import JWTBearer
from backend.auth.auth_handler import signJWT

from backend.db import get_db
from database.tables import UserItem

posts = [
    {
        "id": 1,
        "title": "Hello ",
        "text": "Hello my name is Best."
    },
    {
        "id": 2,
        "title": "Bob ",
        "text": "Bob likes to eat chocolate cake."
    },
    {
        "id": 3,
        "title": "Hawks ",
        "text": "Hawks are a type of bird."
    },
]

users = []

app = FastAPI()



def check_user(data: UserLoginSchema):
    for user in users:
        if user.email == data.email and user.password == data.password:
            return True
    return False


# route handlers

# testing
@app.get("/", tags=["test"])
def greet():
    return {"hello": "world!."}


# Get Posts from the database
@app.get("/posts", tags=["posts"])
def get_posts():
    return { "data": posts }


@app.get("/posts/{id}", tags=["posts"])
def get_single_post(id: int):
    if id > len(posts):
        return {
            "error": "No such post with the supplied ID."
        }

    for post in posts:
        if post["id"] == id:
            return {
                "data": post
            }


@app.post("/posts", dependencies=[Depends(JWTBearer())], tags=["posts"])
def add_post(post: PostSchema):
    post.id = len(posts) + 1
    posts.append(post.dict())
    return {
        "data": "post added."
    }


@app.post("/user/signup", tags=["user"])
def create_user(user: UserSchema = Body(...)):
    users.append(user) # replace with db call, making sure to hash the password first
    return signJWT(user.email)


@app.post("/user/login", tags=["user"])
def user_login(user: UserLoginSchema = Body(...)):
    if check_user(user):
        return signJWT(user.email)
    return {
        "error": "Wrong login details!"
    }
