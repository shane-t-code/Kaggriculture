# BUILD BD2 — SE bundle, corrected combination .
# the gear critique validated: BD1's $8,938 wage line was self-inflicted
# (a 3rd hand from day 17 at fib 144-377/day) and fertilizer was treated as
# scarce when the market SELLS it back (~$40 -> +1 tomato worth $70-150).
# BD2 configuration:
#   Crew: TWO hands the whole way (never the cliff 3rd) -> wages ~fib(n)+
#   fib(n+1)/day, ~2k total.
#   EARLY-TOM 4 tiles (5..8,5) day s (11-13); LATE-TOM 8 tiles day 17;
#   WHEAT 6 tiles (5..7,7..8) staggered rotations (18 tiles total, sized
#   for 2 workers even in the d17-23 overlap: w1=early4+lateA4,
#   w2=wheat6+lateB4).
#   FERTILIZER IS BOUGHT (BUY_PRODUCT FERTILIZER 8) on days s+6, s+9,
#   23, 26 (arrives end of turn; picked up next morning), 24 units total,
#   cost in the forecast at price+10.
#   Sticky approval (exact4 pattern): the economic gate is evaluated at
#   hour 0-1; a pass is cached for the day so the hire-alignment hour
#   cannot re-litigate it after the native's morning fertilizer sale.
# PREDECLARED admission: same structural gates as BD1 (day 11-13, >=1
# PIZZA/FM, <2 YARN, quadrants {NW,NE,SW}, 18 tiles LOCKED, money>=12000,
# no tomato holdings, sheep project not committed, native scan clean).
# Economics: rev_early(4 tiles, fert-bought) + rev_late(8, fert-bought) +
# rev_wheat(72 @ min(40,price)) >= 4000 land + 780 seeds + 24*(fert_price
# +10) + wages(2 hands, s..28) + native-option debit + 1000.
# Fixture gate: zero errors, zero weed deaths; if it fires: paired > 0
# there; if it declines everywhere: paired == 0 everywhere. Then panel.
import hashlib
import sys
from pathlib import Path

sys.path.insert(0, r"C:\Kaggriculture")
sys.dont_write_bytecode = True
from run_local import _silence_fds
with _silence_fds():
    from kaggle_environments.agent import get_last_callable

SRC = Path(r"C:\Kaggriculture\work\\review10\candidate.py")
OUT = Path(r"C:\Kaggriculture\work\build_a\grow\variants\bd2.py")

