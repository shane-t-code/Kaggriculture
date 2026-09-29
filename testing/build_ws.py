# BUILD WS — work-stealing dispatcher patch .
# MEASURED diagnosis (action_budget.py on the b2 fixture trace):
#   leader-tape PROD 47.9% / MOVE 42.7% / PASS 3.9%
#   b2         PROD 30.1% / MOVE 39.0% / PASS 23.4%  (1,556 idle turns;
#   productive deficit 1,286 ~= idle surplus). NOT a walking problem —
#   an ownership-starvation problem: units only serve owned tiles, idle
#   when their list runs dry while other owners' tiles queue up.
# FIX: before PASS, an idle unit steals the nearest unclaimed pending job
# (feed if carrying wheat / unwatered water / ripe ongoing harvest / care /
# fert-collect / unplanted intent with seeds), any hour, any role.
# Collision with the tile's owner this turn is possible (second action
# no-ops) — accepted v1 cost, measured by the same budget tool after.
# Bar: fixture bank vs b2's 45,528; then PROD/PASS shares re-measured.
import hashlib
import sys
from pathlib import Path

sys.path.insert(0, r"C:\Kaggriculture")
sys.dont_write_bytecode = True
from run_local import _silence_fds
with _silence_fds():
    from kaggle_environments.agent import get_last_callable

SRC = Path(r"C:\Kaggriculture\work\\review10\takeover_b2_forced.py")
OUT = Path(r"C:\Kaggriculture\work\\review10\takeover_ws_forced.py")

OLD = "        if cmd is None and cargo and day==29:cmd=_v219_walk(p,home) or ['DROP']"
NEW = """        if cmd is None and day<29:
            steal=[]
            for xy,t in live.items():
                if xy in claimed:continue
                if t.get('animal'):
                    if not t['fed_today'] and inv.get('WHEAT',0):steal.append((0,xy,['FEED']))
                    elif t['yield_units']:steal.append((1,xy,['HARVEST']))
                    elif day<28 and not t['cared_today']:steal.append((2,xy,['CARE']))
                    elif t.get('fertilizer_available'):steal.append((3,xy,['COLLECT_FERTILIZER']))
                elif t.get('crop'):
                    if not t['watered_today']:steal.append((0,xy,['WATER']))
                    elif t['yield_units'] and t['crop'] in ('STRAWBERRY','TOMATO'):steal.append((1,xy,['HARVEST']))
            for xy,item in intents.items():
                if xy in claimed or item=='SHEEP':continue
                t2=tiles[xy[1]][xy[0]]
                if t2 is None and seeds.get(item,0)>0 and hour<=20:steal.append((1,xy,['PLANT',item]))
            if steal:
                _,xy,c=min(steal,key=lambda z:(z[0],_ta_dist(p,z[1]),z[1]))
                claimed.add(xy);cmd=_v219_walk(p,xy) or c
                if cmd[0]=='PLANT':seeds[cmd[1]]-=1
                _TA_REPORT['steals']=_TA_REPORT.get('steals',0)+1
        if cmd is None and cargo and day==29:cmd=_v219_walk(p,home) or ['DROP']"""

text = SRC.read_text(encoding="utf-8")
n = text.count(OLD)
assert n == 1, n
text = text.replace(OLD, NEW)
OUT.write_text(text, encoding="utf-8")
with _silence_fds():
    fn = get_last_callable(text, path=str(OUT))
assert fn.__name__ == "takeover_a_entry", fn.__name__
print("takeover_ws_forced OK sha="
      + hashlib.sha256(OUT.read_bytes()).hexdigest()[:12])
