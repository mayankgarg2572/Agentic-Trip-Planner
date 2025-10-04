import React, { createContext, useState } from 'react';

export const MapContext = createContext();

export const MapProvider = ({ children }) => {
  const [mapCenter, setMapCenter] = useState({ lat: 22.5937, lng: 78.9629 });
  const [searchResults, setSearchResults] = useState([]);
  const [selectedLocations, setSelectedLocations] = useState([])
  const [itinerary, setItinerary] = useState()

  const [agentMapResults, setAgentMapResults] = useState([])

  return (
    <MapContext.Provider value={{ mapCenter, setMapCenter, searchResults, setSearchResults, selectedLocations, setSelectedLocations, itinerary, setItinerary, agentMapResults, setAgentMapResults }}>
      {children}
    </MapContext.Provider>
  );
};
