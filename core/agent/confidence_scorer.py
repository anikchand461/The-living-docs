from core.models.pr import ConfidenceReport, ProcessedDiff
from core.llm.router import LLMRouter
from utils.logging import logger
import json

class ConfidenceScorer:
    def __init__(self):
        self.llm = LLMRouter().get_adapter()

    async def score(self, diff: ProcessedDiff, mappings: list) -> ConfidenceReport:
        if not mappings:
            return ConfidenceReport(score=30, explanation="No matching Notion pages found")

        prompt = f"""You are an architecture documentation assistant.

A code diff touched these modules: {diff.impacted_modules}
These Notion pages were found as potential matches: {[m.title for m in mappings]}

Rate how confident you are (0-100) that these pages should be updated based on this diff.
Respond with ONLY a JSON object like:
{{"score": 85, "explanation": "The diff directly modifies the agent module which matches the Architecture Docs page"}}"""

        try:
            raw = await self.llm.generate_raw(prompt)
            raw = raw.strip().replace("```json", "").replace("```", "").strip()
            data = json.loads(raw)
            score = int(data.get("score", 50))
            explanation = data.get("explanation", "")
            logger.info(f"[ConfidenceScorer] Score: {score} — {explanation}")
            return ConfidenceReport(score=score, explanation=explanation)
        except Exception as e:
            logger.error(f"[ConfidenceScorer] Failed: {e}")
            return ConfidenceReport(score=50, explanation="Could not determine confidence")
