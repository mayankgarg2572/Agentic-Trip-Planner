import axios from "axios";

import { REACT_APP_SEARCH_API_BASE, REACT_APP_AGENTIC_API_BASE, REACT_APP_AGENTIC_API_STATUS, REACT_APP_SEARCH_API_BASE_STATUS } from "./config";

const api = {
  startServer: async () => {
    try{
      console.log("Agentic API Status:", REACT_APP_AGENTIC_API_STATUS)
      const agentResponse =  await axios.get(`${REACT_APP_AGENTIC_API_STATUS}/`)
      console.log("Agent status:", agentResponse.data)
    }
    catch(error){
      console.log("Some error in accessing the agent-server:", error)
      // throw error
    }

    try{
      console.log("Search API Base:", REACT_APP_SEARCH_API_BASE)
      const searchResponse = await axios.get(`${REACT_APP_SEARCH_API_BASE_STATUS}`)
      console.log("Search status:", searchResponse.data)
    }
    catch(err){
      console.log("Some error in accessing the search-server:", err)
    }
  },
  searchLocation: async (address) => {
    try {
      console.log("Search API Base:", REACT_APP_SEARCH_API_BASE)
      const response = await axios.post(`${REACT_APP_SEARCH_API_BASE}/search-location`, {
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
      console.log("Search API Base:", REACT_APP_SEARCH_API_BASE)
      const response = await axios.post(`${REACT_APP_SEARCH_API_BASE}/save-marker-location`, {
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
      console.log("Agentic API Base:", REACT_APP_AGENTIC_API_BASE)
      const response = await axios.post(`${REACT_APP_AGENTIC_API_BASE}/chat`, reqObj);
      return response.data;
    } catch (error) {
      console.error("Error in getItinerary:", error);
      throw error;
    }
  },

  searchLocationMultiple: async (address) => {
    try {
      console.log("Search API Base:", REACT_APP_SEARCH_API_BASE)
      const response = await axios.post(
        `${REACT_APP_SEARCH_API_BASE}/search-location-multiple`,
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
      console.log("Search API Base:", REACT_APP_SEARCH_API_BASE)
      const res  = await axios.get("https://ipapi.co/json/") // Can use http://ip-api.co/json/ but this is not easy for deploying as it is not https.
      
      return res.data
    } catch (error) {
      console.error("Error in Accessing the Locatio  for IP:", error);
      throw error;
    }
    
        
  }
};

export default api;
