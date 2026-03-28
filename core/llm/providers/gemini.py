from google import genai
from core.config import settings
from utils.logging import logger

class GeminiAdapter:
    def __init__(self):
        self.client = genai.Client(api_key=settings.gemini_api_key)

    async def generate_raw(self, prompt: str) -> str:
        logger.info("[Gemini] Sending prompt...")
        response = self.client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt
        )
        return response.text

    async def generate_structured(self, prompt: str, output_schema=None, temperature: float = 0.0, model=None) -> str:
        return await self.generate_raw(prompt)
