"""Integration tests of the gateway against a THROWAWAY n8n instance — never production.

It creates, updates and activates workflows there and runs fixture executions.

    docker run -d --rm --name gw-test -p 5679:5678 n8nio/n8n
    # set up the owner in the browser, then create two API keys:
    #   N8N_SETUP_KEY  - scopes workflow:create/update/read/list/activate/delete, execution:list/read
    #   N8N_SCOPED_KEY - the gateway scopes from the README
    N8N_URL=http://localhost:5679 N8N_SETUP_KEY=... N8N_SCOPED_KEY=... \
        python3 tests/integration_test.py workflow/orqflow-gateway.json
"""
import json, os, sys, time, urllib.request, urllib.error
from pathlib import Path

B = os.environ.get('N8N_URL', 'http://localhost:5679').rstrip('/')
SETUP = os.environ['N8N_SETUP_KEY']
SCOPED = os.environ['N8N_SCOPED_KEY']
TOKEN = 'a' * 8 + 'f3b9c2e1d4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3'  # 56 chars, test only
results = []


def http(method, url, body=None, headers=None, raw=False):
    data = None if body is None else (body if raw else json.dumps(body)).encode()
    req = urllib.request.Request(url, data=data, method=method, headers={'Content-Type': 'application/json', **(headers or {})})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.loads(r.read() or b'null')
    except urllib.error.HTTPError as e:
        txt = e.read()
        try:
            return e.code, json.loads(txt)
        except Exception:
            return e.code, txt.decode()[:300]


def api(method, path, body=None):
    return http(method, B + '/api/v1' + path, body, {'X-N8N-API-KEY': SETUP})


def check(name, cond, detail=''):
    results.append((name, bool(cond)))
    print(('PASS ' if cond else 'FAIL ') + name + ('' if cond else '  -> ' + str(detail)[:400]))


def install(token, n8n_key, instance='http://localhost:5678', name='Gateway under test'):
    w = json.loads(Path(sys.argv[1]).read_text())
    for n in w['nodes']:
        if n['name'] == '⚙️ Config':
            for a in n['parameters']['assignments']['assignments']:
                a['value'] = {'gatewayToken': token, 'n8nApiKey': n8n_key, 'instanceUrl': instance}[a['name']]
    payload = {'name': name, 'nodes': w['nodes'], 'connections': w['connections'], 'settings': {'executionOrder': 'v1'}}
    old = [x for x in api('GET', '/workflows?limit=250')[1]['data'] if x['name'] == name]
    if old:
        api('POST', f"/workflows/{old[0]['id']}/deactivate")
        s, wf = api('PUT', f"/workflows/{old[0]['id']}", payload)
    else:
        s, wf = api('POST', '/workflows', payload)
    assert s == 200, wf
    s, r = api('POST', f"/workflows/{wf['id']}/activate")
    assert s == 200, r
    time.sleep(1)
    return wf['id']


def gw(body, token=TOKEN, raw=False, headers=None):
    h = {} if token is None else {'X-API-Key': token}
    return http('POST', B + '/webhook/mobile-api-gate', body, {**h, **(headers or {})}, raw)


def ensure_fixtures():
    """A plain workflow to toggle, and a webhook workflow that stays running for 40 s."""
    ids = {}
    for name, nodes, conns in [
        ('Fixture toggle', [{'name': 'Manual', 'type': 'n8n-nodes-base.manualTrigger', 'typeVersion': 1,
                              'position': [0, 0], 'parameters': {}}], {}),
        ('Fixture slow', [
            {'name': 'Hook', 'type': 'n8n-nodes-base.webhook', 'typeVersion': 2, 'position': [0, 0],
             'parameters': {'path': 'fixture-slow', 'httpMethod': 'GET', 'responseMode': 'onReceived'}, 'webhookId': 'fixture-slow'},
            {'name': 'Wait', 'type': 'n8n-nodes-base.wait', 'typeVersion': 1.1, 'position': [200, 0],
             'parameters': {'amount': 40, 'unit': 'seconds'}}],
         {'Hook': {'main': [[{'node': 'Wait', 'type': 'main', 'index': 0}]]}}),
    ]:
        found = [x for x in api('GET', '/workflows?limit=250')[1]['data'] if x['name'] == name]
        if found:
            ids[name] = found[0]['id']
            continue
        s, wf = api('POST', '/workflows', {'name': name, 'nodes': nodes, 'connections': conns, 'settings': {'executionOrder': 'v1'}})
        assert s == 200, wf
        ids[name] = wf['id']
    api('POST', f"/workflows/{ids['Fixture slow']}/activate")
    return ids


