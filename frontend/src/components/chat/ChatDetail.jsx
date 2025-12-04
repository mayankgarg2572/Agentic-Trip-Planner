import React, { useContext, useEffect } from 'react';
import { AppContext } from '../../context/AppContext';
import { MapContext } from '../../context/MapContext';
import classes from './ChatDetail.module.css';

const ChatDetail = () => {
  const { 
    curSelectedPromptInd, 
    promptsChatResArr, 
    closeChat,
    allChatItinerariesArr,
    allChatAgentMarkersArr 
  } = useContext(AppContext);

  const { loadChatIntoMap, clearChatFromMap } = useContext(MapContext);

  const chatData = promptsChatResArr[curSelectedPromptInd];
  const itinerary = allChatItinerariesArr[curSelectedPromptInd];
  const markers = allChatAgentMarkersArr[curSelectedPromptInd];

  const handleBack = () => {
    clearChatFromMap();
    closeChat();
  };

  const handleShowItinerary = () => {
    if (itinerary && markers) {
      loadChatIntoMap(itinerary, markers);
    }
  };

  if (!chatData) return null;

  return (
    <div className={classes.detailContainer}>
      <div className={classes.header}>
        <button onClick={handleBack} className={classes.backButton}>
          ← Back
        </button>
        <h3>Trip Details</h3>
      </div>

      <div className={classes.messagesArea}>
        <div className={classes.messageBubble + ' ' + classes.userBubble}>
          <strong>You:</strong>
          <p>{chatData.prompt}</p>
        </div>
        <div className={classes.messageBubble + ' ' + classes.agentBubble}>
          <strong>Agent:</strong>
          <p style={{whiteSpace: 'pre-wrap'}}>{chatData.response}</p>
        </div>
      </div>

      <div className={classes.actionsArea}>
        <button 
          onClick={handleShowItinerary} 
          className={classes.actionButton}
          disabled={!itinerary}
        >
          Show Itinerary on Map
        </button>
        <button className={classes.actionButton}>
          Show Expenses
        </button>
      </div>
    </div>
  );
};

export default ChatDetail;
