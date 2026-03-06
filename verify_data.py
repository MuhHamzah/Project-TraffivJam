import requests

print('Testing API endpoints...\n')

# Test 1: Check jl_djuanda minute data
print('1. Per-minute data untuk jl_djuanda:')
r = requests.get('http://localhost:5000/api/minute/jl_djuanda')
data = r.json()
if data:
    print('   Latest records:')
    for record in data[-3:]:
        print(f'   {record}')
else:
    print('   No data yet')

print()

# Test 2: Check daily data
print('2. Daily data untuk jl_djuanda:')
r = requests.get('http://localhost:5000/api/daily/jl_djuanda')
data = r.json()
if data:
    for record in data[-2:]:
        print(f'   {record}')

print()

# Test 3: Check detection status
print('3. Detection status untuk jl_djuanda:')
r = requests.get('http://localhost:5000/api/detection/status/jl_djuanda')
print(f'   {r.json()}')

print()

# Test 4: Check camera status
print('4. Camera status semua kamera:')
r = requests.get('http://localhost:5000/api/camera-status')
data = r.json()
for cam_id, status in data.items():
    online_emoji = '🟢' if status['status'] == 'online' else '🔴'
    detect_emoji = '✅' if status.get('detection_enabled') else '⏸️'
    cam_status = status['status']
    print(f'   {cam_id}: {online_emoji} {cam_status} | Detection: {detect_emoji}')
