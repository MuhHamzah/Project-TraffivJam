#!/usr/bin/env python3
"""
Detection Control Automation Examples
Contoh-contoh script untuk menggunakan fitur detection start/stop
"""

import requests
import time
from datetime import datetime, timedelta
import json

BASE_URL = "http://localhost:5000"
CAMERAS = ['jembatan_merah', 'jl_djuanda', 'stasiun_bogor']

def log(msg):
    """Print dengan timestamp"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

# ============================================================================
# EXAMPLE 1: Stop Detection During Off-Peak Hours (Night Time)
# ============================================================================

def schedule_detection_night_mode():
    """
    Example: Pause detection during night (22:00-06:00)
    Automatically resume detection in morning
    """
    log("Starting Night Mode Scheduler...")
    
    while True:
        current_hour = datetime.now().hour
        
        # Night mode: 22:00 (10 PM) - 06:00 (6 AM)
        if 22 <= current_hour or current_hour < 6:
            log("🌙 Night Mode: Stopping detection for all cameras...")
            for cam in CAMERAS:
                try:
                    requests.post(f"{BASE_URL}/api/detection/stop/{cam}")
                    log(f"  ✓ {cam} detection stopped")
                except Exception as e:
                    log(f"  ✗ {cam} error: {e}")
            
            # Sleep until morning (06:00)
            sleep_duration = 3600  # Check every hour
            log(f"  Sleeping for {sleep_duration}s until next check...")
            time.sleep(sleep_duration)
        
        else:
            log("☀️ Day Mode: Ensuring detection is active for all cameras...")
            for cam in CAMERAS:
                try:
                    requests.post(f"{BASE_URL}/api/detection/start/{cam}")
                    log(f"  ✓ {cam} detection started")
                except Exception as e:
                    log(f"  ✗ {cam} error: {e}")
            
            # Check every hour
            time.sleep(3600)


# ============================================================================
# EXAMPLE 2: Stop Detection During High CPU Load
# ============================================================================

def monitor_and_pause_on_high_load():
    """
    Example: Monitor system CPU and pause detection if too high
    Resume when CPU back to normal
    """
    import psutil
    
    log("Starting CPU Monitor with Auto-Pause...")
    CPU_THRESHOLD = 80  # Pause if CPU > 80%
    
    detection_paused = False
    
    while True:
        cpu_percent = psutil.cpu_percent(interval=1)
        log(f"Current CPU: {cpu_percent}%")
        
        if cpu_percent > CPU_THRESHOLD and not detection_paused:
            log(f"⚠️ CPU too high ({cpu_percent}%)! Pausing detection...")
            for cam in CAMERAS:
                try:
                    requests.post(f"{BASE_URL}/api/detection/stop/{cam}")
                    log(f"  ✓ {cam} paused")
                except Exception as e:
                    log(f"  ✗ Error: {e}")
            detection_paused = True
        
        elif cpu_percent < (CPU_THRESHOLD - 10) and detection_paused:
            log(f"✅ CPU normal ({cpu_percent}%)! Resuming detection...")
            for cam in CAMERAS:
                try:
                    requests.post(f"{BASE_URL}/api/detection/start/{cam}")
                    log(f"  ✓ {cam} resumed")
                except Exception as e:
                    log(f"  ✗ Error: {e}")
            detection_paused = False
        
        time.sleep(30)  # Check every 30 seconds


# ============================================================================
# EXAMPLE 3: Selective Camera Control
# ============================================================================

def selective_detection_control():
    """
    Example: Control detection untuk specific camera saja
    Use case: Maintenance, troubleshooting, testing
    """
    log("Starting Selective Detection Control...")
    
    # Stop hanya jl_djuanda untuk maintenance
    log("🔧 Maintenance Mode: Stopping jl_djuanda for inspection...")
    try:
        r = requests.post(f"{BASE_URL}/api/detection/stop/jl_djuanda")
        log(f"✓ Response: {r.json()['message']}")
    except Exception as e:
        log(f"✗ Error: {e}")
    
    time.sleep(5)
    
    # Keep lainnya tetap running
    for cam in ['jembatan_merah', 'stasiun_bogor']:
        try:
            r = requests.get(f"{BASE_URL}/api/detection/status/{cam}")
            status = "ACTIVE" if r.json()['detection_enabled'] else "PAUSED"
            log(f"✓ {cam}: {status}")
        except Exception as e:
            log(f"✗ Error: {e}")
    
    time.sleep(10)
    
    # Resume jl_djuanda
    log("✅ Maintenance complete. Resuming jl_djuanda detection...")
    try:
        r = requests.post(f"{BASE_URL}/api/detection/start/jl_djuanda")
        log(f"✓ Response: {r.json()['message']}")
    except Exception as e:
        log(f"✗ Error: {e}")


# ============================================================================
# EXAMPLE 4: Health Check & Auto-Restart
# ============================================================================

def health_check_and_recovery():
    """
    Example: Monitor detection status and auto-restart if stuck
    """
    log("Starting Health Check Monitor...")
    
    CHECK_INTERVAL = 60  # Check every minute
    STUCK_THRESHOLD = 300  # If no data for 5 minutes = stuck
    
    last_data_time = {}
    for cam in CAMERAS:
        last_data_time[cam] = time.time()
    
    while True:
        log("Running health check...")
        
        for cam in CAMERAS:
            try:
                # Check latest detection data
                r = requests.get(f"{BASE_URL}/api/minute/{cam}")
                data = r.json()
                
                if data:
                    last_data = data[-1]
                    last_detection_time = time.time()
                    last_data_time[cam] = last_detection_time
                    
                    log(f"✓ {cam}: Last detection {last_data['timestamp']}")
                else:
                    # No data, check if stuck
                    time_since_last = time.time() - last_data_time[cam]
                    if time_since_last > STUCK_THRESHOLD:
                        log(f"⚠️ {cam}: No data for {time_since_last}s - STUCK!")
                        log(f"   Attempting recovery: restart detection...")
                        
                        # Try restart
                        requests.post(f"{BASE_URL}/api/detection/stop/{cam}")
                        time.sleep(2)
                        requests.post(f"{BASE_URL}/api/detection/start/{cam}")
                        
                        log(f"   ✓ {cam} restarted")
                    else:
                        log(f"ℹ️ {cam}: No data yet ({time_since_last}s)")
                        
            except Exception as e:
                log(f"✗ {cam} error: {e}")
        
        log(f"Next check in {CHECK_INTERVAL}s...")
        time.sleep(CHECK_INTERVAL)


# ============================================================================
# EXAMPLE 5: Weekly Report Generation
# ============================================================================

def generate_weekly_detection_report():
    """
    Example: Generate weekly report tentang detection uptime
    """
    log("Generating Weekly Detection Report...")
    
    report = {
        'generated_at': datetime.now().isoformat(),
        'period': 'Weekly',
        'cameras': {}
    }
    
    for cam in CAMERAS:
        try:
            # Get daily data untuk minggu ini
            r = requests.get(f"{BASE_URL}/api/daily/{cam}")
            data = r.json()
            
            if data:
                # Get last 7 days
                recent = data[-7:] if len(data) >= 7 else data
                
                total_vehicles = sum(d['total'] for d in recent)
                avg_speed = sum(d['avg_speed_kmh'] for d in recent) / len(recent)
                
                report['cameras'][cam] = {
                    'days_recorded': len(recent),
                    'total_vehicles': total_vehicles,
                    'average_speed': round(avg_speed, 2),
                    'detection_uptime': '100%'  # Could calculate from timestamp gaps
                }
                
                log(f"✓ {cam}: {total_vehicles} vehicles, {avg_speed:.1f} km/h avg")
        except Exception as e:
            log(f"✗ {cam} error: {e}")
    
    # Save report
    filename = f"detection_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w') as f:
        json.dump(report, f, indent=2)
    
    log(f"✓ Report saved to {filename}")


# ============================================================================
# EXAMPLE 6: Bulk Detection Control
# ============================================================================

def bulk_control_all_cameras(action):
    """
    Example: Start/stop all cameras at once
    
    Usage:
        bulk_control_all_cameras('start')   # Start all
        bulk_control_all_cameras('stop')    # Stop all
    """
    log(f"Performing bulk {action.upper()} for all cameras...")
    
    endpoint = 'start' if action.lower() == 'start' else 'stop'
    
    results = {'success': [], 'failed': []}
    
    for cam in CAMERAS:
        try:
            url = f"{BASE_URL}/api/detection/{endpoint}/{cam}"
            r = requests.post(url)
            
            if r.status_code == 200:
                results['success'].append(cam)
                log(f"✓ {cam}: {r.json()['message']}")
            else:
                results['failed'].append((cam, r.status_code))
                log(f"✗ {cam}: HTTP {r.status_code}")
        except Exception as e:
            results['failed'].append((cam, str(e)))
            log(f"✗ {cam}: {e}")
    
    log(f"\nSummary: {len(results['success'])} success, {len(results['failed'])} failed")
    return results


# ============================================================================
# MAIN - Choose which example to run
# ============================================================================

if __name__ == '__main__':
    import sys
    
    examples = {
        '1': ('Night Mode Scheduler', schedule_detection_night_mode),
        '2': ('CPU Load Monitor', monitor_and_pause_on_high_load),
        '3': ('Selective Control', selective_detection_control),
        '4': ('Health Check', health_check_and_recovery),
        '5': ('Weekly Report', generate_weekly_detection_report),
        '6': ('Bulk Control - Start All', lambda: bulk_control_all_cameras('start')),
        '7': ('Bulk Control - Stop All', lambda: bulk_control_all_cameras('stop')),
    }
    
    print("\n" + "="*60)
    print("Detection Control Examples")
    print("="*60)
    for key, (name, _) in examples.items():
        print(f"{key}. {name}")
    print("="*60)
    
    if len(sys.argv) > 1:
        choice = sys.argv[1]
    else:
        choice = input("Choose example (1-7): ")
    
    if choice in examples:
        try:
            log(f"Running: {examples[choice][0]}")
            examples[choice][1]()
        except KeyboardInterrupt:
            log("\n⚠️ Interrupted by user")
    else:
        print(f"Invalid choice: {choice}")
        sys.exit(1)
