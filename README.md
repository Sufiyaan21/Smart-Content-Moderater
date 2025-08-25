# Smart Content Moderator API

A FastAPI-based content moderation service that analyzes text and image content for inappropriate material using Google Gemini API, stores results in PostgreSQL, and sends notifications via Slack and email.

## Features

- **Text Moderation**: Analyze text content for toxicity, spam, harassment, and inappropriate content
- **Image Moderation**: Analyze images for inappropriate content using Google Gemini Vision
- **Content Deduplication**: Hash-based content caching to avoid re-analyzing duplicate content
- **Background Notifications**: Asynchronous Slack and email alerts for flagged content
- **Analytics**: User-specific and system-wide analytics and reporting
- **RESTful API**: Clean, documented API endpoints with proper status codes
- **Database Persistence**: PostgreSQL with SQLAlchemy ORM and Alembic migrations
- **Docker Support**: Complete containerization with Docker and Docker Compose

## Tech Stack

- **Backend**: FastAPI with async/await
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Migrations**: Alembic
- **AI/ML**: Google Gemini API (gemini-pro for text, gemini-pro-vision for images)
- **Notifications**: Slack Webhooks, Brevo (Sendinblue) Email API
- **Logging**: Structured logging with structlog
- **Containerization**: Docker & Docker Compose

## Project Structure

```
Smart_Content_Moderator_API/
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── core/                   # Configuration and logging
│   │   ├── config.py          # Settings and environment variables
│   │   └── logger.py          # Structured logging setup
│   ├── db/                    # Database configuration
│   │   └── base.py           # SQLAlchemy setup and session management
│   ├── models/                # SQLAlchemy models
│   │   └── models.py         # Database models and enums
│   ├── routes/                # API routes
│   │   ├── moderation.py     # Text and image moderation endpoints
│   │   └── analytics.py      # Analytics endpoints
│   ├── schemas/               # Pydantic schemas
│   │   └── schemas.py        # Request/response models
│   ├── services/              # Business logic services
│   │   ├── llm_service.py    # Google Gemini API integration
│   │   ├── image_service.py  # Image processing utilities
│   │   └── notification_service.py # Slack and email notifications
│   └── utils/                 # Utility functions
│       └── hashing.py        # Content hashing utilities
├── alembic/                   # Database migrations
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Multi-stage Docker build
├── docker-compose.yml         # Docker Compose configuration
├── alembic.ini               # Alembic configuration
└── README.md                 # This file
```

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Docker & Docker Compose (optional)
- Google Gemini API key
- Slack Webhook URL (optional)
- Brevo API key (optional)

### Environment Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd Smart_Content_Moderator_API
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create environment file:
```bash
cp env.example .env
```

5. Configure environment variables in `.env`:
```env
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/content_moderator

# Google Gemini API
GEMINI_API_KEY=your_gemini_api_key_here

# Slack Configuration (optional)
SLACK_WEBHOOK_URL=your_slack_webhook_url_here

# Brevo Email API (optional)
BREVO_API_KEY=your_brevo_api_key_here
BREVO_SENDER_EMAIL=noreply@yourdomain.com

# Application Configuration
APP_NAME=Smart Content Moderator API
DEBUG=True
LOG_LEVEL=INFO
```

### Database Setup

1. Create PostgreSQL database:
```sql
CREATE DATABASE content_moderator;
```

2. Run database migrations:
```bash
alembic upgrade head
```

### Running the Application

#### Option 1: Local Development
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Option 2: Docker Compose
```bash
docker-compose up --build
```

The API will be available at `http://localhost:8000`

## API Documentation

### Base URL
```
http://localhost:8000
```

### Authentication
Currently, the API doesn't require authentication. In production, implement proper authentication mechanisms.

### Endpoints

