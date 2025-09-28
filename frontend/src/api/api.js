import axios from "axios";

import { API_BASE, AGENTIC_API_BASE, AGENTIC_API_STATUS } from "./config";

const api = {
  startServer: async () => {
    try{
      const response =  await axios.get(`${AGENTIC_API_STATUS}/`)
      
      if (response.data.status !== 'good') {
        console.log(response)
        const error = "Some issue arises in the server"
        throw error  
      }
    }
    catch(error){
      console.log("Some error in accessing the server:")
      throw error
    }
  },
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

  getLatLongForIP: async () => {
    try {
      const res  = await axios.get("https://ipapi.co/json/") // Can use http://ip-api.co/json/ but this is not easy for deploying as it is not https.
      
      return res.data
    } catch (error) {
      console.error("Error in Accessing the Locatio  for IP:", error);
      throw error;
    }
    
        
  }
};

export default api;
