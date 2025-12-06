"""
SurfSmart AI: Multi-Modal Surf Forecast Generator
A Streamlit application demonstrating multi-modal fusion using Google Gemini API

This project demonstrates how to combine different types of data (text + images)
to create intelligent surf forecasts using Google's Gemini AI model.
Created for CA2 - Foundations of Generative AI and LLMs
"""

# Import all the libraries we need for this project
import streamlit as st  # Main framework for building the web interface
import os  # For accessing environment variables (API keys)
from PIL import Image  # Python Imaging Library - for handling image uploads
import google.generativeai as genai  # Google's Gemini AI SDK
from dotenv import load_dotenv  # Loads environment variables from .env file

# ============================================================================
# ENVIRONMENT SETUP
# ============================================================================
# Load environment variables from .env file
# This needs to happen BEFORE we try to access any environment variables
# The .env file contains our API keys and configuration
load_dotenv()

# Optional: Set up LangSmith tracing if it's enabled in .env
# LangSmith helps us track and debug our AI API calls
# This is super useful for understanding what's being sent to/from the AI
if os.getenv("LANGCHAIN_TRACING_V2") == "true":
    # These environment variables are already set by load_dotenv()
    # Just adding a note that tracing is active
    print("🔍 LangSmith tracing is enabled - AI calls will be logged")


# ============================================================================
# PAGE CONFIGURATION
# ============================================================================
# This sets up the basic appearance of our Streamlit app
# The page_icon gives us a cool surf emoji in the browser tab!
st.set_page_config(
    page_title="SurfSmart AI",
    page_icon="🏄",
    layout="wide"  # Uses full width of browser instead of narrow column
)

# ============================================================================
# FUNCTION: Configure Gemini AI Model
# ============================================================================
def configure_gemini():
    """
    This function sets up the connection to Google's Gemini API.
    It grabs the API key from environment variables (more secure than hardcoding!)
    and initializes the model we'll use for generating forecasts.
    
    Returns:
        A configured Gemini model object ready to generate content
    """
    # Try to get the API key from environment variables
    # This is stored in our .env file and loaded when the app starts
    api_key = os.getenv("GEMINI_API_KEY")
    
    # If we can't find the API key, show an error and stop the app
    # This prevents crashes later when we try to use the API
    if not api_key:
        st.error("⚠️ GEMINI_API_KEY not found in environment variables. Please set it before running the app.")
        st.stop()  # Stops execution here - won't continue until key is added
    
    # Configure the Gemini library with our API key
    genai.configure(api_key=api_key)
    
    # Return the model we want to use - gemini-1.5-flash is fast and good for multimodal tasks
    # Could also use gemini-1.5-pro for more complex reasoning but it's slower
    return genai.GenerativeModel('gemini-1.5-flash')

# ============================================================================
# FUNCTION: Simulate Surf Data from APIs
# ============================================================================
def simulate_surf_data():
    """
    In a real app, this would call actual weather and surf APIs (like Stormglass, NOAA, etc.)
    For this prototype, we're just hardcoding some realistic sample data.
    This simulates what we'd get from multiple data sources:
    - Surf forecasting API (wave height, period)
    - Weather API (wind conditions)
    - Tide data API
    - Local safety alerts
    
    Returns:
        tuple: (location, numerical_metrics, safety_context) - all the data we need
    """
    # Hardcoded location - in real version this would be user-selectable
    location = "Liscannor Bay, Ireland"
    
    # Numerical data that would normally come from surf/weather APIs
    # This is the kind of structured data APIs return
    numerical_metrics = (
        "Wave Height: 1.8 meters, Period: 10s. "  # Wave size and how often they come
        "Wind: 12 knots offshore (E). "  # Wind speed and direction (offshore is good!)
        "Tide: High Tide, 1 hour remaining."  # Tide info affects surf quality
    )
    
    # Unstructured text data - safety warnings and local context
    # This might come from local surf schools, lifeguard APIs, or news feeds
    safety_context = (
        "WARNING: Local Riptide Alert for beginners. "  # Critical safety info!
        "Surf School rental shops closed until 12:00 PM."  # Practical info for planning
    )
    
    # Return all three pieces of simulated data
    return location, numerical_metrics, safety_context

