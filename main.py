from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os

# Importa el chatbot
from app.smart_chatbot import generate_response

app = FastAPI()

# Modelo pydantic
class ChatInput(BaseModel):
    message: str

# API raiz
@app.get("/")
def read_root():
    return {"message": "Makers Tech Chatbot API"}

# Endpoint de chat
@app.post("/chat")
def chat(input: ChatInput):
    response = generate_response(input.message)
    return {"response": response}

# Montamos el directorio static
# index.html seguirá disponible en /chatbot
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/chatbot")
def serve_chatbot():
    return FileResponse(os.path.join("static", "index.html"))

# Nueva ruta para tu página con popup de chatbot
@app.get("/page_with_chat")
def serve_page_with_chat():
    return FileResponse(os.path.join("static", "page_with_chat.html"))

