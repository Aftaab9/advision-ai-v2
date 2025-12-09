from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def list_creatives():
    return {"message": "Creatives endpoint - Coming soon"}
