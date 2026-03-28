from core.models.pr import ProcessedDiff, NotionMapping
from core.notion.client import MCPClient
from core.config import settings
from utils.logging import logger

class PageResolver:
    async def resolve(self, diff: ProcessedDiff) -> list[NotionMapping]:
        client = MCPClient()

        # Always include the root architecture page as a fallback
        root_page = NotionMapping(
            page_id=settings.notion_page_id,
            title="Architecture Docs",
            relevance_score=0.7,
            match_reason="Root architecture documentation page"
        )

        # Also search for more specific matches
        queries = diff.architecture_components[:3] + ["Architecture"]
        all_results = []

        for query in queries:
            logger.info(f"[PageResolver] Searching Notion for: {query}")
            results = await client.search_pages(query)
            for r in results:
                if not any(p.page_id == r["id"] for p in all_results):
                    all_results.append(NotionMapping(
                        page_id=r["id"],
                        title=r["title"],
                        relevance_score=0.9,
                        match_reason=f"Matched query: {query}"
                    ))

        if all_results:
            return all_results

        # Fall back to root page
        logger.info(f"[PageResolver] No matches found, using root page")
        return [root_page]
