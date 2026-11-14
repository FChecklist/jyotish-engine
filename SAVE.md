# SAVE.md — session save point (rewrite at end of every session)

Last saved: 2026-11-14 (IST)
One-line state: Design + first modules built; all accuracy tests at chance level; repo just created; Cloudflare connected; D1 jyotish-rules created (id c944c961-83f4-4035-882b-170072748b1f) with empty rules table; nothing deployed.

## Do next (in order)
1. Push this repo to GitHub (FChecklist/jyotish-engine, private) if not yet pushed.
2. Load 24,171 rules into D1 (table exists, empty). Bulk load cannot go through the chat connector (too large); use a private data repo + import Worker via Git deploy.
3. Wrapper around PyJHora: one function per chart type; verify against Swiss Ephemeris + published charts.
4. Normalise rules into checkable conditions (frame + house system).
5. Build modules M0-M11 per docs/SPEC.md.

## Waiting on Rajat
See docs/OPEN_QUESTIONS.md.

## Where the big files are (not in git)
Drive family folder 1KdxtA9DlH5rR2HLnF-qV60vQd8tLKjwd: books_master_v8 parts, ENGINE_SPEC, code tgz, handoffs.
