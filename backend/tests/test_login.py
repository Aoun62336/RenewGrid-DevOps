import urllib.request
import json

def test_login():
    url = 'http://localhost:8000/auth/login'
    data = json.dumps({'email': 'admin@renewgrid.com', 'password': 'admin@1234'}).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    
    try:
        with urllib.request.urlopen(req) as res:
            resp_data = json.loads(res.read().decode('utf-8'))
            print("Login success!", resp_data['user'])
            
            token = resp_data['access_token']
            users_url = 'http://localhost:8000/admin/users?role=collector'
            users_req = urllib.request.Request(users_url, headers={'Authorization': f'Bearer {token}'})
            with urllib.request.urlopen(users_req) as users_res:
                print("Users:", users_res.read().decode('utf-8'))
    except Exception as e:
        print("Error:", e)

test_login()
