from fastapi import FastAPI, Depends, Body, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from typing import List, Dict
from starlette.responses import Response
from pydantic import BaseModel
from backend.chat import get_chat, add_chat, reset_chat
from backend.auth.schema import UserSchema, UserLoginSchema
from backend.auth.JWTencoder import signJWT
from backend.auth.JWTauth import JWTBearer
from backend.db import get_db
from database.tables import UserItem, AgentItem, UtteranceItem


app = FastAPI()
app.add_middleware(
  CORSMiddleware,
  allow_origins=["http://localhost:1414"],
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

#creating instance of classbearer
jwt_bearer = JWTBearer()

class Message(BaseModel):
    user: str

@app.get("/", response_class=HTMLResponse)
def read_home():
    return """<html>
    <head><title>My Chatbot</title></head>
    <body>
        <h1>GTM Chatbot</h1>
        <p>Welcome to our cutting edge chatbot service. This is designed to assist marketing teams with data analysis. This chatbot learns from your inputs and gets smarter every day!</p>
    </body>
    </html>"""

@app.get("/health")
def health_check():
    return {"status": "success"}

@app.get("/messages")
def get_messages():
    return {"messages": get_chat()}

@app.post("/messages")
def post_message(message: Message):
    add_chat(message.user)
    return {"status": "success"}

@app.get("/reset")
def reset():
    reset_chat()
    return {"status": "success"}

@app.post("/user/signup", tags=["user"])
def create_user(user: UserSchema, db = Depends(get_db)):
    if db.query(UserItem).filter(UserItem.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already exists")
    user_item = UserItem(
        first = user.first,
        last = user.last,
        email = user.email,
    )
    user_item.password = user_item.set_password(user.password)
    db.add(user_item)
    db.commit()
    db.refresh(user_item)
    return signJWT(user_item.email)

   

@app.post("/user/login", tags=["user"])
def user_login(user: UserLoginSchema = Body(...), db=Depends(get_db)):
    user_from_db = db.query(UserItem).filter(UserItem.email == user.email).first()

    if user_from_db and user_from_db.check_password(user.password):
        jwt_token = signJWT(user_from_db.email)
        
        # Set the JWT token as an HttpOnly cookie in the response
        response = Response(content="Login Successful")
        response.set_cookie(key="access_token", value=jwt_token, httponly=False, max_age=100, samesite='none', path='/', secure = 'True')
        return response
    
    return {"error": "Wrong login details!"}

@app.post("/user/logout", tags=["user"])
def user_logout(response: Response):
    # Set an expired cookie to delete the existing JWT token
    response.delete_cookie(key="access_token", path = '/')
    return {"message": "Logged out successfully!"}
