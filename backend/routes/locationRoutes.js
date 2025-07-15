const express = require('express');
const router = express.Router();
const {
  searchLocation,
  saveMarkerLocation,
  searchLocationMultiple,
} = require('../controllers/locationController');

router.post('/search-location', searchLocation);
router.post('/save-marker-location', saveMarkerLocation);
router.post('/search-location-multiple', searchLocationMultiple);

module.exports = router;
