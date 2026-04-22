# Missing Persons Search & Rescue AI System

A structured multi-agent Streamlit application for CSCI 4800 Exam 3.

This version includes:
- a cleaner project structure
- a polished Streamlit dashboard
- real LLM calls through the OpenAI Responses API
- deterministic fallback logic for demo stability

## Why this design is strong

Each agent has:
1. A clear role
2. A prompt
3. Deterministic logic
4. Optional LLM enhancement

This means the app can demonstrate true LLM-powered agent behavior while still remaining stable if the API key is missing or a network issue occurs.

## Project Structure

```text
search_rescue_exam_project_llm_ui/
├── app.py
├── README.md
├── requirements.txt
├── .env.example
├── agents/
│   ├── __init__.py
│   ├── case_intake_agent.py
│   ├── signal_detection_agent.py
│   ├── search_zone_predictor_agent.py
│   ├── drone_coordination_agent.py
│   └── volunteer_management_agent.py
├── config/
│   ├── __init__.py
│   ├── prompts.py
│   └── scenarios.py
├── core/
│   ├── __init__.py
│   ├── coordinator.py
│   ├── exceptions.py
│   ├── llm_client.py
│   ├── models.py
│   ├── parsers.py
│   └── utils.py
└── ui/
    ├── __init__.py
    └── streamlit_app.py
```

## Install

```bash
pip install -r requirements.txt
```

## Configure

Copy `.env.example` to `.env` and add your API key:

```bash
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-5.4
```

## Run

```bash
streamlit run app.py
```

## Notes for Presentation

- The system uses the OpenAI **Responses API** through the official Python SDK.
- The app can run in **LLM mode** or **fallback mode**.
- This is useful in a live demo because you can show real model output while still protecting against runtime failure.

## Demo Flow

1. Select a scenario
2. Enable **Use LLM Enhancement**
3. Run the search plan
4. Explain how each agent contributes to the final mission plan
