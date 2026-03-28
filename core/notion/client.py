import httpx
from core.config import settings
from core.models.pr import ContentPlan
from utils.logging import logger

NOTION_VERSION = "2022-06-28"

class MCPClient:
    def __init__(self):
        self.base_url = "https://api.notion.com/v1"
        self.headers = {
            "Authorization": f"Bearer {settings.notion_api_key}",
            "Notion-Version": NOTION_VERSION,
            "Content-Type": "application/json",
        }

    async def search_pages(self, query: str) -> list:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.base_url}/search",
                headers=self.headers,
                json={"query": query, "filter": {"property": "object", "value": "page"}},
                timeout=30.0
            )
            if resp.status_code != 200:
                logger.error(f"Notion search failed: {resp.text}")
                return []
            results = resp.json().get("results", [])
            pages = []
            for r in results:
                try:
                    title = r["properties"]["title"]["title"][0]["plain_text"]
                except Exception:
                    title = "Untitled"
                pages.append({"id": r["id"], "title": title})
            return pages

    async def append_block(self, page_id: str, blocks: list) -> dict:
        async with httpx.AsyncClient() as client:
            resp = await client.patch(
                f"{self.base_url}/blocks/{page_id}/children",
                headers=self.headers,
                json={"children": blocks},
                timeout=30.0
            )
            if resp.status_code != 200:
                logger.error(f"Notion append failed: {resp.text}")
            resp.raise_for_status()
            return resp.json()

    async def create_page(self, title: str, parent_id: str = None) -> dict:
        pid = parent_id or settings.notion_page_id
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.base_url}/pages",
                headers=self.headers,
                json={
                    "parent": {"page_id": pid},
                    "properties": {
                        "title": {"title": [{"text": {"content": title}}]}
                    }
                },
                timeout=30.0
            )
            resp.raise_for_status()
            return resp.json()

    async def create_comment(self, page_id: str, text: str) -> dict:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.base_url}/comments",
                headers=self.headers,
                json={
                    "parent": {"page_id": page_id},
                    "rich_text": [{"text": {"content": text}}]
                },
                timeout=30.0
            )
            resp.raise_for_status()
            return resp.json()

    async def execute_plan(self, plan: ContentPlan):
        page_id = plan.target_page_id or settings.notion_page_id
        blocks = plan.blocks or []
        logger.info(f"[Notion] Writing doc update to page {page_id}")
        return await self.append_block(page_id, blocks)

    async def create_new_page(self, plan: ContentPlan):
        title = plan.new_page_title or "New Architecture Doc"
        logger.info(f"[Notion] Creating new page: {title}")
        return await self.create_page(title)

    async def flag_for_review(self, pr_number: int, plan: ContentPlan):
        page_id = plan.target_page_id or settings.notion_page_id
        text = f"⚠️ PR #{pr_number} needs human review. Reason: {plan.reason}"
        logger.info(f"[Notion] Flagging PR #{pr_number} for review")
        return await self.create_comment(page_id, text)

    async def check_idempotency(self, pr_number: int, diff_hash: str) -> bool:
        return False
