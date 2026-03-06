import threading
import time
import os
import traceback
import json
import requests
from flask import Flask, render_template, jsonify, send_from_directory, request
from detector import CameraWorker, CAMERA_CONFIGS
from config import GOOGLE_MAPS_API_KEY
from routes_handler import (
    get_google_routes, 
    process_google_directions, 
    process_routes_fallback,
    generate_realistic_polyline
)

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

WORKERS = {}
START_TIME = time.time()

@app.route('/')
def index():
    return render_template('index.html', cameras=CAMERA_CONFIGS)


@app.route('/maps')
def maps():
    return render_template('maps.html', cameras=CAMERA_CONFIGS)


@app.route('/test_routes')
def test_routes():
    return render_template('test_routes.html')


@app.route('/analysis')
def analysis():
    return render_template('analysis.html', cameras=CAMERA_CONFIGS)


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', cameras=CAMERA_CONFIGS)


@app.route('/data')
def data():
    return render_template('data.html', cameras=CAMERA_CONFIGS)

@app.route('/api/config')
def api_config():
    """Provide API configuration to frontend"""
    from config import LOCATIONS
    return jsonify({
        'google_maps_api_key': GOOGLE_MAPS_API_KEY,
        'camera_locations': LOCATIONS
    })

@app.route('/api/cameras-locations')
def cameras_locations():
    """Get all camera locations from config"""
    from config import LOCATIONS
    return jsonify(LOCATIONS)

@app.route('/api/maps-data')
def api_maps_data():
    """Get map data for the primary monitoring location"""
    # Return data for Jembatan Merah (primary location)
    return jsonify({
        'latitude': -6.601357,
        'longitude': 106.796838,
        'name': 'Jembatan Merah - Traffic Monitoring',
        'address': 'Jembatan Merah, Bogor Tengah, Kota Bogor, Jawa Barat 16125'
    })

@app.route('/csv/minute/<camera_id>')
def csv_minute(camera_id):
    path = os.path.join('data', camera_id)
    filename = 'per_minute.csv'
    return send_from_directory(path, filename, as_attachment=True)

@app.route('/csv/daily/<camera_id>')
def csv_daily(camera_id):
    path = os.path.join('data', camera_id)
    filename = 'daily.csv'
    return send_from_directory(path, filename, as_attachment=True)

@app.route('/api/daily/<camera_id>')
def api_daily(camera_id):
    import pandas as pd
    path = os.path.join('data', camera_id, 'daily.csv')
    try:
        df = pd.read_csv(path)
        return jsonify(df.to_dict('records'))
    except Exception as e:
        return jsonify([])

@app.route('/api/minute/<camera_id>')
def api_minute(camera_id):
    import pandas as pd
    path = os.path.join('data', camera_id, 'per_minute.csv')
    try:
        df = pd.read_csv(path)
        return jsonify(df.to_dict('records'))
    except Exception as e:
        return jsonify([])

@app.route('/api/second/<camera_id>')
def api_second(camera_id):
    """Get per-second detection data (NEW: untuk lihat setiap deteksi per detik)"""
    import pandas as pd
    path = os.path.join('data', camera_id, 'per_second.csv')
    try:
        df = pd.read_csv(path)
        # Return latest 300 records (last 5 minutes per-second data)
        return jsonify(df.tail(300).to_dict('records'))
    except Exception as e:
        return jsonify([])

@app.route('/csv/second/<camera_id>')
def csv_second(camera_id):
    """Download per-second CSV"""
    path = os.path.join('data', camera_id)
    filename = 'per_second.csv'
    return send_from_directory(path, filename, as_attachment=True)

@app.route('/api/all-cameras-daily')
def api_all_cameras_daily():
    import pandas as pd
    result = {}
    for cam in CAMERA_CONFIGS:
        path = os.path.join('data', cam['id'], 'daily.csv')
        try:
            df = pd.read_csv(path)
            result[cam['id']] = df.to_dict('records')
        except:
            result[cam['id']] = []
    return jsonify(result)

@app.route('/api/forecast/<camera_id>')
def api_forecast(camera_id):
    """Simple trend-based forecast"""
    import pandas as pd
    import numpy as np
    path = os.path.join('data', camera_id, 'daily.csv')
    try:
        df = pd.read_csv(path)
        if len(df) < 3:
            return jsonify({'forecast': []})
        
        # Calculate trend for each vehicle type
        forecast = []
        last_date = pd.to_datetime(df['date'].iloc[-1])
        
        for col in ['cars', 'motorbikes', 'buses', 'trucks']:
            if col not in df.columns:
                continue
            values = df[col].values.astype(float)
            
            # Simple trend: average of recent 3 days + trend
            if len(values) >= 3:
                recent = values[-3:]
                trend = np.polyfit(range(len(recent)), recent, 1)[0]
                next_val = max(0, recent[-1] + trend)
            else:
                next_val = values[-1] if len(values) > 0 else 0
            
            forecast.append({
                'type': col,
                'value': round(next_val, 0)
            })
        
        # Add forecast for next day
        next_date = (last_date + pd.Timedelta(days=1)).strftime('%Y-%m-%d')
        total_forecast = sum(f['value'] for f in forecast)
        
        return jsonify({
            'date': next_date,
            'forecast': forecast,
            'total': total_forecast
        })
    except Exception as e:
        return jsonify({'forecast': []})


