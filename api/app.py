from fastapi import FastAPI

from routers.prediction import router as prediction_router

app = FastAPI(
    title="Immo Eliza House Price Prediction API",
    version="1.0.0"
)


@app.get("/")
def health_check():

    return {
        "status": "alive"
    }


app.include_router(prediction_router)