document.addEventListener('DOMContentLoaded', function() {
  // Initialize flight map if element exists
  const mapElement = document.getElementById('flight-map');
  
  if (mapElement) {
    // Create map
    const map = L.map('flight-map').setView([20, 0], 2);
    
    // Add OpenStreetMap tile layer
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
      maxZoom: 18
    }).addTo(map);
    
    // Check if we're dealing with a direct flight or connecting flight
    const flightId = mapElement.getAttribute('data-flight-id');
    const firstLegId = mapElement.getAttribute('data-first-leg');
    const secondLegId = mapElement.getAttribute('data-second-leg');
    
    if (flightId) {
      // Direct flight
      fetchDirectFlightPath(flightId, map);
    } else if (firstLegId && secondLegId) {
      // Connecting flight
      fetchConnectingFlightPath(firstLegId, secondLegId, map);
    }
  }
});

// Fetch direct flight path data and display on map
function fetchDirectFlightPath(flightId, map) {
  fetch(`/get_flight_path/${flightId}`)
    .then(response => response.json())
    .then(data => {
      drawDirectFlightPath(data, map);
      updateFlightInfo(data);
    })
    .catch(error => console.error('Error fetching flight path:', error));
}

// Fetch connecting flight path data and display on map
function fetchConnectingFlightPath(firstLegId, secondLegId, map) {
  fetch(`/get_connecting_flight_path/${firstLegId}/${secondLegId}`)
    .then(response => response.json())
    .then(data => {
      drawConnectingFlightPath(data, map);
      updateConnectingFlightInfo(data);
    })
    .catch(error => console.error('Error fetching connecting flight path:', error));
}

// Draw direct flight path on map
function drawDirectFlightPath(data, map) {
  // Extract coordinates
  const originCoords = data.origin.coords;
  const destCoords = data.destination.coords;
  
  // Create markers for origin and destination
  const originMarker = L.marker(originCoords, {
    title: data.origin.name
  }).addTo(map);
  
  const destMarker = L.marker(destCoords, {
    title: data.destination.name
  }).addTo(map);
  
  // Add popups
  originMarker.bindPopup(`<b>${data.origin.name}</b><br>Departure`).openPopup();
  destMarker.bindPopup(`<b>${data.destination.name}</b><br>Arrival`);
  
  // Create geodesic line
  const flightPath = L.geodesic([[originCoords, destCoords]], {
    weight: 3,
    opacity: 0.9,
    color: '#ff4081',
    steps: 50,
    dashArray: '5, 5'
  }).addTo(map);
  
  // Create airplane icon that moves along the path
  const airplaneIcon = L.divIcon({
    html: '<i class="fas fa-plane" style="color: #ffffff; transform: rotate(45deg);"></i>',
    className: 'airplane-icon',
    iconSize: [20, 20]
  });
  
  const airplane = L.marker([0, 0], {
    icon: airplaneIcon
  }).addTo(map);
  
  // Animate airplane along the path
  animateAirplane(airplane, originCoords, destCoords);
  
  // Fit bounds to show both markers
  const bounds = L.latLngBounds([originCoords, destCoords]);
  map.fitBounds(bounds, { padding: [50, 50] });
}

// Draw connecting flight path on map
function drawConnectingFlightPath(data, map) {
  // Extract coordinates
  const originCoords = data.origin.coords;
  const connectionCoords = data.connection.coords;
  const destCoords = data.destination.coords;
  
  // Create markers
  const originMarker = L.marker(originCoords, {
    title: data.origin.name
  }).addTo(map);
  
  const connectionMarker = L.marker(connectionCoords, {
    title: data.connection.name
  }).addTo(map);
  
  const destMarker = L.marker(destCoords, {
    title: data.destination.name
  }).addTo(map);
  
  // Add popups
  originMarker.bindPopup(`<b>${data.origin.name}</b><br>First Departure`);
  connectionMarker.bindPopup(`<b>${data.connection.name}</b><br>Connection (${Math.round(data.connection_time_hours)} hours layover)`).openPopup();
  destMarker.bindPopup(`<b>${data.destination.name}</b><br>Final Arrival`);
  
  // Create geodesic lines for both flight legs
  const firstLegPath = L.geodesic([[originCoords, connectionCoords]], {
    weight: 3,
    opacity: 0.9,
    color: '#ff4081',
    steps: 50,
    dashArray: '5, 5'
  }).addTo(map);
  
  const secondLegPath = L.geodesic([[connectionCoords, destCoords]], {
    weight: 3,
    opacity: 0.9,
    color: '#2196f3',
    steps: 50,
    dashArray: '5, 5'
  }).addTo(map);
  
  // Create airplane icons that move along the paths
  const airplaneIcon1 = L.divIcon({
    html: '<i class="fas fa-plane" style="color: #ff4081; transform: rotate(45deg);"></i>',
    className: 'airplane-icon',
    iconSize: [20, 20]
  });
  
  const airplaneIcon2 = L.divIcon({
    html: '<i class="fas fa-plane" style="color: #2196f3; transform: rotate(45deg);"></i>',
    className: 'airplane-icon',
    iconSize: [20, 20]
  });
  
  const airplane1 = L.marker([0, 0], {
    icon: airplaneIcon1
  }).addTo(map);
  
  const airplane2 = L.marker([0, 0], {
    icon: airplaneIcon2
  }).addTo(map);
  
  // Animate airplanes along the paths
  animateAirplane(airplane1, originCoords, connectionCoords);
  
  setTimeout(() => {
    animateAirplane(airplane2, connectionCoords, destCoords);
  }, 3000);
  
  // Fit bounds to show all markers
  const bounds = L.latLngBounds([originCoords, connectionCoords, destCoords]);
  map.fitBounds(bounds, { padding: [50, 50] });
}