LAYER = r'''

# ==== BD2: SE bundle, 2-hand crew, bought fertilizer  ====
_BD_EARLY=[(x,5) for x in range(5,9)]
_BD_LATE=[(9,5),(9,6),(8,6),(5,6),(6,6),(7,6),(8,7),(9,7)]
_BD_WHEAT=[(x,y) for y in (7,8) for x in range(5,8)]
_BD_ALL=_BD_EARLY+_BD_LATE+_BD_WHEAT
_BD_ACCESS=((4,4),(5,4),(4,5),(5,5))
_BD_LATE_DAY=17
_BD_STATES={}
_BD_REPORT={'eligible_checks':0,'economic_declines':0,'budget_declines':0,
            'requests':0,'confirmed':0,'committed':0,'weed_deaths':0,
            'planted_tom':0,'planted_wheat':0,'harvested_tom':0,
            'harvested_wheat':0,'sold_tom':0,'sold_wheat':0,'fert_bought':0,
            'errors':0,'decisions':[]}

def _bd_native_conflict(obs,native):
    step=int(obs['step'])
    for t in range(step+1,719):
        a=_IMPL.chassis.routes[2 if t>=648 else native['route']][t]
        if any(o and (o[0]=='BUY_LAND' or (o[0]=='BUY_SEED' and len(o)>1 and o[1]=='TOMATO')) for o in a.get('market',[])):return True
        if any(c and c[:2]==['PLANT','TOMATO'] for c in [a.get('farmer')]+a.get('hands',[])):return True
    return False

def _bd_native_plants_wheat(obs,native):
    step=int(obs['step'])
    a=_IMPL.chassis.routes[2 if step>=648 else native['route']][step]
    return any(c and c[:2]==['PLANT','WHEAT'] for c in [a.get('farmer')]+a.get('hands',[]))

def _bd_tom_revenue(obs,s,units_per_day):
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

def _bd_eligible(obs,native):
    farm=obs['farms'][obs['player']];day=int(obs['step'])//24
    if not 11<=day<=13:return False
    if len(farm['tiles'])!=10 or set(farm['unlocked_quadrants'])!={'NW','NE','SW'}:return False
    if any(farm['tiles'][y][x]!='LOCKED' for x,y in _BD_ALL):return False
    shops=obs['town']['unlocked_shops']
    if shops.count('YARN_STORE')>=2:return False
    if not any(x in ('PIZZA_SHOP','FARMERS_MARKET') for x in shops):return False
    if farm['money']<12000:return False
    if obs['private']['seeds'].get('TOMATO',0) or obs['private']['shed'].get('TOMATO',0):return False
    if any(isinstance(t,dict) and t.get('crop')=='TOMATO' for row in farm['tiles'] for t in row):return False
    if _V233_STATES.get(int(obs['player']),{}).get('committed'):return False
    if _bd_native_conflict(obs,native):return False
    _BD_REPORT['eligible_checks']+=1
    rev_early=_bd_tom_revenue(obs,day,8.0)
    rev_late=_bd_tom_revenue(obs,_BD_LATE_DAY,16.0)
    rev_wheat=72.0*min(40,int(obs['market']['prices']['WHEAT']))
    wages=0
    for d in range(day,29):
        tape=_IMPL.chassis.routes[2 if d>=27 else native['route']][d*24:min((d+1)*24,719)]
        n=max((len(a.get('hands',[])) for a in tape),default=0)
        wages+=_v219_fib(n)+_v219_fib(n+1)
    fertc=24*(min(60,int(obs['market']['prices']['FERTILIZER']))+10)
    try:
        debit=max(0.0,_cxtb_expected_revenue(obs)-9000.0)
    except Exception:
        debit=0.0
    net=rev_early+rev_late+rev_wheat-4000-780-fertc-wages-debit
    _BD_REPORT['decisions'].append({'step':int(obs['step']),'net':round(net,2),
        'rev_early':round(rev_early,2),'rev_late':round(rev_late,2),
        'rev_wheat':round(rev_wheat,2),'wages':round(wages,2),
        'fertc':fertc,'debit':round(debit,2)})
    if net<1000:
        _BD_REPORT['economic_declines']+=1;return False
    return True

def _bd_request(obs,action,state,native):
    step=int(obs['step']);day=step//24;hour=step%24
    if state.get('requested_day')==day:return action
    committed=state.get('committed')
    if committed and day>28:return action
    if not committed:
        if not 11<=day<=13:return action
        if state.get('approved_day')!=day:
            if hour>1:return action
            if not _bd_eligible(obs,native):return action
            state['approved_day']=day
    planned=_IMPL.chassis.routes[2 if day>=27 else native['route']][day*24:min((day+1)*24,719)]
    deadline=2 if committed else 6
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
    s=state.get('planted_day',12)
    extra=([['BUY_LAND'],['BUY_SEED','TOMATO',4],['BUY_SEED','WHEAT',18]] if initial else [])
    if not initial and day==_BD_LATE_DAY-1:
        extra=extra+[['BUY_SEED','TOMATO',8]]
    if not initial and day in (s+6,s+9,_BD_LATE_DAY+6,_BD_LATE_DAY+9):
        extra=extra+[['BUY_PRODUCT','FERTILIZER',8]]
    extra=extra+[['HIRE'],['HIRE']]
    if len(market)+len(extra)>MAX_ORDERS:return action
    budget=(4000+200+180)*initial
    for o in extra:
        if o[0]=='BUY_SEED' and not initial:budget+=int(o[2])*50
        elif o[0]=='BUY_PRODUCT':budget+=int(o[2])*(int(obs['market']['prices'][o[1]])+10)
    budget+=sum(_v219_fib(n) for n in range(farm['hires_today'],farm['hires_today']+parent_hires+2))
    for o in market:
        if not o:continue
        if o[0]=='BUY_LAND':return action
        if o[0]=='BUY_PRODUCT':budget+=int(o[2])*(int(obs['market']['prices'][o[1]])+10)
        elif o[0]=='BUY_ANIMAL':budget+=int(o[2])*{'SHEEP':500,'COW':400,'GOOSE':300}[o[1]]
        elif o[0]=='BUY_SEED':budget+=int(o[2])*{'WHEAT':10,'CARROT':20,'TOMATO':50,'STRAWBERRY':100,'MELON':80}[o[1]]
    if farm['money']<budget+(3000 if initial else 1000):
        _BD_REPORT['budget_declines']+=1;return action
    state['requested_day']=day
    state['pending']={'first':expected+1,'initial':initial}
    result=copy.deepcopy(action);result['market']=market+extra
    _BD_REPORT['requests']+=1
    return result

def _bd_worker(obs,actor,tiles,state,native):
    farm=obs['farms'][obs['player']];private=obs['private'];step=int(obs['step']);day=step//24
    pos=tuple(farm['hands'][actor-1]);inv=private['inventories'][actor]
    home=min(_BD_ACCESS,key=lambda p:(abs(pos[0]-p[0])+abs(pos[1]-p[1]),p))
    s=state['planted_day']
    fert_days={s+7,s+10,_BD_LATE_DAY+7,_BD_LATE_DAY+10}
    need_fert=[t for t in tiles for tl in [farm['tiles'][t[1]][t[0]]]
               if isinstance(tl,dict) and tl.get('kind')=='PLANT'
               and tl.get('crop')=='TOMATO' and tl.get('fertilized_until_day',-1)<day]
    if day in fert_days and need_fert and not inv.get('FERTILIZER',0) and private['shed'].get('FERTILIZER',0):
        return _v219_walk(pos,home) or ['PICKUP','FERTILIZER',min(len(need_fert),int(private['shed']['FERTILIZER']))]
    wheat_ok=not _bd_native_plants_wheat(obs,native) and private['seeds'].get('WHEAT',0)>=7
    tasks=[]
    for x,y in tiles:
        tile=farm['tiles'][y][x];command=None;rank=1
        early=(x,y) in _BD_EARLY;late=(x,y) in _BD_LATE;wheat=(x,y) in _BD_WHEAT
        if tile is None:
            if early and day>=s and private['seeds'].get('TOMATO',0):command=['PLANT','TOMATO'];rank=2
            elif late and day>=_BD_LATE_DAY and private['seeds'].get('TOMATO',0):command=['PLANT','TOMATO'];rank=2
            elif wheat and wheat_ok and day>=s+1+((x,y) in _BD_WHEAT[3:]) and day<=24:command=['PLANT','WHEAT'];rank=2
        elif isinstance(tile,dict) and tile.get('kind')=='PLANT':
            crop=tile.get('crop');age=day-int(tile.get('planted_day',day))
            if crop=='WHEAT':
                if tile.get('yield_units',0) and (age>=5 or (age>=4 and tile.get('watered_today'))):command=['HARVEST'];rank=0
                elif not tile.get('watered_today') and age<=4:command=['WATER'];rank=1
            elif crop=='TOMATO':
                born=int(tile.get('planted_day',day))
                if tile.get('yield_units',0)>=2 or (day>=born+11 and tile.get('yield_units',0)):command=['HARVEST'];rank=0
                elif day in fert_days and inv.get('FERTILIZER',0) and tile.get('fertilized_until_day',-1)<day:command=['FERTILIZE'];rank=1
                elif not tile.get('watered_today') and day<=born+11:command=['WATER'];rank=1
        if command:tasks.append((rank,abs(pos[0]-x)+abs(pos[1]-y),(x,y),command))
    if tasks:
        tasks.sort()
        _,_,target,command=tasks[0]
        return _v219_walk(pos,target) or command
    return ['PASS']

def bd_agent(observation,configuration=None):
    try:
        action=_BD_PARENT_FN(observation,configuration)
        step=int(observation['step']);player=int(observation['player']);day=step//24
        state=_BD_STATES.get(player)
        if state is None or step<=state['last_step']:
            state={'last_step':step,'day':-1,'workers':{},'work':{},
                   'credit':{'TOMATO':0,'WHEAT':0}}
            _BD_STATES[player]=state
            if step==0:
                _BD_REPORT.update(eligible_checks=0,economic_declines=0,
                    budget_declines=0,requests=0,confirmed=0,committed=0,
                    weed_deaths=0,planted_tom=0,planted_wheat=0,
                    harvested_tom=0,harvested_wheat=0,sold_tom=0,
                    sold_wheat=0,fert_bought=0,errors=0,decisions=[])
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
                for item,key in (('TOMATO','harvested_tom'),('WHEAT','harvested_wheat')):
                    gained=max(0,private['inventories'][actor].get(item,0)-previous['inventory'].get(item,0))
                    if gained:
                        state['credit'][item]+=gained
                        _BD_REPORT[key]+=gained
        pending=state.pop('pending',None)
        if pending:
            funded='SE' in farm['unlocked_quadrants'] and (not pending['initial'] or private['seeds'].get('TOMATO',0)>=4)
            if funded and len(farm['hands'])>=pending['first']+1:
                first=pending['first']
                state['workers'][first]=list(_BD_EARLY)+_BD_LATE[:4]
                state['workers'][first+1]=list(_BD_WHEAT)+_BD_LATE[4:]
                _BD_REPORT['confirmed']+=1
                if pending['initial']:
                    state['committed']=True;state['planted_day']=day
                    _BD_REPORT['committed']+=1
        action=_bd_request(observation,action,state,native)
        if not state.get('committed'):return action
        result=copy.deepcopy(action)
        if day<=28 and state['workers']:
            commands=[result.get('farmer') or ['PASS']]+list(result.get('hands') or [])
            commands+=[['PASS'] for _ in range(len(farm['hands'])+1-len(commands))]
            state['work']={}
            for actor,tiles in state['workers'].items():
                if actor>=len(commands):continue
                command=_bd_worker(observation,actor,tiles,state,native)
                commands[actor]=command
                if command[:2]==['PLANT','TOMATO']:_BD_REPORT['planted_tom']+=1
                if command[:2]==['PLANT','WHEAT']:_BD_REPORT['planted_wheat']+=1
                state['work'][actor]={'step':step,'command':command,'inventory':dict(private['inventories'][actor])}
            result['farmer'],result['hands']=commands[0],commands[1:]
        weeds=sum(1 for x,y in _BD_ALL if isinstance(farm['tiles'][y][x],dict) and farm['tiles'][y][x].get('kind')=='WEED')
        if weeds>_BD_REPORT['weed_deaths']:_BD_REPORT['weed_deaths']=weeds
        stock=projected_shed(result,FarmView(observation))
        for item,key in (('TOMATO','sold_tom'),('WHEAT','sold_wheat')):
            if state['credit'][item] and len(result['market'])<MAX_ORDERS:
                scheduled=sum(int(o[2]) for o in result['market'] if o[:2]==['SELL',item])
                count=min(state['credit'][item],max(0,stock.get(item,0)-scheduled))
                if count:
                    result['market'].append(['SELL',item,count])
                    state['credit'][item]-=count
                    _BD_REPORT[key]+=count
        return result
    except Exception:
        _BD_REPORT['errors']+=1
        return _BD_PARENT_FN(observation,configuration)

_BD_PARENT_FN=r9_scaled_agent

# GROW VARIANT bd2 entry (note guard: unique entry defined LAST).
def grow_variant_agent(observation,configuration=None):
    return bd_agent(observation,configuration)
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
print("bd2 OK entry=grow_variant_agent sha="
      + hashlib.sha256(OUT.read_bytes()).hexdigest()[:12])
