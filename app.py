"""
SurfSmart AI: Multi-Modal Surf Forecast Generator
Streamlit app with LangGraph agent orchestration
"""

import streamlit as st
import os
from PIL import Image
from dotenv import load_dotenv
from agents.forecast_graph import SurfSmartGraph
from agents.webcam_fetcher import WebcamFetcher
import folium
from streamlit_folium import st_folium

# Load environment variables
load_dotenv()

# LangSmith tracing
if os.getenv("LANGCHAIN_TRACING_V2") == "true":
    print("🔍 LangSmith tracing enabled")

# Page configuration
st.set_page_config(
    page_title="SurfSmart AI",
    page_icon="🏄",
    layout="wide"
)

# Location data (for prototype)
LOCATIONS = {
    "Liscannor Bay": {
        "lat": 52.9369, 
        "lon": -9.3981,
        "full_name": "Liscannor Bay, Ireland",
        "description": "Beginner-friendly beach break"
    },
    "Lahinch": {
        "lat": 52.9324, 
        "lon": -9.3477,
        "full_name": "Lahinch, Ireland",
        "description": "Popular surf town, all levels"
    },
    "Bundoran": {
        "lat": 54.4769, 
        "lon": -8.2803,
        "full_name": "Bundoran, Ireland",
        "description": "Premier surf destination"
    }
}

@st.cache_resource
def initialize_graph():
    """Initialize the LangGraph workflow"""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        st.error("⚠️ GEMINI_API_KEY not found. Please set it in .env file.")
        st.stop()
    return SurfSmartGraph(api_key)

@st.cache_resource
def initialize_webcam_fetcher():
    """Initialize the webcam fetcher"""
    return WebcamFetcher()

def create_ireland_map(selected_location=None):
    """Create an interactive map of Ireland with surf spots"""
    # Center map on Ireland
    ireland_map = folium.Map(
        location=[53.4, -7.9],  # Center of Ireland
        zoom_start=7,
        tiles="OpenStreetMap"
    )
    
    # Add markers for each location
    for name, data in LOCATIONS.items():
        # Determine if this location is selected
        is_selected = (selected_location == name)
        
        folium.Marker(
            location=[data["lat"], data["lon"]],
            popup=folium.Popup(
                f"<b>{name}</b><br>{data['description']}<br>Click to select",
                max_width=200
            ),
            tooltip=name,
            icon=folium.Icon(
                color="red" if is_selected else "blue",
                icon="water" if is_selected else "info-sign"
            )
        ).add_to(ireland_map)
    
    return ireland_map

# UI Layout
st.title("🏄 SurfSmart AI: Multi-Modal Forecast Generator")
st.markdown("*Powered by LangGraph Agent Workflow*")
st.markdown("---")

# Initialize graph and webcam fetcher
graph = initialize_graph()
webcam_fetcher = initialize_webcam_fetcher()

# Sidebar configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Skill level selection
    skill_level = st.selectbox(
        "Select Your Skill Level:",
        options=["Beginner", "Intermediate", "Advanced"],
        help="Choose your surfing experience level"
    )
    
    st.markdown("---")
    
    # Image source selection
    image_source = st.radio(
        "Image Source:",
        options=["Upload Image", "Use Live Webcam (Sample)"],
        help="Choose to upload your own image or use a sample webcam image"
    )
    
    st.markdown("---")
    st.info("💡 **Tip:** Click on a marker on the map to select a surf spot!")
    
    # Show agent workflow
    with st.expander("🔄 Agent Workflow"):
        st.markdown("""
        1. **Wave Agent** - Collects wave/tide data
        2. **Weather Agent** - Fetches wind/conditions
        3. **Safety Agent** - Gets alerts & warnings
        4. **Amenities Agent** - Finds local services
        5. **Forecast Agent** - Generates prediction
        """)

# Main content area
st.subheader("🗺️ Select Surf Spot")

# Initialize session state for selected location
if "selected_location" not in st.session_state:
    st.session_state.selected_location = "Lahinch"

# Create and display map with a key based on selected location to force updates
ireland_map = create_ireland_map(st.session_state.selected_location)
map_data = st_folium(
    ireland_map, 
    width=None, 
    height=400, 
    returned_objects=["last_object_clicked"],
    key=f"map_{st.session_state.selected_location}"
)

