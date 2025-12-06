"""
LangGraph workflow for SurfSmart AI
Orchestrates data collection and forecast generation
"""

from typing import TypedDict, Annotated, Dict, Any
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from PIL import Image
import operator

from agents.data_agents import (
    WaveDataAgent,
    WeatherDataAgent,
    SafetyDataAgent,
    AmenitiesDataAgent,
    WebcamAgent
)


class ForecastState(TypedDict):
    """State that flows through the graph"""
    # Input
    location: str
    latitude: float
    longitude: float
    skill_level: str
    image: Any
    
    # Collected data
    wave_data: Dict[str, Any]
    weather_data: Dict[str, Any]
    safety_data: Dict[str, Any]
    amenities_data: Dict[str, Any]
    
    # Output
    forecast: str
    error: str


class SurfSmartGraph:
    """LangGraph orchestrator for surf forecast generation"""
    
    def __init__(self, gemini_api_key: str):
        self.gemini_api_key = gemini_api_key
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=gemini_api_key
        )
        
        # Initialize agents
        self.wave_agent = WaveDataAgent()
        self.weather_agent = WeatherDataAgent()
        self.safety_agent = SafetyDataAgent()
        self.amenities_agent = AmenitiesDataAgent()
        self.webcam_agent = WebcamAgent()
        
        # Build graph
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        workflow = StateGraph(ForecastState)
        
        # Add nodes for each agent
        workflow.add_node("collect_wave_data", self._collect_wave_data)
        workflow.add_node("collect_weather_data", self._collect_weather_data)
        workflow.add_node("collect_safety_data", self._collect_safety_data)
        workflow.add_node("collect_amenities_data", self._collect_amenities_data)
        workflow.add_node("generate_forecast", self._generate_forecast)
        
        # Define edges (workflow)
        workflow.set_entry_point("collect_wave_data")
        workflow.add_edge("collect_wave_data", "collect_weather_data")
        workflow.add_edge("collect_weather_data", "collect_safety_data")
        workflow.add_edge("collect_safety_data", "collect_amenities_data")
        workflow.add_edge("collect_amenities_data", "generate_forecast")
        workflow.add_edge("generate_forecast", END)
        
        return workflow.compile()
    
    def _collect_wave_data(self, state: ForecastState) -> ForecastState:
        """Node: Collect wave and tide data"""
        wave_data = self.wave_agent.fetch_data(state["latitude"], state["longitude"])
        state["wave_data"] = wave_data
        return state
    
    def _collect_weather_data(self, state: ForecastState) -> ForecastState:
        """Node: Collect weather data"""
        weather_data = self.weather_agent.fetch_data(state["latitude"], state["longitude"])
        state["weather_data"] = weather_data
        return state
    
    def _collect_safety_data(self, state: ForecastState) -> ForecastState:
        """Node: Collect safety alerts"""
        safety_data = self.safety_agent.fetch_data(
            state["latitude"], 
            state["longitude"],
            state["location"]
        )
        state["safety_data"] = safety_data
        return state
    
    def _collect_amenities_data(self, state: ForecastState) -> ForecastState:
        """Node: Collect amenities data"""
        amenities_data = self.amenities_agent.fetch_data(state["latitude"], state["longitude"])
        state["amenities_data"] = amenities_data
        return state
    
    def _generate_forecast(self, state: ForecastState) -> ForecastState:
        """Node: Generate forecast using all collected data"""
        try:
            # Build comprehensive prompt
            prompt = self._build_prompt(state)
            
            # For multi-modal with image, we need to use the generativeai library directly
            import google.generativeai as genai
            genai.configure(api_key=self.gemini_api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # Generate forecast with text + image
            response = model.generate_content([prompt, state["image"]])
            state["forecast"] = response.text
            
        except Exception as e:
            state["error"] = f"Forecast generation failed: {str(e)}"
            state["forecast"] = "Unable to generate forecast at this time."
        
        return state
    
    def _build_prompt(self, state: ForecastState) -> str:
        """Build the prompt from all collected data"""
        wave = state["wave_data"]
        weather = state["weather_data"]
        safety = state["safety_data"]
        amenities = state["amenities_data"]
        
        system_prompt = (
            "You are SurfSmart AI, an experienced surf forecaster prioritizing safety. "
            "Analyze all provided data (numerical, text, and image) to generate a concise forecast."
        )
        
        numerical_metrics = (
            f"Wave Height: {wave['wave_height']}m, Period: {wave['wave_period']}s, "
            f"Direction: {wave['swell_direction']}. "
            f"Wind: {weather['wind_speed']} knots {weather['wind_direction']}. "
            f"Tide: {wave['tide_status']}, {wave['tide_remaining']} remaining. "
            f"Temperature: {weather['temperature']}°C."
        )
        
        safety_context = " ".join(safety["warnings"])
        
        amenities_info = f"Nearby: {len(amenities['surf_shops'])} surf shops. Parking available."
        
        user_prompt = (
            f"Generate a 3-sentence surf forecast for a {state['skill_level']} surfer at {state['location']}:\n\n"
            f"1. Numerical Metrics: {numerical_metrics}\n"
            f"2. Safety & Context: {safety_context}\n"
            f"3. Local Amenities: {amenities_info}\n"
            f"4. Visual: Analyze the image for crowd levels and surface conditions.\n\n"
            f"Requirements:\n"
            f"- Start with wave quality assessment\n"
            f"- Include safety warnings if applicable\n"
            f"- Provide skill-specific advice\n"
            f"- Use accessible language"
        )
        
        return f"{system_prompt}\n\n{user_prompt}"
    
    def generate_forecast(self, 
                         location: str,
                         latitude: float,
                         longitude: float,
                         skill_level: str,
                         image: Image.Image) -> Dict[str, Any]:
        """
        Run the complete forecast generation workflow
        
        Args:
            location: Location name
            latitude: Location latitude
            longitude: Location longitude
            skill_level: User's skill level
            image: PIL Image of surf conditions
            
        Returns:
            Complete forecast with all collected data
        """
        initial_state = ForecastState(
            location=location,
            latitude=latitude,
            longitude=longitude,
            skill_level=skill_level,
            image=image,
            wave_data={},
            weather_data={},
            safety_data={},
            amenities_data={},
            forecast="",
            error=""
        )
        
        # Run the graph
        result = self.graph.invoke(initial_state)
        
        return {
            "forecast": result["forecast"],
            "wave_data": result["wave_data"],
            "weather_data": result["weather_data"],
            "safety_data": result["safety_data"],
            "amenities_data": result["amenities_data"],
            "error": result.get("error", "")
        }
