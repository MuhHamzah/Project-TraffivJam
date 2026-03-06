#!/usr/bin/env python3
"""
API TESTING & FEATURE SHOWCASE
=============================
Script untuk testing semua API endpoints dan menampilkan fitur-fitur aplikasi

Usage:
  python api_test.py          # Run all tests
  python api_test.py health   # Run specific test
"""

import requests
import json
import time
import sys
from datetime import datetime
from colorama import Fore, Back, Style, init

init(autoreset=True)

BASE_URL = "http://localhost:5000"

# Color helpers
def log_test(name):
    print(f"\n{Back.BLUE}{Fore.WHITE}{name:^70}{Style.RESET_ALL}")

def log_success(msg):
    print(f"{Fore.GREEN}✓ {msg}{Style.RESET_ALL}")

def log_error(msg):
    print(f"{Fore.RED}✗ {msg}{Style.RESET_ALL}")

def log_info(msg):
    print(f"{Fore.CYAN}ℹ {msg}{Style.RESET_ALL}")

def log_warn(msg):
    print(f"{Fore.YELLOW}⚠ {msg}{Style.RESET_ALL}")

def format_json(data, indent=2):
    return json.dumps(data, indent=indent, ensure_ascii=False)

# ============================================================================
# HEALTH CHECK
# ============================================================================
def test_health():
    log_test("TEST 1: SYSTEM HEALTH CHECK")
    
    try:
        log_info("Testing /api/health endpoint...")
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        
        if response.status_code == 200:
            health = response.json()
            log_success("Health check successful!")
            
            print(f"""
Status: {health.get('status', 'unknown')}
Uptime: {health.get('uptime_seconds', 0)} seconds
Timestamp: {health.get('timestamp', 'N/A')}

Workers Status:
{format_json(health.get('workers', {}))}""")
            return True
        else:
            log_error(f"HTTP {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        log_error(f"Cannot connect to {BASE_URL}")
        return False
    except Exception as e:
        log_error(f"Error: {str(e)}")
        return False

# ============================================================================
# CONFIG TEST
# ============================================================================
def test_config():
    log_test("TEST 2: APPLICATION CONFIG")
    
    try:
        log_info("Testing /api/config endpoint...")
        response = requests.get(f"{BASE_URL}/api/config", timeout=5)
        
        if response.status_code == 200:
            config = response.json()
            log_success("Config retrieved!")
            
            # API Key info
            api_key = config.get('google_maps_api_key', '')
            api_status = "Configured" if api_key else "Not Configured"
            api_preview = api_key[:25] + "..." if api_key else "N/A"
            
            print(f"""
Google Maps API: {api_status}
Key Preview: {api_preview}
Key Length: {len(api_key)} chars

Cameras in Config:
{format_json(config.get('camera_locations', {}))}""")
            return True
        else:
            log_error(f"HTTP {response.status_code}")
            return False
    except Exception as e:
        log_error(f"Error: {str(e)}")
        return False

# ============================================================================
# DIAGNOSTICS
# ============================================================================
def test_diagnostics():
    log_test("TEST 3: API DIAGNOSTICS")
    
    try:
        log_info("Testing /api/diagnostics endpoint...")
        response = requests.get(f"{BASE_URL}/api/diagnostics", timeout=5)
        
        if response.status_code == 200:
            diag = response.json()
            log_success("Diagnostics retrieved!")
            
            api_config = diag.get('google_maps_api_key', {})
            print(f"""
API Configuration:
  Configured: {api_config.get('configured', False)}
  Is Dummy: {api_config.get('is_dummy', False)}
  Key Preview: {api_config.get('key_preview', 'N/A')}
  Key Length: {api_config.get('key_length', 0)} chars

Directions API:
  Status: {diag.get('directions_api', {}).get('status', 'N/A')}
  Message: {diag.get('directions_api', {}).get('message', 'N/A')}

Recommendation:
  {diag.get('recommendation', 'N/A')}""")
            return True
        else:
            log_error(f"HTTP {response.status_code}")
            return False
    except Exception as e:
        log_error(f"Error: {str(e)}")
        return False

# ============================================================================
# CAMERAS LOCATIONS
# ============================================================================
def test_cameras_locations():
    log_test("TEST 4: CAMERAS LOCATIONS")
    
    try:
        log_info("Testing /api/cameras-locations endpoint...")
        response = requests.get(f"{BASE_URL}/api/cameras-locations", timeout=5)
        
        if response.status_code == 200:
            locations = response.json()
            log_success(f"Retrieved {len(locations)} camera locations!")
            
            print(f"\n{format_json(locations)}")
            return True
        else:
            log_error(f"HTTP {response.status_code}")
            return False
    except Exception as e:
        log_error(f"Error: {str(e)}")
        return False

# ============================================================================
# REAL-TIME DATA
# ============================================================================
def test_realtime_data(camera_id='depok_sp_jatijajar'):
    log_test(f"TEST 5: REAL-TIME DATA (Per-Second) - {camera_id}")
    
    try:
        log_info(f"Testing /api/second/{camera_id} endpoint...")
        response = requests.get(f"{BASE_URL}/api/second/{camera_id}", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            log_success(f"Retrieved {len(data)} per-second records!")
            
            print(f"\nSample Data (Last 3 records):")
            if data and len(data) > 0:
                for record in data[-3:]:
                    print(f"  {format_json(record)}")
            return True
        else:
            log_error(f"HTTP {response.status_code}")
            return False
    except Exception as e:
        log_error(f"Error: {str(e)}")
        return False

# ============================================================================
# MINUTE DATA
# ============================================================================
def test_minute_data(camera_id='depok_sp_jatijajar'):
    log_test(f"TEST 6: AGGREGATED DATA (Per-Minute) - {camera_id}")
    
    try:
        log_info(f"Testing /api/minute/{camera_id} endpoint...")
        response = requests.get(f"{BASE_URL}/api/minute/{camera_id}", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            log_success(f"Retrieved {len(data)} per-minute records!")
            
            print(f"\nSample Data (Last 3 records):")
            if data and len(data) > 0:
                for record in data[-3:]:
                    print(f"  {format_json(record)}")
            return True
        else:
            log_error(f"HTTP {response.status_code}")
            return False
    except Exception as e:
        log_error(f"Error: {str(e)}")
        return False

# ============================================================================
# DAILY DATA
# ============================================================================
def test_daily_data(camera_id='depok_sp_jatijajar'):
    log_test(f"TEST 7: DAILY SUMMARY - {camera_id}")
    
    try:
        log_info(f"Testing /api/daily/{camera_id} endpoint...")
        response = requests.get(f"{BASE_URL}/api/daily/{camera_id}", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            log_success(f"Retrieved {len(data)} daily records!")
            
            print(f"\nSample Data (Last 3 records):")
            if data and len(data) > 0:
                for record in data[-3:]:
                    print(f"  {format_json(record)}")
            return True
        else:
            log_error(f"HTTP {response.status_code}")
            return False
    except Exception as e:
        log_error(f"Error: {str(e)}")
        return False

# ============================================================================
# FORECAST
# ============================================================================
def test_forecast(camera_id='depok_sp_jatijajar'):
    log_test(f"TEST 8: TRAFFIC FORECAST - {camera_id}")
    
    try:
        log_info(f"Testing /api/forecast/{camera_id} endpoint...")
        response = requests.get(f"{BASE_URL}/api/forecast/{camera_id}", timeout=5)
        
        if response.status_code == 200:
            forecast = response.json()
            log_success("Forecast generated!")
            
            print(f"""
Date: {forecast.get('date', 'N/A')}
Total Forecast: {forecast.get('total', 0)} vehicles

Details:
{format_json(forecast.get('forecast', []))}""")
            return True
        else:
            log_error(f"HTTP {response.status_code}")
            return False
    except Exception as e:
        log_error(f"Error: {str(e)}")
        return False

# ============================================================================
# MAPS DATA
# ============================================================================
def test_maps_data():
    log_test("TEST 9: MAP DATA")
    
    try:
        log_info("Testing /api/maps-data endpoint...")
        response = requests.get(f"{BASE_URL}/api/maps-data", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            log_success("Map data retrieved!")
            
            print(f"\n{format_json(data)}")
            return True
        else:
            log_error(f"HTTP {response.status_code}")
            return False
    except Exception as e:
        log_error(f"Error: {str(e)}")
        return False

# ============================================================================
# ROUTES API
# ============================================================================
def test_routes():
    log_test("TEST 10: ROUTES / ROUTING ENGINE")
    
    try:
        log_info("Testing /api/routes endpoint...")
        
        route_request = {
            'origin': {
                'lat': -6.595714,
                'lng': 106.789572
            },
            'destination': {
                'lat': -6.604280,
                'lng': 106.796700
            }
        }
        
        print(f"\nRequest Payload:")
        print(format_json(route_request))
        
        response = requests.post(f"{BASE_URL}/api/routes", 
                                json=route_request, 
                                timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            log_success("Route calculated successfully!")
            
            if 'primary_route' in result:
                pr = result['primary_route']
                print(f"""
Primary Route:
  Distance: {pr.get('distance_text', 'N/A')}
  Duration: {pr.get('duration_text', 'N/A')}
  Traffic Status: {pr.get('traffic_status', 'N/A')}
  Polyline Length: {len(pr.get('polyline', ''))} chars
  Source: {result.get('source', 'unknown')}

Alternative Routes: {len(result.get('alternative_routes', []))}
Congestion Detected: {result.get('has_congestion', False)}

Full Response:
{format_json(result)[:500]}...""")
            return True
        else:
            log_error(f"HTTP {response.status_code}")
            print(response.text[:200])
            return False
    except Exception as e:
        log_error(f"Error: {str(e)}")
        return False

# ============================================================================
# DETECTION CONTROL
# ============================================================================
def test_detection_control(camera_id='depok_sp_jatijajar'):
    log_test(f"TEST 11: DETECTION CONTROL - {camera_id}")
    
    try:
        # Check status
        log_info(f"Checking detection status for {camera_id}...")
        response = requests.get(f"{BASE_URL}/api/detection/status/{camera_id}", timeout=5)
        
        if response.status_code == 200:
            status = response.json()
            log_success(f"Detection enabled: {status.get('detection_enabled', False)}")
            
            # Note: We won't actually start/stop to avoid disrupting the system
            log_warn("Note: Start/Stop endpoints available via POST requests")
            print(f"""
Detection Status: {status.get('detection_enabled', False)}
Camera ID: {status.get('camera_id', 'N/A')}

Available Actions:
  POST /api/detection/start/{camera_id}  - Start detection
  POST /api/detection/stop/{camera_id}   - Stop detection
  GET  /api/detection/status/{camera_id} - Get status""")
            return True
        else:
            log_error(f"HTTP {response.status_code}")
            return False
    except Exception as e:
        log_error(f"Error: {str(e)}")
        return False

# ============================================================================
# CSV ENDPOINTS
# ============================================================================
def test_csv_endpoints(camera_id='depok_sp_jatijajar'):
    log_test(f"TEST 12: CSV DOWNLOAD ENDPOINTS - {camera_id}")
    
    endpoints = [
        ('Daily', f'/csv/daily/{camera_id}'),
        ('Minute', f'/csv/minute/{camera_id}'),
        ('Second', f'/csv/second/{camera_id}'),
    ]
    
    all_success = True
    
    for name, endpoint in endpoints:
        try:
            log_info(f"Testing {name} CSV endpoint...")
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
            
            if response.status_code == 200:
                log_success(f"{name} CSV available ({len(response.content)} bytes)")
            else:
                log_error(f"{name} CSV - HTTP {response.status_code}")
                all_success = False
        except Exception as e:
            log_error(f"{name} CSV - Error: {str(e)}")
            all_success = False
    
    return all_success

# ============================================================================
# ALL CAMERAS DAILY
# ============================================================================
def test_all_cameras_daily():
    log_test("TEST 13: ALL CAMERAS DAILY DATA")
    
    try:
        log_info("Testing /api/all-cameras-daily endpoint...")
        response = requests.get(f"{BASE_URL}/api/all-cameras-daily", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            log_success(f"Retrieved data from {len(data)} cameras!")
            
            for camera_id, records in data.items():
                if records and len(records) > 0:
                    latest = records[-1]
                    print(f"  {camera_id}: {len(records)} records, Latest: {format_json(latest)[:100]}...")
            return True
        else:
            log_error(f"HTTP {response.status_code}")
            return False
    except Exception as e:
        log_error(f"Error: {str(e)}")
        return False

# ============================================================================
# PAGE ROUTES
# ============================================================================
def test_page_routes():
    log_test("TEST 14: PAGE ROUTES (HTML Templates)")
    
    pages = [
        ('Dashboard', '/'),
        ('Maps', '/maps'),
        ('Analysis', '/analysis'),
        ('Dashboard', '/dashboard'),
        ('Data', '/data'),
        ('Test Routes', '/test_routes'),
    ]
    
    all_success = True
    
    for name, route in pages:
        try:
            log_info(f"Testing {name} page ({route})...")
            response = requests.get(f"{BASE_URL}{route}", timeout=5)
            
            if response.status_code == 200 and 'html' in response.headers.get('content-type', '').lower():
                log_success(f"{name} page loaded ({len(response.content)} bytes)")
            else:
                log_error(f"{name} page - HTTP {response.status_code}")
                all_success = False
        except Exception as e:
            log_error(f"{name} page - Error: {str(e)}")
            all_success = False
    
    return all_success

# ============================================================================
# MAIN
# ============================================================================
def main():
    print(f"""{Back.CYAN}{Fore.BLACK}{'SMART TRAFFIC MONITORING SYSTEM - API TEST SUITE':^70}{Style.RESET_ALL}""")
    
    # List of all tests
    tests = [
        ('health', test_health),
        ('config', test_config),
        ('diagnostics', test_diagnostics),
        ('cameras-locations', test_cameras_locations),
        ('realtime', test_realtime_data),
        ('minute', test_minute_data),
        ('daily', test_daily_data),
        ('forecast', test_forecast),
        ('maps', test_maps_data),
        ('routes', test_routes),
        ('detection', test_detection_control),
        ('csv', test_csv_endpoints),
        ('all-cameras', test_all_cameras_daily),
        ('pages', test_page_routes),
    ]
    
    # Check if specific test is requested
    if len(sys.argv) > 1:
        test_name = sys.argv[1].lower()
        found = False
        
        for name, test_func in tests:
            if test_name in name or name in test_name:
                test_func()
                found = True
                break
        
        if not found:
            print(f"{Fore.RED}Test '{test_name}' not found{Style.RESET_ALL}")
            print(f"\nAvailable tests: {', '.join([t[0] for t in tests])}")
        return
    
    # Run all tests
    print(f"\n{Fore.YELLOW}Running {len(tests)} tests...{Style.RESET_ALL}\n")
    
    results = []
    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, passed))
            time.sleep(0.3)
        except Exception as e:
            results.append((name, False))
            log_error(f"Test exception: {str(e)}")
    
    # Summary
    print(f"\n{'='*70}")
    print(f"{Back.YELLOW}{Fore.BLACK}TEST SUMMARY{Style.RESET_ALL}")
    print(f"{'='*70}\n")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = f"{Fore.GREEN}✓ PASS{Style.RESET_ALL}" if result else f"{Fore.RED}✗ FAIL{Style.RESET_ALL}"
        print(f"  {name:.<30} {status}")
    
    print(f"\n{Fore.LIGHTBLUE_EX}Total: {passed}/{total} tests passed{Style.RESET_ALL}\n")

if __name__ == "__main__":
    main()
