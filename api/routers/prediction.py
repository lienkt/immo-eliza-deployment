from fastapi import APIRouter

from api.schemas.prediction import PropertyInput
from api.services.prediction_service import predict_price

router = APIRouter(
    prefix="/api/v1"
)

@router.post("/predict")
def predict_house(property: PropertyInput):

    return predict_price(
        property.model_dump()
    )