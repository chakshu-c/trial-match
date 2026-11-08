# Prompt: TrialMatch presentation that answers the critiques

Copy everything below the line into your AI tool, and attach `WRITEUP.md`, `README.md` and `docs/EVALUATION.md` from this repo if it accepts files.

---

You are helping a hackathon team build a presentation for **TrialMatch** (AgentVerse 2026, Biotech track: "Make the path to patients faster"). Judges and mentors raised critiques of an earlier version. The deck must answer each critique directly, show what changed, and back every claim with evidence. Be honest: never invent numbers, and label synthetic data as synthetic.

## What TrialMatch is

Trials stall because finding eligible patients is slow and manual. TrialMatch gives every patient an agent that finds and pre-checks recruiting trials for them, and gives every trial team a ranked list of patients who already fit, so trials fill faster.

- Scope: recruiting and not-yet-recruiting Phase 3 non-small cell lung cancer (NSCLC) trials from ClinicalTrials.gov (205 treatment trials, snapshot 7 Nov 2026), matched against 30 de-identified patient records from public cBioPortal studies (TCGA LUAD, TCGA LUSC, MSKCC NSCLC 2018).
- How matching works: a rule-based parser turns free-text eligibility into fields (stage, histology, ECOG, biomarkers such as EGFR/ALK/ROS1/KRAS/BRAF/RET/MET, PD-L1, prior treatment lines, brain metastases, fresh biopsy, placebo arm). Each criterion is labelled met / not met / unknown with the quoted line from the record and from the trial. "Not met" requires a recorded value; missing data becomes "unknown" and turns into a plain-English question for the patient.
- Ranking: Score = E × F × (1 + 0.2D). E is eligibility (each unknown ×0.7, any "not met" removes the trial). F is feasibility (fresh biopsy ×0.7, evidence-based from screen-failure rates of 49.1% vs 26.5%, Spiegel et al., Cancer 2017; placebo ×0.9; distance). D is a boost for under-enrolled groups (age 70+, Black patients). Weights other than the biopsy penalty are team assumptions.
- Accuracy: the parser was hand-checked against raw trial text. 85% of fields correct on a 12-trial tuning sample before fixes; 92% (58/63) on 8 held-out trials after fixes.
- A research nurse confirms every match. The tool never enrols anyone or tells a patient they qualify.

## The critiques, and our answers

1. **"Swiping is too childish for something this serious."**
   We removed the swipe interface everywhere. Patients now land on their agent: a conversation that recommends trials as cards with "I'm interested", "Not for me" and "Tell me more", and explains any trial in plain English. Clinicians land on a review queue (candidate list beside the open case, with criterion-by-criterion evidence and Pass / Not eligible decisions). Ranking is a pairwise "higher / lower priority than #k" comparison using binary insertion, not a swipe.

2. **"Why would a patient volunteer? What's the incentive?"**
   The target patients are people with advanced or incurable lung cancer who are open to new treatments. For them the incentive is concrete: access to treatments not yet widely available, often when standard options are running out; trial treatment usually provided at no cost with extra specialist monitoring; travel and parking usually reimbursed, sometimes payment for extra visits; and helping the next patient. The agent also shows the trade-offs up front (more visits, fresh biopsies, placebo arms). Exact cover varies by trial and is confirmed by the team, because ClinicalTrials.gov doesn't record it.

3. **"Who is the customer?"**
   Trial teams first (research nurses, coordinators, principal investigators). Recruitment is where trials lose the most time. Sign-in now defaults to the clinician side, and the pitch, metrics and features are built around recruitment speed. The patient agent is how applicants arrive pre-checked.

4. **"What about data and privacy?"**
   Matching runs on the patient's device: the app downloads the trial list and the rules and processes the record locally (in the demo the whole matcher runs in the browser). Applications go only to the chosen trial's team, as a record ID plus evidence; the name is shared only when the patient accepts an invitation to prescreening. Consent controls include "Let my agent apply for me if a trial doesn't work out".

5. **"Can you trust an LLM with medical eligibility?" (MED: MedGemma)**
   The core matcher is rule-based and auditable, with quoted evidence for every decision and a held-out accuracy of 92%. An LLM is optional and only used for criteria the rules don't cover (labs, comorbidities, other drugs). It now defaults to MedGemma, Google's open medical model, running locally through Ollama (4B model: about 8–16 GB RAM; 27B text model: about 32 GB RAM or a 24 GB GPU), so records never leave the machine. Its output follows the same rules: "not met" only with a quoted value, otherwise "unknown". A nurse still confirms every match.

6. **"Is it actually faster? Prove it."**
   The clinician Overview measures only what the app can observe: median days from application to prescreen decision, prescreen pass rate, patients sent on to another trial after failing one, and comparisons needed to rank a batch (against comparing every pair). We deliberately don't claim "days saved", because the demo activity is synthetic. The honest next step is a pilot at one site, compared with its own historical timelines.

7. **"Is any of this real?"**
   Real: the trials, the de-identified records, the matcher, the parser and its evaluation. Synthetic and labelled as such in the app: patient names and cities, blood-test charts, inbox messages, application history, prescreen outcomes.

## Evidence to cite (use exactly these; don't add others unless you can source them)

- Only 5.3% of 9,901 US patients with lung or colorectal cancer enrolled in a trial (CanCORS cohort, J Oncol Pract 2013).
- In a typical trial, 11% of activated sites enrol no one and 37% under-enrol (Tufts CSDD, 2013, about 16,000 sites).
- Of 7,776 phase II–III adult cancer trials, 935 ended early for reasons other than safety or results; 39% of those stopped for poor accrual (Stensland et al., JNCI 2014).
- Fresh-biopsy trials: screen-failure 49.1% vs 26.5% (Spiegel et al., Cancer 2017).

## Deck structure (12–14 slides)

1. Title and one-line pitch.
2. The problem, with the three statistics above.
3. Where recruitment time goes (patients don't hear about trials; manual eligibility checks; late prescreen failures; slow applicant sorting; patients lost after a failed screen).
4. What we heard: the critiques as a single list, framed as "feedback that changed the product".
5. Critique 1, swipe to serious: before and after (swipe deck → agent conversation and review queue).
6. Critique 3, built for trial teams: the clinician workflow (Review → Rank → Applications → Overview).
7. Critique 6, measuring speed: the four Overview metrics, and why we don't claim days saved.
8. Critique 2, why patients take part: the target patient, the incentives, and the trade-offs we show.
9. Critique 4, privacy by design: a simple diagram of trial list + rules downloaded, record processed on device, only applications leave.
10. Critique 5, MedGemma and trust: rules first, local LLM second, nurse always; the 85% → 92% evaluation.
11. Critique 7, real vs synthetic: a two-column table.
12. Limits and next steps: known parser blind spots (rarer biomarkers HER2/NTRK/MET amplification; trials that require brain metastases; some supportive-care studies registered as treatment), synthetic activity, a site pilot to measure real time saved, running MedGemma on-device.
13. Closing: the pitch line again and the live site link https://trial-match-ebon.vercel.app/

## Style

- Serious, clinical and calm: deep navy text on light blue-grey, with a blue-violet-rose gradient (#4285F4 → #9B72CB → #D96570) used sparingly for the title and key numbers.
- One idea per slide, short sentences, sentence case, no jargon without a plain-English gloss.
- Use screenshots of the live demo where they help (agent home, review queue, rank, Overview metrics).
- Speaker notes for each slide: 2–4 sentences on what to say, including how to answer a follow-up question on that critique.
- Never present synthetic numbers as real results, and don't invent statistics, quotes or partner names.
