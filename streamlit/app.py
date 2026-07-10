import streamlit as st
import requests
import pandas as pd
from geopy.geocoders import Nominatim
from math import radians, sin, cos, sqrt, atan2
from pathlib import Path

# ==========================
# CONFIG
# ==========================

# API_URL = "http://localhost:8000/api/v1/predict"
API_URL = st.secrets["API_URL"]

BASE_DIR = Path(__file__).resolve().parent

cities_df = pd.read_csv(
    BASE_DIR / "data" / "communicipalities.csv",
    sep=";"
)

BIG_CITIES = {
    'antwerp': {
        "name": 'Antwerp',
        "longitude": 4.4025,
        "latitude": 51.2194
    },
    'brussels': {
        "name": 'Brussels',
        "longitude": 4.3499,
        "latitude": 50.8467
    },
    'ghent': {
        "name": 'Ghent',
        "longitude": 3.7174,
        "latitude": 51.0543
    },
    'charleroi': {
        "name": 'Charleroi',
        "longitude": 4.4446,
        "latitude": 50.4108
    },
    'liege': {
        "name": 'Liege',
        "longitude": 5.5734,
        "latitude": 50.6451
    },
    'bruges': {
        "name": 'Bruges',
        "longitude": 3.2247,
        "latitude": 51.2093
    },
    'namur': {
        "name": 'Namur',
        "longitude": 4.8719,
        "latitude": 50.4674
    },
    'leuven': {
        "name": 'Leuven',
        "longitude": 4.7005,
        "latitude": 50.8798
    }
}

PROVINCES = {
    "antwerp": "Antwerp",
    "brussels": "Brussels",
    "limburg": "Limburg", 
    "east-flanders": "East Flanders", 
    "vlaams-brabant": "Flemish Brabant", 
    "west-flanders": "West Flanders",
    "hainaut": "Hainaut", 
    "liege": "Liège", 
    "luxembourg": "Luxembourg", 
    "namur": "Namur", 
    "brabant-wallon": "Walloon Brabant"
}
  
# ==========================
# PAGE CONFIG
# ==========================

st.set_page_config(
    page_title="Immo Eliza",
    page_icon="🏠",
    layout="wide"
)


# ==========================
# CUSTOM CSS
# ==========================
st.markdown(
    """
    <style>

    /* Remove form border */
    div[data-testid="stForm"] {
        border: none;
        padding: 0;
        background: transparent;
    }

    .section-card {
        background-color: white;
        padding: 25px;
        border-radius: 18px;
        border: 1px solid #e5e7eb;
        margin-bottom: 25px;
        box-shadow:
        0px 4px 12px rgba(0,0,0,0.05);
    }


    .section-title {
        font-size: 22px;
        font-weight: 700;
        margin-bottom: 15px;
    }

    /* Estimate button */
    div.stButton > button,
    div.stFormSubmitButton > button {
        width: 100%;
        height: 2.5em;
        border-radius: 15px;
        background: linear-gradient(
            135deg,
            #1f4e79,
            #2e86c1
        );
        color: white;
        font-size: 26px;
        font-weight: 500;
        border: none;
        box-shadow:
            0px 6px 15px rgba(0,0,0,0.15);
        transition: all 0.3s ease;
        display: flex;
        justify-content: center;
    }

    div.stButton > button:hover,
    div.stFormSubmitButton > button:hover {
        transform: translateY(-3px);
        background: linear-gradient(
            135deg,
            #163a5c,
            #1f6aa5
        );
        box-shadow:
            0px 10px 20px rgba(0,0,0,0.25);
    }

    </style>
    """,
    unsafe_allow_html=True
)

# ==========================
# HEADER
# ==========================
st.title("🏠 Immo Eliza")

st.subheader(
    "Belgian House Price Estimation"
)

st.write(
    """
    Enter property information.
    The AI model will estimate the market price.
    """
)

# ==========================
# SESSION STATE
# ==========================

if "errors" not in st.session_state:
    st.session_state.errors = {}

if "warnings" not in st.session_state:
    st.session_state.warnings = {}

if "submitted" not in st.session_state:
    st.session_state.submitted = False

# ==========================
# Geolocation
# ==========================
geolocator = Nominatim(
    user_agent="immo-eliza"
)

def get_coordinates(address):

    location = geolocator.geocode(
        address
    )

    if location:
        return (
            location.latitude,
            location.longitude
        )

    return None, None

def haversine_distance(
    lat1,
    lon1,
    lat2,
    lon2
):
    R = 6371  # km

    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        sin(dlat / 2) ** 2
        + cos(lat1)
        * cos(lat2)
        * sin(dlon / 2) ** 2
    )

    c = 2 * atan2(
        sqrt(a),
        sqrt(1 - a)
    )

    if None in [
        lat1,
        lon1,
        lat2,
        lon2
    ]:
        return None
    
    return R * c

# ==========================
# VALIDATION FUNCTION
# ==========================

