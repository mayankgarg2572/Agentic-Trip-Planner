import React, { useState, useContext, useEffect } from "react";
import MapView from "../components/MapView";
// import SearchBar from '../components/SearchBar';
import CustomSearchBar from "../components/CustomSearchBar";
import ResultsSidebar from "../components/ResultsSidebar";
import ChatAgent from "../components/ChatAgent";
import { MapContext } from "../context/MapContext";

const Home = () => {
  const [sidebarWidth, setSidebarWidth] = useState(400);
  const [isResultsSidebarOpen, setResultsSideBarOpen] = useState(true);
  const { searchResults } = useContext(MapContext);

  useEffect(() => {
    if (searchResults.length > 0) setResultsSideBarOpen(true);
  }, [searchResults]);

  return (
    <div style={{ display: "flex", height: "100vh" }}>
      <div style={{ flex: 1, position: "relative" }}>
        < CustomSearchBar />
        {!isResultsSidebarOpen && (
          <button
            style={{ position: "absolute", top: 10, left: 10, zIndex: 1000 }}
            onClick={() => setResultsSideBarOpen(true)}
          >
            🌏 Show Results
          </button>
        )}

        {isResultsSidebarOpen  && (
          <ResultsSidebar onClose={() => setResultsSideBarOpen(false)} />
        )}
        <MapView />
      </div>
      <div style={{ width: sidebarWidth, position: "relative" }}>
        <div
          style={{
            cursor: "col-resize",
            width: "5px",
            position: "absolute",
            left: 0,
            top: 0,
            height: "100%",
            backgroundColor: "#ccc",
            zIndex: 100,
          }}
          draggable="true"
          onDrag={(e) => {
            if (e.clientX > 300 && e.clientX < 800)
              setSidebarWidth(window.innerWidth - e.clientX);
          }}
        />
        <ChatAgent />
      </div>
    </div>
  );
};

export default Home;
