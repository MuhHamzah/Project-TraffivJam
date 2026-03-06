import time
import os
import cv2
import threading
import numpy as np
import pandas as pd
from ultralytics import YOLO

# Camera configs include id, name, hls_url, pixels_per_meter (for speed estimation)
CAMERA_CONFIGS = [
    {"id":"depok_sp_jatijajar","name":"Depok SP Jatijajar","url":"https://dishub.depok.go.id/vi/20228068.m3u8","pixels_per_meter":50},
    {"id":"jl_djuanda","name":"JL. Djuanda","url":"https://restreamer3.kotabogor.go.id/memfs/f6b50f38-9184-418e-b3f9-05faaa9b387d.m3u8","pixels_per_meter":50},
    {"id":"cibadak_bogor","name":"Cibadak Kota Bogor","url":"https://restreamer6.kotabogor.go.id/memfs/19e925c3-f404-409e-9719-ea285acf9377.m3u8","pixels_per_meter":50},
]

MODEL = None
MODEL_LOCK = threading.Lock()

def load_model():
    global MODEL
    if MODEL is None:
        with MODEL_LOCK:
            if MODEL is None:
                print("[DETECTOR] Loading YOLOv8 hard model (better motorcycle accuracy)...")
                try:
                    # Fix for PyTorch 2.6: torch.load now requires weights_only=False for YOLO
                    import torch
                    original_load = torch.load
                    def patched_load(f, *args, **kwargs):
                        kwargs.setdefault('weights_only', False)
                        return original_load(f, *args, **kwargs)
                    torch.load = patched_load
                    
                    MODEL = YOLO('yolov8m.pt')  # Medium model for better accuracy, auto-downloads if not present
                    torch.load = original_load  # restore
                    print("[DETECTOR] YOLOv8 medium model loaded successfully")
                except Exception as e:
                    print(f"[DETECTOR] Error loading model: {e}")
                    raise
    return MODEL

VEHICLE_CLASSES = set(['car','motorcycle','motorbike','bus','truck','bicycle'])

# Detection confidence thresholds - EKSTRIM AGGRESSIVE
# Setiap deteksi apapun akan dihitung, bahkan yang confidence sangat rendah
CONFIDENCE_THRESHOLDS = {
    'car': 0.10,           # mobil: EKSTRIM RENDAH
    'motorcycle': 0.05,    # motor: EKSTRIM SANGAT RENDAH (akan catch semua)
    'motorbike': 0.05,     # sama dengan motorcycle
    'bike': 0.08,          # bike: ekstrim rendah
    'bicycle': 0.15,       # sepeda
    'bus': 0.20,           # bis: lebih permissive
    'truck': 0.20          # truk: lebih permissive
}

# Size constraints (pixel area) - EKSTRIM AGGRESSIVE
# Catch bahkan kendaraan yang SANGAT KECIL atau jauh
MIN_BOX_AREA = {
    'car': 400,            # mobil: EKSTRIM RENDAH
    'motorcycle': 100,     # motor: EKSTRIM SANGAT RENDAH - catch motor apapun
    'motorbike': 100,      # sama
    'bike': 80,            # bike: ekstrim rendah
    'bicycle': 80,         # sepeda: ekstrim rendah
    'bus': 800,            # bis: lebih permissive
    'truck': 800           # truk: lebih permissive
}

# Aspect ratio constraints - VERY PERMISSIVE untuk motorcycle
# Motor bisa dari berbagai sudut - depan (sempit), samping (normal), belakang (panjang)
ASPECT_RATIO_RANGE = {
    'car': (0.5, 2.2),           # mobil: normal
    'motorcycle': (0.20, 3.0),   # motor: SANGAT PERMISSIVE untuk catch semua angle
    'motorbike': (0.20, 3.0),    # sama
    'bike': (0.15, 2.5),         # bike: sangat permissive
    'bicycle': (0.15, 2.5),      # sepeda: sangat permissive
    'bus': (0.8, 2.0),           # bis: tetap normal
    'truck': (0.7, 2.5)          # truk: tetap normal
}