#### 1. Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00",
  "version": "1.0.0"
}
```

#### 2. Text Moderation
```http
POST /api/v1/moderate/text
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "text": "Text content to analyze"
}
```

**Response:**
```json
{
  "success": true,
  "request_id": 123,
  "classification": "safe",
  "confidence": 0.95,
  "reasoning": "Content appears to be appropriate and harmless",
  "message": "Content analyzed successfully"
}
```

#### 3. Image Moderation
```http
POST /api/v1/moderate/image
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "image_url": "https://example.com/image.jpg"
}
```

OR

```json
{
  "email": "user@example.com",
  "image_base64": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ..."
}
```

**Response:**
```json
{
  "success": true,
  "request_id": 124,
  "classification": "safe",
  "confidence": 0.92,
  "reasoning": "Image contains appropriate content",
  "message": "Content analyzed successfully"
}
```

#### 4. User Analytics
```http
GET /api/v1/analytics/summary?user=user@example.com
```

**Response:**
```json
{
  "success": true,
  "data": {
    "email": "user@example.com",
    "total_requests": 10,
    "text_requests": 7,
    "image_requests": 3,
    "safe_content": 8,
    "flagged_content": 2,
    "toxic_content": 1,
    "spam_content": 0,
    "harassment_content": 1,
    "inappropriate_content": 0,
    "average_confidence": 0.89,
    "last_request_date": "2024-01-01T12:00:00"
  },
  "message": "Analytics summary retrieved successfully"
}
```

#### 5. All Users Analytics
```http
GET /api/v1/analytics/summary/all
```

**Response:**
```json
{
  "success": true,
  "overall_stats": {
    "total_users": 5,
    "total_requests": 50,
    "total_flagged_content": 8,
    "flag_rate": 16.0
  },
  "user_analytics": {
    "user1@example.com": {
      "total_requests": 10,
      "text_requests": 7,
      "image_requests": 3,
      "safe_content": 8,
      "flagged_content": 2,
      "toxic_content": 1,
      "spam_content": 0,
      "harassment_content": 1,
      "inappropriate_content": 0,
      "average_confidence": 0.89,
      "last_request_date": "2024-01-01T12:00:00"
    }
  },
  "message": "All users analytics summary retrieved successfully"
}
```

### Classification Types

- **safe**: Appropriate and harmless content
- **toxic**: Hate speech, offensive language, or harmful content
- **spam**: Unwanted promotional content, scams, or repetitive messages
- **harassment**: Bullying, threats, or targeted abuse
- **inappropriate**: Content that violates community guidelines

## Database Schema

### Tables

#### 1. moderation_requests
- `id` (Primary Key)
- `email` (User email)
- `content_type` (text/image)
- `content_hash` (SHA-256 hash of content)
- `status` (pending/processing/completed/failed)
- `created_at` (Timestamp)
- `updated_at` (Timestamp)

#### 2. moderation_results
- `id` (Primary Key)
- `request_id` (Foreign Key to moderation_requests)
- `classification` (safe/toxic/spam/harassment/inappropriate)
- `confidence` (Float 0.0-1.0)
- `reasoning` (Text explanation)
- `llm_response` (Raw LLM response)
- `created_at` (Timestamp)

#### 3. notification_logs
- `id` (Primary Key)
- `request_id` (Foreign Key to moderation_requests)
- `channel` (slack/email)
- `status` (pending/sent/failed)
- `error_message` (Error details if failed)
- `sent_at` (Timestamp)
- `created_at` (Timestamp)

## Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Yes | - |
| `GEMINI_API_KEY` | Google Gemini API key | Yes | - |
| `SLACK_WEBHOOK_URL` | Slack webhook URL | No | - |
| `BREVO_API_KEY` | Brevo email API key | No | - |
| `BREVO_SENDER_EMAIL` | Sender email for notifications | No | - |
| `DEBUG` | Enable debug mode | No | False |
| `LOG_LEVEL` | Logging level | No | INFO |

## Development

### Running Tests
```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest
```

### Database Migrations
```bash
# Create new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Code Formatting
```bash
# Install formatting tools
pip install black isort

# Format code
black app/
isort app/
```

## Deployment

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up --build -d

# View logs
docker-compose logs -f api

# Stop services
docker-compose down
```

### Production Considerations

1. **Security**:
   - Implement proper authentication and authorization
   - Use HTTPS in production
   - Secure environment variables
   - Rate limiting

2. **Performance**:
   - Database connection pooling
   - Redis caching for frequent requests
   - Load balancing for high traffic

3. **Monitoring**:
   - Application metrics
   - Database performance monitoring
   - Error tracking and alerting

4. **Backup**:
   - Regular database backups
   - Log rotation and archiving

## Troubleshooting

### Common Issues

1. **Database Connection Error**:
   - Verify PostgreSQL is running
   - Check DATABASE_URL format
   - Ensure database exists

2. **Gemini API Error**:
   - Verify GEMINI_API_KEY is valid
   - Check API quota limits
   - Ensure internet connectivity

3. **Image Processing Error**:
   - Verify image format is supported
   - Check image file size limits
   - Ensure image URL is accessible

### Logs
Application logs are structured and include:
- Request/response logging
- Error details with stack traces
- Performance metrics
- Database operation logs

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue in the repository
- Check the API documentation at `/docs`
- Review the logs for error details



