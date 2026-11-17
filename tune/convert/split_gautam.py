"""Split one transcript into batch input files. Usage: split_gautam.py SRC.txt OUTDIR NN [maxchars]
Each batch holds whole [timestamp] chunks, about maxchars characters."""
import sys, re, os
src, out, nn = sys.argv[1], sys.argv[2], sys.argv[3]
mx = int(sys.argv[4]) if len(sys.argv) > 4 else 17000
t = open(src, encoding='utf8').read().replace('\\[', '[').replace('\\]', ']')
head = t.split('\n')[0]
chunks = re.findall(r'^\[\d+:\d+(?::\d+)?\].*?(?=^\[\d+:\d+(?::\d+)?\]|\Z)', t, re.M | re.S)
os.makedirs(out, exist_ok=True)
batches, cur, n = [], [], 0
for c in chunks:
    if n + len(c) > mx and cur: batches.append(cur); cur, n = [], 0
    cur.append(c.strip()); n += len(c)
if cur: batches.append(cur)
for i, b in enumerate(batches, 1):
    open(f'{out}/b{i:02d}.in.txt', 'w', encoding='utf8').write('\n'.join(b) + '\n')
print(nn, head[:80], 'chunks', len(chunks), 'batches', len(batches))