class SimpleTracker:
    def __init__(self):
        self.next_id = 1
        # id -> {centroid, last_time, prev_centroid, prev_time, class, speed_m_s}
        self.objects = {}

    def update(self, detections, pixels_per_meter=50):
        # detections: list of (name, (x,y)) atau (name, (x,y), {metadata})
        now = time.time()
        used = set()
        results = {}
        for detection_item in detections:
            # Handle both old format (name, centroid) and new format (name, centroid, metadata)
            if len(detection_item) == 3:
                name, centroid, metadata = detection_item
            else:
                name, centroid = detection_item
                metadata = {}
            
            best_id = None
            best_dist = 1e9
            
            # STRICT tracking distance - SANGAT ketat agar kendaraan berbeda tidak merge!
            # Ini adalah masalah utama: tracking distance terlalu besar membuat banyak kendaraan dihitung sebagai 1
            if name.lower() in ('motorcycle', 'motorbike', 'bike', 'bicycle'):
                max_distance = 25   # motorcycles: SANGAT KETAT (120->25) agar motor berbeda tidak merge
            elif name in ('bus', 'truck'):
                max_distance = 20   # bus/truck: KETAT SEKALI
            else:
                max_distance = 30   # cars: KETAT (60->30)
            
            for oid, obj in self.objects.items():
                if oid in used:
                    continue
                # Prefer matching to same class
                d = np.linalg.norm(np.array(obj['centroid']) - np.array(centroid))
                
                # KHUSUS MOTORCYCLE: sangat lenient dengan class mismatch
                # Sering terjadi motorcycle terdeteksi sebagai bike/motorbike/motorcycle (inconsistent label)
                if obj['class'].lower() != name.lower():
                    # Check apakah keduanya motorcycle-like class
                    motorcycle_classes = ('motorcycle', 'motorbike', 'bike', 'bicycle')
                    if name.lower() in motorcycle_classes and obj['class'].lower() in motorcycle_classes:
                        d = d * 1.0  # NO PENALTY - dianggap sama vehicle
                    elif name.lower() in motorcycle_classes or obj['class'].lower() in motorcycle_classes:
                        d = d * 1.1  # minimal penalty
                    else:
                        d = d * 1.5  # normal penalty untuk vehicle berbeda
                
                if d < best_dist and d < max_distance:
                    best_dist = d
                    best_id = oid
            
            if best_id is None:
                oid = self.next_id
                self.next_id += 1
                self.objects[oid] = {
                    'centroid': centroid, 
                    'last_time': now, 
                    'prev_centroid': None, 
                    'prev_time': None, 
                    'class': name, 
                    'speed_m_s': 0.0,
                    'conf': metadata.get('conf', 1.0)
                }
                results[oid] = self.objects[oid]
                used.add(oid)
            else:
                obj = self.objects[best_id]
                obj['prev_centroid'] = obj['centroid']
                obj['prev_time'] = obj['last_time']
                obj['centroid'] = centroid
                obj['last_time'] = now
                obj['class'] = name  # UPDATE class jika ada mismatch (normalisasi label)
                obj['conf'] = metadata.get('conf', obj.get('conf', 1.0))
                # compute speed if we have previous
                if obj['prev_time'] is not None and (now - obj['prev_time']) > 0:
                    dt = now - obj['prev_time']
                    disp_pixels = np.linalg.norm(np.array(obj['centroid']) - np.array(obj['prev_centroid']))
                    speed_pixels_s = disp_pixels / dt
                    # convert to m/s using pixels_per_meter
                    speed_m_s = speed_pixels_s / pixels_per_meter
                    obj['speed_m_s'] = speed_m_s
                results[best_id] = obj
                used.add(best_id)
        # cleanup old objects not updated recently
        remove = [oid for oid, obj in self.objects.items() if now - obj['last_time'] > 5]
        for oid in remove:
            del self.objects[oid]
        return results

