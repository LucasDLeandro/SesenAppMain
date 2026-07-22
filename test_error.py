import urllib.request
import urllib.error

req = urllib.request.Request(
    'http://127.0.0.1:8090/elevadores/api/elevadoress/dashboard/?inicio=2026-07-01&fim=2026-07-31', 
    headers={'Accept': 'application/json'}
)
try:
    urllib.request.urlopen(req)
    print("Success!")
except urllib.error.HTTPError as e:
    print(f"Error {e.code}")
    print(e.read().decode('utf-8')[:5000])
