const express = require('express');
const router = express.Router();
const { getItinerary } = require('../controllers/itineraryController');

router.post('/get-itinerary', getItinerary);

module.exports = router;
