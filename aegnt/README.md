# Aegis Agent (Aegnt)

The Aegis Agent (Aegnt) is an intelligent AI assistant powered by Google's ADK (Agent Development Kit) and Gemini AI. It provides personalized financial guidance, proactive insights, and comprehensive transaction analysis for the Aegis Financial Assistant platform.

## 🤖 Features

- **Multi-Agent Architecture**: Specialized sub-agents for different financial tasks
- **Intelligent Financial Analysis**: AI-powered spending insights and trend detection
- **Recipe Suggestions**: Smart recipe recommendations based on grocery purchases
- **Proactive Notifications**: Automated alerts for spending patterns and opportunities
- **Natural Language Processing**: Conversational interface for financial queries
- **Transaction Categorization**: Smart categorization of expenses and income
- **Virtual Pantry**: Automatic ingredient detection from grocery receipts

## 🏗️ Architecture

### Sub-Agent System
The Aegnt uses a specialized multi-agent architecture:

- **Transaction Agent**: Handles financial data analysis and queries
- **Proactive Agent**: Monitors spending patterns and generates insights
- **Creative Agent**: Provides recipe suggestions and lifestyle recommendations
- **Main Agent**: Orchestrates sub-agents and handles general queries

## 📋 Prerequisites

- Python 3.8+
- Google ADK (Agent Development Kit)
- Gemini AI API access
- Spoonacular API key (optional, for enhanced recipes)
- Access to Aegis Backend API

## 🛠️ Installation

1. **Navigate to the agent directory**
   ```bash
   cd /path/to/project-aegis/aegnt
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv aegnt-venv
   source aegnt-venv/bin/activate  # On Windows: aegnt-venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the aegnt directory:
   ```env
   # API Configuration
   GEMINI_API_KEY=your-gemini-api-key
   SPOONACULAR_API_KEY=your-spoonacular-api-key
   
   # Backend Configuration
   BACKEND_API_BASE_URL=http://localhost:8000/api/v1
   BACKEND_API_TOKEN=your-backend-api-token
   
   # Agent Configuration
   AGENT_PORT=8001
   AGENT_HOST=0.0.0.0
   ```

## 🚦 Running the Agent

1. **Start the agent service**
   ```bash
   python main_agent.py
   ```

2. **Access the agent**
   - Agent API: http://localhost:8001
   - Health Check: http://localhost:8001/health
   - Agent Invocation: `POST /invoke`

## 🔧 Core Components

### Tool Definitions (`tool_definitions.py`)
Contains all the specialized functions that the agent can use:

- **Financial Analysis Tools**
  - `analyze_financial_data()`: Comprehensive financial analysis
  - `query_transactions()`: Database transaction queries
  - `summarize_transactions()`: Transaction summarization

- **Receipt Processing Tools**
  - `process_receipt()`: OCR and categorization of receipts
  - `create_wallet_pass()`: Google Wallet pass generation

- **Proactive Analysis Tools**
  - `run_proactive_analysis()`: Spending pattern analysis
  - `run_comprehensive_proactive_analysis()`: Extended analysis
  - `send_push_notification()`: User notifications

- **Lifestyle Tools**
  - `generate_recipe_suggestion()`: Recipe recommendations
  - `get_virtual_pantry()`: Pantry item detection
  - `create_calendar_event()`: Calendar integration

### Agent Configuration (`main_agent.py`)
Defines the multi-agent system with specialized roles:

```python
# Transaction Agent - Financial analysis specialist
transaction_agent = Agent(
    name="transaction_agent",
    model="gemini-2.5-flash",
    description="Handles financial transactions and analysis"
)

# Proactive Agent - Pattern detection and insights
proactive_agent = Agent(
    name="proactive_agent", 
    model="gemini-2.5-flash",
    description="Monitors spending patterns and generates insights"
)

