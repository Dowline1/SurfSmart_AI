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
    "Liscannor Bay, Ireland": {"lat": 52.9369, "lon": -9.3981},
    "Lahinch, Ireland": {"lat": 52.9324, "lon": -9.3477},
    "Bundoran, Ireland": {"lat": 54.4769, "lon": -8.2803}
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
    
    # Location selection
    location = st.selectbox(
        "Select Location:",
        options=list(LOCATIONS.keys()),
        help="Choose a surf spot"
    )
    
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
    st.info("💡 **Tip:** Sample webcam images are used for testing. Live webcam fetching from onitsurf.com coming soon!")
    
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
            st.image(image, caption="Uploaded Image", use_container_width=True)
    else:
        # Fetch sample webcam image
        with st.spinner("Fetching webcam image..."):
            image = webcam_fetcher.fetch_webcam_image(location, use_sample=True)
            if image:
                st.image(image, caption=f"Sample Webcam - {location}", use_container_width=True)
                st.caption("📷 Using sample image from web (onitsurf.com integration coming soon)")
            else:
                st.warning("Failed to fetch webcam image. Please upload an image instead.")

with col2:
    st.subheader("📍 Location Information")
    coords = LOCATIONS[location]
    st.markdown(f"**Location:** {location}")
    st.markdown(f"**Coordinates:** {coords['lat']:.4f}, {coords['lon']:.4f}")
    st.markdown(f"**Skill Level:** {skill_level}")
    
    if image_source == "Use Live Webcam (Sample)":
        st.info("🎥 Using sample webcam image. The production version will automatically fetch live webcam screenshots from onitsurf.com")
    else:
        st.info("Data will be collected from multiple agents when you generate the forecast.")

st.markdown("---")

# Generate forecast button
if st.button("🚀 Generate Forecast", type="primary", use_container_width=True):
    if image is None:
        st.error("❌ Please upload an image or select 'Use Live Webcam' to fetch a sample image.")
    else:
        with st.spinner("🔄 Running agent workflow..."):
            # Get location coordinates
            coords = LOCATIONS[location]
            
            # Run LangGraph workflow
            result = graph.generate_forecast(
                location=location,
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
