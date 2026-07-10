import streamlit as st
import requests
import pandas as pd
from geopy.geocoders import Nominatim
from math import radians, sin, cos, sqrt, atan2
from pathlib import Path
import time

# ==========================
# CONFIG
# ==========================

API_URL = st.secrets["API_URL"]
API_TIMEOUTS = [(5, 15), (5, 30)]
API_RETRY_DELAY_SECONDS = 1.2

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

    .hero {
        background: linear-gradient(
            135deg,
            #1f4e79 0%,
            #2e86c1 100%
        );
        border-radius: 20px;
        padding: 28px;
        margin-bottom: 24px;
        color: #ffffff;
        box-shadow: 0 10px 24px rgba(31, 78, 121, 0.25);
    }

    .hero-badge {
        display: inline-block;
        background: rgba(255, 255, 255, 0.16);
        border: 1px solid rgba(255, 255, 255, 0.28);
        border-radius: 999px;
        padding: 6px 12px;
        font-size: 12px;
        font-weight: 600;
        letter-spacing: 0.5px;
        margin-bottom: 12px;
    }

    .hero-title {
        font-size: 40px;
        font-weight: 800;
        line-height: 1.1;
        margin-bottom: 10px;
    }

    .hero-subtitle {
        font-size: 20px;
        font-weight: 600;
        margin-bottom: 8px;
        color: #e8f2ff;
    }

    .hero-desc {
        font-size: 16px;
        max-width: 760px;
        color: #f4f8ff;
    }

    @media (max-width: 768px) {
        .hero {
            padding: 20px;
            border-radius: 16px;
        }

        .hero-title {
            font-size: 30px;
        }

        .hero-subtitle {
            font-size: 17px;
        }

        .hero-desc {
            font-size: 14px;
        }
    }

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

    .result-card {
        background: linear-gradient(
            135deg,
            #f7fbff 0%,
            #eef5fb 100%
        );
        border: 1px solid #cfe0ef;
        border-left: 6px solid #2e86c1;
        border-radius: 20px;
        padding: 22px;
        margin: 10px 0 14px 0;
        color: #183b5f;
        box-shadow: 0 6px 14px rgba(31, 78, 121, 0.10);
    }

    .result-label {
        font-size: 13px;
        letter-spacing: 0.4px;
        opacity: 0.85;
        margin-bottom: 8px;
    }

    .result-price {
        font-size: 44px;
        font-weight: 700;
        line-height: 1;
        margin-bottom: 8px;
        color: #1f4e79;
    }

    .result-sub {
        font-size: 15px;
        color: #3e6688;
    }

    @media (max-width: 768px) {
        .result-price {
            font-size: 34px;
        }

        .result-sub {
            font-size: 14px;
        }
    }

    </style>
    """,
    unsafe_allow_html=True
)

# ==========================
# HEADER
# ==========================
st.markdown(
    """
    <section class="hero">
        <div class="hero-badge">AI PROPERTY VALUATION</div>
        <div class="hero-title">🏠 Immo Eliza</div>
        <div class="hero-subtitle">Belgian House Price Estimation</div>
        <div class="hero-desc">
            Enter property details and location data to receive a fast, data-driven market estimate.
            The model uses geospatial and property attributes to generate a realistic price prediction.
        </div>
    </section>
    """,
    unsafe_allow_html=True
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


def call_prediction_api(payload):
    """
    Retry prediction request to handle first-call cold starts on hosted backends.
    Uses separate connect/read timeouts and increases read timeout on retry.
    """
    last_exception = None

    for attempt, timeout in enumerate(API_TIMEOUTS, start=1):
        try:
            response = requests.post(
                API_URL,
                json=payload,
                timeout=timeout
            )
            return response
        except requests.exceptions.Timeout as exc:
            last_exception = exc

            if attempt < len(API_TIMEOUTS):
                time.sleep(API_RETRY_DELAY_SECONDS)
                continue

            raise

    if last_exception:
        raise last_exception

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


def required_label(text):
    st.markdown(
        f"<div style='font-weight:600; margin-bottom:0.25rem;'>{text} <span style='color:#d62828;'>*</span></div>",
        unsafe_allow_html=True,
    )

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
        st.subheader("Property Information")

        col1,col2 = st.columns(2)

        with col1:
            required_label("Property Type")
            property_type = st.selectbox(
                "",
                [
                    "house",
                    "apartment"
                ],
                key="property_type"
                , label_visibility="collapsed"
            )

            bedrooms = st.number_input(
                "Bedrooms",
                min_value=0,
                max_value=20,
                value=2,
                key="bedrooms"
            )
            show_error("bedrooms")

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
    # SURFACE
    # ======================
    with st.container(border=True):

        st.subheader("Surface Information")

        col1,col2 = st.columns(2)

        with col1:
            required_label("Living Area (m²)")
            livable_surface = st.slider(
                "",
                min_value=0,
                value=80,
                step=10,
                key="livable_surface",
                max_value=1000,
                help="Drag to adjust living area quickly.",
                label_visibility="collapsed"
            )
            show_error("livable_surface")

        with col2:
            total_surface = st.slider(
                "Total Surface (m²)",
                min_value=0,
                value=120,
                step=10,
                max_value=2000,
                key="total_surface"
            )
            show_error("total_surface")

    # ======================
    # FEATURES
    # ======================
    with st.container(border=True):
        st.subheader("Features")

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
        st.subheader("Location")

        col1,col2 = st.columns(2)

        with col1:
            required_label("House Number")
            house_number = st.text_input(
                "",
                placeholder="e.g. 25",
                key="house_number"
                , label_visibility="collapsed"
            )
            show_error("house_number")

            required_label("Street")
            street = st.text_input(
                "",
                placeholder="e.g. Rue de la Loi",
                key="street"
                , label_visibility="collapsed"
            )
            show_error("street")

            required_label("Postcode")
            postcode = st.text_input(
                "",
                placeholder="e.g. 1000",
                key="postcode"
                , label_visibility="collapsed"
            )
            show_error("postcode")
            
        with col2:

            required_label("Province")
            province = st.selectbox(
                "",
                options=list(PROVINCES.keys()),  
                format_func=lambda key: PROVINCES[key],
                index=None,
                placeholder="Select a province",
                key="province",
                label_visibility="collapsed"
            )
            show_error("province")

            required_label("Property City")
            city = st.selectbox(
                "",
                options=sorted(
                    cities_df["Municipality_NL"]
                    .dropna()
                    .unique()
                ),
                index=None,
                placeholder="Type or select a city",
                key="city",
                label_visibility="collapsed"
            )
            show_error("city")
            
            required_label("Nearest Major City")
            nearest_city = st.selectbox(
                "",
                options=list(BIG_CITIES.keys()),  
                format_func=lambda key: BIG_CITIES[key]["name"],
                index=None,
                placeholder="Select a city",
                key="nearest_city",
                label_visibility="collapsed"
            )
            show_error("nearest_city")

    # ======================
    # ACCESSIBILITY
    # ======================
    with st.container(border=True):
        st.subheader("Accessibility")

        energy_consumption = st.slider(
            "Energy Consumption (kWh/m²/year)",
            min_value=0,
            max_value=1000,
            value=0,
            step=10,
            key="energy_consumption"
        )
        show_warning("energy_consumption")

        preschool_distance = st.slider(
            "Preschool Distance (m)",
            min_value=0,
            value=0,
            max_value=20000,
            step=10,
            key="preschool_distance"
        )

        train_station_distance = st.slider(
            "Train Station Distance (m)",
            min_value=0,
            value=0,
            max_value=20000,
            step=10,
            key="train_station_distance"
        )

        supermarket_distance = st.slider(
            "Supermarket Distance (m)",
            min_value=0,
            value=0,
            max_value=20000,
            step=10,
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

    latitude, longitude = get_coordinates(
        full_address
    )
    if latitude is None or longitude is None:
        st.error(
            "Cannot find this address. Please check street, postcode and city."
        )
        st.stop()

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
            response = call_prediction_api(payload)

        if response.status_code != 200:
            st.error(
                f"API Error {response.status_code}"
            )

            st.stop()

        result = response.json()

        prediction = result["prediction"]
        price_per_m2 = (
            prediction / livable_surface
            if livable_surface > 0
            else None
        )

        st.success(
            "Estimation completed!"
        )

        st.markdown(
            f"""
            <div class="result-card">
                <div class="result-label">ESTIMATED PROPERTY PRICE</div>
                <div class="result-price">€ {prediction:,.0f}</div>
                <div class="result-sub">
                    Estimated price per m²: {"€ " + format(price_per_m2, ",.0f") if price_per_m2 is not None else "N/A"}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        with st.expander("Location details", expanded=False):
            st.write(f"Address: {full_address}")
            st.caption(
                f"Latitude: {latitude:.6f} | Longitude: {longitude:.6f}"
            )

    except requests.exceptions.Timeout:

        st.error(
            "API timeout on initial call. Please retry in a few seconds."
        )

    except Exception as e:
        st.error(
            f"Unexpected error: {e}"
        )

    finally:
        # Prevent reruns from re-triggering the same API call automatically.
        st.session_state.submitted = False