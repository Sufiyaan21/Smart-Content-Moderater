import google.generativeai as genai
from typing import Dict, Any, Optional
from app.core.config import settings
from app.core.logger import get_logger
from app.models.models import ClassificationType

logger = get_logger(__name__)

# Configure Google Gemini API
genai.configure(api_key=settings.gemini_api_key)


class LLMService:
    """Service for interacting with Google Gemini API for content moderation."""

    def __init__(self):
        # Use stable, widely available Gemini models
        # gemini-1.5-flash supports text and multimodal prompts
        self.text_model = genai.GenerativeModel("gemini-1.5-flash")
        self.vision_model = genai.GenerativeModel("gemini-1.5-flash")

    async def moderate_text(self, text: str) -> Dict[str, Any]:
        """
        Analyze text content for inappropriate material using Gemini Pro.

        Args:
            text: The text content to analyze

        Returns:
            Dictionary containing classification, confidence, reasoning, and raw response
        """
        try:
            prompt = f"""
            Analyze the following text for inappropriate content. Classify it into one of these categories:
            - safe: Appropriate and harmless content
            - toxic: Hate speech, offensive language, or harmful content
            - spam: Unwanted promotional content, scams, or repetitive messages
            - harassment: Bullying, threats, or targeted abuse
            - inappropriate: Content that violates community guidelines but isn't clearly toxic or spam

            Text to analyze: "{text}"

            Please respond in the following JSON format:
            {{
                "classification": "safe|toxic|spam|harassment|inappropriate",
                "confidence": 0.0-1.0,
                "reasoning": "Brief explanation of the classification",
                "flagged": true/false
            }}

            Be thorough but fair in your analysis. Consider context and intent.
            """

            response = await self.text_model.generate_content_async(prompt)

            # Parse the response
            result_text = self._extract_text_from_response(response)
            result = self._parse_llm_response(result_text)

            logger.info(
                "Text moderation completed",
                classification=result.get("classification"),
                confidence=result.get("confidence"),
                text_length=len(text),
            )

            return result

        except Exception as e:
            logger.error(
                "Error in text moderation", error=str(e), text_length=len(text)
            )
            raise

    async def moderate_image(
        self, image_data: bytes, image_description: str = ""
    ) -> Dict[str, Any]:
        """
        Analyze image content for inappropriate material using Gemini Pro Vision.

        Args:
            image_data: Raw image bytes
            image_description: Optional description of the image

        Returns:
            Dictionary containing classification, confidence, reasoning, and raw response
        """
        try:
            # Create image part for Gemini
            image_part = {
                "mime_type": "image/jpeg",  # Assuming JPEG, could be made dynamic
                "data": image_data,
            }

            prompt = f"""
            Analyze this image for inappropriate content. Classify it into one of these categories:
            - safe: Appropriate and harmless content
            - toxic: Hate speech, offensive symbols, or harmful imagery
            - spam: Unwanted promotional content or misleading imagery
            - harassment: Bullying imagery, threats, or targeted abuse
            - inappropriate: Content that violates community guidelines (nudity, violence, etc.)

            Image description: {image_description}

            Please respond in the following JSON format:
            {{
                "classification": "safe|toxic|spam|harassment|inappropriate",
                "confidence": 0.0-1.0,
                "reasoning": "Brief explanation of the classification",
                "flagged": true/false
            }}

            Be thorough but fair in your analysis. Consider context and cultural sensitivity.
            """

            response = await self.vision_model.generate_content_async([prompt, image_part])

            # Parse the response
            result_text = self._extract_text_from_response(response)
            result = self._parse_llm_response(result_text)

            logger.info(
                "Image moderation completed",
                classification=result.get("classification"),
                confidence=result.get("confidence"),
            )

            return result

        except Exception as e:
            logger.error("Error in image moderation", error=str(e))
            raise

    def _parse_llm_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parse the LLM response and extract structured data.

        Args:
            response_text: Raw response from Gemini API

        Returns:
            Parsed response with classification, confidence, reasoning, and raw response
        """
        try:
            # Try to extract JSON from the response
            import json
            import re

            # Find JSON in the response
            json_match = re.search(r"\{.*\}", response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                parsed = json.loads(json_str)

                # Validate and normalize the response
                classification = parsed.get("classification", "safe").lower()
                confidence = float(parsed.get("confidence", 0.5))
                reasoning = parsed.get("reasoning", "No reasoning provided")
                flagged = parsed.get("flagged", False)

                # Map classification to enum
                classification_map = {
                    "safe": ClassificationType.SAFE,
                    "toxic": ClassificationType.TOXIC,
                    "spam": ClassificationType.SPAM,
                    "harassment": ClassificationType.HARASSMENT,
                    "inappropriate": ClassificationType.INAPPROPRIATE,
                }

                return {
                    "classification": classification_map.get(
                        classification, ClassificationType.SAFE
                    ),
                    "confidence": max(0.0, min(1.0, confidence)),  # Clamp between 0 and 1
                    "reasoning": reasoning,
                    "flagged": flagged,
                    "llm_response": response_text,
                }
            else:
                # Fallback if JSON parsing fails
                logger.warning(
                    "Failed to parse JSON from LLM response", response=response_text
                )
                return {
                    "classification": ClassificationType.SAFE,
                    "confidence": 0.5,
                    "reasoning": "Failed to parse LLM response",
                    "flagged": False,
                    "llm_response": response_text,
                }

        except Exception as e:
            logger.error("Error parsing LLM response", error=str(e), response=response_text)
            return {
                "classification": ClassificationType.SAFE,
                "confidence": 0.5,
                "reasoning": f"Error parsing response: {str(e)}",
                "flagged": False,
                "llm_response": response_text,
            }

    def _extract_text_from_response(self, response: Any) -> str:
        """Robustly extract concatenated text from a Gemini response object."""
        try:
            # Prefer candidates->content->parts traversal
            if getattr(response, "candidates", None):
                parts = getattr(response.candidates[0].content, "parts", [])
                texts = []
                for part in parts:
                    # Newer SDK: part.text, older may use dict-like
                    text_val = getattr(part, "text", None)
                    if text_val:
                        texts.append(text_val)
                if texts:
                    return "\n".join(texts)
            # Fallback to quick accessor if available
            if hasattr(response, "text") and isinstance(response.text, str):
                return response.text
        except Exception as exc:
            logger.warning("Failed to extract text from LLM response", error=str(exc))
        # Final fallback: stringify
        try:
            return str(response)
        except Exception:
            return ""


# Global service instance
llm_service = LLMService()
