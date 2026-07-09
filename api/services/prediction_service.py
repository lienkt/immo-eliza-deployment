from ml.predict import predict


def predict_price(data: dict):

    predicted_price = predict(data)

    return {
        "prediction": round(predicted_price, 2),
        "status_code": 200
    }