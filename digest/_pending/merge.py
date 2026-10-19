import json,sys,os
P='/workspace/frontpage/digest/items.json'; E='2026-10-19'
d=json.load(open(P)); ids={i['id'] for i in d['items']}
secs={s['id']:s for s in d['sections']}
new=[];quiet=[];notes={};phr=[]
for part in 'AB':
    f=f'/workspace/frontpage/digest/_pending/{E}-{part}.json'
    if not os.path.exists(f): print('missing',f); continue
    r=json.load(open(f))
    for it in r.get('items',[]):
        assert it['section'] in secs, it['section']
        assert it['edition']==E and it['sources'] and all(s['url'].startswith('http') and 'google.com/url' not in s['url'] for s in it['sources']), it['id']
        if it['id'] in ids: continue
        new.append(it); ids.add(it['id'])
    for sid,b in r.get('baselines',{}).items():
        secs[sid].update(b); print('baseline updated',sid)
    quiet+=r.get('quiet',[]); notes.update(r.get('quiet_notes',{})); phr+=r.get('intro_phrases',[])
d['items']+=new
json.dump({'new':len(new),'quiet':quiet,'notes':notes,'phrases':phr},open('/workspace/frontpage/digest/_pending/merge_info.json','w'),ensure_ascii=False,indent=1)
if '--write' in sys.argv:
    json.dump(d,open(P,'w'),ensure_ascii=False,indent=2); print('wrote',len(new))
else: print('dry',len(new),quiet,notes,phr)
