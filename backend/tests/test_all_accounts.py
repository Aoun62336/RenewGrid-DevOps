import urllib.request, json

ACCOUNTS = [
    ("admin@renewgrid.com",     "Admin@1234"),
    ("user@renewgrid.com",      "User@1234"),
    ("collector@renewgrid.com", "Collector@1234"),
    ("recycler@renewgrid.com",  "Recycler@1234"),
]

for email, pw in ACCOUNTS:
    url = 'http://localhost:8000/auth/login'
    payload = json.dumps({'email': email, 'password': pw}).encode()
    req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req) as res:
            data = json.loads(res.read())
            print(f"[PASS] {email} | role={data['user']['role']}")
    except urllib.error.HTTPError as e:
        print(f"[FAIL] {email} | HTTP {e.code}: {e.read().decode()}")
