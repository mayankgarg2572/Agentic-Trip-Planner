
import React, { createContext, useState } from "react";

export const MapContext = createContext();

export const MapProvider = ({ children }) => {
  const [mapCenter, setMapCenter] = useState({ lat: 22.5937, lng: 78.9629 });
  const [selectedChatItinerary, setSelectedChatItinerary] = useState();

  const [selectedChatMarkers, setSelectedChatMarkers] = useState([]);
  const [searchMarkers, setSearchMarkers] = useState([])
  const [showSearchMarkers, setShowSearchMarkers] = useState(false);

  const [userMarkedLoc, setUserMarkedLoc] = useState([])

  return (
    <MapContext.Provider
      value={{
        mapCenter, setMapCenter,
        selectedChatItinerary, setSelectedChatItinerary,
        selectedChatMarkers, setSelectedChatMarkers,
        searchMarkers, setSearchMarkers,
        userMarkedLoc, setUserMarkedLoc,
        showSearchMarkers, setShowSearchMarkers,

        // --- API Functions ---
        loadChatIntoMap: (itinerary, markers) => {
          setSelectedChatItinerary(itinerary);
          setSelectedChatMarkers(markers);
          // setShowSearchMarkers(false); // REMOVED per user request
        },
        clearChatFromMap: () => {
          setSelectedChatItinerary(null);
          setSelectedChatMarkers([]);
          // setShowSearchMarkers(true); // REMOVED per user request
        },
        applySearchResultsToMap: (results) => {
          // Assuming results have lat/lon, convert if necessary. 
          // For now, passing directly.
          setSearchMarkers(results);
          setShowSearchMarkers(true);
          // setSelectedChatItinerary(null); // REMOVED per user request
          // setSelectedChatMarkers([]); // REMOVED per user request
        }
      }}
    >
      {children}
    </MapContext.Provider>
  );
};
