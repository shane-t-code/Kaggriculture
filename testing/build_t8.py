# BUILD T8 — early tomato block .
# Source spec: work//review12/SPECS.md (T8) + GAP_LEDGER rank 3.
#
# Design (predeclared):
#   Admission: day 11-13 hour<=1; >=1 PIZZA_SHOP/FARMERS_MARKET revealed;
#   <2 YARN_STOREs (certified sheep project keeps priority in yarn worlds);
#   quadrants exactly {NW,NE,SW}; the 8 target SE tiles LOCKED; money>=12k;
#   no tomato seeds/shed/tiles; sheep project not committed; native route
#   scan clean (no BUY_LAND / tomato from current step on). Economic gate:
#   cxtb-model revenue of our units on sale days s+9..s+12 minus $4,000
#   land, $400 seeds, fertilizer at foregone-sale value, wages for TWO
#   extra hands (fib beyond native) for 13 days, MINUS the native day-18
#   tomato project's expected option value (its cxtb revenue - its $9,000
#   bar, floored at 0) must be >= $1,000.
#   Units/day forecast: 8 tiles x (1 + fert_available/16) where fert is
#   shed stock now capped at 16 — no assumed future fertilizer.
#   Execution: BUY_LAND + BUY_SEED TOMATO 8 + 2 HIREs at the native hire
#   window (cloned from the certified _r9 request); 2 dedicated workers
#   (row y=5, row y=6): PLANT+WATER day s, WATER daily, FERTILIZE (from
#   shed pickup, 4/worker) on s+7 and s+10 before watering, HARVEST at
#   yield>=2 or from s+11, midnight auto-drop, credit-tracked SELL.
#   Engine-verified: tomato ongoing first_yield 8, interval 1, max_yield 4
#   (stock cap 4/tile), fert until day+2, weed at 2 consecutive unwatered.
#   Mechanical kill metrics: weed_deaths, unplanted tiles, unsold credit.
import hashlib
import sys
from pathlib import Path

sys.path.insert(0, r"C:\Kaggriculture")
sys.dont_write_bytecode = True
from run_local import _silence_fds
with _silence_fds():
    from kaggle_environments.agent import get_last_callable

SRC = Path(r"C:\Kaggriculture\work\\review10\candidate.py")
OUT = Path(r"C:\Kaggriculture\work\build_a\grow\variants\t8.py")

