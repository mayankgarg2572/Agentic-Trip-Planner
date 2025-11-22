import React, { createContext, useState } from "react";

export const AppContext = createContext();

export const AppProvider = ({ children }) => {
  const [curSelectedPromptInd, setCurSelectedPromptInd] = useState(0);
  const [promptsResArr, setPromptsResArr] = useState([]);
  const [mapItineries, setMapItineries] = useState([]);
  const [mapResultsArr, setMapResultsArr] = useState([]);
  const [budgetTableArr, setBudgetTableArr] = useState([]);

  return (
    <AppContext.Provider
      value={{
        curSelectedPromptInd,
        setCurSelectedPromptInd,
        promptsResArr,
        setPromptsResArr,
        mapItineries,
        setMapItineries,
        mapResultsArr,
        setMapResultsArr,
        budgetTableArr,
        setBudgetTableArr,
      }}
     >
      {children}
    </AppContext.Provider>
  );
};
