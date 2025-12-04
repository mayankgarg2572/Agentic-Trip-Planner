import React, { useState, useContext } from 'react';
import { AppContext } from '../../context/AppContext';
import classes from './ChatInput.module.css';
import api from "../../api/api";
import { MapContext } from '../../context/MapContext';

const ChatInput = () => {
  const [prompt, setPrompt] = useState("");
  const { failedNewPrompt, saveNewPromptResponse, userMarkedLocations } = useContext(AppContext);
  const {  setSelectedChatMarkers } = useContext(MapContext);
  const [ loading, setLoading] = useState(false);

  const handleSend = async () => {
    if (!prompt.trim()) return;
    setLoading(true)
    try {
      let reqObj = {
        prompt: prompt,
        locations_Selected: userMarkedLocations?.map((loc) => ({
          title: loc.title,
          lat: loc.lat,
          lng: loc.lng,
        })),
      };
      
      // submitNewPrompt(prompt);
      const res = await api.getItinerary(reqObj);
      console.log("Result from Itinery:", res);
      saveNewPromptResponse(prompt, res)
      setSelectedChatMarkers(res?.itinerary?.locations)
    } catch (error) {
      console.error("LLM Error:", error);
      failedNewPrompt(prompt, error)
    }
    setLoading(false);
    setPrompt("");
  };

  return (
    <div className={classes.inputContainer}>
      <textarea
        className={classes.textarea}
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        placeholder="Share your trip plan here..."
        rows={3}
      />
      <button className={classes.sendButton} onClick={handleSend}>
        {loading ? <div className={classes.loader}></div> : "Send"}
      </button>
    </div>
  );
};

export default ChatInput;
