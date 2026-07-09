import os

import joblib
import pandas as pd


MODEL_PATH = os.path.join(
    os.path.dirname(__file__),
    "models",
    "xgb_model.pkl"
)

model = joblib.load(MODEL_PATH)


def prepare_features(data: dict) -> pd.DataFrame:
    """
    Convert request data into the feature format expected by the model.
    """

    df = pd.DataFrame([data])

    # Remove target if provided
    df = df.drop(columns=["price"], errors="ignore")

    # Feature engineering
    if "build_year" in df.columns:
        df["house_age"] = 2026 - df["build_year"]

    return df


def predict(data: dict) -> float:

    df = prepare_features(data)

    prediction = model.predict(df)

    return float(10 ** prediction[0])