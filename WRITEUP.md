# TrialMatch: filling lung cancer trials faster

**Trials stall because finding eligible patients is slow and manual. TrialMatch gives every patient an agent that finds and pre-checks trials for them, and gives every trial team a ranked list of patients who already fit, so trials fill faster and new treatments reach everyone sooner.**

AgentVerse 2026, Biotech track: *Make the path to patients faster.*

## The problem

- **Most patients never join a trial.** Only 5.3% of 9,901 US patients with lung or colorectal cancer in the CanCORS cohort enrolled in a clinical trial. [1]
- **Trial sites struggle to fill trials.** A Tufts CSDD study of about 16,000 sites found that in a typical trial 11% of activated sites enrol no one and 37% enrol fewer patients than planned. [2]
- **Trials close early for lack of patients.** Of 7,776 phase II–III adult cancer trials, 935 ended early for reasons other than safety or results, and 39% of those stopped because of poor accrual. [3]

## Where the time goes, and what TrialMatch does about it

| Slow step | What TrialMatch does | Status |
| --- | --- | --- |
| Patients don't hear about trials that fit | Each patient's agent checks every recruiting Phase 3 NSCLC trial (205 in the 7 Nov 2026 snapshot) against their record and recommends the best fits, and can apply for them with consent | In the demo |
| Checking eligibility is manual reading of long notes against long criteria | Every rule is checked before the application reaches the team, each with the line from the record and the line from the trial. "Not met" needs a recorded value; missing data is "unknown", never a rejection | In the demo |
| Patients fail prescreening after weeks of waiting | The agent asks the patient for missing facts (a brain scan result, PD-L1 score, earlier treatments) before the hospital visit, and re-scores every trial live | In the demo |
| Sorting applicants takes clinicians a long time | Pairwise ranking: compare each new applicant with one already ranked; binary insertion orders a batch in a handful of comparisons, then the top few are invited in one click | In the demo |
| Patients who fail one trial are lost | Their agent moves them on to the next best fit (automatically if they've opted in, otherwise it suggests it) | In the demo |
| Patients who finish a trial drop out of research | Completed results feed into the next match | Planned |

## How we show it's faster

The clinician Overview measures only what the app can actually observe:

- median days from application to a prescreening decision
- the share of patients who pass prescreening
- patients who failed one trial and were sent on to another
- how many comparisons it took to rank each batch (against every-pair comparison)

We deliberately don't show a "days saved" figure: the demo activity is synthetic, so it can't support one honestly. A pilot with a real site, compared with its own historical timelines, would.

## How good is the matching?

The rule-based criteria parser was hand-checked against raw trial text: 85% of fields correct on a 12-trial tuning sample before fixes, **92% (58/63) on 8 held-out trials** after them. Method, fixes and known blind spots are in [docs/EVALUATION.md](docs/EVALUATION.md). A research nurse confirms every match, and the tool never tells a patient they qualify.

## Privacy: matching runs on the device

- The app downloads the trial list and the matching rules, and runs the match locally. In the demo the whole matcher runs in the browser; nothing about the patient is sent anywhere while they browse or talk to their agent.
- When a patient applies, only that trial's team sees the application, as a record ID plus the criteria evidence. The name is shared only when the patient accepts an invitation to prescreening.
- The optional LLM pass (for criteria the rule parser doesn't cover: labs, comorbidities, other drugs) now defaults to **MedGemma**, Google's open medical model, running locally through Ollama: `python run.py --llm 3 --llm-backend local`. The 4B model needs about 8–16 GB of RAM; the 27B text model needs about 32 GB or a 24 GB GPU. [4] The cloud Gemini backend is still available with `--llm-backend gemini`.

## Who it's for, and why patients take part

**Customer: trial teams** (research nurses, coordinators, principal investigators). Recruitment is where trials lose the most time, and every feature on the clinician side is aimed at it.

**Patients: people with advanced or incurable lung cancer** who are open to new treatments. For them, the reasons to take part are concrete:

- access to a treatment that isn't widely available yet, often when standard options are running out
- the trial treatment is usually provided at no cost, with extra monitoring from a specialist team
- most trials pay back travel and parking for trial visits, and some pay for extra visits or tests
- helping the next person with the same disease

The agent also shows the trade-offs before anyone applies: more visits and tests, a fresh biopsy where one is needed, and placebo arms, where the patient may not get the new treatment. Exactly what each trial covers is confirmed by its team; ClinicalTrials.gov doesn't record it.

## What's real and what's synthetic

| Real | Synthetic, and labelled so in the app |
| --- | --- |
| 205 recruiting Phase 3 NSCLC treatment trials from ClinicalTrials.gov (7 Nov 2026) | Patient names and cities |
| 30 de-identified patient records from public cBioPortal studies (TCGA LUAD, TCGA LUSC, MSKCC NSCLC 2018) | Blood-test and weight charts |
| The matcher, the parser and its evaluation | Inbox messages and application history |
| | Prescreen outcomes in `data/prescreen_outcomes_DEMO.csv` |

## Sources

1. Enrollment of patients with lung and colorectal cancers onto clinical trials (CanCORS). *J Oncol Pract* 2013. https://pubmed.ncbi.nlm.nih.gov/23814523/
2. Tufts Center for the Study of Drug Development, site enrolment performance, January 2013. https://www.outsourcing-pharma.com/Article/2013/01/16/Variations-in-site-recruitment-performance-a-risk-says-Tufts
3. Stensland KD et al. Adult cancer clinical trials that fail to complete: an epidemic? *J Natl Cancer Inst* 2014. Summary: https://www.cancernetwork.com/view/one-fifth-cancer-clinical-trials-fail-complete
4. MedGemma model cards: https://huggingface.co/google/medgemma-4b-it and https://huggingface.co/google/medgemma-27b-text-it
5. Fresh-biopsy screen-failure rates (49.1% vs 26.5%) used in the feasibility weight: Spiegel et al., *Cancer* 2017.
