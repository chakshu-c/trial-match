"""Optional LLM pass over the criteria the rule-based parser does not cover.

Runs only on each patient's top few trials. Two backends:

  local  (default for privacy)  MedGemma, Google's open medical model, on this machine through
         Ollama or any server with the same /api/chat endpoint. Patient records never leave the
         machine.
             ollama pull medgemma:4b          # ~3 GB, 8-16 GB RAM; medgemma:27b needs ~32 GB / a 24 GB GPU
             python run.py --llm 3 --llm-backend local
         Settings: LOCAL_LLM_URL (default http://localhost:11434/api/chat), LOCAL_LLM_MODEL (default medgemma:4b).
         The model tag depends on what your Ollama install lists (`ollama list`).

  gemini Gemini in the cloud. Sends the de-identified record lines to Google. Needs either
           GEMINI_API_KEY, or GOOGLE_CLOUD_PROJECT [+ GOOGLE_CLOUD_LOCATION] (Vertex AI)
         pip install google-genai

Not run in our offline build: treat as a starting point to test on the day.
"""
import json
import os

MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")  # swap for the newest Flash your project lists
LOCAL_URL = os.environ.get("LOCAL_LLM_URL", "http://localhost:11434/api/chat")
LOCAL_MODEL = os.environ.get("LOCAL_LLM_MODEL", "medgemma:4b")

PROMPT = """You check a lung cancer patient against clinical trial eligibility criteria.

Patient record (each value is quoted exactly as recorded):
{record}

Criteria to check (I = inclusion, E = exclusion):
{criteria}

For EVERY criterion return one JSON object:
{{"id": <number>, "status": "met" | "not_met" | "unknown" | "not_applicable",
  "patient_evidence": "<exact quote from the record above, or 'none'>",
  "reason": "<one plain-English sentence>"}}
Rules:
- For an exclusion criterion, "met" means the patient is NOT excluded by it.
- Use "not_met" only when a quoted value in the record proves it. Missing information is "unknown".
- Consent, contraception, organ-function labs and similar items the record does not cover are "unknown".
- Administrative lines that are not criteria are "not_applicable".
Return a JSON list only."""


def _client():
    from google import genai
    if os.environ.get("GEMINI_API_KEY"):
        return genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    return genai.Client(vertexai=True, project=os.environ["GOOGLE_CLOUD_PROJECT"],
                        location=os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1"))


def _ask_local(prompt):
    import requests
    r = requests.post(LOCAL_URL, timeout=600, json={
        "model": LOCAL_MODEL, "stream": False, "format": "json", "options": {"temperature": 0},
        "messages": [{"role": "user", "content": prompt}]})
    r.raise_for_status()
    text = r.json()["message"]["content"]
    data = json.loads(text)
    # small local models sometimes wrap the list in an object
    if isinstance(data, dict):
        data = next((v for v in data.values() if isinstance(v, list)), [])
    return data


def _ask_gemini(prompt):
    from google.genai import types
    resp = _client().models.generate_content(
        model=MODEL, contents=prompt,
        config=types.GenerateContentConfig(response_mime_type="application/json", temperature=0))
    return json.loads(resp.text)


def llm_labels(patient, trial, used_evidence, max_lines=40, backend="local"):
    lines = [("I", l) for l in trial["inclusion"]] + [("E", l) for l in trial["exclusion"]]
    lines = [(k, l) for k, l in lines if l not in used_evidence][:max_lines]
    if not lines:
        return []
    record = "\n".join(f"- {v}" for v in patient["evidence"].values())
    criteria = "\n".join(f"{i}. [{k}] {l}" for i, (k, l) in enumerate(lines))
    prompt = PROMPT.format(record=record, criteria=criteria)
    items = _ask_local(prompt) if backend == "local" else _ask_gemini(prompt)
    source = LOCAL_MODEL if backend == "local" else "gemini"
    out = []
    for item in items:
        try:
            i = int(item["id"])
        except (KeyError, TypeError, ValueError):
            continue
        if i < 0 or i >= len(lines) or item.get("status") not in ("met", "not_met", "unknown"):
            continue
        out.append({"field": f"criterion_{lines[i][0]}{i}", "status": item["status"],
                    "patient_evidence": item.get("patient_evidence", "none"),
                    "trial_evidence": lines[i][1], "reason": item.get("reason", ""), "source": source})
    return out
