"""Pinned midnq diagnostic: OUR agent (seat 0) vs the midnq tape (seat 1),
original seed + pinned shop world of ep 112897649.  Reports final banks and
our per-day carrot pipeline (plants, standing tiles, sell orders, price).

Usage: python pinned_midnq.py <agent.py> [label]
"""
import json, os, sys
from collections import Counter

ROOT = r'c:\Kaggriculture'
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'tools'))
os.chdir(ROOT)

SEED = 1574411233
TAPE = r'versions\pool_midnq_112897649.py'

# the real game's shop sequence, read from the replay
rep = json.load(open(r'replays\crushers\episode-112897649-replay.json', encoding='utf-8'))
seq, prev = [], 0
for t in range(0, len(rep['steps']), 24):
    cur = rep['steps'][t][0]['observation']['town']['unlocked_shops']
    if len(cur) > prev:
        seq += cur[prev:]; prev = len(cur)
print('pinned shops:', ' > '.join(seq))

from run_local import _silence_fds
import shop_pin
shop_pin.install(seq)

from kaggle_environments import make
agent = sys.argv[1]
label = sys.argv[2] if len(sys.argv) > 2 else os.path.basename(agent)
with _silence_fds():
    env = make('kaggriculture', configuration={'episodeSteps': 720, 'seed': SEED})
    env.run([agent, TAPE])
final = env.steps[-1]
print(f'{label}: bank {final[0].reward:,.0f} vs midnq-tape {final[1].reward:,.0f}  '
      f'margin {final[0].reward - final[1].reward:+,.0f}  statuses {[s.status for s in final]}')
print('(real game: v120 57,980 vs midnq 75,963 = -17,983)')

TPD = 24
print(f"{'d':>2} | {'cPrice':>6} | {'cTiles':>6} {'cPlant':>6} | {'cSellOrd':>8} | {'strSell':>7} {'wheSell':>7}")
for day in range(6, 30):
    t0 = day * TPD
    if t0 + 12 >= len(env.steps): break
    obs = env.steps[t0 + 12][0]['observation']
    farm = obs['farms'][0]
    ctil = sum(1 for row in farm['tiles'] for tl in row
               if isinstance(tl, dict) and tl.get('kind') == 'PLANT' and tl.get('crop') == 'CARROT')
    pl = Counter(); sell = Counter()
    for t in range(t0, min(t0 + TPD, len(env.steps) - 1)):
        act = env.steps[t + 1][0].get('action') or {}
        if not isinstance(act, dict): continue
        for ua in [act.get('farmer')] + list(act.get('hands') or []):
            if isinstance(ua, list) and ua and ua[0] == 'PLANT' and len(ua) > 1:
                pl[ua[1]] += 1
        for o in (act.get('market') or []):
            if isinstance(o, list) and len(o) > 2 and o[0] == 'SELL':
                try: sell[o[1]] += int(o[2])
                except: pass
    price = obs['market']['prices'].get('CARROT', 0)
    print(f"{day:>2} | {price:>6.0f} | {ctil:>6} {pl.get('CARROT',0):>6} | {sell.get('CARROT',0):>8} | "
          f"{sell.get('STRAWBERRY',0):>7} {sell.get('WHEAT',0):>7}")
tot_pl = Counter()
for t in range(len(env.steps) - 1):
    act = env.steps[t + 1][0].get('action') or {}
    if isinstance(act, dict):
        for ua in [act.get('farmer')] + list(act.get('hands') or []):
            if isinstance(ua, list) and ua and ua[0] == 'PLANT' and len(ua) > 1:
                tot_pl[ua[1]] += 1
print('our total PLANTs by crop:', dict(tot_pl), '(midnq real: CARROT 176)')
