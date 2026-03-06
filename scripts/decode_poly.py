from routes_handler import process_routes_fallback
origin={'lat':-6.595714,'lng':106.789572}
destination={'lat':-6.604280,'lng':106.796700}
routes=process_routes_fallback(origin,destination)
poly=routes['primary_route']['polyline']
print('polylen',len(poly))
# decode
pts=[]
index=0;lat=0;lng=0;enc=poly
while index < len(enc):
    result=0; shift=0
    while True:
        b=ord(enc[index]) - 63; index+=1
        result |= (b & 0x1f) << shift
        shift +=5
        if b < 0x20: break
    dlat = ~(result >>1) if (result &1) else (result>>1)
    lat += dlat
    result=0; shift=0
    while True:
        b=ord(enc[index]) - 63; index+=1
        result |= (b & 0x1f) << shift
        shift +=5
        if b < 0x20: break
    dlng = ~(result >>1) if (result &1) else (result>>1)
    lng += dlng
    pts.append((lat/1e5,lng/1e5))
print('points count',len(pts))
for p in pts:
    print(p)
