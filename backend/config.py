"""
Configuration module for RegLoop AI
Safely loads environment variables and API keys
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class for secure API key management"""
    
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    
    @classmethod
    def validate(cls):
        """Validate that required configuration is present"""
        if not cls.GEMINI_API_KEY:
            raise ValueError(
                "GEMINI_API_KEY not found. "
                "Please set it in the .env file or as an environment variable."
            )
    
    @classmethod
    def is_configured(cls) -> bool:
        """Check if Gemini API is properly configured"""
        return cls.GEMINI_API_KEY is not None and len(cls.GEMINI_API_KEY) > 0

# Validate config on import
if __name__ != "__main__":
    if Config.is_configured():
        print("✓ Gemini API configured successfully")