def validate_inputs(data):

    errors = {}
    warnings = {}

    # Surface
    if data["livable_surface"] <= 0:
        errors["livable_surface"] = (
            "Living area must be greater than 0 m²."
        )

    if data["total_surface"] < data["livable_surface"]:
        errors["total_surface"] = (
            "Total surface cannot be smaller than living area."
        )

    # Address
    if not data["province"]:
        errors["province"] = "Province cannot be empty."

    if not data["city"]:
        errors["city"] = "City cannot be empty."

    if not data["nearest_city"]:
        errors["nearest_city"] = "Nearest city cannot be empty."
    
    if not data["postcode"] or not data["postcode"].strip():
        errors["postcode"] = "Postcode cannot be empty."

    if not data["street"] or not data["street"].strip():
        errors["street"] = "Street cannot be empty."
    
    if not data["house_number"] or not data["house_number"].strip():
        errors["house_number"] = "House number cannot be empty."
    
    # Bedrooms
    if (
        data["property_type"] == "house"
        and data["bedrooms"] < 1
    ):
        errors["bedrooms"] = (
            "House must have at least 1 bedroom."
        )

    if data["bedrooms"] > 20:
        errors["bedrooms"] = (
            "Bedroom number looks unrealistic."
        )

    # Year
    if data["build_year"] > 2026:
        errors["build_year"] = (
            "Build year cannot be in the future."
        )

    if data["build_year"] < 1850:
        warnings["build_year"] = (
            "Very old property. Please verify."
        )

    # Energy
    if data["energy_consumption"] == 0:
        warnings["energy_consumption"] = (
            "Energy consumption is missing."
        )
    elif data["energy_consumption"] > 500:
        warnings["energy_consumption"] = (
            "Energy consumption is unusually high."
        )

    return errors, warnings

def show_error(field):
    if (
        st.session_state.submitted
        and field in st.session_state.errors
    ):
        st.error(st.session_state.errors[field])


def show_warning(field):
    if (
        st.session_state.submitted
        and field in st.session_state.warnings
    ):
        st.warning(st.session_state.warnings[field])

# ==============================================================
# KIỂM TRA LỖI REALTIME TRƯỚC KHI DỰNG FORM (SỬA LỖI KHÔNG RENDER LẠI)
# ==============================================================
data_preview = {
    "property_type": st.session_state.get("property_type", "house"),
    "city": st.session_state.get("city", None),
    "province": st.session_state.get("province", None),
    "nearest_city": st.session_state.get("nearest_city", None),
    "livable_surface": st.session_state.get("livable_surface", 0),
    "total_surface": st.session_state.get("total_surface", 0),
    "bedrooms": st.session_state.get("bedrooms", 2),
    "build_year": st.session_state.get("build_year", 2000),
    "energy_consumption": st.session_state.get("energy_consumption", 0),
    "postcode": st.session_state.get("postcode", ""),
    "street": st.session_state.get("street", ""),
    "house_number": st.session_state.get("house_number", "")
}

errors, warnings = validate_inputs(data_preview)
st.session_state.errors = errors
st.session_state.warnings = warnings