fx = ensure_fixtures()
SECRETS = [TOKEN, SCOPED, SETUP]


def no_secret(name, payload):
    text = json.dumps(payload)
    check(name + ' leaks no secret', not any(s in text for s in SECRETS), text)


# --- Misconfiguration: fail closed -------------------------------------------------------
for label, token in [('placeholder token', 'CHANGE_ME: run openssl rand -hex 32'), ('empty token', ''),
                     ('change-me token', 'change-me'), ('short token', 'abc123')]:
    install(token, SCOPED)
    for presented in [token, 'change-me', None]:
        s, r = gw({'action': 'list_workflows', 'params': {}}, token=presented)
        check(f'{label}: presented {presented!r} rejected', s == 503 and r.get('success') is False, (s, r))
        no_secret(f'{label} reply', r)

# --- Configured gateway --------------------------------------------------------------------
gid = install(TOKEN, SCOPED)
s, r = gw({'action': 'list_endpoints', 'params': {}}, token=None)
check('missing X-API-Key -> 401', s == 401, (s, r))
s, r = gw({'action': 'list_endpoints', 'params': {}}, token=TOKEN[:-1] + 'x')
check('wrong token -> 401', s == 401, (s, r))
s, r = gw({'action': 'list_endpoints', 'params': {}}, token='change-me')
check('change-me token -> 401', s == 401, (s, r))
s, r = gw({'action': 'list_endpoints', 'params': {}}, token=TOKEN[:40])
check('token prefix -> 401', s == 401, (s, r))
no_secret('401 reply', r)

s, r = gw({'action': 'list_endpoints', 'params': {}})
eps = (r.get('data') or {}).get('endpoints', [])
check('list_endpoints ok', s == 200 and r['success'], (s, r))
check('allowlist is exactly the app set', sorted(eps) == sorted([
    'list_endpoints', 'get_system_info', 'list_workflows', 'get_workflow', 'activate_workflow',
    'deactivate_workflow', 'list_executions', 'get_execution', 'stop_execution']), eps)

s, r = gw({'action': 'get_system_info', 'params': {}})
d = r.get('data') or {}
check('get_system_info ok, no internal URL', s == 200 and d.get('api_version') == 'v1' and d.get('workflow_id') == gid
      and 'instance_url' not in d and 'api_base' not in d, (s, r))

s, r = gw({'action': 'list_workflows', 'params': {'limit': 50}})
items = (r.get('data') or {}).get('items', [])
check('list_workflows ok and hides gateway', s == 200 and r['success'] and items and all(i['id'] != gid for i in items), (s, r))
s, r = gw({'action': 'list_workflows', 'params': {'limit': 1}})
cur = (r.get('data') or {}).get('nextCursor')
s2, r2 = gw({'action': 'list_workflows', 'params': {'limit': 1, 'cursor': cur}})
check('list_workflows cursor paging', cur and s2 == 200 and r2['success'], (s2, r2))

tid = fx['Fixture toggle']
s, r = gw({'action': 'get_workflow', 'params': {'workflowId': tid}})
check('get_workflow ok', s == 200 and r['data']['id'] == tid, (s, r))
s, r = gw({'action': 'activate_workflow', 'params': {'workflowId': fx['Fixture slow']}})
check('activate_workflow ok', s == 200 and r['success'] and r['data']['active'] is True, (s, r))
s, r = gw({'action': 'deactivate_workflow', 'params': {'workflowId': fx['Fixture slow']}})
check('deactivate_workflow ok', s == 200 and r['success'] and r['data']['active'] is False, (s, r))
gw({'action': 'activate_workflow', 'params': {'workflowId': fx['Fixture slow']}})
time.sleep(1)

