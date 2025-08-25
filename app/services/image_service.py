import base64
import requests
from typing import Optional, Tuple
from PIL import Image
import io
from app.core.logger import get_logger

logger = get_logger(__name__)


class ImageService:
    """Service for handling image processing and validation."""
    
    def __init__(self):
        self.max_image_size = 10 * 1024 * 1024  # 10MB
        self.supported_formats = ['JPEG', 'PNG', 'GIF', 'BMP', 'WEBP']
    
    async def process_image(self, image_url: Optional[str] = None, 
                          image_base64: Optional[str] = None) -> Tuple[bytes, str]:
        """
        Process image from URL or base64 data.
        
        Args:
            image_url: URL of the image
            image_base64: Base64 encoded image data
            
        Returns:
            Tuple of (image_bytes, mime_type)
        """
        try:
            if image_url:
                return await self._process_image_from_url(image_url)
            elif image_base64:
                return await self._process_image_from_base64(image_base64)
            else:
                raise ValueError("Either image_url or image_base64 must be provided")
                
        except Exception as e:
            logger.error("Error processing image", error=str(e))
            raise
    
    async def _process_image_from_url(self, url: str) -> Tuple[bytes, str]:
        """
        Download and process image from URL.
        
        Args:
            url: Image URL
            
        Returns:
            Tuple of (image_bytes, mime_type)
        """
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # Check content type
            content_type = response.headers.get('content-type', '')
            if not any(format.lower() in content_type.lower() for format in self.supported_formats):
                raise ValueError(f"Unsupported image format: {content_type}")
            
            # Check file size
            if len(response.content) > self.max_image_size:
                raise ValueError(f"Image too large: {len(response.content)} bytes")
            
            # Validate image
            image_bytes = response.content
            mime_type = self._validate_and_get_mime_type(image_bytes)
            
            logger.info("Image processed from URL", url=url, size=len(image_bytes), mime_type=mime_type)
            return image_bytes, mime_type
            
        except requests.RequestException as e:
            logger.error("Error downloading image from URL", url=url, error=str(e))
            raise ValueError(f"Failed to download image from URL: {str(e)}")
    
    async def _process_image_from_base64(self, base64_data: str) -> Tuple[bytes, str]:
        """
        Process image from base64 encoded data.
        
        Args:
            base64_data: Base64 encoded image data
            
        Returns:
            Tuple of (image_bytes, mime_type)
        """
        try:
            # Remove data URL prefix if present
            if base64_data.startswith('data:image'):
                # Extract mime type and base64 data
                header, encoded = base64_data.split(',', 1)
                mime_type = header.split(':')[1].split(';')[0]
            else:
                encoded = base64_data
                mime_type = 'image/jpeg'  # Default assumption
            
            # Decode base64
            image_bytes = base64.b64decode(encoded)
            
            # Check file size
            if len(image_bytes) > self.max_image_size:
                raise ValueError(f"Image too large: {len(image_bytes)} bytes")
            
            # Validate image and get actual mime type
            actual_mime_type = self._validate_and_get_mime_type(image_bytes)
            
            logger.info("Image processed from base64", size=len(image_bytes), mime_type=actual_mime_type)
            return image_bytes, actual_mime_type
            
        except Exception as e:
            logger.error("Error processing base64 image", error=str(e))
            raise ValueError(f"Failed to process base64 image: {str(e)}")
    
    def _validate_and_get_mime_type(self, image_bytes: bytes) -> str:
        """
        Validate image and get its MIME type.
        
        Args:
            image_bytes: Raw image bytes
            
        Returns:
            MIME type string
        """
        try:
            # Open image with PIL to validate
            image = Image.open(io.BytesIO(image_bytes))
            
            # Check if format is supported
            if image.format not in self.supported_formats:
                raise ValueError(f"Unsupported image format: {image.format}")
            
            # Get MIME type
            mime_type_map = {
                'JPEG': 'image/jpeg',
                'PNG': 'image/png',
                'GIF': 'image/gif',
                'BMP': 'image/bmp',
                'WEBP': 'image/webp'
            }
            
            mime_type = mime_type_map.get(image.format, 'image/jpeg')
            
            # Close image
            image.close()
            
            return mime_type
            
        except Exception as e:
            logger.error("Error validating image", error=str(e))
            raise ValueError(f"Invalid image format: {str(e)}")
    
    def resize_image_if_needed(self, image_bytes: bytes, max_dimension: int = 1024) -> bytes:
        """
        Resize image if it exceeds maximum dimensions.
        
        Args:
            image_bytes: Raw image bytes
            max_dimension: Maximum width/height dimension
            
        Returns:
            Resized image bytes
        """
        try:
            image = Image.open(io.BytesIO(image_bytes))
            
            # Check if resizing is needed
            if max(image.size) <= max_dimension:
                image.close()
                return image_bytes
            
            # Calculate new size
            ratio = max_dimension / max(image.size)
            new_size = tuple(int(dim * ratio) for dim in image.size)
            
            # Resize image
            resized_image = image.resize(new_size, Image.Resampling.LANCZOS)
            
            # Convert back to bytes
            output = io.BytesIO()
            resized_image.save(output, format=image.format or 'JPEG', quality=85)
            output.seek(0)
            
            # Close images
            image.close()
            resized_image.close()
            
            resized_bytes = output.getvalue()
            output.close()
            
            logger.info("Image resized", original_size=image.size, new_size=new_size)
            return resized_bytes
            
        except Exception as e:
            logger.error("Error resizing image", error=str(e))
            # Return original if resizing fails
            return image_bytes


# Global service instance
image_service = ImageService()



