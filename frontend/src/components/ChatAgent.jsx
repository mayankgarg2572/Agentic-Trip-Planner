// src/components/ChatAgent.jsx
import React, { useState, useContext } from "react";
import { MapContext } from "../context/MapContext";
import api from "../api/api";
import classes from "./ChatAgent.module.css";

const ChatAgent = () => {
  const [prompt, setPrompt] = useState("");
  const [chatHistory, setChatHistory] = useState([]);
  const [selectedChatIndex, setSelectedChatIndex] = useState(null);
  // const [table, setTable] = useState({});
  const { setSearchResults } = useContext(MapContext);

  const handleSend = async () => {
    if (!prompt.trim()) return;
    try {
      const res = await api.getItinerary(prompt);
      console.log("Result from Itinery:", res);
      // setResponse(res.data.itinerary.final_text);
      setSearchResults(res.data.itinerary.locations);

      const agentResponse = res.data.itinerary.final_text;
      setChatHistory((prev) => [
        ...prev,
        { user: prompt, agent: agentResponse },
      ]);
      setPrompt("");
      setSelectedChatIndex(chatHistory.length);
    } catch (error) {
      console.error("LLM Error:", error);
    }
  };


  const { selectedLocations } = useContext(MapContext);
 
  return (
    <div className={classes.chatAgentContainer}>
      <h4>Chat History</h4>
      <div className={classes.chatHistoryScroll}>
        <ul className={classes.chatList}>
          {chatHistory.map((chat, idx) => (
            <li
              key={idx}
              className={selectedChatIndex === idx ? classes.selected : ""}
              onClick={() => setSelectedChatIndex(idx)}
            >
              <div style={{ marginTop: "10px", whiteSpace: "pre-wrap" }}>
                <b>You:</b> {chat.user}
                <br />
                <b>Agent:</b> {chat.agent}
              </div>
            </li>
          ))}
        </ul>
      </div>
      <div className={classes.chatForm}>
        <textarea
          id = 'usmsg'
          name  = 'user-msg'
          rows={5}
          style={{ width: "100%" }}
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="Ask for itinerary"
        />
        <div style={{ margin: "10px 0", fontSize: "0.95em", color: "#555" }}>
          <b>Selected Locations:</b>{" "}
          {selectedLocations && selectedLocations.length > 0
            ? selectedLocations.map((obj)=>{
                return obj.title
            }).join(", ", )
            : "None"}
        </div>
        <button onClick={handleSend}>Send</button>
      </div>
    </div>
  );
};

export default ChatAgent;
