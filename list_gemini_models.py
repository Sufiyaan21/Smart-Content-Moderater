import google.generativeai as genai
from app.core.config import settings

# Configure Gemini API
genai.configure(api_key=settings.gemini_api_key)

# List available models
models = genai.list_models()
print("Available Gemini models:")
for model in models:
    print(model.name)
