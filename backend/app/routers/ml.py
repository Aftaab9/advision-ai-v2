from fastapi import APIRouter

router = APIRouter()

@router.post("/predict-engagement")
async def predict_engagement():
    return {"message": "ML prediction - Coming soon"}
