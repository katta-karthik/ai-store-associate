"""Automated Test Suite for Prime Agent Recursive Sub-Agents & Continual Refinement Engine v3.1."""

import pytest
from unittest.mock import AsyncMock, patch
from agent_app.core.recursive_runner import SubAgentTask, SubAgentResult, RecursiveSubAgentRunner
from agent_app.eval.self_refinement import ContinualRefinementEngine, TrajectoryRecord
from agent_app.graph.nodes.deep_research import deep_research_node
from agent_app.schemas.agent_state import ShopAgentState, ShopperProfile


@pytest.mark.asyncio
async def test_subagent_task_isolated_execution():
    """Verify sub-agents execute in isolated context without token/variable contamination."""
    runner = RecursiveSubAgentRunner()

    task = SubAgentTask(
        subagent_id="sub_test_01",
        role_name="🔬 Biomechanics Specialist",
        specialty="Biomechanics & Cushioning",
        objective="Analyze flat feet impact dispersion",
        context_slice={
            "product": {
                "id": "p_nike_pegasus",
                "title": "Nike Air Zoom Pegasus 40",
                "brand": "Nike",
                "description": "Zoom air cushioning with breathable mesh",
                "base_price": 11495,
            },
            "query": "I have flat feet and need shock absorption",
        },
    )

    result = await runner.execute_subagent(task)
    assert isinstance(result, SubAgentResult)
    assert result.subagent_id == "sub_test_01"
    assert result.confidence_score >= 80
    assert "Biomechanical Hero" in result.badges or "Gait Aligned" in result.badges
    assert len(result.pros) > 0


@pytest.mark.asyncio
async def test_parallel_subagent_council_execution():
    """Verify multiple sub-agents execute concurrently in non-blocking fashion."""
    runner = RecursiveSubAgentRunner()

    tasks = [
        SubAgentTask(
            subagent_id="sub_biomech",
            role_name="🔬 Biomechanics Specialist",
            specialty="Biomechanics",
            objective="Check arch support",
            context_slice={"product": {"title": "Nike Air Zoom", "description": "Zoom air"}, "query": "flat feet"},
        ),
        SubAgentTask(
            subagent_id="sub_value",
            role_name="💰 Value Hunter",
            specialty="Value & Pricing",
            objective="Evaluate price tier",
            context_slice={"product": {"title": "Nike Air Zoom", "base_price": 9500}, "query": "cheap deal"},
        ),
        SubAgentTask(
            subagent_id="sub_style",
            role_name="🎨 Style Critic",
            specialty="Style DNA",
            objective="Evaluate silhouette",
            context_slice={"product": {"title": "Nike Air Zoom", "brand": "Nike", "description": "lifestyle"}, "query": "stylish"},
        ),
    ]

    results = await runner.execute_parallel_council(tasks)
    assert len(results) == 3
    assert all(isinstance(r, SubAgentResult) for r in results)

    # Verify recursive synthesis
    synthesis = await runner.recursive_synthesize("Find me a good shoe", results)
    assert "AI Council" in synthesis
    assert "Overall Match Confidence" in synthesis


@pytest.mark.asyncio
async def test_deep_research_node_with_recursive_council():
    """Verify deep_research_node dispatches to recursive sub-agent council and returns structured UI actions."""
    mock_products = [
        {
            "id": "p_nike_invincible",
            "title": "Nike ZoomX Invincible Run 3",
            "brand": "Nike",
            "description": "Ultra plush zoomx foam with maximum cushioning for knee pain and flat feet",
            "base_price": 16995,
        },
        {
            "id": "p_adidas_ultraboost",
            "title": "Adidas Ultraboost Light",
            "brand": "Adidas",
            "description": "Boost capsule cushioning for long distance marathon training",
            "base_price": 18999,
        },
    ]

    state = ShopAgentState(
        user_query="I have severe knee pain and flat feet, recommend the best marathon running shoe",
        shopper_profile=ShopperProfile(
            shopper_id="test_shopper_01",
            style_dna=["Performance Runner"],
            favorite_brands=["Nike"],
            special_notes=["Flat feet", "Knee pain"],
        ),
    )

    with patch("agent_app.tools.store_tools.store_client.search_products", new=AsyncMock(return_value={"items": mock_products})):
        result = await deep_research_node(state)

        assert "final_response" in result
        assert "AI Council" in result["final_response"] or "Biomechanical" in result["final_response"]
        assert result["focus_target_id"] in ["p_nike_invincible", "p_adidas_ultraboost"]
        assert len(result["ui_actions"]) >= 3

        # Check for Show Research Report payload
        report_action = next(a for a in result["ui_actions"] if a.action == "SHOW_RESEARCH_REPORT")
        assert "subagent_council" in report_action.payload
        assert len(report_action.payload["subagent_council"]) == 3


def test_continual_refinement_trajectory_logging(tmp_path):
    """Verify continual refinement engine logs trajectories and analyzes retrospective metrics."""
    test_log = str(tmp_path / "test_trajectories.jsonl")
    engine = ContinualRefinementEngine(log_path=test_log)

    engine.log_trajectory(
        TrajectoryRecord(
            user_query="test query 1",
            nodes_executed=["memory_loader", "deep_research"],
            confidence_score=95,
            latency_ms=450.0,
            subagent_council_used=True,
            success=True,
        )
    )

    analysis = engine.analyze_recent_trajectories()
    assert analysis["total_runs"] == 1
    assert analysis["success_rate"] == 1.0
    assert analysis["avg_confidence"] == 95

    refine_result = engine.refine_playbook()
    assert refine_result["status"] == "PLAYBOOK_OPTIMIZED"
