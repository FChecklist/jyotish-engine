# Rule classification layer (spec, written before code) - 2026-11-16
Owner request (Rajat): AI reads every rule that does not run, classifies it in the database, checks the internet for what the rule/sentence means, writes the inference and the combinations/permutations, then the database is updated.

## What it is
- A NEW layer file per wave: jyotish-code/rules/classified_vN.jsonl. One row per rule id. Original rule rows are never edited.
- It is data for Stage 1 (evaluate techniques) and for the ledger. It does NOT make rules fire. Only atoms (atoms_ai_v*) and parsers make rules fire.
- Everything is a tradition claim. No accuracy claim comes from this layer.

## Row schema
- id: rule id (must exist in rules)
- cls: one of
  - needs_feature: chart-testable, but the engine lacks a feature. `needs` lists feature keys.
  - runnable_vocab: can be written with today's atom vocabulary (candidate for the atom converter)
  - definition: fact/definition/table (no chart test)
  - remedy_advice: remedy, do/don't, ritual
  - timing: age/period/dasha-timing statement
  - commentary: general text, no testable condition
  - duplicate_of: restates another rule (give `dup` id if known)
  - unclear: cannot tell from text
- needs: list from FEATURES (below), empty if none
- meaning: one plain sentence, what the rule says
- inference: what the tradition says follows (area, direction good/bad/mixed/neutral), one sentence
- variants: list of short strings: other forms/combinations of the same condition (e.g. other houses, signs, aspects, same in D9)
- web: {checked: true/false, urls: [..], verdict: agrees|partly|differs|not_found}
- conf: low|med|high (how sure the AI is about meaning)
Validator: tune/convert/merge_class.py (strict: enum values, id exists, no empty meaning for non-unclear, urls start with https).

## FEATURES (engine gaps; same names as the ledger kinds)
lalkitab_state, jaimini, dasha_other, divisional, tajika, dosha, upagraha, nodes_eclipse, house_strength, benefic_malefic_strength, panchang, transit, nakshatra, yoga_named, ashtakavarga, kp, prasna, muhurta, numerology, remedy_db, other

## Knowledge protocol (changed 2026-11-16, owner decision)
- Default: the AI classifies from its own training knowledge of the classical books. No web search needed.
- Web search only for a term or technique the agent does not recognise. Then put the https URLs in web.urls, checked=true.
- Row says where it came from: web.checked=false means "training knowledge only".
- Limit, stated plainly: training recall is the same model, not an independent check. It can be wrong or blend schools. So `conf` is honest (low when schools differ) and the layer stays "tradition claim". It never feeds accuracy numbers.
- No copying of page text. Paraphrase only. Allowlist refusals are skipped.

## Order of work
1. Pilot: 3 batches x 40 rules. Check quality by hand. 2. Scale in waves (max 20 agents at once). 3. Merge, ledger re-run (new column: classified count by cls). 4. Convert `runnable_vocab` rows with the atom pipeline. 5. Build engine features by `needs` counts, biggest first.
Ledger rule stays: executable count only rises when atoms/parsers run. Classified is a separate count.
