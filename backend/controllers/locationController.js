const Location = require('../models/Location');
const { geocodeAddress, reverseGeocode, geocodeAddressMultiple  } = require('../services/mapService');

// Search Location: Address to Coordinates
const searchLocation = async (req, res) => {
  const { address } = req.body;
  console.log("Inside 'search_location' controller with args: address:", address);
  if (!address) {
    return res.status(400).json({ error: 'Address is required.' });
  }

  try {
    const { lat, lng, address: formattedAddress } = await geocodeAddress(address);

    const location = new Location({
      type: 'search',
      address: formattedAddress,
      coordinates: { lat, lng },
    });

    await location.save();

    res.json({ lat, lng, address: formattedAddress });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

// Save Marker Location: Coordinates to Address
const saveMarkerLocation = async (req, res) => {
  console.log("Inside saveMarkerLocation controller with args:", req.body);
  const { latitude, longitude } = req.body;

  if (latitude === undefined || longitude === undefined) {
    return res.status(400).json({ error: 'Latitude and longitude are required.' });
  }

  try {
    const address = await reverseGeocode(latitude, longitude);

    const location = new Location({
      type: 'marker',
      address,
      coordinates: { lat:latitude, lng:longitude },
    });

    await location.save();

    res.json({ message: 'Marker location saved successfully.' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

const searchLocationMultiple = async (req, res) => {
  const { address } = req.body;
  console.log("Inside 'search_location_multiple' controller with args: address:", address);
  if (!address) {
    return res.status(400).json({ error: 'Address is required.' });
  }

  try {
    const results = await geocodeAddressMultiple(address);
    res.json({ results });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

module.exports = {
  searchLocation,
  saveMarkerLocation,
  searchLocationMultiple,
};
