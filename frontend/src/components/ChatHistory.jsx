import React from "react";
// import { MapContext, AppContext } from "../context/MapContext";

import classes from "./ChatAgent.module.css";


const ChatHistory = ({
    chatHistory,
    selectedChatIndex,
    setSelectedChatIndex
  }) => {

    return (
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
              {/* <br />
              <b>Agent:</b> {chat.agent.slice(0, 60)}
              {chat.agent.length > 60 ? "..." : ""} */}
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
  }

export default ChatHistory;