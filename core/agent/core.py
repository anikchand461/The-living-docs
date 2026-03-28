from core.diff.preprocessor import DiffPreprocessor
from core.agent.page_resolver import PageResolver
from core.agent.confidence_scorer import ConfidenceScorer
from core.agent.content_planner import ContentPlanner
from core.notion.client import MCPClient
from core.decision.gate import DecisionGate
from core.staleness.tracker import StalenessTracker
from core.github.client import GitHubClient
from core.models.pr import PREvent
from utils.logging import logger
from utils.hash import compute_diff_hash

class MCPAgentCore:
    def __init__(self):
        self.diff_processor = DiffPreprocessor()
        self.page_resolver = PageResolver()
        self.confidence_scorer = ConfidenceScorer()
        self.content_planner = ContentPlanner()
        self.notion_client = MCPClient()
        self.decision_gate = DecisionGate()
        self.staleness_tracker = StalenessTracker()
        self.github_client = GitHubClient()

    async def process(self, event: PREvent) -> dict:
        logger.info(f"Processing PR #{event.pr_number}")

        event.diff_hash = compute_diff_hash(event.diff)
        if await self.notion_client.check_idempotency(event.pr_number, event.diff_hash):
            return {"status": "already_processed"}

        processed_diff = self.diff_processor.process(event.diff)
        logger.info(f"Changed modules: {processed_diff.impacted_modules}")

        mappings = await self.page_resolver.resolve(processed_diff)
        logger.info(f"Found {len(mappings)} matching Notion pages")

        confidence = await self.confidence_scorer.score(processed_diff, mappings)
        logger.info(f"Confidence: {confidence.score}% — {confidence.explanation}")

        plan = await self.content_planner.plan(processed_diff, mappings, confidence)
        logger.info(f"Plan: {plan.action} on page {plan.target_page_id}")

        decision = self.decision_gate.evaluate(confidence.score)

        if decision == "auto_write":
            await self.notion_client.execute_plan(plan)
            await self.staleness_tracker.update(plan.target_page_id, event.pr_number)
            await self.github_client.post_comment(event.pr_number, f"✅ Notion docs updated: notion.so/{plan.target_page_id}")
        elif decision == "create_page":
            await self.notion_client.create_new_page(plan)
        else:
            await self.notion_client.flag_for_review(event.pr_number, plan)

        return {
            "pr": event.pr_number,
            "confidence": confidence.score,
            "action": decision,
            "notion_page": plan.target_page_id,
            "explanation": confidence.explanation
        }
