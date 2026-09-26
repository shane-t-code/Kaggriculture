"""Crusher decode v2: both seats same game, day-by-day capacity + phase sells."""
import json, sys
from collections import Counter, defaultdict

TPD = 24
def profile(path):
    r = json.load(open(path, encoding='utf-8'))
    info = r.get('info', {})
    names = [str(a.get('Name','?')) if isinstance(a,dict) else '?' for a in (info.get('Agents') or [{},{}])]
    if len(names) < 2: names = ['seat0','seat1']
    us = 0 if 'shane' in names[0].lower() else 1
    them = 1 - us
    steps = r['steps']
    rewards = [steps[-1][i].get('reward') for i in (0,1)]
    print(f"\n======== {path.split(chr(92))[-1]} ========")
    print(f"US={names[us]} bank {rewards[us]:,.0f}   THEM={names[them]} bank {rewards[them]:,.0f}   margin {rewards[us]-rewards[them]:+,.0f}")
    # shop sequence
    shops_prev = 0
    seq = []
    for t in range(0, len(steps), TPD):
        town = steps[t][0]['observation'].get('town', {})
        cur = town.get('unlocked_shops', [])
        if len(cur) > shops_prev:
            seq.extend(cur[shops_prev:]); shops_prev = len(cur)
    print("shops:", ' > '.join(seq))
    # daily profile at noon + phase sells (ORDER qty — inflated by dumps)
    sells = [defaultdict(Counter), defaultdict(Counter)]
    waters = [Counter(), Counter()]
    for t in range(len(steps)-1):
        day = t // TPD
        for pid in (0,1):
            act = steps[t+1][pid].get('action') or {}
            if not isinstance(act, dict): continue
            for o in (act.get('market') or []):
                if isinstance(o, list) and o and o[0]=='SELL' and len(o)>2:
                    try: sells[pid][day][o[1]] += int(o[2])
                    except: pass
            for ua in [act.get('farmer')] + list(act.get('hands') or []):
                if isinstance(ua, list) and ua and ua[0]=='WATER':
                    waters[pid][day] += 1
    print(f"{'d':>2} | {'moneyU':>7} {'moneyT':>7} | {'cropU':>5} {'cropT':>5} | {'aniU':>16} {'aniT':>16} | {'hU':>2} {'hT':>2} | {'wU':>2} {'wT':>2}")
    for day in range(0, 30, 2):
        t = day*TPD + 12
        if t >= len(steps): break
        obs = steps[t][0]['observation']
        row = []
        vals = {}
        for pid in (0,1):
            farm = obs['farms'][pid]
            crops = 0; ani = Counter()
            for rw in farm['tiles']:
                for tl in rw:
                    if isinstance(tl, dict):
                        if tl.get('kind')=='PLANT': crops += 1
                        elif tl.get('kind') in ('COOP','PASTURE') and tl.get('animal'): ani[tl['animal']] += 1
            vals[pid] = (farm.get('money',0), crops, '/'.join(f"{k[:3]}{v}" for k,v in sorted(ani.items())), len(farm.get('hands',[])))
        u, th = vals[us], vals[them]
        print(f"{day:>2} | {u[0]:>7,.0f} {th[0]:>7,.0f} | {u[1]:>5} {th[1]:>5} | {u[2]:>16} {th[2]:>16} | {u[3]:>2} {th[3]:>2} | {waters[us][day]:>2} {waters[them][day]:>2}")
    for label, pid in (('US', us), ('THEM', them)):
        tot = Counter()
        ph = {'0-9':Counter(), '10-14':Counter(), '15-29':Counter()}
        for day, c in sells[pid].items():
            key = '0-9' if day<10 else '10-14' if day<15 else '15-29'
            ph[key].update(c); tot.update(c)
        print(f"SELL-orders {label}: " + '   '.join(f"[{k}] " + ','.join(f"{i[:3]}:{n}" for i,n in sorted(p.items(), key=lambda x:-x[1])[:6]) for k,p in ph.items()))

for p in sys.argv[1:]:
    profile(p)
