import React, { useState, useRef, useContext, useEffect } from "react";
import MapView from "../components/MapView";
import CustomSearchBar from "../components/CustomSearchBar";
import ResultsSidebar from "../components/ResultsSidebar";
import ChatAgent from "../components/ChatAgent";
import { MapContext } from "../context/MapContext";
import classes from "./Home.module.css";

const Home = () => {
  const [sidebarWidth, setSidebarWidth] = useState(() => {
    // Dynamically set the initial sidebar width based on the screen size
    if (window.innerWidth <= 768) {
      return window.innerWidth ; // 40% of the screen width for mobile/tablets
    }
    return window.innerWidth * 0.1; // 25% of the screen width for desktops
  });
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
        // const newWidth = Math.min(Math.max(window.innerWidth - e.clientX, 300), 800);
        // setSidebarWidth(newWidth);
        e.preventDefault(); // Prevent default scrolling behavior
      const newWidth = Math.min(
        Math.max(window.innerWidth - e.clientX, window.innerWidth * 0.1), // Minimum width of 300px
        window.innerWidth * 0.8 // Maximum width of 80% of the viewport
      );
      setSidebarWidth(newWidth);
      }
    };
    const handleTouchMove = (e) => {
    if (isResizing) {
      e.preventDefault(); // Prevent default scrolling behavior
      const touch = e.touches[0];
      const newWidth = Math.min(
        Math.max(window.innerWidth - touch.clientX, 300), // Minimum width of 300px
        window.innerWidth * 0.8 // Maximum width of 80% of the viewport
      );
      setSidebarWidth(newWidth);
    }
  };
  const handleTouchEnd = () => {
    setIsResizing(false)
    document.body.style.userSelect = ""; // Re-enable text selection
  };
    const handleMouseUp = () => {
      setIsResizing(false)
      document.body.style.userSelect = ""; // Re-enable text selection
    };

    if (isResizing) {
      document.body.style.userSelect = "none"; 
      window.addEventListener("mousemove", handleMouseMove);
      window.addEventListener("mouseup", handleMouseUp);
      window.addEventListener("touchmove", handleTouchMove, { passive: false });
    window.addEventListener("touchend", handleTouchEnd);
    }
    return () => {
      window.removeEventListener("mousemove", handleMouseMove);
      window.removeEventListener("mouseup", handleMouseUp);
      window.removeEventListener("touchmove", handleTouchMove);
    window.removeEventListener("touchend", handleTouchEnd);
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
        // ref={sidebarRef}
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