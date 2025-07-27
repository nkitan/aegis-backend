# Project Aegis - API Test Commands

This document contains comprehensive curl commands for testing all the APIs and endpoints in the Project Aegis backend system.

## Table of Contents
1. [Backend API Endpoints](#backend-api-endpoints)
   - [Receipt Scanning & Transaction Processing](#receipt-scanning--transaction-processing)
   - [Google Wallet Integration](#google-wallet-integration)
   - [Transaction Management](#transaction-management)
   - [User Management](#user-management)
   - [Financial Analysis via Agent](#financial-analysis-via-agent)
   - [Challenges & Goals](#challenges--goals)
   - [Proactive Analysis](#proactive-analysis)
   - [Calendar Integration](#calendar-integration)
   - [Push Notifications](#push-notifications)
2. [Aegnt Service Endpoints](#aegnt-service-endpoints)
   - [Natural Language Financial Queries](#natural-language-financial-queries)
   - [Virtual Pantry & Recipe Suggestions](#virtual-pantry--recipe-suggestions)
   - [Proactive Insights](#proactive-insights)

---

## Backend API Endpoints

### Receipt Scanning & Transaction Processing

#### Process Receipt Image with Google Wallet Pass Creation
```bash
# Process a receipt image and get comprehensive transaction data + Google Wallet pass URL
curl -X POST "http://localhost:8000/api/v1/transactions/process" \
  -H "Authorization: Bearer test_token" \
  -F "file=@/path/to/receipt/image.jpg"

# Example with sample receipt
curl -X POST "http://localhost:8000/api/v1/transactions/process" \
  -H "Authorization: Bearer test_token" \
  -F "file=@/home/notroot/Work/project-aegis/sample_reciepts/picture_1.jpg"
```

**Expected Response:**
```json
{
  "status": "success",
  "transaction_id": "generated_transaction_id_123",
  "transaction_data": {
    "user_id": "vg21F4xzYJdg5yikFrEDAotLqli1",
    "store_name": "Coffee Shop ABC",
    "transaction_date": "2025-07-27T10:30:00",
    "items": [
      {
        "name": "Large Coffee",
        "price": 4.50,
        "quantity": 1,
        "category": "Beverages"
      }
    ],
    "total_amount": 24.99,
    "subtotal_amount": 22.75,
    "tax_amount": 2.24,
    "currency": "USD",
    "payment_method": "Credit Card",
    "category": "Food & Dining",
    "location": "123 Main St, San Francisco, CA 94105"
  },
  "google_wallet_pass_url": "https://pay.google.com/gp/v/save/eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJ5b3VyLXNlcnZpY2UtYWNjb3VudEBleGFtcGxlLmNvbSIsImF1ZCI6Imdvb2dsZSIsIm9yaWdpbnMiOlsiaHR0cHM6Ly8xMjcuMC4wLjE6ODAwMCJdLCJ0eXAiOiJzYXZldG93YWxsZXQiLCJwYXlsb2FkIjp7fX0.signature"
}
```

> **Note:** The `google_wallet_pass_url` should be a clean URL without any `b'` prefix. If you see a URL starting with `b'`, this indicates a bytes encoding issue that has been fixed.

---

### Google Wallet Integration

#### Create Custom Google Wallet Pass
```bash
curl -X POST "http://localhost:8000/api/v1/integrations/wallet/pass" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test_token" \
  -d '{
    "pass_type": "transaction",
    "pass_data": {
      "transaction_id": "test_txn_123456789",
      "store_name": "Sample Coffee Shop",
      "total_amount": 24.99,
      "subtotal_amount": 22.75,
      "tax_amount": 2.24,
      "transaction_date": "2025-07-27",
      "category": "Food & Dining",
      "currency": "USD",
      "payment_method": "Credit Card",
      "items": [
        {
          "name": "Large Coffee",
          "price": 4.50,
          "quantity": 1
        },
        {
          "name": "Blueberry Muffin",
          "price": 3.25,
          "quantity": 2
        }
      ],
      "store_location": {
        "address": "123 Main Street",
        "city": "San Francisco",
        "state": "CA",
        "postal_code": "94105",
        "country": "US"
      },
      "location_string": "123 Main Street, San Francisco, CA 94105"
    }
  }'
```

#### Minimal Google Wallet Pass
```bash
curl -X POST "http://localhost:8000/api/v1/integrations/wallet/pass" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test_token" \
  -d '{
    "pass_type": "transaction",
    "pass_data": {
      "transaction_id": "simple_test_123",
      "store_name": "Test Store",
      "total_amount": 15.99,
      "transaction_date": "2025-07-27"
    }
  }'
```

---

### Transaction Management

#### Get User Transactions
```bash
# Get all transactions for a date range
curl -X GET "http://localhost:8000/api/v1/transactions?start_date=2025-01-01&end_date=2025-12-31" \
  -H "Authorization: Bearer test_token"

# Get transactions filtered by category
curl -X GET "http://localhost:8000/api/v1/transactions?start_date=2025-01-01&end_date=2025-12-31&category=Food%20%26%20Dining" \
  -H "Authorization: Bearer test_token"

# Get transactions filtered by store
curl -X GET "http://localhost:8000/api/v1/transactions?start_date=2025-01-01&end_date=2025-12-31&store_name=Starbucks" \
  -H "Authorization: Bearer test_token"

# Get transactions filtered by item
curl -X GET "http://localhost:8000/api/v1/transactions?start_date=2025-01-01&end_date=2025-12-31&item_name=coffee" \
  -H "Authorization: Bearer test_token"
```

---

### User Management

#### Get Current User Profile
```bash
curl -X GET "http://localhost:8000/api/v1/users/me" \
  -H "Authorization: Bearer test_token"
```

#### Update FCM Token for Push Notifications
```bash
curl -X POST "http://localhost:8000/api/v1/users/me/fcm_token" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test_token" \
  -d '{
    "fcm_token": "your_fcm_token_here"
  }'
```

#### Ask Financial Questions in Natural Language
```bash
# General spending analysis
curl -X POST "http://localhost:8000/api/v1/users/me/agent/invoke" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test_token" \
  -d '{
    "prompt": "How much did I spend on restaurant food last month?"
  }'

# Spending trends analysis
curl -X POST "http://localhost:8000/api/v1/users/me/agent/invoke" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test_token" \
  -d '{
    "prompt": "Show me my spending trends by category for this year"
  }'

# Store-specific analysis
curl -X POST "http://localhost:8000/api/v1/users/me/agent/invoke" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test_token" \
  -d '{
    "prompt": "What store did I spend the most money at?"
  }'

# Historical spending
curl -X POST "http://localhost:8000/api/v1/users/me/agent/invoke" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test_token" \
  -d '{
    "prompt": "What was my total spending in 2017?"
  }'

# Category-specific analysis
curl -X POST "http://localhost:8000/api/v1/users/me/agent/invoke" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test_token" \
  -d '{
    "prompt": "How much did I spend on groceries this quarter?"
  }'

# Budget analysis
curl -X POST "http://localhost:8000/api/v1/users/me/agent/invoke" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test_token" \
  -d '{
    "prompt": "Compare my spending this month vs last month"
  }'

# Recipe suggestions from purchases
curl -X POST "http://localhost:8000/api/v1/users/me/agent/invoke" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test_token" \
  -d '{
    "prompt": "Suggest some recipes based on my recent grocery purchases"
  }'
```

---

### Challenges & Goals

#### Start a New Financial Challenge
```bash
# Savings challenge
curl -X POST "http://localhost:8000/api/v1/challenges" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test_token" \
  -d '{
    "challenge_type": "savings_goal",
    "details": {
      "target_amount": 1000.00,
      "target_date": "2025-12-31",
      "category": "Emergency Fund",
      "current_amount": 0.00
    },
    "status": "active"
  }'

# Spending reduction challenge
curl -X POST "http://localhost:8000/api/v1/challenges" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test_token" \
  -d '{
    "challenge_type": "spending_reduction",
    "details": {
      "category": "dining_out",
      "target_reduction_percent": 20,
      "baseline_amount": 500.00,
      "duration_months": 3
    },
    "status": "active"
  }'
```

#### Get Active Challenges
```bash
curl -X GET "http://localhost:8000/api/v1/challenges" \
  -H "Authorization: Bearer test_token"
```

---

### Proactive Analysis

#### Trigger Proactive Financial Analysis
```bash
curl -X POST "http://localhost:8000/api/v1/tasks/proactive_analysis" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test_token" \
  -d '{
    "user_id": "vg21F4xzYJdg5yikFrEDAotLqli1"
  }'
```

---

### Calendar Integration

#### Create Calendar Event for Financial Reminder
```bash
curl -X POST "http://localhost:8000/api/v1/integrations/calendar/event" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test_token" \
  -d '{
    "event_data": {
      "summary": "Credit Card Payment Due",
      "description": "Monthly credit card payment reminder",
      "start_time": "2025-08-15T09:00:00Z",
      "end_time": "2025-08-15T09:30:00Z",
      "reminder_minutes": 1440
    }
  }'
```

---

### Push Notifications

#### Send Push Notification
```bash
curl -X POST "http://localhost:8000/api/v1/integrations/notifications/send" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test_token" \
  -d '{
    "user_id": "vg21F4xzYJdg5yikFrEDAotLqli1",
    "message": "You have exceeded your monthly dining budget by $50"
  }'
```

---

## Aegnt Service Endpoints

### Natural Language Financial Queries

#### Direct Agent Invocation
```bash
# General financial analysis
curl -X POST "http://localhost:5000/invoke_agent" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "vg21F4xzYJdg5yikFrEDAotLqli1",
    "prompt": "Analyze my spending patterns for the last 6 months",
    "id_token": "test_token"
  }'

# Spending by category
curl -X POST "http://localhost:5000/invoke_agent" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "vg21F4xzYJdg5yikFrEDAotLqli1",
    "prompt": "How much did I spend on entertainment last month?",
    "id_token": "test_token"
  }'

# Budget recommendations
curl -X POST "http://localhost:5000/invoke_agent" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "vg21F4xzYJdg5yikFrEDAotLqli1",
    "prompt": "Help me create a budget based on my spending history",
    "id_token": "test_token"
  }'

# Expense anomaly detection
curl -X POST "http://localhost:5000/invoke_agent" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "vg21F4xzYJdg5yikFrEDAotLqli1",
    "prompt": "Are there any unusual spending patterns in my recent transactions?",
    "id_token": "test_token"
  }'

# Financial goal planning
curl -X POST "http://localhost:5000/invoke_agent" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "vg21F4xzYJdg5yikFrEDAotLqli1",
    "prompt": "Help me plan to save $5000 for vacation next year",
    "id_token": "test_token"
  }'
```

---

### Virtual Pantry & Recipe Suggestions

#### Get Recipe Suggestions Based on Recent Purchases
```bash
# Generic recipe suggestions
curl -X POST "http://localhost:5000/invoke_agent" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "vg21F4xzYJdg5yikFrEDAotLqli1",
    "prompt": "What can I cook with the ingredients from my recent grocery purchases?",
    "id_token": "test_token"
  }'

# Dietary preference-based suggestions
curl -X POST "http://localhost:5000/invoke_agent" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "vg21F4xzYJdg5yikFrEDAotLqli1",
    "prompt": "Suggest healthy vegetarian recipes based on my recent purchases",
    "id_token": "test_token"
  }'

# Quick meal suggestions
curl -X POST "http://localhost:5000/invoke_agent" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "vg21F4xzYJdg5yikFrEDAotLqli1",
    "prompt": "I need a quick 30-minute dinner recipe using ingredients I recently bought",
    "id_token": "test_token"
  }'

# Meal planning
curl -X POST "http://localhost:5000/invoke_agent" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "vg21F4xzYJdg5yikFrEDAotLqli1",
    "prompt": "Plan a week of meals using ingredients from my pantry",
    "id_token": "test_token"
  }'
```

---

### Proactive Insights

#### Get Proactive Financial Insights
```bash
curl -X POST "http://localhost:5000/invoke_agent" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "vg21F4xzYJdg5yikFrEDAotLqli1",
    "prompt": "Give me proactive insights about my financial health",
    "id_token": "test_token"
  }'

# Request specific insights
curl -X POST "http://localhost:5000/invoke_agent" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "vg21F4xzYJdg5yikFrEDAotLqli1",
    "prompt": "Schedule weekly spending reports and budget alerts",
    "id_token": "test_token"
  }'

# Trend analysis
curl -X POST "http://localhost:5000/invoke_agent" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "vg21F4xzYJdg5yikFrEDAotLqli1",
    "prompt": "Analyze my spending trends and predict next month expenses",
    "id_token": "test_token"
  }'
```

---

## Configuration Requirements

### Environment Variables
Make sure these environment variables are set before running the tests:

```bash
# Backend configuration
export GOOGLE_WALLET_ISSUER_ID="your_google_wallet_issuer_id"
export GOOGLE_WALLET_SERVICE_ACCOUNT_KEY_FILE="/path/to/service-account-key.json"
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/firebase-credentials.json"
export GEMINI_API_KEY="your_gemini_api_key"
export GOOGLE_MAPS_API_KEY="your_google_maps_api_key"

# Aegnt configuration
export SPOONACULAR_API_KEY="your_spoonacular_api_key"
export AEGNT_API_URL="http://localhost:5000"
```

### Running the Services

1. **Start Backend Service:**
   ```bash
   cd backend
   python main.py
   # Runs on http://localhost:8000
   ```

2. **Start Aegnt Service:**
   ```bash
   cd aegnt
   python main_agent.py
   # Runs on http://localhost:5000
   ```

---

## Sample Test Sequences

### Complete Receipt Processing Flow
```bash
# 1. Process a receipt
curl -X POST "http://localhost:8000/api/v1/transactions/process" \
  -H "Authorization: Bearer test_token" \
  -F "file=@sample_reciepts/picture_1.jpg"

# 2. Ask about the transaction
curl -X POST "http://localhost:8000/api/v1/users/me/agent/invoke" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test_token" \
  -d '{"prompt": "What did I just buy?"}'

# 3. Get recipe suggestions if it was a grocery receipt
curl -X POST "http://localhost:8000/api/v1/users/me/agent/invoke" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test_token" \
  -d '{"prompt": "What can I cook with my recent purchases?"}'
```

### Financial Analysis Flow
```bash
# 1. Analyze spending patterns
curl -X POST "http://localhost:5000/invoke_agent" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "vg21F4xzYJdg5yikFrEDAotLqli1",
    "prompt": "Analyze my spending for the last 3 months",
    "id_token": "test_token"
  }'

# 2. Create a savings challenge based on analysis
curl -X POST "http://localhost:8000/api/v1/challenges" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test_token" \
  -d '{
    "challenge_type": "savings_goal",
    "details": {"target_amount": 500, "target_date": "2025-12-31"},
    "status": "active"
  }'

# 3. Set up proactive monitoring
curl -X POST "http://localhost:8000/api/v1/tasks/proactive_analysis" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test_token" \
  -d '{"user_id": "vg21F4xzYJdg5yikFrEDAotLqli1"}'
```

This comprehensive test suite covers all major functionality in the Project Aegis system, from receipt processing and Google Wallet integration to natural language financial analysis and virtual pantry recipe suggestions.

---

## Troubleshooting

### Common Issues and Solutions

#### Google Wallet Pass URL Issues
- **Problem**: URL starts with `b'` prefix
  - **Solution**: This was a bytes encoding issue that has been fixed. The JWT token is now properly decoded to a string.
  - **Expected Format**: `https://pay.google.com/gp/v/save/[JWT_TOKEN]`

#### Authentication Issues
- **Problem**: 401 Unauthorized errors
  - **Solution**: The system uses Firebase authentication bypass for testing. Use any valid Bearer token format.
  - **Test Token**: `Bearer test_token` works for all endpoints.

#### File Upload Issues
- **Problem**: Receipt processing fails with file errors
  - **Solution**: Ensure the file path is correct and the image format is supported (JPG, PNG).
  - **Example**: Use absolute paths like `/home/notroot/Work/project-aegis/sample_reciepts/picture_1.jpg`

#### Service Connectivity Issues
- **Problem**: Connection refused errors
  - **Solution**: Ensure both services are running:
    - Backend: `cd backend && python main.py` (port 8000)
    - Aegnt: `cd aegnt && python main_agent.py` (port 5000)

#### Environment Configuration Issues
- **Problem**: Missing API keys or service account files
  - **Solution**: Set all required environment variables before starting services.
  - **Check**: `echo $GOOGLE_WALLET_ISSUER_ID` to verify environment setup.
