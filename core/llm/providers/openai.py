class OpenAIAdapter:
    async def generate_raw(self, prompt: str) -> str:
        raise NotImplementedError("OpenAI not configured. Set OPENAI_API_KEY to use.")

    async def generate_structured(self, prompt: str, output_schema=None, temperature: float = 0.0, model=None) -> str:
        return await self.generate_raw(prompt)
