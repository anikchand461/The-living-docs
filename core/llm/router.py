from core.config import settings
from utils.logging import logger

class LLMRouter:
    def get_adapter(self, complexity: str = "normal"):
        logger.info(f"[LLMRouter] groq={bool(settings.groq_api_key)} gemini={bool(settings.gemini_api_key)} anthropic={bool(settings.anthropic_api_key)}")
        
        if settings.groq_api_key:
            from core.llm.providers.groq import GroqAdapter
            logger.info("[LLMRouter] Using Groq")
            return GroqAdapter()
        if settings.anthropic_api_key:
            from core.llm.providers.claude import ClaudeAdapter
            logger.info("[LLMRouter] Using Claude")
            return ClaudeAdapter()
        if settings.gemini_api_key:
            from core.llm.providers.gemini import GeminiAdapter
            logger.info("[LLMRouter] Using Gemini")
            return GeminiAdapter()
        if settings.openai_api_key:
            from core.llm.providers.openai import OpenAIAdapter
            logger.info("[LLMRouter] Using OpenAI")
            return OpenAIAdapter()
        raise RuntimeError(
            "No LLM API key found. Set GROQ_API_KEY in your .env file."
        )
