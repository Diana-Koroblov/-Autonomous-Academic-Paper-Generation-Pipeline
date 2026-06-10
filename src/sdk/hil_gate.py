import logging
import os
from pathlib import Path
from typing import Callable, Dict, List

logger = logging.getLogger(__name__)

AUTO_APPROVE_ENV = "HIL_AUTO_APPROVE"
AFFIRMATIVE = {"y", "yes", "approve", "approved", "1", "true"}

REVIEW_ITEMS: List[str] = [
    "Academic prose quality and tone (4.3.2)",
    "Validity of TikZ source formulas and mathematics (4.3.3)",
    "Accuracy of factual references and citations (4.3.4)",
    "Positive AI Economy compliance (4.3.1)",
]


class HumanInLoopGate:
    """
    Enforces a hard Human-in-the-Loop pause after draft generation. Execution
    halts pending manual sign-off across the mandated Positive AI Economy review
    items. Supports non-interactive auto-approval via the HIL_AUTO_APPROVE env var.
    """

    def __init__(self, input_fn: Callable[[str], str] = input, auto_approve: bool | None = None) -> None:
        self.input_fn = input_fn
        if auto_approve is None:
            auto_approve = os.environ.get(AUTO_APPROVE_ENV, "").strip().lower() in AFFIRMATIVE
        self.auto_approve = auto_approve

    def _banner(self, artifact_path: str | Path) -> None:
        logger.warning("=" * 70)
        logger.warning("HARD HUMAN-IN-THE-LOOP PAUSE — Positive AI Economy compliance gate.")
        logger.warning(f"Draft awaiting manual review: {artifact_path}")
        logger.warning("Pipeline execution is halted until every item is approved.")
        logger.warning("=" * 70)

    def _decide(self, item: str) -> bool:
        if self.auto_approve:
            logger.info(f"[AUTO-APPROVED] {item}")
            return True
        answer = self.input_fn(f"Approve -> {item}? [y/N]: ").strip().lower()
        return answer in AFFIRMATIVE

    def request_approval(self, artifact_path: str | Path) -> Dict[str, object]:
        """
        Halts and collects a sign-off decision for each mandated review item.
        Returns a dict with the overall 'approved' flag and per-item 'decisions'.
        """
        self._banner(artifact_path)
        decisions: Dict[str, bool] = {}
        for item in REVIEW_ITEMS:
            decisions[item] = self._decide(item)

        approved = all(decisions.values())
        if approved:
            logger.warning("HIL GATE PASSED: all review items approved. Resuming pipeline.")
        else:
            rejected = [k for k, v in decisions.items() if not v]
            logger.error(f"HIL GATE BLOCKED: rejected items -> {rejected}")
        return {"approved": approved, "decisions": decisions}
