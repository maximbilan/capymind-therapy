# CapyMind Therapy

A compassionate AI therapy assistant built with Google ADK, designed to provide immediate mental health support through evidence-based therapeutic approaches. CapyMind offers a safe, non-judgmental space for users to explore their thoughts and feelings while providing practical coping strategies and crisis support.

## 🌟 Features

### Core Capabilities
- **Evidence-Based Therapy**: Incorporates CBT, DBT, ACT, and mindfulness techniques
- **Crisis Support**: Specialized crisis line finder with location-based resources
- **Personalized Care**: Data-driven insights from user profiles and session history
- **Privacy-First**: Local data storage with optional Firestore integration

### Therapeutic Approaches
- **Cognitive Behavioral Therapy (CBT)**: Thought-feeling-behavior analysis and reframing
- **Dialectical Behavior Therapy (DBT)**: Distress tolerance and emotion regulation
- **Acceptance and Commitment Therapy (ACT)**: Values clarification and mindfulness
- **Mindfulness Techniques**: Grounding exercises and present-moment awareness

### Safety Features
- **Crisis Detection**: Automatic risk assessment and crisis intervention
- **Location-Aware Support**: Finds local crisis lines based on user location
- **Emergency Protocols**: Directs users to appropriate emergency services
- **Trauma-Informed Care**: Gentle, validating communication style

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or higher
- Google Cloud Project (for ADK deployment)
- Gemini API key (for debug mode)

### Installation

1. **Clone and setup environment:**
```bash
git clone <repository-url>
cd capymind-session
python -m venv .venv
source .venv/bin/activate
pip install google-adk
pip install google-cloud-firestore
```
2. **Configure API access:**
```bash
export GOOGLE_API_KEY=your-gemini-api-key
```

### Local Development

**Start the web interface:**
```bash
adk web
```

**Command-line chat:**
```bash
adk run capymind_agent
```

## 🏗️ Architecture

### Agent Structure
- **Root Agent**: Main therapy assistant with Gemini 2.5 Flash
- **Crisis Line Agent**: Specialized crisis support and resource finding
- **Data Fetcher Agent**: User profile and session data management

### Tools & Integrations
- **Firestore Integration**: User data storage and retrieval
- **Google Search**: Crisis line and resource discovery
- **Data Formatting**: Human-readable data presentation
- **Session Management**: Persistent conversation history

## 📁 Project Structure

```
capymind-session/
├── capymind_agent/           # Main agent package
│   ├── agent.py              # Root agent configuration
│   ├── prompt.py             # Therapy assistant prompt
│   ├── sug_agents/           # Specialized sub-agents
│   │   ├── crisis_line/      # Crisis support agent
│   │   └── data_fetcher/     # Data management agent
│   └── tools/                # Agent tools
│       ├── firestore_data.py # Firestore integration
│       └── format_data.py    # Data formatting
├── scripts/                  # Deployment scripts
├── main.py                   # FastAPI application
└── requirements.txt          # Dependencies
```
