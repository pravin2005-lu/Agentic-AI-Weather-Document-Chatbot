# Agentic AI Chatbot — Weather Intelligence & Document Understanding

A Python chatbot with **exactly two specialized agents**:
1. **Weather Intelligence Agent** — current weather and forecasts through OpenWeatherMap; historical weather and last-10-day daily records through Open-Meteo Archive.
2. **Document Understanding Agent** — PDF/TXT extraction, relevant passage retrieval, and grounded question answering.

The LLM-based router chooses the appropriate agent from the meaning of the request. The UI is built with Streamlit and displays tables and Plotly charts.

## Architecture

```text
User question
     |
     v
LLM Agent Router
     |
     +--------------------------+
     |                          |
     v                          v
Weather Intelligence       Document Understanding
     |                          |
OpenWeatherMap             PDF/TXT extraction
(current/forecast)         chunking + retrieval
Open-Meteo Archive              |
(history/10 days)          LLM grounded answer
     |
Pandas table + Plotly chart
     |
     v
Streamlit chatbot UI
```

## Requirements

- Python 3.10+
- Groq API key for LLM routing and document QA
- OpenWeatherMap API key for current weather and forecast
- Internet connection

Historical data is fetched from Open-Meteo Archive, so it does not depend on a paid OpenWeatherMap historical endpoint. Historical availability may have a short data delay.

## Setup (Windows)

```powershell
# 1. Open this project folder in VS Code terminal
python -m venv .venv

# 2. Activate virtual environment
.venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create environment file
copy .env.example .env

# 5. Open .env and add your API keys

# 6. Run the application
streamlit run app.py
```

If PowerShell blocks activation, run:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\activate
```

## API keys

- Groq: https://console.groq.com/keys
- OpenWeatherMap: https://home.openweathermap.org/api_keys

Never commit `.env` or expose API keys in screenshots or GitHub.

## Sample questions

### Weather agent
- What is the weather in Chennai today?
- Give me the forecast for London tomorrow.
- What was the weather in Bengaluru yesterday?
- Show the last 10 days of weather in Chennai as a table.
- Compare the temperature trend in Coimbatore for the last 10 days.

### Document agent
Upload a PDF or TXT first, then ask:
- What skills are mentioned in my resume?
- Summarize my education.
- What projects have I worked on?
- How much work experience is listed?
- Does the document mention SQL?

## Project structure

```text
weather_document_agentic_chatbot/
├── agents/
│   ├── __init__.py
│   ├── weather_agent.py
│   └── document_agent.py
├── services/
│   ├── __init__.py
│   ├── llm.py
│   ├── router.py
│   ├── prompts.py
│   └── document_store.py
├── app.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Design and limitations

- The router uses an LLM to select between the two agents; it is not based solely on keyword rules.
- Document answers are restricted to retrieved text from the uploaded file. Scanned/image-only PDFs are not OCR-processed and may fail text extraction.
- OpenWeatherMap's standard 5-day/3-hour endpoint is aggregated into daily forecast rows; it is not a 10-day forecast.
- Historical daily observations are obtained from Open-Meteo Archive. The app does not fabricate missing weather observations.
- Pie charts are only meaningful when the returned data has a suitable numeric category (for example humidity values); line/bar charts are more appropriate for temperature trends.

## Before GitHub submission

1. Run all sample questions.
2. Test with a real PDF resume and a TXT file.
3. Verify current weather, forecast, historical, and 10-day table.
4. Capture screenshots of the UI, chart, and document Q&A.
5. Confirm `.env` is ignored by Git and no key appears in commits.
6. Push the source to a **public** GitHub repository.
