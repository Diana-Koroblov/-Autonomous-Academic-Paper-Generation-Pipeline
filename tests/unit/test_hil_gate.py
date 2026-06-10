import os
import sys

# Add src to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

from sdk.hil_gate import REVIEW_ITEMS, HumanInLoopGate


def test_auto_approve_via_flag():
    gate = HumanInLoopGate(auto_approve=True)
    result = gate.request_approval("data/processed/output.md")
    assert result["approved"] is True
    assert len(result["decisions"]) == len(REVIEW_ITEMS)
    assert all(result["decisions"].values())


def test_auto_approve_via_env(monkeypatch):
    monkeypatch.setenv("HIL_AUTO_APPROVE", "yes")
    gate = HumanInLoopGate()
    assert gate.auto_approve is True
    assert gate.request_approval("out.md")["approved"] is True


def test_interactive_all_approved():
    gate = HumanInLoopGate(input_fn=lambda _prompt: "y", auto_approve=False)
    result = gate.request_approval("out.md")
    assert result["approved"] is True


def test_interactive_one_rejected():
    answers = iter(["y", "n", "y", "y"])
    gate = HumanInLoopGate(input_fn=lambda _prompt: next(answers), auto_approve=False)
    result = gate.request_approval("out.md")
    assert result["approved"] is False
    rejected = [k for k, v in result["decisions"].items() if not v]
    assert len(rejected) == 1


def test_env_default_is_blocking(monkeypatch):
    monkeypatch.delenv("HIL_AUTO_APPROVE", raising=False)
    gate = HumanInLoopGate(input_fn=lambda _prompt: "n")
    assert gate.auto_approve is False
    assert gate.request_approval("out.md")["approved"] is False