@app.route('/api/health')
def health():
    uptime = time.time() - START_TIME
    workers_status = {}
    for cam_id, worker in WORKERS.items():
        workers_status[cam_id] = {
            'running': worker.running if hasattr(worker, 'running') else False,
            'has_cap': worker.cap is not None if hasattr(worker, 'cap') else False
        }
    return jsonify({
        'status': 'ok',
        'uptime_seconds': int(uptime),
        'workers': workers_status,
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
    })


@app.route('/api/detection/start/<camera_id>', methods=['POST'])
def start_detection(camera_id):
    """Start detection for a specific camera"""
    from detector import CameraWorker
    CameraWorker.start_detection(camera_id)
    return jsonify({'status': 'success', 'message': f'Detection started for {camera_id}', 'camera_id': camera_id})


@app.route('/api/detection/stop/<camera_id>', methods=['POST'])
def stop_detection(camera_id):
    """Stop detection for a specific camera"""
    from detector import CameraWorker
    CameraWorker.stop_detection(camera_id)
    return jsonify({'status': 'success', 'message': f'Detection stopped for {camera_id}', 'camera_id': camera_id})


@app.route('/api/detection/status/<camera_id>')
def detection_status(camera_id):
    """Get detection status for a specific camera"""
    from detector import CameraWorker
    is_enabled = CameraWorker.is_detection_enabled(camera_id)
    return jsonify({'camera_id': camera_id, 'detection_enabled': is_enabled})


@app.route('/api/diagnostics')
def diagnostics():
    """Diagnostic endpoint to check Google Maps API configuration"""
    print("\n" + "="*60)
    print("[DIAGNOSTICS] Checking Google Maps API configuration")
    print("="*60)
    
    diag = {
        'google_maps_api_key': {
            'configured': bool(GOOGLE_MAPS_API_KEY),
            'is_dummy': GOOGLE_MAPS_API_KEY.startswith('AIzaSyDummy') if GOOGLE_MAPS_API_KEY else False,
            'key_preview': GOOGLE_MAPS_API_KEY[:20] + '...' if GOOGLE_MAPS_API_KEY else 'NOT SET',
            'key_length': len(GOOGLE_MAPS_API_KEY) if GOOGLE_MAPS_API_KEY else 0
        },
        'directions_api': {
            'status': 'UNKNOWN',
            'message': 'Run a route calculation to test'
        },
        'recommendation': ''
    }
    
    # Test if API key works
    if diag['google_maps_api_key']['is_dummy']:
        diag['recommendation'] = 'API key is DUMMY/NOT SET. Go to https://console.cloud.google.com/apis/credentials to get a real API key'
    elif not diag['google_maps_api_key']['configured']:
        diag['recommendation'] = 'API key is NOT configured. Set GOOGLE_MAPS_API_KEY in config.py'
    else:
        # Try to make a simple API request
        try:
            test_url = 'https://maps.googleapis.com/maps/api/directions/json'
            test_params = {
                'origin': '-6.595714,106.789572',
                'destination': '-6.604280,106.796700',
                'key': GOOGLE_MAPS_API_KEY
            }
            test_response = requests.get(test_url, params=test_params, timeout=5)
            test_data = test_response.json()
            
            if test_data.get('status') == 'OK':
                diag['directions_api']['status'] = 'OK ✓'
                diag['directions_api']['message'] = 'Google Maps Directions API is working'
                diag['recommendation'] = 'All systems GO! Polylines should work correctly.'
            else:
                diag['directions_api']['status'] = test_data.get('status', 'UNKNOWN')
                diag['directions_api']['message'] = test_data.get('error_message', 'Check API key permissions')
                diag['recommendation'] = f'API returned: {test_data.get("status")}. Check if Directions API is enabled in Google Cloud Console.'
        except Exception as e:
            diag['directions_api']['status'] = 'ERROR'
            diag['directions_api']['message'] = str(e)
            diag['recommendation'] = 'Could not reach Google Maps API. Check internet connection and API key.'
    
    print(f"Config: {diag}")
    print("="*60 + "\n")
    
    return jsonify(diag)


