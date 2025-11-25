import React, { useState, useContext } from "react";
import { MapContext } from "../context/MapContext";
import api from "../api/api";

import "leaflet/dist/leaflet.css";
import "leaflet-control-geocoder/dist/Control.Geocoder.css";
import "leaflet-control-geocoder";
import classes from "./CustomSearchBar.module.css";

const CustomSearchBar = () => {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const { setSearchResults } = useContext(MapContext);

  const fetchNominationResults = async (query) => {
    const endpoint = `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(
      query
    )}`;

    try {
      const response = await fetch(endpoint, {
        method: "GET",
        headers: {
          Accept: "application/json",
        },
      });

      if (!response.ok) {
        console.error("Network response was not OK", response.statusText);
        return [];
      }

      const data = await response.json();

      // console.log("Direct Nominatim API results obtained:", data);

      return data.map((res) => ({
        address: res.display_name,
        lat: parseFloat(res.lat),
        lng: parseFloat(res.lon),
        source: "Nominatim",
      }));
    } catch (error) {
      console.error("Fetch Nominatim API error:", error);
      return [];
    }
  };
  const handleSearch = async () => {
    if (!query.trim()) return;
    
    setLoading(true);
    let nominatimResults = [];
    let geoapifyResults = [];

    try {
      // Fetch results from Nominatim API
      nominatimResults = await fetchNominationResults(query);
    } catch (err) {
      console.error("Error fetching Nominatim results:", err);
    }

    try {
      // Fetch results from Geoapify API
      const geoapifyResponse = await api.searchLocationMultiple(query);
      geoapifyResults = (geoapifyResponse?.results ?? []).map((r) => ({
        ...r,
        source: "Geoapify",
      }));
    } catch (err) {
      console.error("Error fetching Geoapify results:", err);
    }

    // Combine results and update the state
    setSearchResults([...nominatimResults, ...geoapifyResults]);
    setLoading(false);
  };
  return (
    <div className={classes.serachBarForm}>
      <input
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === "Enter" && !e.shiftKey && !e.ctrlKey && !e.altKey) {
            handleSearch();
          }
        }}
        placeholder="Search Location ..."
        disabled={loading}
      />
      <button onClick={handleSearch} disabled={loading}>
        {loading ? <div className={classes.loader}></div> : "🔎"}
      </button>
    </div>
  );
};

export default CustomSearchBar;
