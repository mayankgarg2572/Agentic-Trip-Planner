const { generateItinerary } = require('../services/llmService');

const getItinerary = async (req, res) => {
  const { prompt } = req.body;

  if (!prompt) {
    return res.status(400).json({ error: 'Prompt is required.' });
  }

  try {
    const itinerary = await generateItinerary(prompt);
    res.json({ itinerary });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

module.exports = {
  getItinerary,
};