class CameraWorker:
    # Global status tracker
    camera_status = {}  # {camera_id: {'status': 'online'/'offline', 'last_frame_time': timestamp, 'detection_enabled': bool}}
    # Global detection control
    detection_control = {}  # {camera_id: bool} - True = detection enabled, False = detection paused
    
    def __init__(self, cam_config):
        self.cam = cam_config
        self.running = True
        self.detection_enabled = True  # Individual flag untuk detection
        self.cap = None
        self.tracker = SimpleTracker()
        self.minute_buffer = []
        self.data_dir = os.path.join('data', self.cam['id'])
        os.makedirs(self.data_dir, exist_ok=True)
        self.minute_csv = os.path.join(self.data_dir, 'per_minute.csv')
        self.daily_csv = os.path.join(self.data_dir, 'daily.csv')
        self.second_csv = os.path.join(self.data_dir, 'per_second.csv')  # NEW: Per-second logging
        self.last_second = int(time.time())  # Track last recorded second
        # Initialize camera status
        CameraWorker.camera_status[self.cam['id']] = {'status': 'initializing', 'last_frame_time': None, 'last_update': time.time(), 'detection_enabled': True}
        CameraWorker.detection_control[self.cam['id']] = True
        if not os.path.exists(self.minute_csv):
            df = pd.DataFrame(columns=['timestamp','camera','cars','motorbikes','buses','trucks','avg_speed_kmh'])
            df.to_csv(self.minute_csv, index=False)
        if not os.path.exists(self.daily_csv):
            df = pd.DataFrame(columns=['date','camera','cars','motorbikes','buses','trucks','total','avg_speed_kmh'])
            df.to_csv(self.daily_csv, index=False)
        # NEW: Initialize per-second CSV untuk track setiap deteksi
        if not os.path.exists(self.second_csv):
            df = pd.DataFrame(columns=['timestamp','camera','cars','motorbikes','buses','trucks','total_detected'])
            df.to_csv(self.second_csv, index=False)

    def open_stream(self):
        url = self.cam['url']
        self.cap = cv2.VideoCapture(url)
    
    @classmethod
    def start_detection(cls, camera_id):
        """Enable detection for a specific camera"""
        cls.detection_control[camera_id] = True
        if camera_id in cls.camera_status:
            cls.camera_status[camera_id]['detection_enabled'] = True
        print(f"[{camera_id}] Detection STARTED")
    
    @classmethod
    def stop_detection(cls, camera_id):
        """Disable detection for a specific camera"""
        cls.detection_control[camera_id] = False
        if camera_id in cls.camera_status:
            cls.camera_status[camera_id]['detection_enabled'] = False
        print(f"[{camera_id}] Detection STOPPED")
    
    @classmethod
    def is_detection_enabled(cls, camera_id):
        """Check if detection is enabled for a camera"""
        return cls.detection_control.get(camera_id, True)

    def run(self):
        model = load_model()
        self.open_stream()
        last_minute = int(time.time()//60)
        last_second_record = int(time.time())  # Track per-second recording
        counts = {'car':0,'motorbike':0,'bus':0,'truck':0}
        second_counts = {'car':0,'motorbike':0,'bus':0,'truck':0}  # Buffer untuk second yang sedang berjalan
        counted_vehicles_this_minute = set()  # Track vehicle IDs already counted in this minute
        speed_samples = []
        reconnect_attempts = 0
        max_reconnect_attempts = 5
        
        while self.running:
            try:
                ret, frame = self.cap.read()
                if not ret:
                    reconnect_attempts += 1
                    # Update status to offline
                    CameraWorker.camera_status[self.cam['id']]['status'] = 'offline'
                    CameraWorker.camera_status[self.cam['id']]['last_update'] = time.time()
                    
                    if reconnect_attempts > max_reconnect_attempts:
                        print(f"[{self.cam['id']}] Max reconnection attempts reached, sleeping 30s...")
                        time.sleep(30)
                        reconnect_attempts = 0
                    print(f"[{self.cam['id']}] Reconnecting... (attempt {reconnect_attempts})")
                    time.sleep(2)
                    self.open_stream()
                    continue
                
                reconnect_attempts = 0  # reset on successful frame read
                # Update status to online
                CameraWorker.camera_status[self.cam['id']]['status'] = 'online'
                CameraWorker.camera_status[self.cam['id']]['last_frame_time'] = time.time()
                CameraWorker.camera_status[self.cam['id']]['last_update'] = time.time()
                
                # RUN DETECTION SETIAP FRAME (bukan setiap 1 detik!)
                # Ini memastikan NO VEHICLE MISSED, bahkan yang lewat cepat
                t0 = time.time()
                # Check if detection is enabled for this camera
                if CameraWorker.is_detection_enabled(self.cam['id']):
                    try:
                        # Primary detection - EKSTRIM SENSITIF untuk catch SETIAP kendaraan
                        # conf=0.05 adalah SANGAT rendah - akan menangkap setiap deteksi yang mungkin
                        res = model(frame, imgsz=320, verbose=False, conf=0.05, iou=0.2)
                        
                        # parse detections dengan filtering ketat
                        detections = []
                        motorcycle_detections = []  # separate list untuk motorcycle
                        
                        for r in res:
                            boxes = getattr(r, 'boxes', [])
                            for b in boxes:
                                try:
                                    cls = int(b.cls.cpu().numpy())
                                    conf = float(b.conf.cpu().numpy()) if hasattr(b.conf, 'cpu') else float(b.conf)
                                except Exception:
                                    cls = int(b.cls)
                                    conf = float(b.conf) if b.conf is not None else 0.5
                                
                                name = r.names.get(cls, '')
                                if name not in VEHICLE_CLASSES:
                                    continue
                                
                                # Check confidence threshold
                                min_conf = CONFIDENCE_THRESHOLDS.get(name, 0.5)
                                if conf < min_conf:
                                    continue
                                
                                # Extract box coordinates
                                xy = b.xyxy[0].cpu().numpy()
                                x1, y1, x2, y2 = xy
                                width = x2 - x1
                                height = y2 - y1
                                box_area = width * height
                                
                                # Check minimum box area
                                min_area = MIN_BOX_AREA.get(name, 500)
                                if box_area < min_area:
                                    continue
                                
                                # Check aspect ratio
                                if height > 0:
                                    aspect_ratio = width / height
                                    min_ar, max_ar = ASPECT_RATIO_RANGE.get(name, (0.2, 3.0))
                                    if aspect_ratio < min_ar or aspect_ratio > max_ar:
                                        continue
                                
                                # Calculate center
                                cx = (x1 + x2) / 2
                                cy = (y1 + y2) / 2
                                
                                # Store with additional info for better tracking
                                detection_info = (name, (cx, cy), {'box_area': box_area, 'conf': conf, 'width': width, 'height': height})
                                
                                # Separate motorcycles untuk special handling
                                if name.lower() in ('motorcycle', 'motorbike'):
                                    motorcycle_detections.append(detection_info)
                                else:
                                    detections.append(detection_info)
                        
                        # Combine detections (motorcycles prioritized if multiple detections at same location)
                        detections.extend(motorcycle_detections)
                        
                        mapped = self.tracker.update(detections, pixels_per_meter=self.cam.get('pixels_per_meter', 50))
                        
                        # Count UNIQUE tracked vehicles ONCE per minute!
                        # Only count vehicles the first time they appear in this minute
                        frame_counts = {'car':0,'motorbike':0,'bus':0,'truck':0}
                        
                        # Count based on tracked object IDs (unique vehicles in this frame)
                        for oid, obj in mapped.items():
                            clsname = obj['class'].lower()
                            
                            # Only count this vehicle if we haven't counted it yet this minute
                            if oid not in counted_vehicles_this_minute:
                                # Count based on vehicle class
                                if clsname == 'car':
                                    counts['car'] += 1
                                    frame_counts['car'] += 1
                                elif clsname in ('motorcycle', 'motorbike'):
                                    counts['motorbike'] += 1
                                    frame_counts['motorbike'] += 1
                                elif clsname in ('bike', 'bicycle'):
                                    counts['motorbike'] += 1
                                    frame_counts['motorbike'] += 1
                                elif clsname == 'bus':
                                    counts['bus'] += 1
                                    frame_counts['bus'] += 1
                                elif clsname == 'truck':
                                    counts['truck'] += 1
                                    frame_counts['truck'] += 1
                                
                                # Mark this vehicle as counted in this minute
                                counted_vehicles_this_minute.add(oid)
                        
                        # Accumulate ke second_counts (buffer untuk detik ini)
                        for vehicle_type in frame_counts:
                            second_counts[vehicle_type] += frame_counts[vehicle_type]
                        
                        # Collect speed samples dari tracked objects
                        # Only count meaningful speed (>0.5 km/h to avoid noise)
                        for oid, obj in mapped.items():
                            sp = obj.get('speed_m_s', 0.0)
                            if sp is not None:
                                speed_kmh = sp * 3.6
                                # Only add if speed is meaningful (>0.5 km/h) to avoid zero-speed noise
                                if speed_kmh > 0.5:
                                    speed_samples.append(speed_kmh)
                    except Exception as e:
                        print(f"[{self.cam['id']}] Detection error: {e}")
                else:
                    # Detection disabled - just keep camera connection alive
                    pass
                
                # CHECK per-second boundary and record setiap detik
                current_second = int(time.time())
                if current_second != last_second_record:
                    # Detik baru - record data dari second_counts dan reset
                    timestamp_sec = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(last_second_record))
                    total_detected = sum(second_counts.values())
                    
                    row_sec = {
                        'timestamp': timestamp_sec,
                        'camera': self.cam['id'],
                        'cars': second_counts['car'],
                        'motorbikes': second_counts['motorbike'],
                        'buses': second_counts['bus'],
                        'trucks': second_counts['truck'],
                        'total_detected': total_detected
                    }
                    try:
                        df_sec = pd.DataFrame([row_sec])
                        df_sec.to_csv(self.second_csv, mode='a', header=False, index=False)
                        # Log setiap detik yang ada deteksi
                        if total_detected > 0:
                            print(f"[{self.cam['id']}] {timestamp_sec} - Per-second: 🚗:{second_counts['car']} 🏍️:{second_counts['motorbike']} 🚌:{second_counts['bus']} 🚚:{second_counts['truck']} (Total:{total_detected})")
                    except Exception as e:
                        print(f"[{self.cam['id']}] Error writing per-second CSV: {e}")
                    
                    # Reset second_counts untuk second berikutnya
                    second_counts = {'car':0,'motorbike':0,'bus':0,'truck':0}
                    last_second_record = current_second
                
                # minute aggregation
                current_minute = int(time.time()//60)
                if current_minute != last_minute:
                    # compute average speed
                    avg_speed = np.mean(speed_samples) if len(speed_samples)>0 else 0.0
                    timestamp = time.strftime('%Y-%m-%d %H:%M:00', time.localtime(last_minute*60))
                    
                    # Log detections dengan breakdown lebih detail untuk motorcycle
                    total = counts['car'] + counts['motorbike'] + counts['bus'] + counts['truck']
                    # Highlight motorcycle detection untuk monitoring
                    bike_emoji = "🏍️" if counts['motorbike'] > 0 else ""
                    print(f"[{self.cam['id']}] {timestamp} - Cars:{counts['car']}, Bikes:{counts['motorbike']} {bike_emoji}, Buses:{counts['bus']}, Trucks:{counts['truck']} (Total:{total}, Speed:{avg_speed:.1f}km/h)")
                    
                    row = {'timestamp':timestamp,'camera':self.cam['id'],'cars':counts['car'],'motorbikes':counts['motorbike'],'buses':counts['bus'],'trucks':counts['truck'],'avg_speed_kmh':round(avg_speed,2)}
                    try:
                        df = pd.DataFrame([row])
                        df.to_csv(self.minute_csv, mode='a', header=False, index=False)
                        # update daily
                        self.update_daily(row)
                    except Exception as e:
                        print(f"[{self.cam['id']}] Error writing CSV: {e}")
                    
                    # reset untuk minute berikutnya
                    counts = {'car':0,'motorbike':0,'bus':0,'truck':0}
                    counted_vehicles_this_minute = set()  # Reset vehicles yang sudah di-count
                    speed_samples = []
                    last_minute = current_minute
                
                # throttle
                elapsed = time.time()-t0
                time.sleep(max(0.1, 1.0-elapsed))
                
            except Exception as e:
                print(f"[{self.cam['id']}] Unexpected error: {e}")
                time.sleep(5)

    def update_daily(self, row):
        import pandas as pd
        date = row['timestamp'].split(' ')[0]
        try:
            df = pd.read_csv(self.daily_csv)
            # Ensure required columns exist
            if 'camera' not in df.columns:
                df['camera'] = self.cam['id']
            if 'avg_speed_kmh' not in df.columns:
                df['avg_speed_kmh'] = 0.0
            if 'total' not in df.columns:
                df['total'] = 0
        except Exception:
            df = pd.DataFrame(columns=['date','camera','cars','motorbikes','buses','trucks','total','avg_speed_kmh'])
        
        # Safely handle mask creation
        if 'camera' in df.columns and len(df) > 0:
            mask = (df['date']==date) & (df['camera']==self.cam['id'])
        elif len(df) > 0:
            mask = (df['date']==date)
        else:
            mask = pd.Series([False] * len(df))
        if mask.any():
            idx = df[mask].index[0]
            df.at[idx,'cars'] += row['cars']
            df.at[idx,'motorbikes'] += row['motorbikes']
            df.at[idx,'buses'] += row['buses']
            df.at[idx,'trucks'] += row['trucks']
            df.at[idx,'total'] = df.at[idx,'cars']+df.at[idx,'motorbikes']+df.at[idx,'buses']+df.at[idx,'trucks']
            # weighted avg speed
            prev_avg = df.at[idx,'avg_speed_kmh']
            df.at[idx,'avg_speed_kmh'] = round((prev_avg+row['avg_speed_kmh'])/2,2)
        else:
            new = {
                'date': date,
                'camera': self.cam['id'],
                'cars': row['cars'],
                'motorbikes': row['motorbikes'],
                'buses': row['buses'],
                'trucks': row['trucks'],
                'total': row['cars']+row['motorbikes']+row['buses']+row['trucks'],
                'avg_speed_kmh': row['avg_speed_kmh']
            }
            # Use append method instead of concat for better compatibility
            new_row = pd.DataFrame([new])
            df = pd.concat([df, new_row], ignore_index=True)
        
        df.to_csv(self.daily_csv, index=False)
