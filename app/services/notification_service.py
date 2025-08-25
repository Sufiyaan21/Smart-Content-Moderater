import requests
import json
from typing import Dict, Any, Optional
from datetime import datetime
from app.core.config import settings
from app.core.logger import get_logger
from app.models.models import NotificationChannel, NotificationStatus, ClassificationType

logger = get_logger(__name__)


class NotificationService:
    """Service for sending notifications via Slack and email."""
    
    def __init__(self):
        self.slack_webhook_url = settings.slack_webhook_url
        self.brevo_api_key = settings.brevo_api_key
        self.brevo_sender_email = settings.brevo_sender_email
    
    async def send_notifications(self, request_id: int, email: str, 
                               classification: ClassificationType, 
                               content_type: str, content_preview: str,
                               confidence: float, reasoning: str) -> Dict[str, Any]:
        """
        Send notifications for flagged content.
        
        Args:
            request_id: Moderation request ID
            email: User email
            classification: Content classification
            content_type: Type of content (text/image)
            content_preview: Preview of the content
            confidence: Confidence score
            reasoning: Reasoning for classification
            
        Returns:
            Dictionary with notification results
        """
        results = {}
        
        # Only send notifications for flagged content
        if classification == ClassificationType.SAFE:
            logger.info("Content is safe, skipping notifications", request_id=request_id)
            return results
        
        # Send Slack notification
        if self.slack_webhook_url:
            try:
                slack_result = await self._send_slack_notification(
                    request_id, email, classification, content_type, 
                    content_preview, confidence, reasoning
                )
                results['slack'] = slack_result
            except Exception as e:
                logger.error("Failed to send Slack notification", error=str(e), request_id=request_id)
                results['slack'] = {'status': 'failed', 'error': str(e)}
        
        # Send email notification
        if self.brevo_api_key and self.brevo_sender_email:
            try:
                email_result = await self._send_email_notification(
                    request_id, email, classification, content_type,
                    content_preview, confidence, reasoning
                )
                results['email'] = email_result
            except Exception as e:
                logger.error("Failed to send email notification", error=str(e), request_id=request_id)
                results['email'] = {'status': 'failed', 'error': str(e)}
        
        return results
    
    async def _send_slack_notification(self, request_id: int, email: str,
                                     classification: ClassificationType,
                                     content_type: str, content_preview: str,
                                     confidence: float, reasoning: str) -> Dict[str, Any]:
        """
        Send Slack notification via webhook.
        
        Args:
            request_id: Moderation request ID
            email: User email
            classification: Content classification
            content_type: Type of content
            content_preview: Preview of content
            confidence: Confidence score
            reasoning: Reasoning for classification
            
        Returns:
            Notification result
        """
        try:
            # Create Slack message
            color_map = {
                ClassificationType.TOXIC: "#ff0000",      # Red
                ClassificationType.HARASSMENT: "#ff6600", # Orange
                ClassificationType.INAPPROPRIATE: "#ffcc00", # Yellow
                ClassificationType.SPAM: "#999999"        # Gray
            }
            
            color = color_map.get(classification, "#ff0000")
            
            message = {
                "attachments": [
                    {
                        "color": color,
                        "title": f"🚨 Content Moderation Alert - {classification.value.upper()}",
                        "fields": [
                            {
                                "title": "Request ID",
                                "value": str(request_id),
                                "short": True
                            },
                            {
                                "title": "User Email",
                                "value": email,
                                "short": True
                            },
                            {
                                "title": "Content Type",
                                "value": content_type,
                                "short": True
                            },
                            {
                                "title": "Confidence",
                                "value": f"{confidence:.2%}",
                                "short": True
                            },
                            {
                                "title": "Content Preview",
                                "value": content_preview[:200] + "..." if len(content_preview) > 200 else content_preview,
                                "short": False
                            },
                            {
                                "title": "Reasoning",
                                "value": reasoning,
                                "short": False
                            }
                        ],
                        "footer": "Smart Content Moderator API",
                        "ts": int(datetime.now().timestamp())
                    }
                ]
            }
            
            # Send to Slack
            response = requests.post(
                self.slack_webhook_url,
                json=message,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            response.raise_for_status()
            
            logger.info("Slack notification sent successfully", request_id=request_id)
            return {'status': 'sent', 'response': response.text}
            
        except Exception as e:
            logger.error("Error sending Slack notification", error=str(e), request_id=request_id)
            raise
    
    async def _send_email_notification(self, request_id: int, email: str,
                                     classification: ClassificationType,
                                     content_type: str, content_preview: str,
                                     confidence: float, reasoning: str) -> Dict[str, Any]:
        """
        Send email notification via Brevo API.
        
        Args:
            request_id: Moderation request ID
            email: User email
            classification: Content classification
            content_type: Type of content
            content_preview: Preview of content
            confidence: Confidence score
            reasoning: Reasoning for classification
            
        Returns:
            Notification result
        """
        try:
            # Brevo API endpoint
            url = "https://api.brevo.com/v3/smtp/email"
            
            # Email headers
            headers = {
                "accept": "application/json",
                "content-type": "application/json",
                "api-key": self.brevo_api_key
            }
            
            # Email content
            subject = f"Content Moderation Alert - {classification.value.upper()} Content Detected"
            
            html_content = f"""
            <html>
            <body>
                <h2>🚨 Content Moderation Alert</h2>
                <p><strong>Classification:</strong> {classification.value.upper()}</p>
                <p><strong>Request ID:</strong> {request_id}</p>
                <p><strong>User Email:</strong> {email}</p>
                <p><strong>Content Type:</strong> {content_type}</p>
                <p><strong>Confidence:</strong> {confidence:.2%}</p>
                <p><strong>Content Preview:</strong></p>
                <blockquote>{content_preview}</blockquote>
                <p><strong>Reasoning:</strong></p>
                <p>{reasoning}</p>
                <hr>
                <p><em>This is an automated alert from Smart Content Moderator API</em></p>
            </body>
            </html>
            """
            
            text_content = f"""
            Content Moderation Alert
            
            Classification: {classification.value.upper()}
            Request ID: {request_id}
            User Email: {email}
            Content Type: {content_type}
            Confidence: {confidence:.2%}
            
            Content Preview:
            {content_preview}
            
            Reasoning:
            {reasoning}
            
            ---
            This is an automated alert from Smart Content Moderator API
            """
            
            # Email payload
            payload = {
                "sender": {
                    "name": "Content Moderator",
                    "email": self.brevo_sender_email
                },
                "to": [
                    {
                        "email": email,
                        "name": email.split('@')[0]
                    }
                ],
                "subject": subject,
                "htmlContent": html_content,
                "textContent": text_content
            }
            
            # Send email
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            
            logger.info("Email notification sent successfully", request_id=request_id, email=email)
            return {'status': 'sent', 'response': response.json()}
            
        except Exception as e:
            logger.error("Error sending email notification", error=str(e), request_id=request_id, email=email)
            raise


# Global service instance
notification_service = NotificationService()



