# Immo Eliza - House Price Prediction API

A machine learning deployment project that exposes a real estate price prediction model through a FastAPI API and provides a Streamlit interface for non-technical users.

The project contains:

- A FastAPI backend for model inference
- A trained machine learning model with preprocessing artifacts
- A Dockerized API deployed on Render
- A Streamlit frontend application consuming the API

---

# Architecture

```
                 User
                  |
                  |
                  v
            Streamlit App
                  |
                  |
                  v
          FastAPI Prediction API
                  |
                  |
                  v
          Prediction Service
                  |
                  |
                  v
          ML Prediction Pipeline
                  |
                  |
                  v
        Trained Model + Artifacts
```

---

# Project Structure

```
immo-eliza-deployment/

│
├── api/
│   │
│   ├── __init__.py
│   ├── app.py                      # FastAPI application entry point
│   ├── requirements.txt
│   ├── Dockerfile
│   │
│   ├── routers/                    # API routes
│   │   ├── __init__.py
│   │   └── prediction.py
│   │
│   ├── schemas/                    # Request/Response validation
│   │   ├── __init__.py
│   │   └── prediction.py
│   │
│   ├── services/                   # Business logic
│   │   ├── __init__.py
│   │   └── prediction_service.py
│   │
│   ├── ml/                         # Machine learning layer
│   │   ├── __init__.py
│   │   ├── predict.py
│   │   └── models/
│   │       ├── xgb_model.pkl
│   │
│   └── core/
│       ├── __init__.py
│       └── config.py
│
│
├── streamlit/
│   ├── app.py                      # Streamlit frontend
│   └── requirements.txt
│
├── README.md
└── .gitignore
```

---

# API Request Flow

```
Client Request

      |
      v

routers/prediction.py

      |
      v

services/prediction_service.py

      |
      v

ml/predict.py

      |
      v

Machine Learning Model

      |
      v

Prediction Response
```

---

# Features

## FastAPI Backend

Available endpoints:

### Health Check

```
GET /
```

Response:

```json
{
  "status": "alive"
}
```

---

---

# Prediction Features

The API accepts the following features:

| Feature                | Type    | Description                |
| ---------------------- | ------- | -------------------------- |
| property_type          | str     | Property type              |
| city                   | str     | City location              |
| province               | str     | Province location          |
| latitude               | float64 | Latitude coordinate        |
| longitude              | float64 | Longitude coordinate       |
| property_state         | str     | Property condition         |
| build_year             | int64   | Construction year          |
| bedroom_count          | float64 | Number of bedrooms         |
| livable_surface        | float64 | Living surface area        |
| total_surface          | float64 | Total surface area         |
| garage                 | int64   | Garage availability        |
| terrace                | float64 | Terrace availability       |
| energy_consumption     | float64 | Energy consumption         |
| swimming_pool          | int64   | Swimming pool availability |
| preschool_distance     | float64 | Distance to preschool      |
| train_station_distance | float64 | Distance to train station  |
| supermarket_distance   | float64 | Distance to supermarket    |
| nearest_city           | str     | Closest city               |
| nearest_city_distance  | float64 | Distance to nearest city   |

### House Price Prediction

```
POST /api/v1/prediction
```

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
  "nearest_city": "Antwerp",
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

---

# Local Installation

## 1. Clone repository

```bash
git clone <repository-url>

cd immo-eliza-deployment
```

---

# Running FastAPI Locally

## 1. Move into API folder

```bash
cd api
```

## 2. Create virtual environment

```bash
python -m venv .venv
```

Activate:

### Windows

```bash
.venv\Scripts\activate
```

### Mac/Linux

```bash
source .venv/bin/activate
```

---

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Start FastAPI server

```bash
uvicorn api.app:app --reload
```

API available at:

```
http://localhost:8000
```

Swagger documentation:

```
http://localhost:8000/docs
```

---

# Running Streamlit Application

Open another terminal:

```bash
cd streamlit
```

Create environment:

```bash
python -m venv .venv
```

Activate environment:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run Streamlit:

```bash
streamlit run app.py
```

The application will run at:

http://localhost:8501

---

# Docker Deployment

Build API image:

```bash
docker build -t immo-api ./api
```

Run container:

```bash
docker run -p 8000:10000 immo-api
```

The API will be available at:

```
http://localhost:8000
```

---

# Deployment

## Backend

The FastAPI application is deployed using:

- Docker
- Render

## Frontend

The Streamlit application is deployed using:

- Streamlit Community Cloud

---

# Machine Learning Model

The API loads:

- trained regression model
- preprocessing pipeline
- encoding/scaling artifacts

The prediction pipeline:

```
Input JSON
      |
      v
Pandas DataFrame
      |
      v
Saved sklearn Pipeline
      |
      |
      ├── ColumnTransformer
      │       |
      │       ├── Numerical
      │       │       ├── KNNImputer
      │       │       └── StandardScaler
      │       │
      │       └── Categorical
      │               ├── SimpleImputer
      │               └── OneHotEncoder
      |
      v
XGBRegressor
      |
      v
log10(price)
      |
      v
10 ** prediction
      |
      v
House price (€)
```

---

# Model Artifact

```text
The deployed model:

xgb_model.pkl
├── Preprocessor
│   ├── Numerical Pipeline
│   │   ├── StandardScaler
│   │   └── KNNImputer
│   └── Categorical Pipeline
│       ├── SimpleImputer (most_frequent)
│       └── OneHotEncoder
└── XGBRegressor
```

# 🎨 Streamlit Frontend Application

The project includes a Streamlit frontend application that allows users to predict house prices through a simple web interface.

The Streamlit application is only responsible for:

- Collecting user inputs
- Sending prediction requests to FastAPI
- Displaying prediction results

The machine learning model is hosted inside the FastAPI backend.

---

# Streamlit Architecture

User
|
v
Streamlit Web App
|
| HTTP POST Request
|
v
FastAPI Prediction API
|
v
Prediction Service
|
v
XGBRegressor Pipeline
|
v
Predicted House Price (€)

---

# Streamlit User Interface

The application provides a property prediction form where users can enter:

| Feature                | Type  |
| ---------------------- | ----- |
| property_type          | str   |
| city                   | str   |
| province               | str   |
| latitude               | float |
| longitude              | float |
| property_state         | str   |
| build_year             | int   |
| bedroom_count          | float |
| livable_surface        | float |
| total_surface          | float |
| garage                 | int   |
| terrace                | int   |
| energy_consumption     | float |
| swimming_pool          | int   |
| preschool_distance     | float |
| train_station_distance | float |
| supermarket_distance   | float |
| nearest_city           | str   |
| nearest_city_distance  | float |

---

# Technologies

- Python
- FastAPI
- Pydantic
- Scikit-learn
- Pandas
- Docker
- Render
- Streamlit

---

# Future Improvements

Possible improvements:

- Add automated tests
- Add logging
- Add model versioning
- Add authentication
- Add database for prediction history
