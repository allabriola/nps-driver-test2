import subprocess, json, sys, re
sys.stdout.reconfigure(encoding='utf-8')

BQ = 'bq.cmd'
sql = open('_q_tr_wide.sql', encoding='utf-8').read()

import time
time.sleep(5)
r = subprocess.run([BQ,'query','--nouse_legacy_sql','--format=json','--project_id=meli-bi-data','--max_rows=10000'],
    input=sql.encode('utf-8'), capture_output=True, timeout=150)
stdout = r.stdout.decode('utf-8', errors='replace')

def fix_escapes(s):
    # Fix \UXXXXXXXX (8 hex digit unicode — invalid in JSON)
    def fix_u8(m):
        cp = int(m.group(1), 16)
        if cp <= 0xFFFF:
            return '\\u{:04x}'.format(cp)
        return ''  # surrogate pairs out of scope
    s = re.sub(r'\\U([0-9a-fA-F]{8})', fix_u8, s)
    # Fix \xNN hex byte escapes
    s = re.sub(r'\\x([0-9a-fA-F]{2})', lambda m: '\\u00' + m.group(1), s)
    return s

stdout2 = fix_escapes(stdout)
try:
    data = json.loads(stdout2)
    with open('_lt_tr_wide.json','w',encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=None)
    print(f'OK: {len(data)} msgs')
    if data:
        print('Sample:', str(data[0])[:200])
except Exception as e:
    print('ERROR:', e)
    pos = int(str(e).split('(char ')[-1].rstrip(')')) if '(char' in str(e) else 0
    print('Context around error:', repr(stdout2[max(0,pos-40):pos+40]))
