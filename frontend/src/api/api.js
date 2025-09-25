import axios from "axios";

import { API_BASE, AGENTIC_API_BASE } from "./config";

const api = {
  searchLocation: async (address) => {
    try {
      const response = await axios.post(`${API_BASE}/search-location`, {
        address,
      });
      return response.data;
    } catch (error) {
      console.error("Error in searchLocation:", error);
      throw error; // Re-throw the error if needed
    }
  },

  saveMarkerLocation: async (latitude, longitude) => {
    try {
      const response = await axios.post(`${API_BASE}/save-marker-location`, {
        latitude,
        longitude,
      });
      return response.data;
    } catch (error) {
      console.error("Error in saveMarkerLocation:", error);
      throw error;
    }
  },

  getItinerary: async (reqObj) => {
    try {
      const response = await axios.post(`${AGENTIC_API_BASE}/chat`, reqObj);
      return response.data;
    } catch (error) {
      console.error("Error in getItinerary:", error);
      throw error;
    }
  },

  searchLocationMultiple: async (address) => {
    try {
      const response = await axios.post(
        `${API_BASE}/search-location-multiple`,
        { address }
      );
      return response.data;
    } catch (error) {
      console.error("Error in searchLocationMultiple:", error);
      throw error;
    }
  },
};

export default api;
