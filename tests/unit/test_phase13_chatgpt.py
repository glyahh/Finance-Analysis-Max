from finance_research.adapters.chatgpt import ChatGPTAdapter


def test_chatgpt_adapter_returns_fixed_rendered_answer():
    response = ChatGPTAdapter().respond(
        {
            "prompt": "研究未来3个月",
            "minimum_evidence": 3,
            "candidates": [
                {
                    "instrument_id": "000001",
                    "name": "示例标的",
                    "prices": [100, 101, 103, 102, 106, 110, 108],
                    "evidence": [
                        {"topic": "market", "value": "observed", "source": "test", "fetched_at": "2026-09-16T00:00:00+00:00"},
                        {"topic": "earnings", "value": "observed", "source": "test", "fetched_at": "2026-09-16T00:00:00+00:00"},
                        {"topic": "outflow", "value": "observed", "source": "test", "fetched_at": "2026-09-16T00:00:00+00:00"},
                    ],
                }
            ],
        }
    )
    assert response["status"] == "ready"
    assert "## 1. 研究结论摘要" in response["answer"]
    assert "## 6. 购买优先级" in response["answer"]


def test_chatgpt_adapter_does_not_hide_missing_conditions():
    response = ChatGPTAdapter().respond({"prompt": "分析", "candidates": []})
    assert response["status"] == "needs_information"
    assert "forecast_horizon" in response["answer"]