# A running execution to stop.
http('GET', B + '/webhook/fixture-slow')
time.sleep(2)
s, r = gw({'action': 'list_executions', 'params': {'limit': 20, 'status': 'running', 'workflowId': fx['Fixture slow']}})
running = (r.get('data') or {}).get('items', [])
check('list_executions with filters ok', s == 200 and r['success'] and running, (s, r))
s, r = gw({'action': 'list_executions', 'params': {'limit': 100}})
check('list_executions hides gateway runs', s == 200 and all(e['workflowId'] != gid for e in r['data']['items']), (s, r))
if running:
    eid = running[0]['id']
    s, r = gw({'action': 'get_execution', 'params': {'executionId': eid}})
    check('get_execution ok, no run data', s == 200 and r['data']['id'] == eid and 'data' not in r['data'], (s, r))
    s, r = gw({'action': 'stop_execution', 'params': {'executionId': eid}})
    check('stop_execution ok', s == 200 and r['success'], (s, r))
    s, r = gw({'action': 'get_execution', 'params': {'executionId': int(eid)}})
    check('numeric executionId accepted', s == 200 and r['success'], (s, r))

# --- Refused actions and malformed input -------------------------------------------------
for action in ['delete_execution', 'create_workflow', 'update_workflow', 'delete_workflow', 'list_credentials',
               'create_credential', 'delete_credential', 'list_variables', 'create_variable', 'delete_variable',
               'list_tags', 'create_tag', 'delete_tag', 'list_users', 'generate_audit', 'list_projects',
               'pull_source_control', 'push_source_control', 'constructor', '__proto__', 'toString', '']:
    s, r = gw({'action': action, 'params': {}})
    check(f'refused action {action!r} -> 400', s == 400 and r.get('error') == 'Unknown action', (s, r))

for label, params in [
    ('missing workflowId', {}),
    ('path traversal workflowId', {'workflowId': '../credentials'}),
    ('encoded traversal workflowId', {'workflowId': '..%2Fcredentials'}),
    ('query in workflowId', {'workflowId': 'abc?limit=1'}),
    ('object workflowId', {'workflowId': {'a': 1}}),
    ('extra param', {'workflowId': tid, 'force': True}),
]:
    s, r = gw({'action': 'get_workflow', 'params': params})
    check(f'get_workflow {label} -> 400', s == 400 and r.get('success') is False, (s, r))
for label, params in [
    ('includeData', {'includeData': True}), ('bad status', {'status': 'deleted'}), ('limit 0', {'limit': 0}),
    ('limit 1000', {'limit': 1000}), ('limit string', {'limit': '10'}), ('traversal workflowId', {'workflowId': '../x'}),
]:
    s, r = gw({'action': 'list_executions', 'params': params})
    check(f'list_executions {label} -> 400', s == 400, (s, r))
s, r = gw({'action': 'list_workflows', 'params': [1, 2]})
check('params array -> 400', s == 400, (s, r))
s, r = gw('not json', raw=True)
check('non-JSON body rejected', s >= 400, (s, r))
s, r = gw({'action': 'get_workflow', 'params': {'workflowId': 'doesnotexist123'}})
check('unknown workflow -> n8n 404 passed as success:false', s == 200 and r['success'] is False and r['httpStatus'] == 404, (s, r))

# --- Server-side misconfiguration --------------------------------------------------------
install(TOKEN, 'CHANGE_ME: n8n Settings → n8n API → Create an API key')
s, r = gw({'action': 'list_workflows', 'params': {}})
check('placeholder n8nApiKey -> 503', s == 503, (s, r))
install(TOKEN, 'wrong-key-0000')
s, r = gw({'action': 'list_workflows', 'params': {}})
check('invalid n8nApiKey -> success:false 401 message', s == 200 and r['httpStatus'] == 401, (s, r))
no_secret('invalid key reply', r)
install(TOKEN, SCOPED, instance='ftp://n8n')
s, r = gw({'action': 'list_workflows', 'params': {}})
check('non-http instanceUrl -> 503', s == 503, (s, r))
install(TOKEN, SCOPED, instance='http://localhost:1')
s, r = gw({'action': 'list_workflows', 'params': {}})
check('unreachable instanceUrl -> 502 message', s == 200 and r.get('httpStatus') == 502, (s, r))
no_secret('unreachable reply', r)

# Restore a working gateway for manual checks.
install(TOKEN, SCOPED)
print(f"\n{sum(ok for _, ok in results)}/{len(results)} passed")
sys.exit(0 if all(ok for _, ok in results) else 1)