# ============================================================================
# FUNCTION: Build the Prompt for Gemini
# ============================================================================
def construct_prompt(skill_level, numerical_metrics, safety_context):
    """
    This function builds the text prompt that tells Gemini exactly what we want.
    Prompt engineering is super important - the better the prompt, the better the output!
    We're using a system prompt (defines the AI's role) + user prompt (specific task).
    
    Args:
        skill_level: The user's surfing experience (Beginner/Intermediate/Advanced)
        numerical_metrics: The wave/wind/tide data
        safety_context: Safety warnings and local info
    
    Returns:
        str: The complete prompt to send to Gemini
    """
    # System prompt: Defines WHO the AI should act as
    # This sets the "personality" and priorities of the AI assistant
    system_prompt = (
        "You are the SurfSmart AI, a highly experienced and safety-conscious surf forecaster. "
        "Your role is to interpret all provided data (numerical, text, and image) and generate "
        "a concise, natural language forecast. Prioritize safety above all else."
    )
    
    # User prompt: The specific task and data to analyze
    # Using f-strings to inject our variables into the prompt
    user_prompt = (
        f"Based on the following data, write a 3-sentence surf forecast for a {skill_level} surfer:\n\n"
        f"1. Numerical Metrics: {numerical_metrics}\n"
        f"2. Safety & Context: {safety_context}\n"
        f"3. Visual Confirmation: Analyze the attached image to confirm the actual crowd level "
        f"and water surface conditions.\n\n"
        f"Output Constraints:\n"
        f"- Start with the wave quality\n"
        f"- Include a specific safety warning if applicable\n"
        f"- Provide specific advice tailored to the skill level\n"
        f"- Do not use technical jargon"  # Keep it accessible to everyone!
    )
    
    # Combine both prompts into one complete instruction
    full_prompt = f"{system_prompt}\n\n{user_prompt}"
    return full_prompt

# ============================================================================
# FUNCTION: Generate Forecast Using Gemini
# ============================================================================
def generate_forecast(model, prompt, image):
    """
    This is where the magic happens! We send our prompt + image to Gemini's API
    and it analyzes everything to generate a personalized surf forecast.
    This demonstrates MULTI-MODAL AI - combining text and image inputs.
    
    Args:
        model: The configured Gemini model object
        prompt: The text prompt we constructed
        image: The PIL Image object from the user's upload
    
    Returns:
        str: The AI-generated forecast text, or None if there's an error
    """
    try:
        # The generate_content method accepts a list of content parts
        # Here we're passing both text (prompt) and image - this is multi-modal!
        # Gemini can "see" the image and understand it in context with the text
        response = model.generate_content([prompt, image])
        
        # Extract just the text from the response object
        return response.text
    except Exception as e:
        # If something goes wrong (API error, rate limit, etc.), show the error
        # Using exception handling prevents the whole app from crashing
        st.error(f"Error generating forecast: {str(e)}")
        return None

# UI Layout
st.title("🏄 SurfSmart AI: Multi-Modal Forecast Generator")
st.markdown("---")

# Sidebar configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    skill_level = st.selectbox(
        "Select Your Skill Level:",
        options=["Beginner", "Intermediate", "Advanced"],
        help="Choose your surfing experience level for personalized forecasts"
    )
    st.markdown("---")
    st.info("💡 **Tip:** Upload a clear image of the surf conditions for best results.")

# Main content area
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📸 Upload Surf Conditions Image")
    uploaded_file = st.file_uploader(
        "Choose a webcam snapshot of the surf spot:",
        type=["jpg", "jpeg", "png"],
        help="Upload an image showing current surf conditions"
    )
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Surf Conditions", use_container_width=True)

with col2:
    st.subheader("📊 Simulated Data Sources")
    location, numerical_metrics, safety_context = simulate_surf_data()
    st.markdown(f"**📍 Location:** {location}")
    st.markdown(f"**🌊 Conditions:**")
    st.code(numerical_metrics, language=None)
    st.markdown(f"**⚠️ Safety Alerts:**")
    st.warning(safety_context)

st.markdown("---")

# Generate forecast button
if st.button("🚀 Generate Forecast", type="primary", use_container_width=True):
    if uploaded_file is None:
        st.error("❌ Please upload an image before generating a forecast.")
    else:
        with st.spinner("🔄 Processing multi-modal data and generating forecast..."):
            model = configure_gemini()
            prompt = construct_prompt(skill_level, numerical_metrics, safety_context)
            forecast = generate_forecast(model, prompt, image)
            
            if forecast:
                st.markdown("---")
                st.subheader("🎯 Generated Surf Forecast")
                st.success(forecast)
                
                st.markdown("---")
                st.subheader("📈 Visual Infographic")
                st.info(
                    "🎨 **Visual Infographic Placeholder:**\n\n"
                    "Status Graphic would be generated here showing:\n"
                    "- Wave quality indicator (color-coded)\n"
                    "- Safety status badge\n"
                    "- Skill level compatibility meter\n"
                    "- Real-time condition summary"
                )
                
                with st.expander("🔍 View Processing Details"):
                    st.markdown(f"**Skill Level:** {skill_level}")
                    st.markdown(f"**Location:** {location}")
                    st.markdown("**Multi-Modal Inputs:**")
                    st.markdown("- ✅ Numerical weather data")
                    st.markdown("- ✅ Safety context text")
                    st.markdown("- ✅ Visual webcam image")
                    st.markdown("**AI Model:** Google Gemini 1.5 Flash")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
    <p>SurfSmart AI • Multi-Modal Surf Forecasting System</p>
    <p>Powered by Google Gemini API</p>
    </div>
    """,
    unsafe_allow_html=True
)