# Update selected location based on map click
if map_data and map_data.get("last_object_clicked"):
    clicked_lat = map_data["last_object_clicked"]["lat"]
    clicked_lon = map_data["last_object_clicked"]["lng"]
    
    # Find which location was clicked
    for name, data in LOCATIONS.items():
        if abs(data["lat"] - clicked_lat) < 0.01 and abs(data["lon"] - clicked_lon) < 0.01:
            if st.session_state.selected_location != name:
                st.session_state.selected_location = name
                st.rerun()
            break

# Display selected location info
location = st.session_state.selected_location
location_data = LOCATIONS[location]
full_location_name = location_data["full_name"]

col_info1, col_info2, col_info3 = st.columns(3)
with col_info1:
    st.metric("📍 Selected Spot", location)
with col_info2:
    st.metric("📊 Skill Level", skill_level)
with col_info3:
    st.metric("🌊 Description", location_data["description"])

st.markdown("---")

# Image and data section
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📸 Surf Conditions Image")
    
    image = None
    
    if image_source == "Upload Image":
        uploaded_file = st.file_uploader(
            "Choose a webcam snapshot:",
            type=["jpg", "jpeg", "png"],
            help="Upload current surf conditions"
        )
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image", width="stretch")
    else:
        # Fetch sample webcam image based on selected location
        image = webcam_fetcher.fetch_webcam_image(full_location_name, use_sample=True)
        if image:
            st.image(image, caption=f"Sample Webcam - {location}", width="stretch")
            st.caption("📷 Local sample image (onitsurf.com integration coming soon)")
        else:
            st.warning("Failed to load webcam image. Please upload an image instead.")
            st.info(f"Looking for image at: agents/sample_images/{location.lower().replace(' ', '_')}.jpg")

with col2:
    st.subheader("📍 Location Details")
    st.markdown(f"**Location:** {location}")
    st.markdown(f"**Full Name:** {full_location_name}")
    st.markdown(f"**Coordinates:** {location_data['lat']:.4f}, {location_data['lon']:.4f}")
    st.markdown(f"**Skill Level:** {skill_level}")
    st.markdown(f"**Description:** {location_data['description']}")
    
    if image_source == "Use Live Webcam (Sample)":
        st.info("🎥 Using sample webcam image. Production version will fetch live webcams from onitsurf.com")
    else:
        st.info("Upload an image to see the multi-agent workflow in action")

st.markdown("---")

# Generate forecast button
if st.button("🚀 Generate Forecast", type="primary", use_container_width=True):
    if image is None:
        st.error("❌ Please upload an image or select 'Use Live Webcam' to fetch a sample image.")
    else:
        with st.spinner("🔄 Running agent workflow..."):
            # Get location coordinates
            coords = location_data
            
            # Run LangGraph workflow
            result = graph.generate_forecast(
                location=full_location_name,
                latitude=coords["lat"],
                longitude=coords["lon"],
                skill_level=skill_level,
                image=image
            )
            
            if result.get("error"):
                st.error(f"Error: {result['error']}")
            
            if result["forecast"]:
                st.markdown("---")
                st.subheader("🎯 Generated Surf Forecast")
                st.success(result["forecast"])
                
                # Display collected data
                st.markdown("---")
                st.subheader("📊 Data Collected by Agents")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**🌊 Wave Data**")
                    wave = result["wave_data"]
                    st.json({
                        "Height": f"{wave['wave_height']}m",
                        "Period": f"{wave['wave_period']}s",
                        "Direction": wave['swell_direction'],
                        "Tide": wave['tide_status']
                    })
                    
                    st.markdown("**💨 Weather Data**")
                    weather = result["weather_data"]
                    st.json({
                        "Wind Speed": f"{weather['wind_speed']} knots",
                        "Wind Direction": weather['wind_direction'],
                        "Temperature": f"{weather['temperature']}°C"
                    })
                
                with col2:
                    st.markdown("**⚠️ Safety Alerts**")
                    safety = result["safety_data"]
                    for warning in safety["warnings"]:
                        st.warning(warning)
                    
                    st.markdown("**🏪 Local Amenities**")
                    amenities = result["amenities_data"]
                    st.info(f"Found {len(amenities['surf_shops'])} surf shops nearby")
                
                with st.expander("🔍 View All Agent Data"):
                    st.json(result)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
    <p>SurfSmart AI • LangGraph Multi-Agent System</p>
    <p>Powered by Google Gemini API</p>
    </div>
    """,
    unsafe_allow_html=True
)
