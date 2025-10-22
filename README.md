# CapyMind Session

A compassionate AI therapy assistant built with Google ADK, designed to provide immediate mental health support through evidence-based therapeutic approaches. CapyMind offers a safe, non-judgmental space for users to explore their thoughts and feelings while providing practical coping strategies and crisis support.

## 🌟 Features

### Core Capabilities
- **Evidence-Based Therapy**: Incorporates CBT, DBT, ACT, and mindfulness techniques
- **Crisis Support**: Specialized crisis line finder with location-based resources
- **Personalized Care**: Data-driven insights from user profiles and session history
- **Privacy-First**: Local data storage with optional Firestore integration
- **Multiple Deployment Options**: Local chat, Cloud Run, and Google Cloud Functions

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
- Gemini API key (for fallback mode)

### Installation

1. **Clone and setup environment:**
```bash
git clone <repository-url>
cd capymind-session
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. **Install dependencies:**
```bash
pip install -e .
# For ADK deployment (recommended)
pip install -e .[adk]
```

3. **Configure API access:**
```bash
export GOOGLE_API_KEY=your-gemini-api-key
```

### Local Development

**Start the web interface:**
```bash
python main.py
```
Access the web interface at `http://localhost:8080`

**Command-line chat:**
```bash
capymind-session chat
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

### Deployment Options

#### Google Cloud Run
```bash
# Deploy using ADK
adk deploy cloud_run \
  --project=your-project-id \
  --region=us-central1 \
  --service_name=capymind-agent \
  --app_name=capymind_agent \
  capymind_agent
```

#### 3. Local Development
```bash
python main.py
```

## 💬 Usage Examples

### Interactive Chat Commands
- `/journal <text>` - Save a private journal entry
- `/recent [n]` - Show last n journal entries (default 5)
- `/mood <label> <1-10>` - Log your mood with intensity
- `/moodsum [n]` - Show mood averages over last n logs (default 20)
- `/plan <mood>` - Get coping strategies for specific mood

### API Usage
```bash
curl -X POST "https://your-region-your-project.cloudfunctions.net/capymind-agent-chat" \
  -H 'Content-Type: application/json' \
  -d '{"message": "I feel anxious about my presentation tomorrow. Can you help me prepare?"}'
```

### Example Conversations
**User:** "I'm feeling overwhelmed with work stress"
**CapyMind:** "That sounds really heavy—thanks for sharing it. Would a brief grounding exercise help right now, or should we explore what's making work feel so overwhelming?"

**User:** "I can't stop worrying about everything"
**CapyMind:** "I hear how exhausting that constant worry must be. Two small options: 1) a 3-breath reset to pause the spiral, 2) jotting down one specific worry to revisit later. What feels manageable right now?"

## 🔧 Configuration

### Environment Variables
- `CAPY_GEMINI_API_KEY`: Your Gemini API key
- `CAPY_GEMINI_MODEL`: Model to use (default: gemini-2.5-flash)
- `PORT`: Server port (default: 8080)

### Data Storage
- **Local**: Data stored in `~/.capymind_session/`
- **Cloud**: Optional Firestore integration for persistent user profiles

### Security & Privacy
- All conversations are private and encrypted
- User data is stored locally by default
- Crisis situations trigger appropriate safety protocols
- No data is shared without explicit user consent

## 🛡️ Safety & Crisis Support

### Crisis Detection
The system automatically detects crisis situations and:
1. Assesses immediate safety with direct questions
2. Activates specialized crisis support agents
3. Provides location-specific crisis line numbers
4. Offers to stay with users during crisis calls

### Emergency Resources
- **US**: 988 (Suicide & Crisis Lifeline), 911 for emergencies
- **Canada**: 1-833-456-4566 (Talk Suicide Canada)
- **UK/ROI**: 116 123 (Samaritans), 999/112 for emergencies
- **EU**: 112 for emergencies
- **Crisis Text Line**: Text HOME to 741741

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

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## ⚠️ Important Disclaimers

- **Not a replacement for professional therapy**: This assistant provides support but is not a substitute for licensed mental health professionals
- **Crisis situations**: In emergencies, always contact local emergency services (911, 112, etc.)
- **Professional help**: For ongoing mental health concerns, please consult with qualified therapists or counselors

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For technical issues or questions about the project, please open an issue on GitHub. For mental health emergencies, please contact your local crisis line or emergency services.
