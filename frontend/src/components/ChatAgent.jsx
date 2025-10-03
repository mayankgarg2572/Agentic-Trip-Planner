// src/components/ChatAgent.jsx
import React, { useState, useContext } from "react";
import { MapContext } from "../context/MapContext";
import api from "../api/api";
import classes from "./ChatAgent.module.css";

const ChatAgent = () => {
  const [prompt, setPrompt] = useState("");
  const [chatHistory, setChatHistory] = useState([]);
  const [selectedChatIndex, setSelectedChatIndex] = useState(null);
  const [loading, setLoading] = useState(false);
  // const [table, setTable] = useState({});
  // const {  } = useContext(MapContext);
  const { setSearchResults, selectedLocations, setItinerary } =
    useContext(MapContext);

  const handleSend = async () => {
    if (!prompt.trim()) return;
    setLoading(true);
    try {
      let reqObj = {
        prompt: prompt,
        locations_Selected: selectedLocations.map((loc) => ({
          title: loc.title,
          lat: loc.lat,
          lng: loc.lng,
        })),
      };

      const res = await api.getItinerary(reqObj);
      console.log("Result from Itinery:", res);

      setSearchResults(
        Array.isArray(res?.itinerary?.locations)
          ? res.itinerary.locations.map((loc) => {
              return {
                address: loc.address,
                lat: parseFloat(loc.lat),
                lng: parseFloat(loc.lng),
                source: "Agent",
              };
            })
          : []
      );

      const agentResponse = res?.itinerary?.final_text;

      setItinerary(res?.api_result_itineraries?.features?.[0] ?? null);
      setChatHistory((prev) => [
        ...prev,
        { user: prompt, agent: agentResponse },
      ]);
    } catch (error) {
      console.error("LLM Error:", error);
      setSearchResults([]);
      setChatHistory((prev) => [
        ...prev,
        {
          user: prompt,
          agent: "Something went wrong while processing your query",
        },
      ]);
    }
    setPrompt("");
    setSelectedChatIndex(chatHistory.length);
    setLoading(false);
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
            maxHeight: "38vh",
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
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="Share your trip plan here..."
          disabled={loading}
        />
        <div className={classes.selectedLocations}>
          <b>Selected Locations:</b>{" "}
          {selectedLocations && selectedLocations.length > 0
            ? selectedLocations.map((obj) => obj.title).join(", ")
            : "None"}
        </div>
        <button onClick={handleSend} disabled={loading}>
          {loading ? <div className={classes.loader}></div> : "Send"}
        </button>
      </div>
    </div>
  );
};

export default ChatAgent;
