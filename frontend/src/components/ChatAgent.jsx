// src/components/ChatAgent.jsx
import React, { useState } from 'react';
import api from '../api/api';

const ChatAgent = () => {
  const [prompt, setPrompt] = useState('');
  const [response, setResponse] = useState('');

  const handleSend = async () => {
    try {
      const res = await api.getItinerary(prompt);
      setResponse(res.data.itinerary);
    } catch (error) {
      console.error('LLM Error:', error);
    }
  };

  return (
    <div style={{ padding: '10px', height: '100%',  overflowY: 'auto', }}>
      <textarea
        rows={5}
        style={{ width: '100%' }}
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        placeholder="Ask for itinerary"
      />
      <button onClick={handleSend}>Send</button>
      <div style={{ marginTop: '10px', whiteSpace: 'pre-wrap' }}>
        {response}
      </div>
    </div>
  );
};

export default ChatAgent;
