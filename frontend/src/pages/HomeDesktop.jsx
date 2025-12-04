import React, { useState, useEffect, useContext } from "react";
import MapView from "../components/MapView";
import CustomSearchBar from "../components/CustomSearchBar";
import ResultsSidebar from "../components/ResultsSidebar";
import ChatSidebar from "../components/ChatSidebar";
import classes from "./Home.module.css";
import { AppContext } from "../context/AppContext";


const HomeDesktop = () => {
    // --- Chat Sidebar Resizing Logic ---
    const [chatSidebarWidth, setChatSidebarWidth] = useState(() => {
        return Math.max(350, window.innerWidth * 0.25); // Default 25% or min 350px
    });
    const { searchResults } = useContext(AppContext);
    const [isResizing, setIsResizing] = useState(false);
    const [isResultsOpen, setIsResultsOpen] = useState(true);

    useEffect(() => {
        const handleMouseMove = (e) => {
            if (isResizing) {
                e.preventDefault();
                // Calculate new width: Total Width - Mouse X
                const newWidth = window.innerWidth - e.clientX;

                // Constraints
                const minWidth = 300;
                const maxWidth = window.innerWidth * 0.4; // Max 40%

                if (newWidth >= minWidth && newWidth <= maxWidth) {
                    setChatSidebarWidth(newWidth);
                }
            }
        };

        const handleMouseUp = () => {
            setIsResizing(false);
            document.body.style.userSelect = "";
        };

        if (isResizing) {
            document.body.style.userSelect = "none";
            window.addEventListener("mousemove", handleMouseMove);
            window.addEventListener("mouseup", handleMouseUp);
        }

        return () => {
            window.removeEventListener("mousemove", handleMouseMove);
            window.removeEventListener("mouseup", handleMouseUp);
        };
    }, [isResizing]);

    useEffect(() => {
    if (searchResults.length > 0) setIsResultsOpen(true);
  }, [searchResults]);

    return (
        <div className={classes.container}>
            {/* 1. Left Sidebar: Results */}
            {isResultsOpen ? (
                <div className={classes.resultsSidebar}>
                    <ResultsSidebar onClose={() => setIsResultsOpen(false)} />
                </div>
            ): (
                <div>
                    <button style={{ position: "absolute", top: 10, left: 10, zIndex: 1000 }} onClick={()=> setIsResultsOpen(true)}>Search Results🌏</button>
                     
                </div>
            )}

            {/* 2. Center: Map */}
            <div className={classes.mapSection}>
                <CustomSearchBar />
                {!isResultsOpen && (
                    <button
                        className={classes.showResultsBtn}
                        onClick={() => setIsResultsOpen(true)}
                    >
                        Show Results
                    </button>
                )}
                <MapView />
            </div>

            {/* 3. Right Sidebar: Chat */}
            <ChatSidebar
                width={chatSidebarWidth}
                onResizeStart={() => setIsResizing(true)}
            />
        </div>
    );
};

export default HomeDesktop;
