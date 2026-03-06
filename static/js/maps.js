// ========== Initialize Map ==========
let map;
let marker;

document.addEventListener('DOMContentLoaded', () => {
    // Fetch map coordinates from API
    fetchMapData();
    
    // Initialize map
    setTimeout(initializeMap, 100);
});

async function fetchMapData() {
    try {
        const response = await fetch('/api/maps-data');
        const data = await response.json();
        
        // Store coordinates
        window.mapCoordinates = {
            lat: data.latitude,
            lng: data.longitude,
            name: data.name,
            address: data.address
        };
        
        // Update display
        const coordsDisplay = document.getElementById('coordsDisplay');
        if (coordsDisplay) {
            coordsDisplay.textContent = `${data.latitude}, ${data.longitude}`;
        }
    } catch (error) {
        console.error('Error fetching map data:', error);
        // Use default coordinates
        window.mapCoordinates = {
            lat: -6.595611,
            lng: 106.788194,
            name: 'Jembatan Merah - Traffic Monitoring',
            address: 'Jembatan Merah, Bogor Tengah, Kota Bogor, Jawa Barat'
        };
    }
}

function initializeMap() {
    // Use default if not loaded yet
    const coords = window.mapCoordinates || {
        lat: -6.595611,
        lng: 106.788194,
        name: 'Jembatan Merah - Traffic Monitoring',
        address: 'Jembatan Merah, Bogor Tengah, Kota Bogor, Jawa Barat'
    };
    
    // Create map
    map = L.map('map').setView([coords.lat, coords.lng], 15);
    
    // Add tile layer
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 19
    }).addTo(map);
    
    // Add marker
    marker = L.marker([coords.lat, coords.lng]).addTo(map)
        .bindPopup(`
            <div style="text-align: center;">
                <h3>${coords.name}</h3>
                <p><strong>Alamat:</strong> ${coords.address}</p>
                <p><strong>Koordinat:</strong> ${coords.lat}, ${coords.lng}</p>
                <p>🚨 Traffic Monitoring Active</p>
            </div>
        `)
        .openPopup();
    
    // Add circle for monitoring area
    L.circle([coords.lat, coords.lng], {
        color: 'red',
        fillColor: '#f03',
        fillOpacity: 0.2,
        radius: 500 // 500 meters
    }).addTo(map);
}

// Listen for tab changes and resize map
const tabBtns = document.querySelectorAll('.tab-btn');
if (tabBtns.length === 0) {
    // We're on maps page, wait for DOM to fully load
    setTimeout(() => {
        if (map) map.invalidateSize();
    }, 500);
}
