# 🚁 Missing Persons Search & Rescue AI System

A multi-agent AI system that simulates real-world search-and-rescue coordination using both deterministic logic and LLM-enhanced reasoning.

Built for **CSCI 4800 – Intelligent Systems**

---

## 🧠 Overview

This project models a **search-and-rescue operation** using a pipeline of specialized agents. Each agent contributes to generating a complete mission plan for locating a missing person.

The system combines:
- **Rule-based logic** (reliable baseline)
- **LLM-enhanced reasoning** (context-aware improvements)

This hybrid design ensures:
- consistent results during demos
- intelligent decision-making when the LLM is enabled

---

## ⚙️ Agent Architecture

### 1. Case Intake Agent
- Validates user input
- Structures the case
- (LLM) Generates risk flags and urgency level

### 2. Signal Detection Agent
- Interprets phone/wearable signals
- Estimates signal confidence
- Recommends priority zones

### 3. Search Zone Predictor Agent
- Combines terrain, behavior, weather, and time
- Ranks zones by probability
- (LLM) Refines ranking and reasoning

### 4. Drone Coordination Agent
- Assigns drones to top zones
- Selects search patterns
- Generates aerial objectives

### 5. Volunteer Management Agent
- Assigns ground teams
- Matches team roles to conditions
- Generates operational instructions

---

## 🧩 Project Structure

search_rescue_exam_project/
├── app.py
├── requirements.txt
├── README.md
├── .env.example
├── agents/
├── config/
├── core/
└── ui/

---

## 🖥️ UI Features

- Interactive case input form
- Scenario presets for quick demos
- Real-time loading status panel
- Tabbed agent outputs
- Clean dashboard layout

---

## 🤖 LLM Integration

Uses the OpenAI Responses API.

- Each agent has its own prompt
- Structured JSON outputs
- Deterministic fallback if LLM fails

---

## 🔐 Setup

1. Install dependencies:

pip install -r requirements.txt

2. Configure environment:

OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-5.4

3. Run:

streamlit run app.py

---

## 🎯 Key Features

- Multi-agent system design
- LLM + deterministic hybrid architecture
- Robust error handling
- Streamlit dashboard with live feedback

---

## 👤 Author

Rodney Santana  
University of North Georgia  

---

## ⚠️ Disclaimer

Academic simulation only. Not for real-world emergency deployment.
