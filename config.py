# Configuration for Smart Traffic Monitoring System

# Flask app settings
DEBUG = False
HOST = '0.0.0.0'
PORT = 5000

# Google Maps API Key
# SETUP INSTRUCTIONS:
# 1. Go to: https://console.cloud.google.com/apis/credentials
# 2. Create a new API Key (or use existing one)
# 3. Enable these APIs in your Google Cloud project:
#    - Maps JavaScript API
#    - Directions API
#    - Maps Embed API
#    - Maps Static API
#    - Roads API (optional, for better polyline snapping)
# 4. If using API restrictions, add "HTTP referrer" for your domain
# 5. Replace the key below with your actual API key
# EXAMPLE: GOOGLE_MAPS_API_KEY = 'AIzaSyDxxxxxxxxxxxxxxxxxxxxxxxx'
# 
# ⚠️  If key is not set or is dummy, app will fall back to Leaflet + OSRM
GOOGLE_MAPS_API_KEY = 'YOUR_API_KEY_HERE'  # TODO: REPLACE WITH ACTUAL KEY FROM GOOGLE CLOUD CONSOLE

# YOLO Detection settings
DETECTION_INTERVAL = 1.0  # seconds between detections
FRAME_SIZE = 640  # imgsz for YOLO

# Object tracking settings
TRACKING_MAX_DISTANCE = 60  # pixels, max distance to match objects
TRACKING_TIMEOUT = 5  # seconds, max age of tracked object

# Speed estimation
DEFAULT_PIXELS_PER_METER = 50  # calibration constant, adjust per camera

# Data storage
DATA_DIR = 'data'
CSV_MINUTE_FILENAME = 'per_minute.csv'
CSV_DAILY_FILENAME = 'daily.csv'

# CCTV locations (name -> coordinates for maps)
LOCATIONS = {
    'depok_sp_jatijajar': {'lat': -6.410424, 'lng': 106.861203, 'name': 'Depok SP Jatijajar'},
    'jl_djuanda': {'lat': -6.604280, 'lng': 106.796700, 'name': 'JL. Djuanda'},
    'cibadak_bogor': {'lat': -6.554979, 'lng': 106.777037, 'name': 'Cibadak Kota Bogor'},
}

# Traffic detection thresholds
TRAFFIC_SPEED_THRESHOLD = 20  # km/h - kecepatan di bawah ini dianggap macet
TRAFFIC_DURATION_THRESHOLD = 300  # seconds - durasi minimum untuk dianggap kemacetan
