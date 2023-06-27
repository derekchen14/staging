from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from typing import List, Dict
from pydantic import BaseModel
from backend.chat import get_chat, add_chat

app = FastAPI()
app.add_middleware(
  CORSMiddleware,
  allow_origins=["*"],
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

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
