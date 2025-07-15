// src/api/api.js
import axios from 'axios';

const API_BASE = 'http://localhost:5000/api'; // your backend URL

const api = {
  searchLocation: (address) => axios.post(`${API_BASE}/search-location`, { address }),
  saveMarkerLocation: (latitude, longitude) =>
    axios.post(`${API_BASE}/save-marker-location`, { latitude, longitude }),
  getItinerary: (prompt) => axios.post(`${API_BASE}/get-itinerary`, { prompt }),
  searchLocationMultiple: (address) => axios.post(`${API_BASE}/search-location-multiple`, { address }),
};

export default api;
