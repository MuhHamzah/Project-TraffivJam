# Smart Traffic Monitoring System

This application provides a simple web interface powered by Flask for monitoring traffic from CCTV cameras. It performs vehicle detection (cars, bikes, buses, trucks) using YOLOv8 models and stores aggregated statistics to CSV files. The front-end includes maps, dashboards, and analysis tools that can leverage Google Maps or open-source alternatives.

---

## Features

- Real-time vehicle detection using YOLOv8
- Multiple camera support with location configuration
- Data export (per-second, per-minute, daily CSV)
- Trend forecasting and health/status API
- Interactive maps with Google Maps support (fallback to Leaflet/OSRM)
- Simple UI: dashboard, analysis, data views, and routing tests
- Designed for easy deployment with provided setup/run scripts

---

## Prerequisites

- Python 3.9 or newer
- Git (for cloning)
- Optional: Google Cloud account for Maps API key

---

## Installation

1. **Clone repository**
   ```sh
   git clone https://github.com/MuhHamzah/Project-TraffivJam.git
   cd Project-TraffivJam
   ```

2. **Run setup script**
   - **Linux / macOS**
     ```sh
     ./setup.sh
     ```
   - **Windows (PowerShell or CMD)**
     ```bat
     setup.bat
     ```
   This will create a Python virtual environment, install dependencies from `requirements.txt`, and create initial `data/` directories.

3. **Configure application**
   - Open `config.py` and replace `GOOGLE_MAPS_API_KEY` with your API key (see below).
   - You may also adjust detection parameters (interval, frame size, thresholds) in `config.py`.
   - If you prefer not to use Google Maps, leave the key as `'YOUR_API_KEY_HERE'`; the app will fallback to Leaflet/OSRM.


---

## Google Maps API Key Setup (optional but recommended)

1. Go to [Google Cloud Console - Credentials](https://console.cloud.google.com/apis/credentials)
2. Create a new API Key or use an existing one.
3. Enable the following APIs in your project:
   - Maps JavaScript API
   - Directions API
   - Maps Embed API
   - Maps Static API
   - Roads API (optional)
4. (Optional) Restrict the key by HTTP referrer or IP.
5. Paste the key into `config.py` and optionally in `templates/maps.html` if hard-coded.

---

## Running the Application

### Linux / macOS

```sh
source venv/bin/activate     # activate virtual environment
export FLASK_APP=app.py
export FLASK_ENV=production
python -m flask run --host=0.0.0.0 --port=5000
```

or simply run:

```sh
./run.sh
```

### Windows

```bat
call venv\Scripts\activate.bat
set FLASK_APP=app.py
set FLASK_ENV=production
python -m flask run --host=0.0.0.0 --port=5000
```

or run the provided batch file:

```bat
run.bat
```

Visit the application in your browser at `http://localhost:5000`.

---

## Directory Structure

```
├── app.py                # main Flask application
├── config.py             # configuration settings
├── detector.py           # YOLO-based detection and camera worker
├── routes_handler.py     # Google Maps/route helpers
├── requirements.txt      # Python dependencies
├── templates/            # HTML templates used by Flask
├── static/               # JS/CSS assets
├── data/                 # generated CSV output per camera
├── run.sh / run.bat      # convenience scripts
└── setup.sh / setup.bat  # environment setup scripts
```

After running detections, each camera generates a subdirectory under `data/` containing:
- `per_second.csv` — raw per-second detection log
- `per_minute.csv` — aggregated counts per minute
- `daily.csv` — daily summary counts

---

## API Endpoints

The app exposes several JSON and CSV endpoints. A few examples:

- `/api/config` – returns configuration (maps key, camera locations)
- `/api/minute/<camera_id>` – per-minute data for a camera
- `/csv/daily/<camera_id>` – download daily CSV for camera
- `/api/health` – service health and worker status

Consult `app.py` for full list of routes and behaviors.

---

## Customization

- Add or modify cameras by editing `detector.CAMERA_CONFIGS` in `detector.py`.
- Adjust detection/tracking parameters in `config.py`.
- Extend templates or static assets to modify UI.

---

## Troubleshooting

- Ensure your virtual environment is activated when installing dependencies or running the server.
- If you see import errors, run `pip install -r requirements.txt` again.
- For issues with Google Maps, verify your API key and enabled APIs.

---

## License & Contribution

This repository is maintained as a personal project. Feel free to fork or contribute improvements via pull requests.

---

Enjoy monitoring traffic! 🚦
