"""Run the normaliser over the whole rules file and print coverage per system. Usage: python rules/normalise_all.py path/to/books_master_v8.jsonl"""
import sys, os, json, collections
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'core'))
import rules_norm as N
rows = [json.loads(l) for l in open(sys.argv[1])]
cov = collections.defaultdict(collections.Counter)
for r in rows:
    cov[r['system']][N.parse(r['input'], r['system'])['status']] += 1
tot = collections.Counter()
for s, c in sorted(cov.items(), key=lambda kv: -sum(kv[1].values())):
    n = sum(c.values()); tot.update(c)
    print(f"{s:14s} n={n:6d} parsed={c['parsed']:5d} ({100*c['parsed']/n:4.1f}%) partial={c['partial']:5d} unparsed={c['unparsed']:5d}")
n = sum(tot.values()); print(f"ALL n={n} parsed={tot['parsed']} ({100*tot['parsed']/n:.1f}%) partial={tot['partial']} unparsed={tot['unparsed']}")