# Creative Agent - Lifestyle and recipe recommendations
creative_agent = Agent(
    name="creative_agent",
    model="gemini-2.5-flash", 
    description="Provides recipe suggestions and lifestyle advice"
)
```

## 📊 Agent Capabilities

### Financial Analysis
- **Spending Trends**: Analyze spending patterns by category, merchant, and time
- **Budget Insights**: Compare actual vs. planned spending
- **Anomaly Detection**: Identify unusual transactions or spending spikes
- **Subscription Tracking**: Monitor recurring payments and price changes

### Proactive Monitoring
- **Smart Alerts**: Automated notifications for important financial events
- **Trend Analysis**: Long-term spending pattern recognition
- **Budget Warnings**: Proactive budget overage alerts
- **Opportunity Detection**: Savings and optimization recommendations

### Lifestyle Integration
- **Recipe Suggestions**: AI-powered recipe recommendations based on purchases
- **Virtual Pantry**: Automatic ingredient tracking from grocery receipts
- **Shopping Lists**: Smart shopping list generation
- **Meal Planning**: Integration with grocery purchases and meal suggestions

## 🔍 API Usage

### Basic Agent Invocation
```bash
curl -X POST http://localhost:8001/invoke \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "id_token": "firebase-auth-token",
    "message": "What did I spend the most on last month?"
  }'
```

### Financial Analysis Query
```bash
curl -X POST http://localhost:8001/invoke \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123", 
    "id_token": "firebase-auth-token",
    "message": "Analyze my spending trends by category"
  }'
```

### Recipe Suggestion Request
```bash
curl -X POST http://localhost:8001/invoke \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "id_token": "firebase-auth-token", 
    "message": "Suggest a recipe based on my recent grocery purchases"
  }'
```

## 🧠 AI Intelligence Features

### Smart Query Understanding
The agent automatically understands various types of financial queries:
- "What did I spend the most on?" → Merchant analysis
- "Show me my restaurant spending trends" → Category analysis with time filtering
- "Find duplicate charges" → Transaction anomaly detection
- "What ingredients do I have?" → Virtual pantry analysis

### Contextual Responses
- Adapts responses based on available transaction data
- Provides fallback insights when specific data is unavailable
- Offers actionable recommendations with each analysis

### Learning and Adaptation
- Improves suggestions based on user spending patterns
- Adapts recipe recommendations to purchase history
- Personalizes insights based on individual financial behavior

## 🔧 Development

### Adding New Tools
1. Define the function in `tool_definitions.py`
2. Register it with the appropriate sub-agent
3. Update the agent's instruction set
4. Test with various query patterns

### Extending Analysis Capabilities
1. Add new analysis functions to `tool_definitions.py`
2. Enhance the Gemini prompts for better insights
3. Update the routing logic in `main_agent.py`
4. Test with representative data sets

## 📊 Monitoring and Debugging

### Logging
The agent includes comprehensive logging:
- Request/response tracking
- Tool execution monitoring
- Error handling and reporting
- Performance metrics

### Testing
```bash
# Run basic functionality tests
python -m pytest tests/

# Test specific agent functions
python test_agent_tools.py
```

## 🚀 Deployment

### Production Configuration
```env
AGENT_HOST=0.0.0.0
AGENT_PORT=8001
BACKEND_API_BASE_URL=https://your-backend-api.com/api/v1
GEMINI_API_KEY=production-gemini-key
```

### Docker Deployment
```bash
docker build -t aegis-agent .
docker run -p 8001:8001 aegis-agent
```

## 🔐 Security

- All API calls require valid Firebase authentication tokens
- Sensitive data is not logged or cached
- User data is processed securely and not stored by the agent
- All external API calls use secure HTTPS connections

## 🤝 Contributing

1. Follow the existing code structure and patterns
2. Add comprehensive docstrings to new functions
3. Include error handling and fallback mechanisms
4. Test with various user scenarios and edge cases
5. Update documentation for new features

## 📄 License

This project is part of the Aegis Financial Assistant platform.

## 🆘 Troubleshooting

### Common Issues

1. **Agent not starting**
   - Check that all environment variables are set
   - Verify Python dependencies are installed
   - Ensure the backend service is accessible

2. **Tool execution failures**
   - Verify backend API connectivity
   - Check Firebase authentication tokens
   - Review error logs for specific tool failures

3. **Poor analysis quality**
   - Ensure sufficient transaction data is available
   - Verify Gemini API key is valid and has quota
   - Check that user has uploaded recent receipts

### Debug Mode
```bash
# Run with debug logging
PYTHONPATH=. python main_agent.py --debug
```

For additional support, check the logs and ensure all external services (Backend API, Gemini AI, Firebase) are properly configured and accessible.
