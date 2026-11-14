# Two-step contract: software report -> AI inference

## Step 1: SOFTWARE (plain code, no AI). Output = one report per chart and per question window.
Every item carries: method, technique id, steps shown (inputs, house system, reference frame), rule source(s), and a number.
- events[]: {area, event, window_start, window_end, score, probability, calibration, techniques_fired[], techniques_against[], sources_agree, sources_conflict}
- timing[]: dasha/antardasha/transit/ashtakavarga/KP windows with their date uncertainty (+-3 to +-5 days today)
- dos[], donts[], precautions[], remedies[]: each with rule id, source book, label "tradition claim", and cross-source agreement count
- chart facts: D1-D60, panchang, KP lords, ashtakavarga, transits, with settings used (ayanamsa, node, house system)
- quality block: birth-time grade and sensitivity (which divisional charts flip if time is off by N minutes)
`probability` is only a calibrated number: the fraction of past cases with the same fired pattern where the event happened, with sample size and interval. If a technique has no validation record, probability is null and calibration = "none". Today every validated skill test is at chance, so calibrated probabilities equal base rates; the report must say so.

## Step 2: AI INFERENCE (reads only the Step 1 report)
- Acts like an astrologer: weighs conflicting techniques, explains why, gives the window, likely outcome, do's, don'ts, precautions, in simple words.
- Must cite the technique ids and numbers it relies on. Must not add predictions that are not in the report. Must not raise confidence above the report's numbers.
- Must say plainly when the report has no validated signal. No death dates, medical diagnoses, or investment advice.
- Remedies and do/don't are shown as tradition claims, never as proven effects.

## Why two steps
Software is repeatable and testable. AI inference is where judgment and wording live. Accuracy is measured on Step 1 outputs against real events; Step 2 is checked for faithfulness to the report.