LAYER = r'''

# ==== T8: early tomato block  ====
# 8 SE tiles, days 11-13 entry, pizza/farmers-market worlds, cxtb-priced.
_T8_TILES=[(x,y) for y in (5,6) for x in range(5,9)]
_T8_ACCESS=((4,4),(5,4),(4,5),(5,5))
_T8_STATES={}
_T8_REPORT={'eligible_checks':0,'economic_declines':0,'budget_declines':0,
            'requests':0,'confirmed':0,'committed':0,'weed_deaths':0,
            'planted':0,'harvested':0,'sold':0,'errors':0,'decisions':[]}

def _t8_native_conflict(obs,native):
    step=int(obs['step'])
    for t in range(step+1,719):
        a=_IMPL.chassis.routes[2 if t>=648 else native['route']][t]
        if any(o and (o[0]=='BUY_LAND' or (o[0]=='BUY_SEED' and len(o)>1 and o[1]=='TOMATO')) for o in a.get('market',[])):return True
        if any(c and c[:2]==['PLANT','TOMATO'] for c in [a.get('farmer')]+a.get('hands',[])):return True
    return False

def _t8_revenue(obs,s,units_per_day):
    inventory=float(obs['market']['inventory']['TOMATO'])
    day=int(obs['step'])//24
    shops=float(sum(x in ('PIZZA_SHOP','FARMERS_MARKET') for x in obs['town']['unlocked_shops']))
    pending={22:0.25,24:0.25}
    last=min(29,s+12)
    theirs=_cxtb_their_supply(obs,last)
    revenue=0.0
    for d in range(day,last+1):
        shops+=pending.get(d,0.0)
        inventory-=1.0+6.0*shops-_CXTB_DRAIN_SLACK
        inventory+=theirs.get(d,0.0)
        if s+9<=d<=s+12:
            for _ in range(int(units_per_day)):
                revenue+=_r37_market_price('TOMATO',int(round(inventory)))
                inventory+=1
    return revenue

def _t8_eligible(obs,native):
    farm=obs['farms'][obs['player']];day=int(obs['step'])//24
    if not 11<=day<=13:return False
    if len(farm['tiles'])!=10 or set(farm['unlocked_quadrants'])!={'NW','NE','SW'}:return False
    if any(farm['tiles'][y][x]!='LOCKED' for x,y in _T8_TILES):return False
    shops=obs['town']['unlocked_shops']
    if shops.count('YARN_STORE')>=2:return False
    if not any(x in ('PIZZA_SHOP','FARMERS_MARKET') for x in shops):return False
    if farm['money']<12000:return False
    if obs['private']['seeds'].get('TOMATO',0) or obs['private']['shed'].get('TOMATO',0):return False
    if any(isinstance(t,dict) and t.get('crop')=='TOMATO' for row in farm['tiles'] for t in row):return False
    if _V233_STATES.get(int(obs['player']),{}).get('committed'):return False
    if _t8_native_conflict(obs,native):return False
    _T8_REPORT['eligible_checks']+=1
    fert=min(16,int(obs['private']['shed'].get('FERTILIZER',0)))
    revenue=_t8_revenue(obs,day,8.0*(1.0+fert/16.0))
    wages=0
    for d in range(day,min(30,day+13)):
        tape=_IMPL.chassis.routes[2 if d>=27 else native['route']][d*24:min((d+1)*24,719)]
        n=max((len(a.get('hands',[])) for a in tape),default=0)
        wages+=_v219_fib(n)+_v219_fib(n+1)
    fertc=fert*min(30,obs['market']['prices']['FERTILIZER'])
    try:
        debit=max(0.0,_cxtb_expected_revenue(obs)-9000.0)
    except Exception:
        debit=0.0
    net=revenue-4000-400-fertc-wages-debit
    _T8_REPORT['decisions'].append({'step':int(obs['step']),'net':round(net,2),
        'revenue':round(revenue,2),'wages':round(wages,2),'fert':fert,
        'debit':round(debit,2)})
    if net<1000:
        _T8_REPORT['economic_declines']+=1;return False
    return True

def _t8_request(obs,action,state,native):
    step=int(obs['step']);day=step//24;hour=step%24
    if state.get('requested_day')==day:return action
    committed=state.get('committed')
    if committed and day>state.get('planted_day',99)+11:return action
    if not committed and (hour>1 or not 11<=day<=13 or not _t8_eligible(obs,native)):return action
    planned=_IMPL.chassis.routes[2 if day>=27 else native['route']][day*24:min((day+1)*24,719)]
    deadline=2 if committed else 1
    if committed:
        last_native_hire=max((h for h,a in enumerate(planned) if any(o and o[0]=='HIRE' for o in a.get('market',[]))),default=0)
        if 2<last_native_hire<=6:deadline=6
    if hour>deadline:return action
    if any(o and o[0]=='HIRE' for a in planned[hour+1:] for o in a.get('market',[])):return action
    farm=obs['farms'][obs['player']];market=action.get('market',[])
    parent_hires=sum(bool(o) and o[0]=='HIRE' for o in market)
    expected=max(len(a.get('hands',[])) for a in planned)
    if len(farm['hands'])+parent_hires!=expected:return action
    initial=not committed
    extra=([['BUY_LAND'],['BUY_SEED','TOMATO',8]] if initial else [])+[['HIRE'],['HIRE']]
    if len(market)+len(extra)>MAX_ORDERS:return action
    budget=4400*initial
    budget+=sum(_v219_fib(n) for n in range(farm['hires_today'],farm['hires_today']+parent_hires+2))
    for o in market:
        if not o:continue
        if o[0]=='BUY_LAND':return action
        if o[0]=='BUY_PRODUCT':budget+=int(o[2])*(int(obs['market']['prices'][o[1]])+10)
        elif o[0]=='BUY_ANIMAL':budget+=int(o[2])*{'SHEEP':500,'COW':400,'GOOSE':300}[o[1]]
        elif o[0]=='BUY_SEED':budget+=int(o[2])*{'WHEAT':10,'CARROT':20,'TOMATO':50,'STRAWBERRY':100,'MELON':80}[o[1]]
    if farm['money']<budget+(3000 if initial else 1000):
        _T8_REPORT['budget_declines']+=1;return action
    state['requested_day']=day
    state['pending']={'first':expected+1,'initial':initial}
    result=copy.deepcopy(action);result['market']=market+extra
    _T8_REPORT['requests']+=1
    return result

def _t8_worker(obs,actor,tiles,state):
    farm=obs['farms'][obs['player']];private=obs['private'];day=int(obs['step'])//24
    pos=tuple(farm['hands'][actor-1]);inv=private['inventories'][actor]
    home=min(_T8_ACCESS,key=lambda p:(abs(pos[0]-p[0])+abs(pos[1]-p[1]),p))
    s=state['planted_day']
    fert_day=day in (s+7,s+10)
    need_fert=[t for t in tiles for tl in [farm['tiles'][t[1]][t[0]]]
               if isinstance(tl,dict) and tl.get('kind')=='PLANT'
               and tl.get('fertilized_until_day',-1)<day]
    if fert_day and need_fert and not inv.get('FERTILIZER',0) and private['shed'].get('FERTILIZER',0):
        return _v219_walk(pos,home) or ['PICKUP','FERTILIZER',min(len(need_fert),int(private['shed']['FERTILIZER']))]
    tasks=[]
    for x,y in tiles:
        tile=farm['tiles'][y][x];command=None
        if tile is None:
            if private['seeds'].get('TOMATO',0):command=['PLANT','TOMATO']
        elif isinstance(tile,dict) and tile.get('kind')=='WEED':
            pass
        elif isinstance(tile,dict) and tile.get('kind')=='PLANT' and tile.get('crop')=='TOMATO':
            if tile.get('yield_units',0)>=2 or (day>=s+11 and tile.get('yield_units',0)):command=['HARVEST']
            elif fert_day and inv.get('FERTILIZER',0) and tile.get('fertilized_until_day',-1)<day:command=['FERTILIZE']
            elif not tile.get('watered_today'):command=['WATER']
        if command:tasks.append((abs(pos[0]-x)+abs(pos[1]-y),(x,y),command))
    if tasks:
        tasks.sort(key=lambda t:(0 if t[2][0]=='HARVEST' else 1,t[0],t[1]))
        _,target,command=tasks[0]
        return _v219_walk(pos,target) or command
    return ['PASS']

def t8_agent(observation,configuration=None):
    try:
        action=_T8_PARENT_FN(observation,configuration)
        step=int(observation['step']);player=int(observation['player']);day=step//24
        state=_T8_STATES.get(player)
        if state is None or step<=state['last_step']:
            state={'last_step':step,'day':-1,'workers':{},'work':{},'credit':0}
            _T8_STATES[player]=state
            if step==0:
                _T8_REPORT.update(eligible_checks=0,economic_declines=0,
                    budget_declines=0,requests=0,confirmed=0,committed=0,
                    weed_deaths=0,planted=0,harvested=0,sold=0,errors=0,decisions=[])
        state['last_step']=step
        if configuration is not None and any(configuration.get(k,v)!=v for k,v in
            (('boardSize',10),('turnsPerDay',24),('shedCapacity',100),('maxMarketOrdersPerTurn',10))):return action
        if day<11:return action
        farm=observation['farms'][player];private=observation['private']
        native=_IMPL.chassis.players[player]
        if state['day']!=day:state['day']=day;state['workers']={};state['work']={}
        for actor,previous in state['work'].items():
            if previous['step']!=step-1 or actor>=len(private['inventories']):continue
            if previous['command'][0]=='HARVEST':
                gained=max(0,private['inventories'][actor].get('TOMATO',0)-previous['inventory'].get('TOMATO',0))
                state['credit']+=gained
                _T8_REPORT['harvested']+=gained
        pending=state.pop('pending',None)
        if pending:
            funded='SE' in farm['unlocked_quadrants'] and (not pending['initial'] or private['seeds'].get('TOMATO',0)>=8)
            if funded and len(farm['hands'])>=pending['first']+1:
                state['workers'][pending['first']]=[(x,5) for x in range(5,9)]
                state['workers'][pending['first']+1]=[(x,6) for x in range(5,9)]
                _T8_REPORT['confirmed']+=1
                if pending['initial']:
                    state['committed']=True;state['planted_day']=day
                    _T8_REPORT['committed']+=1
        action=_t8_request(observation,action,state,native)
        if not state.get('committed'):return action
        if day>state['planted_day']+12:return action
        result=copy.deepcopy(action)
        commands=[result.get('farmer') or ['PASS']]+list(result.get('hands') or [])
        commands+=[['PASS'] for _ in range(len(farm['hands'])+1-len(commands))]
        state['work']={}
        for actor,tiles in state['workers'].items():
            if actor>=len(commands):continue
            command=_t8_worker(observation,actor,tiles,state)
            commands[actor]=command
            if command[:2]==['PLANT','TOMATO']:_T8_REPORT['planted']+=1
            state['work'][actor]={'step':step,'command':command,'inventory':dict(private['inventories'][actor])}
        result['farmer'],result['hands']=commands[0],commands[1:]
        weeds=sum(1 for x,y in _T8_TILES if isinstance(farm['tiles'][y][x],dict) and farm['tiles'][y][x].get('kind')=='WEED')
        if weeds>_T8_REPORT['weed_deaths']:_T8_REPORT['weed_deaths']=weeds
        if state['credit'] and len(result['market'])<MAX_ORDERS:
            stock=projected_shed(result,FarmView(observation))
            scheduled=sum(int(o[2]) for o in result['market'] if o[:2]==['SELL','TOMATO'])
            count=min(state['credit'],max(0,stock.get('TOMATO',0)-scheduled))
            if count:
                result['market'].append(['SELL','TOMATO',count])
                state['credit']-=count
                _T8_REPORT['sold']+=count
        return result
    except Exception:
        _T8_REPORT['errors']+=1
        return _T8_PARENT_FN(observation,configuration)

_T8_PARENT_FN=r9_scaled_agent

# GROW VARIANT t8 entry (note guard: unique entry defined LAST).
def grow_variant_agent(observation,configuration=None):
    return t8_agent(observation,configuration)
agent=grow_variant_agent
kaggle_submission_agent=grow_variant_agent
'''

text = SRC.read_text(encoding="utf-8")
for needed in ("_cxtb_their_supply", "_cxtb_expected_revenue",
               "_r37_market_price", "_v219_fib", "_v219_walk",
               "projected_shed", "FarmView", "MAX_ORDERS", "_V233_STATES",
               "_CXTB_DRAIN_SLACK", "def r9_scaled_agent", "import copy"):
    assert needed in text, needed
out_text = text + LAYER
OUT.write_text(out_text, encoding="utf-8")
with _silence_fds():
    fn = get_last_callable(out_text, path=str(OUT))
assert fn.__name__ == "grow_variant_agent", fn.__name__
print("t8 OK entry=grow_variant_agent sha="
      + hashlib.sha256(OUT.read_bytes()).hexdigest()[:12])
