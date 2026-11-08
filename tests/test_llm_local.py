"""The local (MedGemma via Ollama) LLM backend, with the HTTP call faked so no model is needed."""
import json
import trialmatch.llm as llm


class FakeResp:
    def __init__(self, items):
        self.items = items

    def raise_for_status(self):
        pass

    def json(self):
        return {"message": {"content": json.dumps({"results": self.items})}}


def test_local_backend_parses_and_filters(monkeypatch):
    sent = {}

    def fake_post(url, json=None, timeout=None):
        sent.update(url=url, body=json)
        return FakeResp([
            {"id": 0, "status": "met", "patient_evidence": "ECOG 1", "reason": "ok"},
            {"id": 1, "status": "not_applicable"},
            {"id": 7, "status": "met"},          # out of range: dropped
            {"id": "x", "status": "met"},        # malformed: dropped
        ])

    import requests
    monkeypatch.setattr(requests, "post", fake_post)
    patient = {"evidence": {"ecog": "ECOG 1"}}
    trial = {"inclusion": ["Adequate organ function", "Signed consent"], "exclusion": []}
    out = llm.llm_labels(patient, trial, used_evidence="", backend="local")
    assert sent["url"] == llm.LOCAL_URL and sent["body"]["model"] == llm.LOCAL_MODEL
    assert [o["status"] for o in out] == ["met"]
    assert out[0]["trial_evidence"] == "Adequate organ function" and out[0]["source"] == llm.LOCAL_MODEL
