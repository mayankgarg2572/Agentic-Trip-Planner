const axios = require('axios');

const OPENAI_API_KEY = process.env.OPENAI_API_KEY;

const generateItinerary = async (prompt) => {
  try {
    const response = await axios.post(
      'https://api.openai.com/v1/chat/completions',
      {
        model: 'gpt-3.5-turbo',
        messages: [{ role: 'user', content: prompt }],
      },
      {
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${OPENAI_API_KEY}`,
        },
      }
    );

    const itinerary = response.data.choices[0].message.content.trim();
    return itinerary;
  } catch (error) {
    throw new Error(`Itinerary generation failed: ${error.message}`);
  }
};

module.exports = {
  generateItinerary,
};