@app.route('/api/routes', methods=['POST'])
def get_routes():
    """Get routes from Google Maps with real polylines for road-following paths.
    
    Request body:
    {
        "origin": {"lat": -6.595714, "lng": 106.789572},
        "destination": {"lat": -6.604280, "lng": 106.796700}
    }
    
    Response:
    {
        "primary_route": {
            "polyline": "encoded polyline string",
            "distance_text": "1.2 km",
            "duration_text": "5 mins",
            "traffic_status": "free|slow|congested",
            ...
        },
        "alternative_routes": [...],
        "traffic_status": "free" | "slow" | "congested",
        "has_congestion": bool,
        "source": "google" | "fallback"
    }
    """
    try:
        data = request.get_json()
        if not data:
            print("ERROR: No JSON data in request")
            return jsonify({'error': 'No JSON data provided'}), 400
            
        origin = data.get('origin')
        destination = data.get('destination')
        
        print(f"\n{'='*60}")
        print(f"[API ROUTE REQUEST]")
        print(f"  Origin:      {origin}")
        print(f"  Destination: {destination}")
        print(f"  API Key:     {GOOGLE_MAPS_API_KEY[:30] if GOOGLE_MAPS_API_KEY else 'NOT SET'}...")
        print(f"{'='*60}")
        
        if not origin or not destination:
            print(f"ERROR: Missing origin or destination")
            return jsonify({'error': 'Missing origin or destination'}), 400
        
        # Try Google Maps API first if key is configured
        routes_info = None
        source = 'fallback'
        
        if GOOGLE_MAPS_API_KEY and GOOGLE_MAPS_API_KEY != 'YOUR_API_KEY_HERE':
            print(f"[ATTEMPT 1] Trying Google Maps Directions API...")
            directions_data = get_google_routes(origin, destination, GOOGLE_MAPS_API_KEY)
            
            if directions_data:
                print(f"[SUCCESS] Google Maps API returned routes")
                routes_info = process_google_directions(directions_data)
                source = 'google'
            else:
                print(f"⚠️  Google Maps API failed, using fallback")
        else:
            print(f"⚠️  API key not configured properly, using fallback data")
        
        # If Google not configured or failed, try OSRM public server before using synthetic fallback
        if not routes_info:
            try:
                from routes_handler import get_osrm_routes
                print('[ATTEMPT] Trying OSRM public server for routing...')
                osrm_data = get_osrm_routes(origin, destination)
                if osrm_data:
                    print('[SUCCESS] OSRM returned routes')
                    routes_info = process_google_directions(osrm_data)
                    source = 'osrm'
                else:
                    print('[WARN] OSRM did not return routes')
            except Exception as e:
                print(f'[ERROR] OSRM attempt failed: {e}')
        
        # Use fallback if Google API didn't work
        if not routes_info:
            print(f"[ATTEMPT 2] Generating realistic fallback routes...")
            routes_info = process_routes_fallback(origin, destination)
            source = 'fallback'
        
        if routes_info and routes_info.get('primary_route'):
            pr = routes_info['primary_route']
            poly_len = len(pr.get('polyline', ''))
            print(f"[FINAL] Route ready:")
            print(f"  Distance:    {pr.get('distance_text')}")
            print(f"  Duration:    {pr.get('duration_text')}")
            print(f"  Traffic:     {pr.get('traffic_status')}")
            print(f"  Polyline:    {poly_len} chars (Valid: {'✓' if poly_len > 20 else '✗'})")
            print(f"  Source:      {source}")
            
            # Ensure source is set
            if 'source' not in routes_info:
                routes_info['source'] = source
        
        print(f"{'='*60}\n")
        
        return jsonify(routes_info or {'error': 'Could not generate routes'})
    
    except Exception as e:
        print(f"❌ EXCEPTION in /api/routes: {str(e)}")
        traceback.print_exc()
        try:
            print(f"⚠️  Falling back to ERROR routes")
            origin = data.get('origin', {'lat': 0, 'lng': 0})
            destination = data.get('destination', {'lat': 1, 'lng': 1})
            return jsonify(process_routes_fallback(origin, destination))
        except:
            return jsonify({'error': 'Failed to calculate route'}), 500






@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def server_error(error):
    return jsonify({'error': 'Server error', 'message': str(error)}), 500

def start_workers():
    for cam in CAMERA_CONFIGS:
        cam_id = cam['id']
        worker = CameraWorker(cam)
        t = threading.Thread(target=worker.run, daemon=True)
        WORKERS[cam_id] = worker
        t.start()

if __name__ == '__main__':
    if not os.path.exists('data'):
        os.makedirs('data')
    start_workers()
    app.run(host='0.0.0.0', port=5000, threaded=True)