// Animate airplane along flight path
function animateAirplane(airplane, start, end) {
  // Calculate intermediate points
  const numPoints = 100;
  const points = [];
  
  for (let i = 0; i <= numPoints; i++) {
    const t = i / numPoints;
    const lat = start[0] + (end[0] - start[0]) * t;
    const lng = start[1] + (end[1] - start[1]) * t;
    points.push([lat, lng]);
  }
  
  // Animate
  let i = 0;
  const intervalId = setInterval(() => {
    if (i >= points.length) {
      clearInterval(intervalId);
      return;
    }
    
    airplane.setLatLng(points[i]);
    i++;
  }, 50);
}

// Update flight information in the sidebar
function updateFlightInfo(data) {
  const infoElement = document.getElementById('flight-info');
  if (!infoElement) return;
  
  // Calculate intermediate points
  const distance = data.distance_km;
  const duration = data.duration_hours;
  
  infoElement.innerHTML = `
    <div class="map-info">
      <h4>Flight Details</h4>
      <p><strong>Flight:</strong> ${data.flight_number}</p>
      <p><strong>Route:</strong> ${data.origin.name} → ${data.destination.name}</p>
      
      <div class="map-route-details">
        <div class="map-detail">
          <div class="map-detail-label">Distance</div>
          <div class="map-detail-value">${distance} km</div>
        </div>
        <div class="map-detail">
          <div class="map-detail-label">Duration</div>
          <div class="map-detail-value">${Math.floor(duration)}h ${Math.round((duration % 1) * 60)}m</div>
        </div>
      </div>
    </div>
  `;
}

// Update connecting flight information in the sidebar
function updateConnectingFlightInfo(data) {
  const infoElement = document.getElementById('flight-info');
  if (!infoElement) return;
  
  // Calculate totals
  const totalDistance = data.first_leg.distance_km + data.second_leg.distance_km;
  const totalDuration = data.first_leg.duration_hours + data.connection_time_hours + data.second_leg.duration_hours;
  
  infoElement.innerHTML = `
    <div class="map-info">
      <h4>Connecting Flight Details</h4>
      <p><strong>Route:</strong> ${data.origin.name} → ${data.connection.name} → ${data.destination.name}</p>
      
      <div class="map-route-details">
        <div class="map-detail">
          <div class="map-detail-label">Total Distance</div>
          <div class="map-detail-value">${totalDistance} km</div>
        </div>
        <div class="map-detail">
          <div class="map-detail-label">Total Duration</div>
          <div class="map-detail-value">${Math.floor(totalDuration)}h ${Math.round((totalDuration % 1) * 60)}m</div>
        </div>
      </div>
      
      <hr>
      
      <h5>First Flight: ${data.first_leg.flight_number}</h5>
      <p>${data.origin.name} → ${data.connection.name}</p>
      <p>Duration: ${Math.floor(data.first_leg.duration_hours)}h ${Math.round((data.first_leg.duration_hours % 1) * 60)}m</p>
      
      <h5>Layover at ${data.connection.name}</h5>
      <p>Duration: ${Math.floor(data.connection_time_hours)}h ${Math.round((data.connection_time_hours % 1) * 60)}m</p>
      
      <h5>Second Flight: ${data.second_leg.flight_number}</h5>
      <p>${data.connection.name} → ${data.destination.name}</p>
      <p>Duration: ${Math.floor(data.second_leg.duration_hours)}h ${Math.round((data.second_leg.duration_hours % 1) * 60)}m</p>
    </div>
  `;
}
