from app.v6_bridge.v6_bridge import V6Bridge, V6BridgeConfig

P=0
F=0

def T(n,name,fn):
    global P,F
    try:
        fn(); print(f'[PASS] {n:02d} - {name}'); P+=1
    except Exception as e:
        print(f'[FAIL] {n:02d} - {name} :: {type(e).__name__}: {e}'); F+=1

def valid():
    b=V6Bridge()
    r=b.translate({'event_type':'MARKET','action':'UPDATE','symbol':'BTCUSDT'})
    assert r['event_type']=='MARKET' and r['action']=='UPDATE'

def missing_event():
    b=V6Bridge()
    try: b.translate({'action':'UPDATE'})
    except Exception: return
    raise AssertionError('missing event_type accepted')

def missing_action():
    b=V6Bridge()
    try: b.translate({'event_type':'MARKET'})
    except Exception: return
    raise AssertionError('missing action accepted')

def disabled():
    b=V6Bridge(V6BridgeConfig(enabled=False))
    try: b.translate({'event_type':'MARKET','action':'UPDATE'})
    except Exception: return
    raise AssertionError('disabled bridge translated payload')

def unknown():
    b=V6Bridge(V6BridgeConfig(preserve_unknown_fields=True))
    r=b.translate({'event_type':'MARKET','action':'UPDATE','custom_field':'KEEP'})
    assert r.get('unknown_fields',{}).get('custom_field')=='KEEP'

def original():
    b=V6Bridge(V6BridgeConfig(preserve_original_payload=True))
    p={'event_type':'MARKET','action':'UPDATE','nested':{'x':1}}
    before={'event_type':'MARKET','action':'UPDATE','nested':{'x':1}}
    r=b.translate(p)
    assert p==before
    assert r.get('original_payload')==before

def isolation():
    seen={}
    def h(x):
        x['action']='MUTATED'
        x.setdefault('nested',{})['x']=999
        seen['ok']=1
        return x
    b=V6Bridge(translation_handler=h)
    p={'event_type':'MARKET','action':'UPDATE','nested':{'x':1}}
    b.dispatch(p)
    assert p=={'event_type':'MARKET','action':'UPDATE','nested':{'x':1}}
    assert seen.get('ok')==1

def handler_exception():
    def h(x): raise RuntimeError('handler-test')
    b=V6Bridge(translation_handler=h)
    try: b.dispatch({'event_type':'MARKET','action':'UPDATE'})
    except RuntimeError: return
    raise AssertionError('handler exception was swallowed')

def no_handler():
    b=V6Bridge()
    r=b.dispatch({'event_type':'MARKET','action':'UPDATE'})
    assert not (isinstance(r,dict) and r.get('success') is False)

def strict_enabled():
    b=V6Bridge()
    for x in ('false',1,0,None,[],{}):
        try: b.set_enabled(x)
        except (TypeError,ValueError): continue
        raise AssertionError(f'accepted {x!r}')

def many():
    b=V6Bridge()
    ps=[{'event_type':'MARKET','action':'UPDATE','id':1},{'event_type':'MARKET','action':'UPDATE','id':2}]
    r=b.translate_many(ps)
    assert len(r)==2

def no_execution():
    b=V6Bridge()
    forbidden={'execute','submit_order','place_order','cancel_order','create_order'}
    found=forbidden.intersection(dir(b))
    assert not found, f'forbidden methods exposed: {found}'

print('='*72)
print('V6 BRIDGE - 12 RUNTIME CONTRACT TESTS')
print('='*72)
T(1,'valid payload translation',valid)
T(2,'missing event_type rejected',missing_event)
T(3,'missing action rejected',missing_action)
T(4,'disabled bridge blocks translation',disabled)
T(5,'unknown-field preservation',unknown)
T(6,'original payload immutability/preservation',original)
T(7,'handler mutation isolation',isolation)
T(8,'handler exception propagates',handler_exception)
T(9,'dispatch without handler',no_handler)
T(10,'strict set_enabled validation',strict_enabled)
T(11,'translate_many',many)
T(12,'no execution/broker methods exposed',no_execution)
print('='*72)
print(f'RESULT: PASS={P} FAIL={F} TOTAL={P+F}')
print('='*72)
raise SystemExit(1 if F else 0)
