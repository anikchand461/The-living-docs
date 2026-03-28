from core.models.pr import ContentPlan, ProcessedDiff, NotionMapping, ConfidenceReport
from core.llm.router import LLMRouter
from utils.logging import logger

class ContentPlanner:
    def __init__(self):
        self.llm = LLMRouter().get_adapter()

    async def plan(self, diff: ProcessedDiff, mappings: list, confidence: ConfidenceReport) -> ContentPlan:
        if not mappings:
            return ContentPlan(
                action="create_page",
                new_page_title=f"Architecture: {', '.join(diff.impacted_modules[:2])}",
                reason="No matching page found"
            )

        target = mappings[0]

        prompt = f"""You are an architecture documentation assistant.

A code change was made to these modules: {diff.impacted_modules}
Files changed: {diff.files}

Write a concise architecture documentation update (2-4 sentences) explaining:
- What changed
- Why it matters architecturally
- Any impact on other components

Be specific and technical. Write in present tense."""

        try:
            doc_content = await self.llm.generate_raw(prompt)
            logger.info(f"[ContentPlanner] Gemini response: {doc_content[:100]}...")
        except Exception as e:
            logger.error(f"[ContentPlanner] Gemini failed: {e}")
            doc_content = f"Code changes detected in modules: {', '.join(diff.impacted_modules)}. Files modified: {', '.join(diff.files)}. Manual review recommended."

        logger.info(f"[ContentPlanner] Writing to page: {target.title}")

        blocks = [
            {
                "object": "block",
                "type": "heading_3",
                "heading_3": {
                    "rich_text": [{"type": "text", "text": {"content": f"📝 Update — {', '.join(diff.impacted_modules)}"}}]
                }
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": doc_content.strip()}}]
                }
            },
            {
                "object": "block",
                "type": "divider",
                "divider": {}
            }
        ]

        return ContentPlan(
            action="append_block",
            target_page_id=target.page_id,
            blocks=blocks,
            reason=f"Matched page '{target.title}' with confidence {confidence.score}%"
        )
