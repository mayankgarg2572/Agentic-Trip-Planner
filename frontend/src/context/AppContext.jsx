import React, { createContext, useState } from "react";

export const AppContext = createContext();

export const AppProvider = ({ children }) => {
  const [curSelectedPromptInd, setCurSelectedPromptInd] = useState(null);
  const [promptsChatResArr, setPromptsChatResArr] = useState([]);
  const [allChatItinerariesArr, setAllChatItinerariesArr] = useState([]);
  const [allChatAgentMarkersArr, setAllChatAgentMarkersArr] = useState([]);
  const [budgetTableArr, setBudgetTableArr] = useState([]);
  const [activeMobileTab, setActiveMobileTab] = useState("results");
  const [searchResults, setSearchResults] = useState([]);
  const openChat = (index) => {
    setCurSelectedPromptInd(index);
  };

  const closeChat = () => {
    setCurSelectedPromptInd(null);
  };

  const submitNewPrompt = (promptText) => {
    // 1. Append new prompt with loading state
    setPromptsChatResArr((prev) => [
      ...prev,
      { prompt: promptText, response: "Loading..." },
    ]);

    // 2. Initialize empty slots for this new chat index
    setAllChatItinerariesArr((prev) => [...prev, null]);
    setAllChatAgentMarkersArr((prev) => [...prev, []]);
    setBudgetTableArr((prev) => [...prev, null]);

    // 3. Set current index to this new chat
    setCurSelectedPromptInd(promptsChatResArr.length);
  }; 

  const saveNewPromptResponse = (promptText, resp) => {
    // 1. Append new prompt with loading state
    setPromptsChatResArr((prev) => [
      ...prev,
      { prompt: promptText, response: resp?.itinerary?.final_text },
    ]);

    // 2. Initialize empty slots for this new chat index resp?.itinerary?.location_to_mark_on_ui
    setAllChatItinerariesArr((prev) => [
      ...prev,
      resp?.api_result_itineraries?.features?.[0] ?? null,
    ]);
    setAllChatAgentMarkersArr((prev) => [...prev, resp?.itinerary?.locations]);
    setBudgetTableArr((prev) => [...prev, resp?.itinerary?.budget_table
]);

    // 3. Set current index to this new chat
    setCurSelectedPromptInd(promptsChatResArr.length);
    setActiveMobileTab("chat")
  };

  const failedNewPrompt = (promptText, err) => {
    // 1. Append new prompt with loading state
    setPromptsChatResArr((prev) => [
      ...prev,
      { prompt: promptText, response: "Something went wrong while processing your query:"+ err},
    ]);

    // 2. Initialize empty slots for this new chat index
    setAllChatItinerariesArr((prev) => [...prev, null]);
    setAllChatAgentMarkersArr((prev) => [...prev, []]);
    setBudgetTableArr((prev) => [...prev, null]);

    // 3. Set current index to this new chat
    setCurSelectedPromptInd(promptsChatResArr.length);
  };

  return (
    <AppContext.Provider
      value={{
        curSelectedPromptInd,
        setCurSelectedPromptInd,
        promptsChatResArr,
        setPromptsChatResArr,
        searchResults,
        setSearchResults,
        allChatItinerariesArr,
        setAllChatItinerariesArr,
        allChatAgentMarkersArr,
        setAllChatAgentMarkersArr,
        budgetTableArr,
        setBudgetTableArr,
        activeMobileTab,
        setActiveMobileTab,
        openChat,
        closeChat,
        submitNewPrompt,
        saveNewPromptResponse,
        failedNewPrompt
      }}
    >
      {children}
    </AppContext.Provider>
  );
};
