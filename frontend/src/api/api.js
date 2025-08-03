// src/api/api.js
import axios from "axios";


const API_BASE = process.env.API_BASE; // your backend URL
const AGENTIC_API_BASE = process.envAGENTIC_API_BASE;
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
