# TrialMatch

**Fill lung cancer trials faster: an agent for every patient, a ranked, pre-checked list for every trial team.**
AgentVerse 2026 · Biotech track · *Make the path to patients faster*

Trials stall because finding eligible patients is slow and manual. Only 5.3% of 9,901 US patients with lung or colorectal cancer joined a trial (CanCORS), and 39% of cancer trials that closed early for reasons other than safety or results stopped for poor accrual (Stensland et al., 2014). TrialMatch ranks recruiting Phase III non-small cell lung cancer (NSCLC) trials by how likely a patient is to **succeed** in each one: be eligible, enrol, and stay to the end. A research nurse prescreens every match, and their results feed back into the matcher. The full case, with sources, is in [WRITEUP.md](WRITEUP.md).

- **Trial teams** (the customer) review pre-checked applicants with the evidence for every criterion, rank them in a handful of comparisons, and move them through prescreening to enrolment.
- **Patients** talk to their agent, which recommends trials that fit, explains them, and applies when they're ready. Matching runs on their device.

## Quick start

```bash
pip install -r requirements.txt
python run.py                       # match 30 patients x 205 recruiting Phase 3 NSCLC treatment trials -> results/
python build_app.py                 # rebuild the app from the matcher -> app/index.html
python -m pytest -q tests           # parser tests
```

Open `app/index.html` in a browser: no server or install needed.

Other options:

```bash
python run.py --refresh                                    # re-download trials from ClinicalTrials.gov first
python run.py --home 51.5246,-0.1340                       # add travel distance from a home location
python run.py --feedback data/prescreen_outcomes_DEMO.csv  # feed nurse prescreening back in (demo rows are synthetic)
python run.py --llm 3                                      # optional MedGemma pass over remaining criteria, run locally via Ollama
python run.py --llm 3 --llm-backend gemini                 # same pass on cloud Gemini (needs GEMINI_API_KEY or GOOGLE_CLOUD_PROJECT)
```

## How it works

1. **Trial Scout** (`fetch_trials.py`): recruiting and not-yet-recruiting Phase 3 NSCLC trials from the ClinicalTrials.gov API v2. Snapshot of 7 Nov 2026: 210 trials, 205 with treatment as their primary purpose, 46 with UK sites.
2. **Criteria Parser** (`trialmatch/criteria.py`): turns free-text eligibility into the fields that decide most NSCLC matches. These are stage range, histology, ECOG limit, required or excluded biomarkers (EGFR, ALK, ROS1, KRAS G12C/G12D, BRAF V600E, RET, MET exon 14), PD-L1 threshold, prior treatment lines, brain metastases, fresh biopsy and placebo arm. Each field keeps the criterion line it came from.
3. **Eligibility Checker** (`trialmatch/match.py`): labels each criterion *met / not met / unknown*, quoting both the patient record and the trial text.
4. **Verifier**: a "not met" without a recorded value becomes "unknown", so nobody is ruled out on missing data.
5. **Interviewer**: turns unknowns into plain questions, asking first the one that settles the most trials. Untested biomarkers become "needs testing", never "no".
6. **Feasibility and ranking**: `Score = E x F x (1 + 0.2D)`
   - **E**, eligibility: each unknown x0.7, and any criterion not met removes the trial.
   - **F**, feasibility: 0.8 base. Fresh biopsy required x0.7, from screen-failure rates of 49.1% vs 26.5% (Spiegel et al., *Cancer* 2017). Placebo arm x0.9. Distant sites x0.85 / x0.7.
   - **D**, a boost for groups lung cancer trials under-enrol (age 70+, Black patients). It only ever raises a score.
   - Patients at stage IIIB–IV with ECOG 1 or more are flagged "refer this week".
   - Apart from the biopsy penalty, the weights are team assumptions, tunable in `W` in `trialmatch/match.py`.
