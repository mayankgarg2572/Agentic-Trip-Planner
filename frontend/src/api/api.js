import axios from "axios";

import {API_BASE,AGENTIC_API_BASE } from './config'


const api = {

  searchLocation: (address) =>
    axios.post(`${API_BASE}/search-location`, { address }),

  saveMarkerLocation: (latitude, longitude) =>
    axios.post(`${API_BASE}/save-marker-location`, { latitude, longitude }),

  getItinerary: (reqObj) =>
    axios.post(`${AGENTIC_API_BASE}/chat`, reqObj),
    
  searchLocationMultiple: (address) =>{
    axios.post(`${API_BASE}/search-location-multiple`, { address })},
};

export default api;
