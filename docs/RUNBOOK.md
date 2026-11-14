# Runbook
- Tests: python3 -I tests/test_houses.py (expects exit 0).
- PyJHora venv (not in git): python3 -m venv ref/venv; ref/venv/bin/pip install PyJHora numpy pandas pytz geocoder timezonefinder geopy pyswisseph
- pip needs --break-system-packages on the cloud box.
- Backtest: tune/fit.py, tune/people_loader.py (people data not in git; in Drive tgz).
- Rules DB: join Drive books_master_v8 part1..6 in order into books_master_v8.jsonl.
- Drive limit ~4.2 MB per call; split big files.
- Deploy: Cloudflare Git integration from this repo (set up once by Rajat on phone).
