import streamlit as st
import requests


# ==========================
# CONFIG
# ==========================

API_URL = "http://localhost:8000/api/v1/predict"


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

    /* Predict button */
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
# SIDEBAR
# ==========================

# with st.sidebar:

#     st.title("Immo Eliza")

#     st.write(
#         """
#         Belgian House Price Estimation AI

#         Model features:

#         ✅ Location  
#         ✅ Surface  
#         ✅ Property condition  
#         ✅ Amenities  
#         ✅ Accessibility  
#         """
#     )

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

# ==========================
# VALIDATION FUNCTION
# ==========================

def validate_inputs(data):

    errors = {}
    warnings = {}

    # Text
    if not data["city"].strip():
        errors["city"] = "City cannot be empty."

    if not data["province"].strip():
        errors["province"] = "Province cannot be empty."

    if not data["nearest_city"].strip():
        errors["nearest_city"] = "Nearest city cannot be empty."

    # Surface
    if data["livable_surface"] <= 0:
        errors["livable_surface"] = (
            "Living area must be greater than 0 m²."
        )

    if data["total_surface"] < data["livable_surface"]:
        errors["total_surface"] = (
            "Total surface cannot be smaller than living area."
        )

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

    # Coordinates
    if not (
        49 <= data["latitude"] <= 52
    ):
        errors["latitude"] = (
            "Latitude should be between 49 and 52."
        )

    if not (
        2 <= data["longitude"] <= 7
    ):
        errors["longitude"] = (
            "Longitude should be between 2 and 7."
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

# ==========================
# FORM
# ==========================
show_errors = bool(st.session_state.errors)
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
                ]
            )
            city = st.text_input(
                "City",
                ""
            )

            if show_errors and "city" in st.session_state.errors:
                st.error(
                    st.session_state.errors["city"]
                )
                
            province = st.text_input(
                "Province",
                ""
            )

            if show_errors and "province" in st.session_state.errors:
                st.error(
                    st.session_state.errors["province"]
                )

        with col2:
            property_state = st.selectbox(
                "Property Condition",
                [
                    "Normal",
                    "Good",
                    "To renovate"
                ]
            )
            bedrooms = st.number_input(
                "Bedrooms",
                min_value=0,
                max_value=20,
                value=2
            )

            if show_errors and "bedrooms" in st.session_state.errors:
                st.error(
                    st.session_state.errors["bedrooms"]
                )
                
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
                value=0
            )

            if show_errors and "livable_surface" in st.session_state.errors:
                st.error(
                    st.session_state.errors["livable_surface"]
                )

            total_surface = st.number_input(
                "Total Surface (m²)",
                min_value=0,
                value=0
            )

            if show_errors and "total_surface" in st.session_state.errors:
                st.error(
                    st.session_state.errors["total_surface"]
                )

        with col2:

            build_year = st.number_input(
                "Build Year",
                min_value=1850,
                max_value=2026,
                value=2000
            )

            if show_errors and "build_year" in st.session_state.errors:
                st.error(
                    st.session_state.errors["build_year"]
                )

            if show_errors and "build_year" in st.session_state.warnings:
                st.warning(
                    st.session_state.warnings["build_year"]
                )
    # ======================
    # FEATURES
    # ======================
    with st.container(border=True):
        st.header("⚙️ Features")

        col1,col2,col3 = st.columns(3)

        with col1:
            garage = st.checkbox(
                "Garage"
            )

        with col2:
            terrace = st.checkbox(
                "Terrace"
            )

        with col3:
            swimming_pool = st.checkbox(
                "Swimming Pool"
            )

    # ======================
    # LOCATION
    # ======================
    with st.container(border=True):
        st.header("📍 Location")

        col1,col2 = st.columns(2)

        with col1:

            latitude = st.number_input(
                "Latitude",
                value=0
            )

            if show_errors and "latitude" in st.session_state.errors:
                st.error(
                    st.session_state.errors["latitude"]
                )

        with col2:

            longitude = st.number_input(
                "Longitude",
                value=0
            )
            if show_errors and "longitude" in st.session_state.errors:
                st.error(
                    st.session_state.errors["longitude"]
                )

        nearest_city = st.text_input(
            "Nearest City",
            ""
        )

        if show_errors and "nearest_city" in st.session_state.errors:
            st.error(
                st.session_state.errors["nearest_city"]
            )

        nearest_city_distance = st.number_input(
            "Distance to nearest city (km)",
            min_value=0.0,
            value=6.07
        )

    # ======================
    # ACCESSIBILITY
    # ======================
    with st.container(border=True):
        st.header("🚉 Accessibility")

        energy_consumption = st.number_input(
            "Energy Consumption (kWh/m²/year)",
            min_value=0,
            max_value=1000,
            value=0
        )

        if show_errors and "energy_consumption" in st.session_state.warnings:
            st.warning(
                st.session_state.warnings["energy_consumption"]
            )

        preschool_distance = st.number_input(
            "Preschool Distance (m)",
            min_value=0,
            value=0
        )

        train_station_distance = st.number_input(
            "Train Station Distance (m)",
            min_value=0,
            value=0
        )

        supermarket_distance = st.number_input(
            "Supermarket Distance (m)",
            min_value=0,
            value=0
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

    data = {
        "property_type": property_type,
        "city": city,
        "province": province,
        "nearest_city": nearest_city,
        "livable_surface": livable_surface,
        "total_surface": total_surface,
        "bedrooms": bedrooms,
        "build_year": build_year,
        "latitude": latitude,
        "longitude": longitude,
        "energy_consumption": energy_consumption
    }

    errors, warnings = validate_inputs(data)

    # clear old validation
    st.session_state.errors.clear()
    st.session_state.warnings.clear()

    st.session_state.errors.update(errors)
    st.session_state.warnings.update(warnings)

    # stop if errors
    if errors:
        st.rerun()

    # warnings
    for warning in st.session_state.warnings.values():
        st.warning(warning)

    # ======================
    # PAYLOAD
    # ======================
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
            "Prediction completed!"
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