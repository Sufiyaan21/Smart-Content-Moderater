Smart Content Moderator API

A FastAPI-based backend service for moderating user-submitted text and image content using Google Gemini AI. The service stores moderation results in a database, sends real-time notifications via Slack for inappropriate content, and provides analytics.

✅ Features Implemented

✔ Text Moderation – Classifies text as safe, toxic, spam, or harassment using Gemini API.
✔ Image Moderation – Analyzes images for unsafe content using Gemini Vision API.
✔ Slack Integration – Sends alerts when inappropriate content is detected.
✔ Database Storage – Uses SQLite for persistence.
✔ Analytics Endpoint – Provides summary of moderation requests by user.

✅ Tech Stack

FastAPI (async API framework)

SQLite (lightweight database)

SQLAlchemy (ORM)

Gemini AI API (text & image moderation)

Slack Webhooks (for alerts)

Python 3.12

✅ Project Structure
Smart_Content_Moderator_API/
│
├── start.py               # App entry point
├── config.py              # Env configuration
├── database.py            # DB setup (SQLite)
├── models.py              # ORM models
├── routes/
│   ├── text_moderation.py
│   ├── image_moderation.py
│   └── analytics.py
├── services/
│   ├── moderation_service.py
│   ├── slack_service.py
│   └── gemini_service.py
└── README.md

✅ API Endpoints
1. POST /api/v1/moderate/text

Analyze text content for inappropriate language.

Request:

{
  "email": "user@example.com",
  "text": "This is a sample text"
}


Response:

{
  "classification": "safe",
  "confidence": 0.95,
  "reasoning": "No harmful content detected"
}

2. POST /api/v1/moderate/image

Analyze image content for inappropriate material.

Request:

multipart/form-data with:

email (string)

file (image)

Response:

{
  "classification": "safe",
  "confidence": 0.90,
  "reasoning": "Image is appropriate"
}

3. GET /api/v1/analytics/summary?user=email@example.com

Get moderation summary for a specific user.

Response:

{
  "total_requests": 5,
  "safe": 4,
  "toxic": 1,
  "last_activity": "2025-08-25T10:15:00"
}

✅ Notifications

Slack Alerts: When classification ≠ safe, a message is sent to a configured Slack channel with details.

✅ Setup Instructions
1. Clone & Install
git clone <repo-url>
cd Smart_Content_Moderator_API
pip install -r requirements.txt

2. Configure Environment

Create .env:

DATABASE_URL=sqlite:///./moderator.db
GEMINI_API_KEY=your_gemini_api_key
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/xxxx/yyyy/zzzz

3. Run the App
python start.py

4. Test the API
   python test_api.py

5. Access App after running both commands seperate terminals at http://localhost:8000/docs
