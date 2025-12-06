# 🏄 SurfSmart AI - Multi-Modal Surf Forecast Generator

**Foundations of Generative AI and LLMs - CA2**  
A Streamlit prototype demonstrating multi-modal AI fusion using Google Gemini API

## 📋 Overview

SurfSmart AI combines multiple data sources (text, numerical metrics, and images) to generate personalized surf forecasts. The system demonstrates **multi-modal AI fusion** by analyzing webcam images alongside weather data.

### Features

- 🤖 Multi-modal AI processing (text + image)
- 🎯 Personalized forecasts by skill level
- ⚠️ Safety-first approach
- 📊 Data fusion from multiple sources
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

### Multi-Modal Workflow

1. **Input Layer**
   - 📸 Visual: Webcam image (user upload)
   - 📊 Structured: Wave height, wind, tide data
   - ⚠️ Unstructured: Safety alerts and context

2. **Processing Layer**
   - Prompt engineering (system + user prompts)
   - Gemini API multi-modal processing
   - Skill level personalization

3. **Output Layer**
   - Natural language forecast (3 sentences)
   - Safety warnings
   - Skill-specific advice

---

## 💻 Technical Stack

- **Streamlit**: Web framework
- **Google Gemini API**: Multi-modal AI (gemini-1.5-flash)
- **PIL (Pillow)**: Image processing
- **python-dotenv**: Environment variables
- **LangSmith**: AI tracing (optional)

### Key Functions

- `configure_gemini()`: API setup
- `simulate_surf_data()`: Sample data generation
- `construct_prompt()`: Multi-modal prompt engineering
- `generate_forecast()`: API call and response handling

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
├── app.py              # Main application
├── requirements.txt    # Dependencies
├── .env               # API keys (DO NOT COMMIT!)
├── .env.example       # Template
├── .gitignore         # Git protection
└── README.md          # This file
```

## 🔒 Security

- API keys stored in `.env` file
- `.gitignore` prevents committing sensitive files
- Error handling prevents key exposure

## 📚 CA2 Context

**Course**: Foundations of Generative AI and LLMs  
**Demonstrates**:
- Multi-modal input processing (text + images)
- Prompt engineering
- Safety-conscious AI design
- Data fusion from multiple sources

---

**Built for CA2 - Foundations of Generative AI and LLMs**