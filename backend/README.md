# Aegis Backend

The Aegis Backend is a FastAPI-based service that powers the Aegis Financial Assistant platform. It provides comprehensive APIs for transaction management, financial analysis, receipt processing, Google Wallet integration, and user management.

## 🚀 Features

- **Transaction Management**: Store, query, and analyze financial transactions
- **Receipt Processing**: OCR-powered receipt scanning and automatic categorization
- **Google Wallet Integration**: Create digital passes for shopping lists and budget tracking
- **Firebase Authentication**: Secure user authentication and authorization
- **Financial Analytics**: AI-powered spending insights and trend analysis
- **Proactive Notifications**: Automated financial alerts and recommendations
- **Calendar Integration**: Warranty tracking and payment reminders

## 📋 Prerequisites

- Python 3.8+
- Firebase project with Admin SDK credentials
- Google Wallet API credentials
- Gemini AI API key
- Virtual environment (recommended)

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   cd /path/to/project-aegis/backend
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv backend-venv
   source backend-venv/bin/activate  # On Windows: backend-venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the backend directory:
   ```env
   # Firebase Configuration
   FIREBASE_PROJECT_ID=your-firebase-project-id
   FIREBASE_PRIVATE_KEY_ID=your-private-key-id
   FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
   FIREBASE_CLIENT_EMAIL=your-service-account@your-project.iam.gserviceaccount.com
   FIREBASE_CLIENT_ID=your-client-id
   FIREBASE_AUTH_URI=https://accounts.google.com/o/oauth2/auth
   FIREBASE_TOKEN_URI=https://oauth2.googleapis.com/token
   
   # API Keys
   GEMINI_API_KEY=your-gemini-api-key
   GOOGLE_WALLET_ISSUER_ID=your-wallet-issuer-id
   GOOGLE_WALLET_SERVICE_ACCOUNT_EMAIL=your-wallet-service-account@your-project.iam.gserviceaccount.com
   
   # Application Settings
   PROJECT_NAME=Aegis Backend
   API_V1_STR=/api/v1
   SECRET_KEY=your-secret-key-here
   ```

5. **Place Firebase service account key**
   - Download your Firebase service account key as JSON
   - Place it in `backend/creds/service-account-key.json`

## 🚦 Running the Application

1. **Start the development server**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Access the API**
   - API Documentation: http://localhost:8000/docs
   - Alternative Docs: http://localhost:8000/redoc
   - Health Check: http://localhost:8000/api/v1/health

## 📚 API Endpoints

### Authentication
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/register` - User registration
- `GET /api/v1/auth/verify` - Token verification

### Transactions
- `GET /api/v1/transactions` - Query transactions with filters
- `POST /api/v1/transactions/process` - Process receipt uploads
- `GET /api/v1/transactions/analytics` - Financial analytics

### Users
- `GET /api/v1/users/me` - Get current user profile
- `POST /api/v1/users/me/agent/invoke` - Invoke AI agent
- `GET /api/v1/users/me/insights/proactive` - Get proactive insights

### Integrations
- `POST /api/v1/wallet/pass` - Create Google Wallet passes
- `POST /api/v1/calendar/event` - Create calendar events
- `POST /api/v1/notifications/send` - Send push notifications

### Challenges & Tasks
- `GET /api/v1/challenges` - List available challenges
- `POST /api/v1/tasks` - Create tasks and reminders

## 🏗️ Architecture

```
backend/
├── main.py                 # FastAPI application entry point
├── requirements.txt        # Python dependencies
├── core/                   # Core application modules
│   ├── config.py          # Configuration settings
│   ├── auth.py            # Authentication handlers
│   └── database.py        # Database connections
├── models/                 # Pydantic models
│   ├── user.py            # User data models
│   ├── transaction.py     # Transaction models
│   └── wallet.py          # Wallet pass models
├── routers/               # API route handlers
│   ├── users.py           # User endpoints
│   ├── transactions.py    # Transaction endpoints
│   └── integrations.py    # Third-party integrations
├── services/              # Business logic services
│   ├── receipt_processor.py  # OCR and categorization
│   ├── wallet_service.py     # Google Wallet integration
│   └── analytics_service.py  # Financial analytics
└── creds/                 # Credentials and keys
    └── service-account-key.json
```

## 🔧 Configuration

### Firebase Setup
1. Create a Firebase project
2. Enable Authentication and Firestore
3. Download service account credentials
4. Configure environment variables

### Google Wallet Setup
1. Enable Google Wallet API
2. Create issuer account
3. Configure service account permissions
4. Set up wallet credentials

### AI Services
- Configure Gemini AI API key for financial analysis
- Set up OCR service for receipt processing

## 🔍 Development

### Running Tests
```bash
pytest tests/
```

### Code Formatting
```bash
black .
isort .
```

### Linting
```bash
flake8 .
```

## 📊 Monitoring

The backend includes built-in logging and request monitoring:
- Request/response logging
- Error tracking
- Performance metrics
- Health check endpoints

## 🚀 Deployment

### Docker Deployment
```bash
docker build -t aegis-backend .
docker run -p 8000:8000 aegis-backend
```

### Environment Variables for Production
Ensure all sensitive credentials are properly configured in your production environment.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is part of the Aegis Financial Assistant platform.

## 🆘 Support

For issues and questions:
1. Check the API documentation at `/docs`
2. Review the logs for error details
3. Ensure all environment variables are configured
4. Verify Firebase and external service connectivity
