from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os

# chatbot
from app.smart_chatbot import generate_response

app = FastAPI()

class ChatInput(BaseModel):
    message: str

# API
@app.get("/")
def read_root():
    return {"message": "Makers Tech Chatbot API"}

# Endpoint
@app.post("/chat")
def chat(input: ChatInput):
    response = generate_response(input.message)
    return {"response": response}

# Static directory
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/chatbot")
def serve_chatbot():
    return FileResponse(os.path.join("static", "index.html"))

# Popup chatbot
@app.get("/page_with_chat")
def serve_page_with_chat():
    return FileResponse(os.path.join("static", "page_with_chat.html"))

