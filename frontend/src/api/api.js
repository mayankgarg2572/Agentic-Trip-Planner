// src/api/api.js
import axios from "axios";

const API_BASE = "http://localhost:5000/api"; // your backend URL
const AGENTIC_API_BASE = "http://localhost:8000/api/v1/agent";
const api = {
  searchLocation: (address) =>
    axios.post(`${API_BASE}/search-location`, { address }),

  saveMarkerLocation: (latitude, longitude) =>
    axios.post(`${API_BASE}/save-marker-location`, { latitude, longitude }),

  getItinerary: (prompt) =>
    axios.post(`${AGENTIC_API_BASE}/chat`, {
      prompt,
      existing_markers: [],
    }),
    
  searchLocationMultiple: (address) =>
    axios.post(`${API_BASE}/search-location-multiple`, { address }),
};

export default api;
