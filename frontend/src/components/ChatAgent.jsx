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
  // const {  } = useContext(MapContext);
  const { setSearchResults, selectedLocations } = useContext(MapContext);

  const handleSend = async () => {
    if (!prompt.trim()) return;
    try {

      let reqObj  = {prompt:prompt, locations_Selected: selectedLocations.map(loc => ({
        title: loc.title,
        lat: loc.lat,
        lng: loc.lng
      })) }
      console.log(reqObj)
      const res = await api.getItinerary(reqObj);
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


  
 
  // New ChatHistory component for better interaction
  const ChatHistory = ({
    chatHistory,
    selectedChatIndex,
    setSelectedChatIndex,
    classes,
  }) => (
    <div className={classes.chatHistoryScroll}>
      <ul className={classes.chatList}>
        {chatHistory.map((chat, idx) => (
          <li
            key={idx}
            className={selectedChatIndex === idx ? classes.selected : ""}
            onClick={() => setSelectedChatIndex(idx)}
            style={{ cursor: "pointer" }}
          >
            <div style={{ marginTop: "10px", whiteSpace: "pre-wrap" }}>
              <b>You:</b> {chat.user.slice(0, 60)}
              {chat.user.length > 60 ? "..." : ""}
              <br />
              <b>Agent:</b> {chat.agent.slice(0, 60)}
              {chat.agent.length > 60 ? "..." : ""}
            </div>
          </li>
        ))}
      </ul>
      {selectedChatIndex !== null && (
        <div
          className={classes.selectedChatDetail}
          style={{
            maxHeight: "200px",
            overflowY: "auto",
            marginTop: "10px",
            border: "1px solid #ddd",
            borderRadius: "6px",
            padding: "10px",
            background: "#fafafa",
          }}
        >
          <div style={{ whiteSpace: "pre-wrap" }}>
            <b>You:</b> {chatHistory[selectedChatIndex].user}
            <br />
            <b>Agent:</b> {chatHistory[selectedChatIndex].agent}
          </div>
        </div>
      )}
    </div>
  );

  return (
    <div className={classes.chatAgentContainer}>
      <h4>Chat History</h4>
      <ChatHistory
        chatHistory={chatHistory}
        selectedChatIndex={selectedChatIndex}
        setSelectedChatIndex={setSelectedChatIndex}
        classes={classes}
      />
      <div className={classes.chatForm}>
        <textarea
          id="usmsg"
          name="user-msg"
          rows={5}
          style={{ width: "100%" }}
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="Ask for itinerary"
        />
        <div style={{ margin: "10px 0", fontSize: "0.95em", color: "#555" }}>
          <b>Selected Locations:</b>{" "}
          {selectedLocations && selectedLocations.length > 0
            ? selectedLocations.map((obj) => obj.title).join(", ")
            : "None"}
        </div>
        <button onClick={handleSend}>Send</button>
      </div>
    </div>
  );
};

export default ChatAgent;
