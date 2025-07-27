# Project Aegis - Test UI

A simple web interface to test and demonstrate the core functionalities of Project Aegis APIs.

## Features

🔥 **Core Features Demonstrated:**

1. **📸 Receipt Scanner** - Upload receipt images and get Google Wallet passes
2. **💡 Proactive Insights** - Get AI-powered financial insights
3. **💬 NLP Finance Questions** - Ask questions about finances in natural language
4. **🍳 Virtual Pantry Recipes** - Get recipe suggestions from recent purchases

## Quick Start

### Prerequisites
Make sure you have the following service running:
- **Backend API** on `http://localhost:8000` (includes integrated agent functionality)

### Setup Instructions

1. **Install Dependencies:**
   ```bash
   cd test-ui
   npm install
   ```

2. **Start the UI Server:**
   ```bash
   npm start
   ```

3. **Open in Browser:**
   ```
   http://localhost:3000
   ```

## Usage Guide

### 1. Receipt Scanning 📸
- Click "Choose Receipt Image" to upload a receipt photo
- Click "Process Receipt" to extract transaction data
- If successful, you'll see an "Add to Google Wallet" button
- Click the button to open the Google Wallet pass

### 2. Proactive Insights 💡
- Click "Get Random Insight" to receive AI-powered financial advice
- The insight will appear in a styled card format

### 3. Finance Questions 💬
- Type any finance-related question in natural language
- Examples:
  - "How much did I spend on restaurants last month?"
  - "What was my total spending in 2024?"
  - "Show me my spending trends by category"
- Click "Ask Question" or press Enter

### 4. Recipe Suggestions 🍳
- Optionally add dietary preferences (e.g., "vegetarian", "gluten-free")
- Click "Get Recipe Ideas" to get suggestions based on recent grocery purchases
- The system automatically detects ingredients from your purchase history

## Configuration

You can modify the API endpoints and authentication in the configuration section at the top of the UI:

- **Backend URL**: Default `http://localhost:8000`
- **Auth Token**: Default `test_token`
- **User ID**: Default `vg21F4xzYJdg5yikFrEDAotLqli1`

## API Endpoints Used

### Backend API (Port 8000)
- `POST /api/v1/transactions/process` - Receipt processing with Google Wallet
- `POST /api/v1/users/me/agent/invoke` - Natural language finance questions, insights, and recipe suggestions

## Sample Test Data

### Receipt Images
Use the sample receipts from your project:
```
/home/notroot/Work/project-aegis/sample_reciepts/picture_1.jpg
/home/notroot/Work/project-aegis/sample_reciepts/picture_2.jpg
```

### Sample Finance Questions
- "How much did I spend on food this month?"
- "What store did I spend the most at?"
- "Compare my spending this month vs last month"
- "Are there any unusual spending patterns?"

### Sample Recipe Queries
- "What can I cook with my recent purchases?"
- "Suggest healthy vegetarian recipes"
- "Quick 30-minute dinner ideas"

## Troubleshooting

### CORS Issues
The UI server includes CORS headers, but if you encounter issues:
1. Make sure all services are running on the correct ports
2. Check browser console for detailed error messages

### API Connection Issues
1. Verify backend service is running:
   ```bash
   # Backend (includes integrated agent functionality)
   cd backend && python main.py
   ```

2. Check the configuration section in the UI for correct URL

### File Upload Issues
1. Ensure you're uploading image files (JPG, PNG)
2. Check browser console for upload errors
3. Verify the backend service is accessible

## Development

To modify or extend the UI:

1. **HTML Structure**: Edit `index.html`
2. **Styling**: Modify the `<style>` section in `index.html`
3. **JavaScript Logic**: Update the `<script>` section in `index.html`
4. **Server Configuration**: Modify `server.js`

## Features in Detail

### Receipt Processing Flow
1. User uploads image → Frontend sends to `/transactions/process`
2. Backend processes with Gemini AI → Extracts transaction data
3. Creates Google Wallet pass → Returns pass URL
4. User clicks "Add to Google Wallet" → Opens pass in new tab

### Natural Language Processing
1. User types question → Frontend sends to `/users/me/agent/invoke`
2. Backend processes with integrated agent → AI processes query
3. Returns formatted response → Displayed in UI

### Virtual Pantry System
1. User requests recipes → Frontend sends to `/users/me/agent/invoke`
2. Backend forwards to integrated agent → Analyzes recent purchases
3. Extracts ingredients and calls Spoonacular API → Returns recipe suggestions
4. Formatted response displayed → With cooking instructions

This UI provides a comprehensive demonstration of Project Aegis's core capabilities in an easy-to-use web interface.
