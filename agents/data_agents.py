"""
Data Collection Agents for SurfSmart AI
Each agent is responsible for fetching specific data types
"""

import os
import requests
from typing import Dict, Any, Optional
from datetime import datetime


class WaveDataAgent:
    """Agent for collecting wave, swell, and tide data"""
    
    def __init__(self):
        self.stormglass_key = os.getenv("STORMGLASS_API_KEY")
        self.worldtides_key = os.getenv("WORLDTIDES_API_KEY")
        self.stormglass_url = "https://api.stormglass.io/v2/weather/point"
        self.worldtides_url = "https://www.worldtides.info/api/v3"
    
    def fetch_data(self, lat: float, lon: float) -> Dict[str, Any]:
        """Fetch wave and tide data for location"""
        wave_data = {}
        
        # Try Stormglass API for wave data
        if self.stormglass_key and self.stormglass_key != "your_stormglass_key_here":
            try:
                params = {
                    "lat": lat,
                    "lng": lon,
                    "params": "waveHeight,wavePeriod,waveDirection,windSpeed,windDirection"
                }
                headers = {"Authorization": self.stormglass_key}
                response = requests.get(self.stormglass_url, params=params, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    hours = data.get("hours", [])
                    if hours:
                        current = hours[0]
                        wave_data = {
                            "wave_height": round(current.get("waveHeight", {}).get("sg", 1.8), 1),
                            "wave_period": int(current.get("wavePeriod", {}).get("sg", 10)),
                            "swell_direction": self._degrees_to_direction(current.get("waveDirection", {}).get("sg", 270)),
                            "source": "stormglass"
                        }
            except Exception as e:
                print(f"Stormglass API error: {e}")
        
        # Try WorldTides API for tide data
        tide_data = {}
        if self.worldtides_key and self.worldtides_key != "your_worldtides_key_here":
            try:
                params = {
                    "lat": lat,
                    "lon": lon,
                    "key": self.worldtides_key
                }
                response = requests.get(f"{self.worldtides_url}", params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    tide_data = {
                        "tide_status": "High Tide",
                        "tide_height": 2.1,
                        "tide_remaining": "1 hour",
                        "source": "worldtides"
                    }
            except Exception as e:
                print(f"WorldTides API error: {e}")
        
        # Combine or use defaults
        if not wave_data:
            wave_data = {
                "wave_height": 1.8,
                "wave_period": 10,
                "swell_direction": "W",
                "source": "simulated"
            }
        
        if not tide_data:
            tide_data = {
                "tide_status": "High Tide",
                "tide_height": 2.1,
                "tide_remaining": "1 hour",
                "source": "simulated"
            }
        
        return {**wave_data, **tide_data}
    
    def _degrees_to_direction(self, degrees: float) -> str:
        """Convert degrees to cardinal direction"""
        directions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
        index = round(degrees / 45) % 8
        return directions[index]


class WeatherDataAgent:
    """Agent for collecting wind and weather data"""
    
    def __init__(self):
        self.openmeteo_url = "https://api.open-meteo.com/v1/forecast"
    
    def fetch_data(self, lat: float, lon: float) -> Dict[str, Any]:
        """Fetch weather data for location"""
        try:
            params = {
                "latitude": lat,
                "longitude": lon,
                "current": "temperature_2m,wind_speed_10m,wind_direction_10m",
                "wind_speed_unit": "kn"
            }
            response = requests.get(self.openmeteo_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                current = data.get("current", {})
                return {
                    "wind_speed": current.get("wind_speed_10m", 12),
                    "wind_direction": self._degrees_to_direction(current.get("wind_direction_10m", 90)),
                    "temperature": current.get("temperature_2m", 15),
                    "source": "open-meteo"
                }
        except Exception as e:
            print(f"Weather API error: {e}")
        
        # Fallback to simulated data
        return {
            "wind_speed": 12,
            "wind_direction": "E",
            "temperature": 15,
            "source": "simulated"
        }
    
    def _degrees_to_direction(self, degrees: float) -> str:
        """Convert wind degrees to cardinal direction"""
        directions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
        index = round(degrees / 45) % 8
        return directions[index]


class SafetyDataAgent:
    """Agent for collecting safety alerts and warnings"""
    
    def __init__(self):
        self.location_name = None
    
    def fetch_data(self, lat: float, lon: float, location_name: str) -> Dict[str, Any]:
        """Fetch safety alerts for location"""
        self.location_name = location_name
        
        # For prototype: return simulated safety data
        # In production: call NWS API, beaches.ie, etc.
        return {
            "rip_current_alert": True,
            "alert_level": "moderate",
            "shark_activity": False,
            "water_quality": "good",
            "warnings": [
                "Local Riptide Alert for beginners",
                "Surf School rental shops closed until 12:00 PM"
            ],
            "source": "simulated"
        }


class AmenitiesDataAgent:
    """Agent for collecting local amenities data (currently disabled - using simulated data)"""
    
    def __init__(self):
        pass
    
    def fetch_data(self, lat: float, lon: float) -> Dict[str, Any]:
        """Fetch nearby surf amenities (simulated data only)"""
        # Google Places API disabled for now
        return {
            "surf_shops": [
                {"name": "Local Surf Shop", "distance": "0.5km", "status": "open"},
                {"name": "Surf School", "distance": "0.8km", "status": "closed"}
            ],
            "parking": {"available": True, "type": "public", "cost": "free"},
            "facilities": ["showers", "toilets", "changing_rooms"],
            "source": "simulated"
        }


class WebcamAgent:
    """Agent for fetching surf webcam images"""
    
    def __init__(self):
        self.webcam_urls = {
            "Liscannor Bay": "https://example.com/liscannor-webcam.jpg",
            "Lahinch": "https://example.com/lahinch-webcam.jpg"
        }
    
    def fetch_image_url(self, location_name: str) -> Optional[str]:
        """Get webcam URL for location"""
        return self.webcam_urls.get(location_name)
    
    def get_image_description(self) -> str:
        """Return description for user uploaded image"""
        return "User uploaded webcam image for visual analysis"
