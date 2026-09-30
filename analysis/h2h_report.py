import json
from collections import defaultdict
rows=[json.loads(l) for l in open('h2h/rows.jsonl',encoding='utf-8') if l.strip()]
rows=[r for r in rows if 'players' in r]
print(len(rows),'games vs opponents rated >=2100; ledger mismatches:',sum(r['errors'] for r in rows))
def split(r):
    us=next(p for p in r['players'] if 'Shane' in p['team']); th=next(p for p in r['players'] if 'Shane' not in p['team'])
    return us,th
for name,sel in (('SAME-OPENING (family) opponents',lambda r:r['clone60']>=58),('DIFFERENT-ENGINE opponents',lambda r:r['clone60']<58)):
    g=[r for r in rows if sel(r)]
    if not g: continue
    n=len(g)
    print(f'\n######## {name}: {n} games, mean opp rating {sum(r["opp_score"] for r in g)/n:.0f}')
    us=[split(r)[0] for r in g]; th=[split(r)[1] for r in g]
    print(f'  our record W{sum(u["margin"]>0 for u in us)}-L{sum(u["margin"]<0 for u in us)}   mean margin {sum(u["margin"] for u in us)/n:+,.0f}   bank ours {sum(u["bank"] for u in us)/n:,.0f} theirs {sum(t["bank"] for t in th)/n:,.0f}')
    print(f'  idle share ours {sum(u["pass_share"] for u in us)/n:.1%} theirs {sum(t["pass_share"] for t in th)/n:.1%} | walking ours {sum(u["move_share"] for u in us)/n:.1%} theirs {sum(t["move_share"] for t in th)/n:.1%}')
    print('  land purchase days ours', sorted(set(tuple(round(x,1) for x in u['land']) for u in us))[:4], ' theirs', sorted(set(tuple(round(x,1) for x in t['land']) for t in th))[:6])
    print('  SALES per game: product | ours | theirs | gap   (units ours/theirs, avg price ours/theirs)')
    tot=0
    for item in ('STRAWBERRY','MILK','WOOL','WHEAT','EGG','TOMATO','CARROT','MELON','FERTILIZER'):
        o=sum(sum(v for k,v in u['sales'].items() if k.startswith(item+':')) for u in us)/n
        t=sum(sum(v for k,v in x['sales'].items() if k.startswith(item+':')) for x in th)/n
        ou=sum(sum(v for k,v in u['units'].items() if k.startswith(item+':')) for u in us)/n
        tu=sum(sum(v for k,v in x['units'].items() if k.startswith(item+':')) for x in th)/n
        tot+=o-t
        print(f'    {item:10} {o:>8,.0f} {t:>8,.0f} {o-t:>+8,.0f}   units {ou:5.0f}/{tu:5.0f}  price {o/ou if ou else 0:5.0f}/{t/tu if tu else 0:5.0f}')
        ph=' '.join(f'{sum(u["sales"].get(f"{item}:{p}",0) for u in us)/n:>6,.0f}/{sum(x["sales"].get(f"{item}:{p}",0) for x in th)/n:<6,.0f}' for p in range(4))
        print(f'        by phase (ours/theirs) d0-9, d10-15, d16-23, d24-29: {ph}')
    print(f'    total sales gap {tot:+,.0f}')
    print('  SPENDING per game (ours / theirs):')
    keys=sorted({k for p in us+th for k in p['spend']})
    for k in keys:
        o=sum(u['spend'].get(k,0) for u in us)/n; t=sum(x['spend'].get(k,0) for x in th)/n
        if abs(o)+abs(t)>300: print(f'    {k:24} {o:>9,.0f} {t:>9,.0f}   diff {o-t:+,.0f}')
    print('  FARM by day (ours/theirs):')
    for d in ('3','6','9','12','15','18','24'):
        line=f'    d{d:>2} bank {sum(u["daily"][d]["bank"] for u in us)/n:>7,.0f}/{sum(t["daily"][d]["bank"] for t in th)/n:<7,.0f} '
        for k in ('STRAWBERRY','WHEAT','TOMATO','CARROT','MELON','SHEEP','COW','GOOSE'):
            line+=f'{k[:4]} {sum(u["daily"][d]["census"].get(k,0) for u in us)/n:4.1f}/{sum(t["daily"][d]["census"].get(k,0) for t in th)/n:<4.1f} '
        line+=f'land {sum(u["daily"][d]["quads"] for u in us)/n:.1f}/{sum(t["daily"][d]["quads"] for t in th)/n:.1f} hands {sum(u["daily"][d]["hands"] for u in us)/n:.1f}/{sum(t["daily"][d]["hands"] for t in th)/n:.1f}'
        print(line)
    for r in sorted(g,key=lambda r:split(r)[0]['margin'])[:30]:
        u,t=split(r); print(f'     {u["margin"]:>+8,.0f} vs {r["opp"][:22]:22} ({r["opp_score"]:.0f}) us {u["bank"]:,.0f} them {t["bank"]:,.0f}')
