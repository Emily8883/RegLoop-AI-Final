"""
Gemini AI Service for RegLoop AI
Provides safe integration with Google Generative AI API
"""

import logging
import google.generativeai as genai
from config import Config

logger = logging.getLogger(__name__)

# Validate configuration
if not Config.is_configured():
    logger.warning("Gemini API not configured. Some features may be unavailable.")
else:
    # Configure the Google Generative AI client
    genai.configure(api_key=Config.GEMINI_API_KEY)
    logger.info("✓ Gemini API configured successfully")


class GeminiService:
    """Service for interacting with Google Generative AI"""
    
    MODEL_NAME = "gemini-2.0-flash"
    
    @staticmethod
    def is_available() -> bool:
        """Check if Gemini API is available"""
        return Config.is_configured()
    
    @staticmethod
    def generate_text(prompt: str, max_tokens: int = 1024) -> str:
        """
        Generate text using Gemini API
        
        Args:
            prompt: The text prompt
            max_tokens: Maximum tokens in response
            
        Returns:
            Generated text response
        """
        if not GeminiService.is_available():
            raise RuntimeError(
                "Gemini API is not configured. "
                "Please set GEMINI_API_KEY in .env file."
            )
        
        try:
            model = genai.GenerativeModel(GeminiService.MODEL_NAME)
            response = model.generate_content(prompt)
            logger.info(f"✓ Generated text using Gemini API")
            return response.text
        except Exception as e:
            logger.error(f"Error calling Gemini API: {str(e)}")
            raise
    
    @staticmethod
    def analyze_obligations(text: str) -> dict:
        """
        Use Gemini to analyze and enhance obligation extraction
        
        Args:
            text: Document text to analyze
            
        Returns:
            Dictionary with analysis results
        """
        if not GeminiService.is_available():
            logger.warning("Gemini API not available, skipping enhancement")
            return {}
        
        try:
            prompt = f"""Analyze the following text and extract regulatory obligations.
For each obligation found, provide:
1. The obligation text
2. Category (operational, reporting, security, compliance)
3. Priority (high, medium, low)
4. Responsible team

Text:
{text[:2000]}

Return as JSON."""
            
            response = GeminiService.generate_text(prompt)
            logger.info("✓ Analyzed obligations with Gemini API")
            return {"analysis": response}
        except Exception as e:
            logger.error(f"Error analyzing obligations: {str(e)}")
            return {}


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    if GeminiService.is_available():
        print("Testing Gemini API...")
        result = GeminiService.generate_text("What are compliance obligations?")
        print(f"Result: {result}")
    else:
        print("Gemini API is not configured")
