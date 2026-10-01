# BUILD SP — strawberry sale pacing .
# Source: AUTOPSY price gap (we realize $98/berry d16-23 on 165 units;
# leaders realize $145-172 on similar volume) + .md thesis #2 +
# GAP_LEDGER rank 1. Market-orders-only change: town draw stays a control.
#
# PREDECLARED policy (before any game):
#   V2 (declared after v1's fixture KILL — v1 stranded
#   trimmed units: native credit treats them as sold, so blocked releases
#   rot in the shed; 11/12 cells negative, worst -12,285):
#   Scope: STRAWBERRY, days 14-29. Daily cap = engine drain (1+6*inst);
#   day 27 = 2*drain, day 28 = 10*drain; NO hourly spreading (native's
#   in-day timing preserved whenever it is under cap). From step 690 the
#   layer LIQUIDATES: all shed berries beyond scheduled are sold, cap
#   ignored — nothing may strand. Shed pressure (projected >= 85 items)
#   also lifts the cap instead of freezing the layer. Money guard < $6,000
#   unchanged. Errors fall back to the unmodified parent action.
#   Telemetry: throttled/released/held_max/errors in _SP_REPORT.
#   Fixture gate before ANY panel game: mean paired >= 0 AND zero losing
#   flips on the 3 fixture seeds, else KILL the lane for tonight.
# Gates for the screen (same as all grower variants, declared in
# screen.py header): KEEP iff mean paired > 0, zero losing flips,
# majkel stratum >= -250 with scoreD >= 0. Full battery before any
# submission talk; Shane submits.
import hashlib
import sys
from pathlib import Path

sys.path.insert(0, r"C:\Kaggriculture")
sys.dont_write_bytecode = True
from run_local import _silence_fds
with _silence_fds():
    from kaggle_environments.agent import get_last_callable

SRC = Path(r"C:\Kaggriculture\work\\review10\candidate.py")
OUT = Path(r"C:\Kaggriculture\work\build_a\grow\variants\sp.py")

LAYER = r'''

# ==== SP: strawberry sale pacing  ====
_SP_PRODUCT='STRAWBERRY'
_SP_SHOPS=('BRUNCH_SPOT','ICE_CREAM_SHOP','SMOOTHIE_SHOP','FARMERS_MARKET')
_SP_STATES={}
_SP_REPORT={'throttled':0,'released':0,'held_max':0,'active_days':0,'errors':0}

def sp_agent(observation,configuration=None):
    try:
        action=_SP_PARENT_FN(observation,configuration)
        step=int(observation['step']);player=int(observation['player']);day=step//24;hour=step%24
        st=_SP_STATES.get(player)
        if st is None or step<=st['last_step']:
            st={'last_step':step,'day':-1,'sold':0}
            _SP_STATES[player]=st
            if step==0:_SP_REPORT.update(throttled=0,released=0,held_max=0,active_days=0,errors=0)
        st['last_step']=step
        if configuration is not None and any(configuration.get(k,v)!=v for k,v in
            (('boardSize',10),('turnsPerDay',24),('shedCapacity',100),('maxMarketOrdersPerTurn',10))):return action
        if not 14<=day<=29:return action
        farm=observation['farms'][player]
        shops=observation['town']['unlocked_shops']
        nshop=sum(shops.count(s) for s in _SP_SHOPS)
        if nshop<2:return action
        if farm['money']<6000:return action
        if st['day']!=day:
            st['day']=day;st['sold']=0;_SP_REPORT['active_days']+=1
        drain=1+6*nshop
        cap=drain if day<27 else (2*drain if day==27 else 10*drain)
        stock=projected_shed(action,FarmView(observation))
        if step>=690 or sum(stock.values())>=85:
            cap=99999
        allowed=max(0,cap-st['sold'])
        market=list(action.get('market',[]))
        out=[];scheduled=0;changed=False;remaining=allowed
        for o in market:
            if o and o[:2]==['SELL',_SP_PRODUCT]:
                q=int(o[2]);take=min(q,remaining)
                if take<q:
                    changed=True;_SP_REPORT['throttled']+=q-take
                if take>0:
                    out.append(['SELL',_SP_PRODUCT,take]);scheduled+=take;remaining-=take
            else:out.append(o)
        avail=int(stock.get(_SP_PRODUCT,0))
        extra=min(remaining,max(0,avail-scheduled))
        if extra>0 and len(out)<MAX_ORDERS:
            out.append(['SELL',_SP_PRODUCT,extra]);scheduled+=extra
            _SP_REPORT['released']+=extra;changed=True
        st['sold']+=scheduled
        _SP_REPORT['held_max']=max(_SP_REPORT['held_max'],max(0,avail-scheduled))
        if not changed:return action
        result=copy.deepcopy(action);result['market']=out
        return result
    except Exception:
        _SP_REPORT['errors']+=1
        return _SP_PARENT_FN(observation,configuration)

_SP_PARENT_FN=r9_scaled_agent

# GROW VARIANT sp entry (note guard: unique entry defined LAST).
def grow_variant_agent(observation,configuration=None):
    return sp_agent(observation,configuration)
agent=grow_variant_agent
kaggle_submission_agent=grow_variant_agent
'''

text = SRC.read_text(encoding="utf-8")
for needed in ("projected_shed", "FarmView", "MAX_ORDERS",
               "def r9_scaled_agent", "import copy"):
    assert needed in text, needed
out_text = text + LAYER
OUT.write_text(out_text, encoding="utf-8")
with _silence_fds():
    fn = get_last_callable(out_text, path=str(OUT))
assert fn.__name__ == "grow_variant_agent", fn.__name__
print("sp OK entry=grow_variant_agent sha="
      + hashlib.sha256(OUT.read_bytes()).hexdigest()[:12])
