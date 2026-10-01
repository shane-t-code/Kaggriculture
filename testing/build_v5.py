# BUILD TAKEOVER V5 — blueprint patches on the LIVE _ta engine .
# Live-engine deltas from the AUTOPSY blueprint:
#   P1 berries 18->22 and window d12->d14 (leaders 20-36 by d15).
#   P2 land proactive from day 8 when funded (leaders 2nd d8.2-9.2, 3rd d10.5).
#   P3 COWS to 6 by day 10 (leaders' milk $19-25k/season; b2 buys zero cows).
#   P4 builder generalized to place SHEEP or COW (pickup/place/carry).
# Bar unchanged: fixture 114225946 bank vs b2's 45,528 (progress) and route-9
# par 72,401 (deploy bar); zero escapes; honest report either way.
import hashlib
import sys
from pathlib import Path

sys.path.insert(0, r"C:\Kaggriculture")
sys.dont_write_bytecode = True
from run_local import _silence_fds
with _silence_fds():
    from kaggle_environments.agent import get_last_callable

SRC = Path(r"C:\Kaggriculture\work\\review10\takeover_b2_forced.py")
OUT = Path(r"C:\Kaggriculture\work\\review10\takeover_v5_forced.py")

text = SRC.read_text(encoding="utf-8")
SUBS = [
    ("    want_b=(4 if day<7 else 18) if day<=12 else 0",
     "    want_b=(6 if day<7 else 22) if day<=14 else 0", 1),
    ("        if len(farm['unlocked_quadrants'])<4 and len(empties)<3 and day<=15 and cash>=landcost+200:order(['BUY_LAND'],landcost)",
     "        if len(farm['unlocked_quadrants'])<4 and day<=15 and cash>=landcost+200 and (len(empties)<3 or (day>=8 and cash>=landcost+2500)):order(['BUY_LAND'],landcost)", 1),
    ("        if day<=12 and sheep+stockanimals<15 and stockanimals<6 and len(empties)+len(pastures)>stockanimals and cash>=500:\n"
     "            order(['BUY_ANIMAL','SHEEP',1],500)",
     "        if day<=12 and sheep+stockanimals<15 and stockanimals<6 and len(empties)+len(pastures)>stockanimals and cash>=500:\n"
     "            order(['BUY_ANIMAL','SHEEP',1],500)\n"
     "        if day<=10 and sum(t['animal']=='COW' for _,t in animals)<6 and stockanimals<6 and len(empties)+len(pastures)>stockanimals and cash>=900:\n"
     "            order(['BUY_ANIMAL','COW',1],400)", 1),
    ("        if cmd is None and i==builder and inv.get('SHEEP',0):",
     "        if cmd is None and i==builder and (inv.get('SHEEP',0) or inv.get('COW',0)):", 1),
    ("                c=['PLACE','SHEEP'] if xy in pastures else ['BUILD_PASTURE'] if t is None else ['DIG']",
     "                spec='SHEEP' if inv.get('SHEEP',0) else 'COW'\n"
     "                c=['PLACE',spec] if xy in pastures else ['BUILD_PASTURE'] if t is None else ['DIG']", 1),
    ("        if cmd is None and i==builder and build and not inv.get('SHEEP',0) and shed.get('SHEEP',0)>0:\n"
     "            q=min(len(build),shed['SHEEP']);cmd=_v219_walk(p,home) or ['PICKUP','SHEEP',q]\n"
     "            if cmd[0]=='PICKUP':shed['SHEEP']-=q",
     "        if cmd is None and i==builder and build and not (inv.get('SHEEP',0) or inv.get('COW',0)) and (shed.get('SHEEP',0)>0 or shed.get('COW',0)>0):\n"
     "            spec='SHEEP' if shed.get('SHEEP',0)>0 else 'COW'\n"
     "            q=min(len(build),shed[spec]);cmd=_v219_walk(p,home) or ['PICKUP',spec,q]\n"
     "            if cmd[0]=='PICKUP':shed[spec]-=q", 1),
]
for old, new, count in SUBS:
    found = text.count(old)
    assert found == count, (found, count, old[:70])
    text = text.replace(old, new)

OUT.write_text(text, encoding="utf-8")
with _silence_fds():
    fn = get_last_callable(text, path=str(OUT))
assert fn.__name__ == "takeover_a_entry", fn.__name__
print("takeover_v5_forced OK sha="
      + hashlib.sha256(OUT.read_bytes()).hexdigest()[:12])
