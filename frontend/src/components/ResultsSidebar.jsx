import React, { useContext, useState } from "react";
import { MapContext } from "../context/MapContext";
import styles from "./ResultsSidebar.module.css";

const ResultsSidebar = ({ onClose }) => {
  const {
    searchResults,
    setMapCenter,
    setSearchResults,
    agentMapResults,
    setAgentMapResults
  } = useContext(MapContext);

  const [resultType, setResultType] = useState("searchResult");

  if ((!Array.isArray(searchResults) || searchResults.length === 0) && (!Array.isArray(agentMapResults) || agentMapResults.length === 0)) return null;

  const removeResult = (idx) => {
    if (!Array.isArray(searchResults)) return;
    const updatedResults = [...searchResults];
    updatedResults.splice(idx, 1);
    setSearchResults(updatedResults);
  };

  return (
    <div className={styles.resultSideBar}>
      <p>Search Results</p>
      <button onClick={onClose}>✖️</button>
      <div className={styles.resultType}>
        <label>
          <input
            type="radio"
            checked={resultType === "search"}
            onChange={() => setResultType("search")}
          />
          Search Results
        </label>
        <label>
          <input
            type="radio"
            checked={resultType === "agent"}
            onChange={() => setResultType("agent")}
          />
          Agent Results
        </label>
      </div>
      <ul style={{ listStyle: "none", padding: 0 }}>
        {resultType === "search"
          ? searchResults?.map((result, idx) => (
              <li key={idx} className={styles.resultLIstElement}>
                <div
                  onClick={() =>
                    setMapCenter({ lat: result.lat, lng: result.lng })
                  }
                >
                  <strong>{result.source}</strong>: {result.address}
                </div>
                <button
                  onClick={() => removeResult(idx)}
                  className={styles.resultLIstElementCloseBtn}
                >
                  ❌ Remove
                </button>
              </li>
            ))
          : agentMapResults?.map((result, idx) => (
              <li key={idx} className={styles.resultLIstElement}>
                <div
                  onClick={() =>
                    setMapCenter({ lat: result.lat, lng: result.lng })
                  }
                >
                  <strong>{result.source}</strong>: {result.address}
                </div>
                <button
                  onClick={() => {
                    const updatedResults = [...agentMapResults];
                    updatedResults.splice(idx, 1);
                    setAgentMapResults(updatedResults);
                  }}
                  className={styles.resultLIstElementCloseBtn}
                >
                  ❌ Remove
                </button>
              </li>
            ))}
      </ul>
    </div>
  );
};

export default ResultsSidebar;
