# Immo Eliza Deployment

Machine learning deployment project for Belgian real estate price estimation.

The project contains:

- A FastAPI backend for model inference
- A trained machine learning model with preprocessing artifacts
- A Dockerized API deployed on Render
- A Streamlit frontend application consuming the API

---

# Architecture

```text
User -> Streamlit UI -> FastAPI (/api/v1/predict) -> ML inference -> Predicted price
```

## Project Structure

```text
immo-eliza-deployment/
├── api/
│   ├── app.py
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── core/
│   ├── ml/
│   │   ├── predict.py
│   │   └── models/
│   │       └── xgb_model.pkl
│   ├── routers/
│   │   └── prediction.py
│   ├── schemas/
│   │   └── prediction.py
│   └── services/
│       └── prediction_service.py
├── streamlit/
│   ├── app.py
│   ├── requirements.txt
│   ├── data/
│   │   └── communicipalities.csv
│   └── testing/
│       └── test.ipynb
└── README.md
```

## API

Base URL (local): `http://127.0.0.1:8000`

### Health Check

- Method: `GET`
- Path: `/`

Example response:

```json
{
  "status": "alive"
}
```

### Predict Price

- Method: `POST`
- Path: `/api/v1/predict`

Request body (schema summary):

| Field                  | Type   | Required |
| ---------------------- | ------ | -------- |
| property_type          | string | yes      |
| city                   | string | yes      |
| province               | string | yes      |
| latitude               | float  | no       |
| longitude              | float  | no       |
| property_state         | string | no       |
| build_year             | int    | no       |
| bedroom_count          | int    | no       |
| livable_surface        | float  | no       |
| total_surface          | float  | no       |
| garage                 | int    | no       |
| terrace                | int    | no       |
| swimming_pool          | int    | no       |
| energy_consumption     | float  | no       |
| preschool_distance     | float  | no       |
| train_station_distance | float  | no       |
| supermarket_distance   | float  | no       |
| nearest_city           | string | no       |
| nearest_city_distance  | float  | no       |

Example request:

```json
{
  "property_type": "apartment",
  "city": "Mortsel",
  "province": "antwerp",
  "latitude": 51.17245,
  "longitude": 4.446859,
  "property_state": "Normal",
  "build_year": 1969,
  "bedroom_count": 1,
  "livable_surface": 60,
  "total_surface": 100,
  "garage": 0,
  "terrace": 0,
  "energy_consumption": 505,
  "swimming_pool": 0,
  "preschool_distance": 796,
  "train_station_distance": 1000,
  "supermarket_distance": 181,
  "nearest_city": "antwerp",
  "nearest_city_distance": 6.07
}
```

Example response:

```json
{
  "prediction": 450000.0,
  "status_code": 200
}
```

### Quick cURL test

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/predict" \
      -H "Content-Type: application/json" \
      -d '{
            "property_type": "house",
            "city": "Brussels",
            "province": "brussels",
            "bedroom_count": 3,
            "livable_surface": 140,
            "total_surface": 180
      }'
```

## Local Setup

### 1. Clone and enter project

```bash
git clone <repository-url>
cd immo-eliza-deployment
```

### 2. Create and activate a virtual environment (recommended at repo root)

```bash
python -m venv .venv
source .venv/bin/activate
```

Windows (PowerShell):

```bash
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r api/requirements.txt
pip install -r streamlit/requirements.txt
```

## Run the API

From the repository root:

```bash
cd api
uvicorn app:app --reload
```

Useful links:

- API root: `http://127.0.0.1:8000`
- Swagger UI: `http://127.0.0.1:8000/docs`

## Run the Streamlit App

Open a second terminal (same virtual environment), then:

```bash
cd streamlit
streamlit run app.py
```

Streamlit URL: `http://127.0.0.1:8501`

## Streamlit Configuration

The Streamlit app reads the API endpoint from secrets:

```toml
# streamlit/.streamlit/secrets.toml
API_URL = "http://127.0.0.1:8000/api/v1/predict"
```

If you deploy the API, update `API_URL` to your deployed endpoint.

## Model Notes

- Model file is loaded from `api/ml/models/xgb_model.pkl`.
- Inference applies: 1. Request dict -> pandas DataFrame 2. Optional feature engineering (`house_age = 2026 - build_year`) 3. Model prediction 4. Inverse log transform: `price = 10 ** prediction`

## Current Deployment/Docker Status

- `api/Dockerfile` currently exists but is empty.
- Deployment instructions should be completed after the Dockerfile is implemented.

## Troubleshooting

- `ModuleNotFoundError` when starting API: - Run from the `api` directory (`cd api`) before `uvicorn app:app --reload`.
- Streamlit shows API timeout/error: - Confirm API is running and `API_URL` in Streamlit secrets points to `/api/v1/predict`.
- Geocoding fails for an address: - Recheck street/postcode/city spelling in the Streamlit form.
