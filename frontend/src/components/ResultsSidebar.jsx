import React, { useContext, useState } from "react";
import { MapContext } from "../context/MapContext";
import { AppContext } from "../context/AppContext";
import styles from "./ResultsSidebar.module.css";

const ResultsSidebar = ({ onClose }) => {
  const {
    setMapCenter,
    selectedChatMarkers,
    // setSelectedChatMarkers,
    applySearchResultsToMap
  } = useContext(MapContext);

  const { searchResults, setSearchResults } = useContext(AppContext);

  const [resultType, setResultType] = useState("search");


  const removeResult = (idx) => {
    if (!Array.isArray(searchResults)) return;
    const updatedResults = [...searchResults];
    updatedResults.splice(idx, 1);
    setSearchResults(updatedResults);
    applySearchResultsToMap(updatedResults);
  };

  return (
    <div className={styles.resultSideBar}>
      <div className={styles.resultBarHeader}>
      <p>Search Results</p>
      <button onClick={onClose}>✖️</button>
      </div>
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
                ❌
              </button>
            </li>
          ))
          : selectedChatMarkers?.map((result, idx) => (
            <li key={idx} className={styles.resultLIstElement}>
              <div
                onClick={() =>
                  setMapCenter({ lat: result.lat, lng: result.lng })
                }
              >
                <strong>{result.source}</strong>: {result.address}
              </div>
              {/* <button
                onClick={() => {
                  const updatedResults = [...selectedChatMarkers];
                  updatedResults.splice(idx, 1);
                  setSelectedChatMarkers(updatedResults);
                }}
                className={styles.resultLIstElementCloseBtn}
              >
                ❌
              </button> */}
            </li>
          ))}
      </ul>
    </div>
  );
};

export default ResultsSidebar;
