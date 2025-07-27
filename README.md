# Aegis Financial Assistant

> An AI-powered financial management platform that transforms receipt processing, spending analysis, and personal finance insights through intelligent automation.

## 🌟 Platform Overview

Aegis Financial Assistant is a comprehensive financial management ecosystem that combines cutting-edge AI technology with practical financial tools. The platform automatically processes receipts, provides intelligent spending insights, generates proactive financial alerts, and even suggests recipes based on your grocery purchases.

### Key Capabilities
- 📸 **Smart Receipt Processing**: OCR-powered receipt scanning with automatic categorization
- 🚀 **Ability to scan crumpled receipts in mulitple languages, payment app screenshots and handwritted bills**
- 🧠 **AI Financial Analysis**: Natural language queries for spending insights, trends and planning
- 🔔 **Proactive Monitoring**: Automated alerts for subscription changes, duplicate charges, spending patterns and opportunities in the market.
- 🍳 **Domain specific Intelligence**: Smart meal suggestions based on grocery purchases, smart saving plans based on pattern recognition
- **Smart subscription manager** tracks recurring subscriptions and payments and guides users to reduce spending
- 💳 **Google Wallet Integration**: Digital passes for budgets, shopping lists, and warranty tracking
- 📅 **Calendar Integration**: Automated reminders for warranties and payment due dates

### Features in development
- 

## 🏗️ Architecture

Aegis consists of three main components working together:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│                 │    │                 │    │                 │
│  Frontend Apps  │◄──►│   Aegis Agent   │◄──►│ Backend Service │
│                 │    │    (Aegnt)      │    │                 │
│  • React Native │    │                 │    │ • FastAPI       │
│  • Web Test UI  │    │ • Multi-Agent   │    │ • Firebase      │
│  • Mobile App   │    │ • AI Analysis   │    │ • OCR Service   │
│                 │    │ • Tool Execution│    │ • Integrations  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📁 Project Structure

```
project-aegis/
├── README.md                     # This file - global overview
├── USE_CASES.md                  # Comprehensive use cases and user scenarios
├── SETUP.md                      # Quick setup guide
│
├── backend/                      # FastAPI backend service
│   ├── README.md                 # Backend-specific documentation
│   ├── main.py                   # FastAPI application entry point
│   ├── requirements.txt          # Python dependencies
│   ├── core/                     # Core modules (auth, config, database)
│   ├── models/                   # Pydantic data models
│   ├── routers/                  # API route handlers
│   ├── services/                 # Business logic services
│   └── creds/                    # Credentials and API keys
│
├── aegnt/                        # AI Agent service
│   ├── README.md                 # Agent-specific documentation
│   ├── main_agent.py             # Multi-agent orchestration
│   ├── tool_definitions.py       # AI tool implementations
│   ├── config.py                 # Agent configuration
│   └── requirements.txt          # Python dependencies
│
├── aegis-frontend/               # React Native mobile application
│   ├── README.md                 # Frontend documentation
│   ├── app.json                  # Expo configuration
│   ├── package.json              # Node.js dependencies
│   └── app/                      # React Native screens and components
│
├── test-ui/                      # Web-based testing interface
│   ├── index.html                # Simple web UI for testing
│   └── package.json              # Web UI dependencies
│
└── sample_receipts/              # Sample receipt images for testing
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+ (for frontend)
- Firebase project with Firestore
- Google Gemini AI API key
- Google Wallet API credentials (optional)

### 1. Backend Setup
```bash
cd backend
python -m venv backend-venv
source backend-venv/bin/activate  # Windows: backend-venv\Scripts\activate
pip install -r requirements.txt
# Configure environment variables (see backend/README.md)
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Agent Setup
```bash
cd aegnt
python -m venv aegnt-venv
source aegnt-venv/bin/activate  # Windows: aegnt-venv\Scripts\activate
pip install -r requirements.txt
# Configure environment variables (see aegnt/README.md)
python main_agent.py
```

### 3. Test the Platform
```bash
cd test-ui
npm install
npm start
# Open http://localhost:3000 to test the platform
```

**📖 For detailed setup instructions, see [SETUP.md](SETUP.md)**

## 📚 Documentation

### Component Documentation
- **[Backend Documentation](backend/README.md)** - FastAPI service setup, API endpoints, and configuration
- **[Agent Documentation](aegnt/README.md)** - AI agent architecture, tools, and capabilities  
- **[Frontend Documentation](aegis-frontend/README.md)** - React Native mobile app setup and features

