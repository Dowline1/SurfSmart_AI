# 🏄 SurfSmart AI - Multi-Modal Surf Forecast Generator

**Foundations of Generative AI and LLMs - CA2**  
A Streamlit prototype with LangGraph multi-agent orchestration using Google Gemini API

## 📋 Overview

SurfSmart AI uses a **LangGraph agent workflow** to collect data from multiple sources and generate personalized surf forecasts. Each specialized agent handles a specific data type, demonstrating **multi-modal AI fusion** with text, numerical, and image inputs.

### Features

- 🤖 LangGraph multi-agent orchestration
- 🌊 Specialized agents for wave, weather, safety, and amenities data
- 🎯 Personalized forecasts by skill level
- ⚠️ Safety-first approach
- 📊 Real-time data fusion
- 🔍 LangSmith tracing for debugging

---

## 🚀 Setup

### Prerequisites
- Python 3.10+
- Google Gemini API key ([Get yours here](https://makersuite.google.com/app/apikey))

### Installation

```powershell
# Install dependencies
pip install -r requirements.txt

# Edit .env file and add your API keys
# GEMINI_API_KEY=your_key_here

# Run the app
streamlit run app.py
```

---

## 🏗️ Architecture

### LangGraph Agent Workflow

**Agent Pipeline:**
1. **Wave Data Agent** → Fetches wave height, swell period, tide data
2. **Weather Data Agent** → Collects wind speed/direction, temperature
3. **Safety Data Agent** → Retrieves riptide alerts, warnings
4. **Amenities Data Agent** → Finds surf shops, parking, facilities
5. **Forecast Generation** → Gemini analyzes all data + image

**Data Sources:**
- 📊 Structured: Stormglass, Open-Meteo, WorldTides APIs
- ⚠️ Unstructured: Safety alerts, local advisories
- 📸 Visual: Webcam image (user upload)

**Multi-Modal Output:**
- Natural language forecast (3 sentences)
- Safety warnings
- Skill-specific advice
- Collected data visualization

---

## 💻 Technical Stack

- **Streamlit**: Web framework
- **LangGraph**: Agent orchestration workflow
- **LangChain**: Agent framework
- **Google Gemini API**: Multi-modal AI (gemini-1.5-flash)
- **PIL (Pillow)**: Image processing
- **python-dotenv**: Environment variables
- **LangSmith**: AI tracing (optional)
- **Requests/HTTPX**: API calls

### Agent Architecture

```
agents/
├── __init__.py
├── data_agents.py      # Specialized data collection agents
└── forecast_graph.py   # LangGraph workflow orchestrator
```

**Agents:**
- `WaveDataAgent`: Wave/swell/tide data
- `WeatherDataAgent`: Wind/temperature data  
- `SafetyDataAgent`: Alerts and warnings
- `AmenitiesDataAgent`: Local services
- `WebcamAgent`: Image handling

---

## 📊 Testing

Test with different combinations:
- **Beginner** + rough seas image → Safety warnings
- **Intermediate** + moderate waves → Balanced advice
- **Advanced** + clean conditions → Technical details

LangSmith tracing (optional) provides prompt visibility and debugging.

---

## 📁 Project Structure

```
SurfSmart_AI/
├── agents/
│   ├── __init__.py
│   ├── data_agents.py       # Data collection agents
│   └── forecast_graph.py    # LangGraph workflow
├── app.py                   # Streamlit interface
├── requirements.txt         # Dependencies
├── .env                     # API keys (DO NOT COMMIT!)
├── .env.example            # Template
├── .gitignore              # Git protection
└── README.md               # This file
```

## 🔒 Security

- API keys stored in `.env` file
- `.gitignore` prevents committing sensitive files
- Error handling prevents key exposure

## 📚 CA2 Context

**Course**: Foundations of Generative AI and LLMs  
**Demonstrates**:
- LangGraph multi-agent orchestration
- Agent-based data collection workflow
- Multi-modal input processing (text + images)
- Prompt engineering
- Safety-conscious AI design

---

**Built for CA2 - Foundations of Generative AI and LLMs**