import httpx
from core.config import settings
from utils.logging import logger

class GroqAdapter:
    def __init__(self):
        self.api_key = settings.groq_api_key
        self.base_url = "https://api.groq.com/openai/v1"
        self.model = "llama-3.3-70b-versatile"

    async def generate_raw(self, prompt: str) -> str:
        logger.info("[Groq] Sending prompt...")
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3
                },
                timeout=30.0
            )
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"]

    async def generate_structured(self, prompt: str, output_schema=None, temperature: float = 0.0, model=None) -> str:
        return await self.generate_raw(prompt)
