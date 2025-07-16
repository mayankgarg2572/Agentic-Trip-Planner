import React, { useState, useRef, useContext, useEffect } from "react";
import MapView from "../components/MapView";
import CustomSearchBar from "../components/CustomSearchBar";
import ResultsSidebar from "../components/ResultsSidebar";
import ChatAgent from "../components/ChatAgent";
import { MapContext } from "../context/MapContext";
import classes from "./Home.module.css";

const Home = () => {
  const [sidebarWidth, setSidebarWidth] = useState(400);
  const [isResizing, setIsResizing] = useState(false);
  const sidebarRef = useRef(null);
  const { searchResults } = useContext(MapContext);

  useEffect(() => {
    if (searchResults.length > 0) setResultsSideBarOpen(true);
  }, [searchResults]);

  // Mouse event handlers for resizing
  useEffect(() => {
    const handleMouseMove = (e) => {
      if (isResizing) {
        const newWidth = Math.min(Math.max(window.innerWidth - e.clientX, 300), 800);
        setSidebarWidth(newWidth);
      }
    };
    const handleMouseUp = () => setIsResizing(false);

    if (isResizing) {
      window.addEventListener("mousemove", handleMouseMove);
      window.addEventListener("mouseup", handleMouseUp);
    }
    return () => {
      window.removeEventListener("mousemove", handleMouseMove);
      window.removeEventListener("mouseup", handleMouseUp);
    };
  }, [isResizing]);

  const [isResultsSidebarOpen, setResultsSideBarOpen] = useState(true);

  return (
    <div className={classes.container}>
      <div className={classes.mapSection}>
        <CustomSearchBar />
        {!isResultsSidebarOpen && (
          <button
            style={{ position: "absolute", top: 10, left: 10, zIndex: 1000 }}
            onClick={() => setResultsSideBarOpen(true)}
          >
            🌏 Show Results
          </button>
        )}
        {isResultsSidebarOpen && (
          <ResultsSidebar onClose={() => setResultsSideBarOpen(false)} />
        )}
        <MapView />
      </div>
      <div
        ref={sidebarRef}
        className={classes.sidebar}
        style={{ width: sidebarWidth }}
      >
        <div
          className={classes.resizer}
          onMouseDown={() => setIsResizing(true)}
        />
        <ChatAgent />
      </div>
    </div>
  );
};

export default Home;