# ==========================
# FORM
# ==========================
with st.form("property_form"):

    # ======================
    # PROPERTY
    # ======================
    with st.container(border=True):
        st.header("🏡 Property Information")

        col1,col2 = st.columns(2)

        with col1:
            property_type = st.selectbox(
                "Property Type",
                [
                    "house",
                    "apartment"
                ],
                key="property_type"
            )

        with col2:
            property_state = st.selectbox(
                "Property Condition",
                [
                    "Normal",
                    "Good",
                    "To renovate"
                ],
                key="property_state"
            )
            bedrooms = st.number_input(
                "Bedrooms",
                min_value=0,
                max_value=20,
                value=2,
                key="bedrooms"
            )
            show_error("bedrooms")
            
    # ======================
    # SURFACE
    # ======================
    with st.container(border=True):

        st.header("📐 Surface Information")

        col1,col2 = st.columns(2)

        with col1:
            livable_surface = st.number_input(
                "Living Area (m²)",
                min_value=0,
                value=0,
                key="livable_surface"
            )
            show_error("livable_surface")

            total_surface = st.number_input(
                "Total Surface (m²)",
                min_value=0,
                value=0,
                key="total_surface"
            )
            show_error("total_surface")

        with col2:

            build_year = st.number_input(
                "Build Year",
                min_value=1850,
                max_value=2026,
                value=2000,
                key="build_year"
            )
            show_error("build_year")
            show_warning("build_year")

    # ======================
    # FEATURES
    # ======================
    with st.container(border=True):
        st.header("⚙️ Features")

        col1,col2,col3 = st.columns(3)

        with col1:
            garage = st.checkbox(
                "Garage",
                key="garage"
            )

        with col2:
            terrace = st.checkbox(
                "Terrace",
                key="terrace"
            )

        with col3:
            swimming_pool = st.checkbox(
                "Swimming Pool",
                key="swimming_pool"
            )

    # ======================
    # LOCATION
    # ======================
    with st.container(border=True):
        st.header("📍 Location")

        col1,col2 = st.columns(2)

        with col1:

            house_number = st.text_input(
                "House Number",
                placeholder="e.g. 25",
                key="house_number"
            )
            show_error("house_number")

            street = st.text_input(
                "Street",
                placeholder="e.g. Rue de la Loi",
                key="street"
            )
            show_error("street")

            postcode = st.text_input(
                "Postcode",
                placeholder="e.g. 1000",
                key="postcode"
            )
            show_error("postcode")
            
        with col2:

            province = st.selectbox(
                "Province",
                options=list(PROVINCES.keys()),  
                format_func=lambda key: PROVINCES[key],
                index=None,
                placeholder="Select a province",
                key="province"
            )
            show_error("province")

            city = st.selectbox(
                "Property City",
                options=sorted(
                    cities_df["Municipality_NL"]
                    .dropna()
                    .unique()
                ),
                index=None,
                placeholder="Type or select a city",
                key="city"
            )
            show_error("city")
            
            nearest_city = st.selectbox(
                "Nearest Major City",
                options=list(BIG_CITIES.keys()),  
                format_func=lambda key: BIG_CITIES[key]["name"],
                index=None,
                placeholder="Select a city",
                key="nearest_city"
            )
            show_error("nearest_city")

    # ======================
    # ACCESSIBILITY
    # ======================
    with st.container(border=True):
        st.header("🚉 Accessibility")

        energy_consumption = st.number_input(
            "Energy Consumption (kWh/m²/year)",
            min_value=0,
            max_value=1000,
            value=0,
            key="energy_consumption"
        )
        show_warning("energy_consumption")

        preschool_distance = st.number_input(
            "Preschool Distance (m)",
            min_value=0,
            value=0,
            key="preschool_distance"
        )

        train_station_distance = st.number_input(
            "Train Station Distance (m)",
            min_value=0,
            value=0,
            key="train_station_distance"
        )

        supermarket_distance = st.number_input(
            "Supermarket Distance (m)",
            min_value=0,
            value=0,
            key="supermarket_distance"
        )
        
    col1, col2, col3 = st.columns([1, 1, 1])

    with col2:
        submit = st.form_submit_button(
            "Estimate Property Price",
            use_container_width=True
        )

# ==========================
# PREDICTION
# ==========================
if submit:
    st.session_state.submitted = True
    st.rerun()

if st.session_state.submitted:
    if st.session_state.errors:
        st.stop()

    # ======================
    # PAYLOAD
    # ======================

    full_address = f"{house_number} {street}, {postcode} {city}, Belgium"

    st.write("Address:", full_address)

    latitude, longitude = get_coordinates(
        full_address
    )
    if latitude is None or longitude is None:
        st.error(
            "Cannot find this address. Please check street, postcode and city."
        )
        st.stop()

    st.write("Latitude:", latitude)
    st.write("Longitude:", longitude)

    nearest_city_distance = haversine_distance(
        latitude,
        longitude,
        BIG_CITIES[nearest_city]["latitude"],
        BIG_CITIES[nearest_city]["longitude"]
    )

    get_coordinates(
            f"{BIG_CITIES[nearest_city]['name']}, Belgium"
        )
    
    payload = {
        "property_type": property_type,
        "city": city,
        "province": province,
        "latitude": latitude,
        "longitude": longitude,
        "price": 0,
        "property_state": property_state,
        "build_year": build_year,
        "bedroom_count": bedrooms,
        "livable_surface": livable_surface,
        "total_surface": total_surface,
        "garage": int(garage),
        "terrace": int(terrace),
        "energy_consumption": energy_consumption,
        "swimming_pool": int(swimming_pool),
        "preschool_distance": preschool_distance,
        "train_station_distance": train_station_distance,
        "supermarket_distance": supermarket_distance,
        "nearest_city": nearest_city,
        "nearest_city_distance": nearest_city_distance
    }

    # ======================
    # API CALL
    # ======================

    try:

        with st.spinner(
            "🤖 AI is estimating the price..."
        ):

            response = requests.post(
                API_URL,
                json=payload,
                timeout=10
            )

        if response.status_code != 200:
            st.error(
                f"API Error {response.status_code}"
            )

            st.stop()

        result = response.json()

        prediction = result["prediction"]

        st.success(
            "Estimation completed!"
        )

        st.metric(
            "🏠 Estimated Property Price",
            f"€ {prediction:,.0f}"
        )

        if livable_surface > 0:

            price_per_m2 = (
                prediction /
                livable_surface
            )

            st.info(
                f"Estimated price per m²: € {price_per_m2:,.0f}"
            )

    except requests.exceptions.Timeout:

        st.error(
            "API timeout. Server took too long."
        )

    except Exception as e:
        st.error(
            f"Unexpected error: {e}"
        )