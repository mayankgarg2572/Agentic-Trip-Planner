import React, { useContext, useEffect, useRef } from "react";
import { MapContext } from "../context/MapContext";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import "leaflet-control-geocoder/dist/Control.Geocoder.css";
import "leaflet-control-geocoder";
import api from "../api/api";

const colorPerMarkerType = {
  "Agent-Type": "blue",
  "User-Type": "red",
  "Search-Type": "green",
}


const MapView = () => {
  const mapRef = useRef(null);
  const overlayRef = useRef(null);
  const markersLayerRef = useRef(null);

  const {
    mapCenter,
    setMapCenter,
    selectedChatItinerary,
    selectedChatMarkers,
    searchMarkers,
    showSearchMarkers,
    userMarkedLoc,
    setUserMarkedLoc
  } = useContext(MapContext);

  // 1. Initialize Map
  useEffect(() => {
    if (!mapRef.current) {
      mapRef.current = L.map("map", { zoomControl: false }).setView(
        [mapCenter.lat, mapCenter.lng],
        13 // Default zoom
      );
      L.control.zoom({ position: "bottomright" }).addTo(mapRef.current);
      L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: "© OpenStreetMap contributors",
      }).addTo(mapRef.current);

      // Initialize Layer Groups
      overlayRef.current = L.layerGroup().addTo(mapRef.current); // For Itinerary
      markersLayerRef.current = L.layerGroup().addTo(mapRef.current); // For Markers

      // Fix Leaflet Icon
      L.Icon.Default.mergeOptions({
        iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
        iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
        shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
      });

      // Context Menu for User Markers
      mapRef.current.on("contextmenu", (e) => {
        L.popup()
          .setLatLng(e.latlng)
          .setContent('<button id="addMarker">Mark this Location</button>')
          .openOn(mapRef.current);

        setTimeout(() => {
          const btn = document.getElementById("addMarker");
          if (btn) {
            btn.onclick = () => {
              const newMarker = {
                lat: e.latlng.lat,
                lng: e.latlng.lng,
                title: `User Loc ${Date.now()}` // Simple unique title
              };
              setUserMarkedLoc(prev => [...prev, newMarker]);
              mapRef.current.closePopup();
            };
          }
        }, 0);
      });

      // Initial IP Location Fetch
      const fetchIPLocation = async () => {
        try {
          const data = await api.getLatLongForIP();
          // console.log(data)
          if (data.lat && data.lon) {
            // console.log(data)
            setMapCenter({ lat: data.lat, lng: data.lon });
          }
          else if (data.latitude && data.longitude) {
          setMapCenter({ lat: data.latitude, lng: data.longitude });
        }
        } catch (error) {
          console.error("IP Location Error:", error);
        }
      };
      fetchIPLocation();
      
      
    }

    return () => {
      mapRef.current?.remove();
      mapRef.current = null;
    };
  }, []); // Run once on mount

  // 2. Update Map Center
  useEffect(() => {
    if (mapRef.current && mapCenter.lat && mapCenter.lng) {
      mapRef.current.setView([mapCenter.lat, mapCenter.lng], mapRef.current.getZoom());
    }
  }, [mapCenter]);

  // 3. Handle Container Resize
  useEffect(() => {
    const mapContainer = document.getElementById("map");
    if (!mapContainer || !mapRef.current) return;

    const resizeObserver = new ResizeObserver(() => {
      mapRef.current?.invalidateSize();
    });

    resizeObserver.observe(mapContainer);

    return () => {
      resizeObserver.disconnect();
    };
  }, []);

  // 3. Render Itinerary (Polyline)
  useEffect(() => {
    if (!overlayRef.current) return;
    overlayRef.current.clearLayers();

    if (selectedChatItinerary) {
      const route = L.geoJSON(selectedChatItinerary).addTo(overlayRef.current);
      try {
        mapRef.current.fitBounds(route.getBounds(), { padding: [50, 50] });
      } catch (e) {
        console.log("Error fitting bounds:", e);
      }
    }
  }, [selectedChatItinerary]);

  // 4. Render Markers (Search, Agent, User)
  useEffect(() => {
    if (!markersLayerRef.current) return;
    markersLayerRef.current.clearLayers();

    // Helper to get colored icon
    const getColoredIcon = (color) => {
      return new L.Icon({
        iconUrl: `https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-${color}.png`,
        shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowSize: [41, 41]
      });
    };

    // Helper to add marker
    const addMarker = (lat, lng, title, type) => {
      if (!lat || !lng) return;
      const color = colorPerMarkerType[type] || 'blue';
      L.marker([lat, lng], {
        title: title,
        icon: getColoredIcon(color)
      })
        .bindPopup(title)
        .addTo(markersLayerRef.current);
    };

    // A. Search Markers
    if (showSearchMarkers && searchMarkers) {
      searchMarkers.forEach(m => addMarker(m.lat, m.lng, m.name || m.address, "Search-Type"));
    }

    // B. Agent Markers (from Chat)
    if (selectedChatMarkers) {
      selectedChatMarkers.forEach(m => addMarker(m.lat, m.lng, m.address || "Agent Location", "Agent-Type"));
    }

    // C. User Markers (Always visible)
    if (userMarkedLoc) {
      userMarkedLoc.forEach(m => {
        const marker = L.marker([m.lat, m.lng], {
          title: m.title,
          icon: getColoredIcon(colorPerMarkerType["User-Type"])
        }).addTo(markersLayerRef.current);

        // Remove logic
        marker.bindPopup(`<button id="rmv-${m.title}">Remove</button>`);
        marker.on('popupopen', () => {
          setTimeout(() => {
            const btn = document.getElementById(`rmv-${m.title}`);
            if (btn) {
              btn.onclick = () => {
                setUserMarkedLoc(prev => prev.filter(p => p.title !== m.title));
              };
            }
          }, 0);
        });
      });
    }

  }, [searchMarkers, showSearchMarkers, selectedChatMarkers, userMarkedLoc]);

  return <div id="map" style={{ height: "100%", width: "100%" }} />;
};

export default MapView;