7. **Prescreening loop** (`trialmatch/feedback.py`): the nurse's prescreen log feeds back in four ways.
   - Patient answers fill gaps in the record.
   - Corrections to a misread trial rule are saved for that trial.
   - Verdicts on a specific patient–trial pair override the agent; a screen failure or decline removes it, and an enrolled pair is listed first.
   - Outcomes re-estimate the weights (Beta-Binomial, starting from the team's guesses).
8. **LLM pass** (`trialmatch/llm.py`, optional): checks the criteria the parser doesn't model (labs, comorbidities, other drugs) for each patient's top trials. Defaults to MedGemma, Google's open medical model, running locally through Ollama (`ollama pull medgemma:4b`, then `--llm-backend local`), so records never leave the machine; `--llm-backend gemini` uses the cloud API instead. Same rules as the parser: "not met" only with a quoted value. Not run in the offline build.

## The app (`app/index.html`)

Live demo: https://chakshu-c.github.io/trial-match/

- **Sign in:** trial-team accounts first, or a demo patient. A new patient account links a spare research record.
- **Clinician**
  - **Review (home):** a queue of candidates for a trial beside the open case: criterion-by-criterion evidence with Confirm met / Not met, then Pass prescreening or Not eligible. Applicants come first, then anyone to refer this week.
  - **Overview:** what needs you today, recruitment-speed measures (application to prescreen decision, pass rate, patients sent on after a failed screen, comparisons per ranked batch), the applicant funnel, and the prescreen log (copies out in the format `run.py --feedback` reads).
  - **Rank:** compare each new applicant with one already ranked (binary insertion), then invite the top N to prescreening.
  - **Applications:** every application, filterable by trial and stage; open one to move it on, mark it not eligible or record a withdrawal.
- **Patient**
  - **Your agent (home):** a conversation that recommends trials as cards (I'm interested / Not for me / Tell me more), explains any trial, what taking part offers and how data is kept private. It's a preview: answers are scripted from the demo data and worked out in the browser.
  - **My trials:** each application with a 7-step progress bar, plus open matches and closed ones.
  - **My health:** diagnosis and biomarkers from the record, six-month charts with typical ranges and trial minimums (falling values in red), and privacy and consent settings, including letting the agent apply to the next best trial if one doesn't work out.
  - **Inbox:** messages from the agent and care team as an application moves.
- **No swiping:** decisions are explicit buttons with the evidence in view.
- **Synthetic demo data:** names, cities, lab charts, messages and application history are made up and labelled as such. Demo state is kept in the browser; reset it from Overview.

## Data

| Data | Source | Notes |
| --- | --- | --- |
| Trials | [ClinicalTrials.gov API v2](https://clinicaltrials.gov/data-api/api) (US National Library of Medicine) | Snapshot in `data/trials.json`, 7 Nov 2026 |
| Patients | `data/lung_cancer_patients.xlsx`: 30 de-identified records from public cBioPortal studies ([TCGA LUAD](https://www.cbioportal.org/study/summary?id=luad_tcga), [TCGA LUSC](https://www.cbioportal.org/study/summary?id=lusc_tcga), [MSKCC NSCLC 2018](https://www.cbioportal.org/study/summary?id=nsclc_pd1_msk_2018)) | Sources and limits in `docs/Patient_Data_Report.docx`. Treated as snapshots at diagnosis |
| Prescreen outcomes | `data/prescreen_outcomes_DEMO.csv` | **Synthetic**, hand-written to show the feedback loop. Never reported as performance |

No identifiable or private patient data is used.

## Evaluation and limits

The rule-based parser was hand-checked against raw trial text. It got 85% of fields right on a 12-trial tuning sample before fixes, and 92% (58/63) on 8 held-out trials after them. Method, fixes and known blind spots are in [`docs/EVALUATION.md`](docs/EVALUATION.md). Results are a demonstration on public research data, not real-world performance. TrialMatch recommends and explains; a research nurse confirms every match, and the tool never enrols anyone or tells a patient they qualify.

## Repo layout

```
app/            index.html (built app), template.html (app source)
data/           trials snapshot, patient records, synthetic prescreen demo
docs/           evaluation notes, patient data report
results/        matcher output; results_after_feedback_DEMO/ shows the loop
tests/          parser unit tests
trialmatch/     patients.py, criteria.py, match.py, feedback.py, llm.py
run.py          run the matcher      fetch_trials.py   download trials      build_app.py   rebuild the app
```
