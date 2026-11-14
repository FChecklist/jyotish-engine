# SAVE.md — session save point (rewrite at end of every session)

Last saved: 2026-11-14 (IST)
One-line state: Design + first modules built; all accuracy tests at chance level; repo just created; Cloudflare connected; D1 jyotish-rules created (id c944c961-83f4-4035-882b-170072748b1f) with empty rules table; nothing deployed.

## Do next (in order)
1. DONE: repo pushed (public) FChecklist/jyotish-engine. Rules are in public repo FChecklist/jyotish-code (rules/ parts 01-06, no quote_short), by Rajat's decision. D1 table exists and is still empty.
2. Load 24,171 rules into D1 (table exists, empty). Bulk load cannot go through the chat connector (too large); use a private data repo + import Worker via Git deploy.
3. DONE: core/charts.py (D1-D60 signs), core/dasha.py (Vimshottari maha +-3d, antar +-5d, order and durations exact). Next: nodes, KP, panchang, transit, ashtakavarga, other dasha systems (Narayana first) + verification.
4. Normalise rules into checkable conditions (frame + house system).
5. Build modules M0-M11 per docs/SPEC.md.

## Waiting on Rajat
See docs/OPEN_QUESTIONS.md.

## Where the big files are (not in git)
Drive family folder 1KdxtA9DlH5rR2HLnF-qV60vQd8tLKjwd: books_master_v8 parts, ENGINE_SPEC, code tgz, handoffs.