### User Documentation
- **[Use Cases & User Scenarios](USE_CASES.md)** - Comprehensive guide to platform capabilities and user workflows
- **[API Test Commands](API_TEST_COMMANDS.md)** - Sample API calls and testing procedures
- **[Setup Guide](SETUP.md)** - Quick setup instructions for development

## 🔧 Development Workflow

### Running the Full Stack
1. **Start Backend** (Port 8000):
   ```bash
   cd backend && uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Start Agent** (Port 8001):
   ```bash
   cd aegnt && python main_agent.py
   ```

3. **Start Temporary Web UI** (Port 3000):
   ```bash
   cd test-ui && npm start
   ```
4. **Start Frontend**:
    ```bash
    cd frontend && npx expo start
    ```

### Testing the Platform
- **Test UI**: http://localhost:3000
- **Backend API Docs**: http://localhost:8000/docs
- **Agent Health Check**: http://localhost:8001/health*
- **Frontend Homepage**

## 🎯 Core Features Demo

### 1. Receipt Processing
```bash
# Upload a receipt photo
curl -X POST http://localhost:8000/api/v1/transactions/process \
  -H "Authorization: Bearer your-token" \
  -F "file=@sample_receipts/grocery.jpg" \
  -F "user_id=test-user"
```

### 2. Financial Analysis
```bash
# Ask natural language financial questions
curl -X POST http://localhost:8001/invoke \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-user",
    "id_token": "your-token", 
    "message": "What did I spend the most on last month?"
  }'
```

### 3. Recipe Suggestions
```bash
# Get recipe suggestions based on grocery purchases
curl -X POST http://localhost:8001/invoke \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-user",
    "id_token": "your-token",
    "message": "What can I cook with my recent grocery purchases?"
  }'
```

## 🔐 Security & Privacy

- **Authentication**: Firebase-based user authentication with JWT tokens
- **Data Privacy**: User data is processed securely and stored in Firebase Firestore
- **API Security**: All endpoints protected with authentication middleware
- **Secure Storage**: Sensitive credentials managed through environment variables

## 🌍 Deployment

### Production Deployment
- **Backend**: Deploy to cloud platforms (Google Cloud, AWS, Azure)
- **Agent**: Can be deployed as a containerized service
- **Frontend**: Build for mobile app stores or web deployment
- **Database**: Firebase Firestore for scalable, real-time data storage

### Environment Configuration
Each component requires specific environment variables for production:
- Backend: Firebase credentials, API keys, database connections
- Agent: AI service keys, backend API endpoints
- Frontend: Backend URLs, Firebase configuration

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Follow component-specific development guidelines** (see individual README files)
4. **Test your changes** across all components
5. **Submit a pull request** with detailed description

### Development Guidelines
- Follow existing code structure and patterns
- Add comprehensive documentation for new features
- Include tests for new functionality
- Update relevant README files for changes

## 📊 Project Status

- ✅ **Backend Service**: Fully functional with comprehensive API
- ✅ **AI Agent**: Multi-agent system with intelligent financial analysis
- ✅ **Receipt Processing**: OCR and automatic categorization working
- ✅ **Financial Analytics**: Natural language query processing
- ✅ **Proactive Insights**: Automated pattern detection and notifications
- ✅ **Recipe Suggestions**: AI-powered meal recommendations
- ✅ **Google Wallet Integration**: Automatically generates passes that can be issued to specific users
- 🔧 **Mobile App**: React Native frontend in development
- 🔧 **Advanced Integrations**: Google Maps and Calendar features expanding

## 🆘 Support & Troubleshooting

### Common Issues
1. **Services not starting**: Check environment variables and dependencies
2. **API connection errors**: Verify backend and agent are running on correct ports
3. **Authentication failures**: Ensure Firebase credentials are properly configured
4. **AI analysis issues**: Verify Gemini API key and quota availability

### Getting Help
- Check component-specific README files for detailed troubleshooting
- Review API documentation at http://localhost:8000/docs
- Ensure all required environment variables are configured
- Verify external service connectivity (Firebase, Gemini AI)

## 📄 License

This project is part of the Aegis Financial Assistant platform. See individual component licenses for specific terms.

---

**🚀 Ready to transform your financial management experience?**  
Start with the [Setup Guide](SETUP.md) or explore the [Use Cases](USE_CASES.md) to understand the full potential of Aegis Financial Assistant.
