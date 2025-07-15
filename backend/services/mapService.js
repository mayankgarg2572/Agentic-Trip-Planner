const axios = require('axios');



// Forward Geocoding: Address to Coordinates
const geocodeAddress = async (address) => {
    const GEOAPIFY_API_KEY = process.env.GEOAPIFY_API_KEY;
  try {
    const encodedAddress = encodeURIComponent(address);
    console.log("API Key:", GEOAPIFY_API_KEY, " address:", address); // Debugging line to check API key
    const url = `https://api.geoapify.com/v1/geocode/search?text=${encodedAddress}&apiKey=${GEOAPIFY_API_KEY}`;

    const response = await axios.get(url);

    if (response.data.features.length === 0) {
      throw new Error('No results found for the provided address.');
    }

    const { lat, lon } = response.data.features[0].properties;
    const formattedAddress = response.data.features[0].properties.formatted;
    console.log("Geocoding response:", formattedAddress, "latitude:", lat, "longitude:", lon); // Debugging line to check the response
    return {
      lat,
      lng: lon,
      address: formattedAddress,
    };
  } catch (error) {
    throw new Error(`Geocoding failed: ${error.message}`);
  }
};

// Reverse Geocoding: Coordinates to Address (also corrected clearly)
const reverseGeocode = async (lat, lng) => {
    const GEOAPIFY_API_KEY = process.env.GEOAPIFY_API_KEY;
  try {
    const url = `https://api.geoapify.com/v1/geocode/reverse?lat=${lat}&lon=${lng}&apiKey=${GEOAPIFY_API_KEY}`;

    const response = await axios.get(url);

    if (response.data.features.length === 0) {
      throw new Error('No address found for the provided coordinates.');
    }

    const formattedAddress = response.data.features[0].properties.formatted;

    return formattedAddress;
  } catch (error) {
    throw new Error(`Reverse geocoding failed: ${error.message}`);
  }
};

// clearly new method for multiple search results
const geocodeAddressMultiple = async (address) => {
  console.log("Inside geocodeAddressMultiple service with args, address:", address);
  const GEOAPIFY_API_KEY = process.env.GEOAPIFY_API_KEY;
  try {
    const encodedAddress = encodeURIComponent(address);
    const url = `https://api.geoapify.com/v1/geocode/search?text=${encodedAddress}&apiKey=${GEOAPIFY_API_KEY}`;
    const response = await axios.get(url);

    const results = response.data.features.map(feature => ({
      address: feature.properties.formatted,
      lat: feature.properties.lat,
      lng: feature.properties.lon,
    }));

    console.log(" geocodeAddressMultiple service's results:", results); // Debugging line to check the response
    return results;
  } catch (error) {
    throw new Error(`Geocoding failed: ${error.message}`);
  }
};

module.exports = {
  geocodeAddress,
  reverseGeocode,
  geocodeAddressMultiple,
};
