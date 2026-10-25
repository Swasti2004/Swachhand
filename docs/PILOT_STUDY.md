# Pilot Study Protocol & Volunteer User Study Plan (Milestone M6)

*Companion protocol for the academic evaluation of the Swachhand recommendation system.*

---

## 1. Objectives & Research Questions
- **RQ1 (Feasibility)**: Do time-budgeted, fatigue-aware outdoor suggestions lower decision friction for taking short work breaks?
- **RQ2 (Safety & Burnout)**: Does down-weighting strenuous activities when users report prior physical load prevent over-exertion?
- **RQ3 (User Agency & Privacy)**: Does coarse local coordinate rounding (~110 m) satisfy user privacy comfort compared to centralized GPS tracking?

---

## 2. Participant Recruitment & Ethics
- **Cohort**: 15–20 volunteer developers, students, and remote desk workers.
- **Duration**: 7 to 14 days of free-living use.
- **Informed Consent**:
  - Voluntary participation with right to withdraw at any time.
  - No health or clinical diagnosis claims. Explicit disclaimer: *"Swachhand offers lifestyle outdoor suggestions; it is not a medical or mental health intervention."*
  - Immediate local data deletion via in-app "Delete all my data" endpoint (`DELETE /api/history`).

---

## 3. Data Collection (Privacy-Preserving)
- **Local Metrics Stored**:
  - Outing choice (`accepted`, `skipped`, `done`).
  - Stated energy level and duration budget.
  - Coarsened location (~110 m) used only for immediate lookups, never logged to persistent remote telemetry.
- **Anonymized Telemetry Export**:
  - At the end of the pilot, volunteers can optionally export an anonymized summary of acceptance rates and session timestamps for thesis figures.

---

## 4. Post-Pilot Survey Instrument (5-Point Likert Scale)

1. **Decision Friction**: *"The app reduced the mental effort required to decide where to take a break."* (1: Strongly Disagree - 5: Strongly Agree)
2. **Fatigue Appropriateness**: *"When I had low energy or felt tired from earlier activity, the recommendations were gentle enough."*
3. **Time Accuracy**: *"The suggested walk and stay times matched reality."*
4. **Offline Card Utility**: *"The ability to save an outing card that worked without a mobile signal was useful."*
5. **Privacy Comfort**: *"Knowing my exact coordinates and prompts remained on my device made me comfortable using the app."*

---

## 5. Exit Criteria & Analysis Plan
- Calculate mean System Usability Scale (SUS) equivalent and Likert satisfaction scores.
- Compare actual acceptance rates between rested vs. high-load sessions to validate fatigue scaling.
