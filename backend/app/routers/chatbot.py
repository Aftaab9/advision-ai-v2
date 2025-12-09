from fastapi import APIRouter

router = APIRouter()

@router.post("/message")
async def chat_message():
    return {"message": "Chatbot - Coming soon"}
