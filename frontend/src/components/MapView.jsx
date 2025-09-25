import React, { useContext, useEffect, useRef } from "react";
import { MapContext } from "../context/MapContext";
// import api from "../api/api";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import "leaflet-control-geocoder/dist/Control.Geocoder.css";
import "leaflet-control-geocoder";


const MapView = () => {
  // console.log("MapView is Mounting");
  const mapRef = useRef(null);
  const {
    mapCenter,
    setMapCenter,
    setSearchResults,
    setSelectedLocations,
  } = useContext(MapContext);

  useEffect(() => {
    if (!mapRef.current) {
      mapRef.current = L.map("map", { zoomControl: false }).setView(
        [mapCenter.lat, mapCenter.lng],
        21
      );
      L.control.zoom({ position: "bottomright" }).addTo(mapRef.current);
      L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: "© OpenStreetMap contributors",
      }).addTo(mapRef.current);

      mapRef.current.on("contextmenu", (e) => {
        L.popup()
          .setLatLng(e.latlng)
          .setContent('<button id="addMarker">Mark this Location</button>')
          .openOn(mapRef.current);
        
        document.getElementById("addMarker").onclick = () => {
          setSelectedLocations((prevLocations) => {
            const newMarkerTitle = `${prevLocations.length + 1}`; // Use the latest length of selectedLocations
            const newMarker = {
              lat: e.latlng.lat,
              lng: e.latlng.lng,
              title: newMarkerTitle,
            };

            // Create a new marker with a tooltip
            const marker = L.marker(e.latlng, {
              icon: L.icon({
              iconUrl:
                "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
              iconSize: [25, 41],
              iconAnchor: [12, 41],
              popupAnchor: [1, -34],
              shadowUrl:
                "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
              shadowSize: [41, 41],
              }),
              title: newMarkerTitle,
            });

            // Bind a tooltip to the marker
            marker.bindTooltip(newMarkerTitle, {
              permanent: true,
              direction: "top",
              offset: [0, -10],
            });

            // Add a popup with a remove button
            marker.bindPopup(
              `<button id="removeMarker-${newMarkerTitle}">Unmark this Location</button>`
            );

            // Listen for marker click to open popup
            marker.on("click", function () {
              marker.openPopup();
              setTimeout(() => {
              const btn = document.getElementById(`removeMarker-${newMarkerTitle}`);
              if (btn) {
                btn.onclick = () => {
                mapRef.current.removeLayer(marker);
                setSelectedLocations((prev) =>
                  prev.filter(
                  (loc) =>
                    !(loc.lat === e.latlng.lat && loc.lng === e.latlng.lng)
                  )
                );
                };
              }
              }, 0);
            });

            // Add the marker to the map
            marker.addTo(mapRef.current);

            // console.log("The saving object", e.latlng);

            // Save location via API
            // const saveLocation = async () => {
            //   try {
            //     await api.saveMarkerLocation(e.latlng.lat, e.latlng.lng);
            //   } catch (err) {
            //     console.error("Issue in saving the marked Location:", err);
            //   }
            // };
            // saveLocation();

            // Return the updated locations array
            return [...prevLocations, newMarker];
          });

          mapRef.current.closePopup();
        };
      });
    } else if (mapCenter.lat && mapCenter.lng) {
      mapRef.current.setView([mapCenter.lat, mapCenter.lng], 16);
    }
    // Doing below because we just need to set the selectedLocations for now no need to remove them
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [mapCenter, setMapCenter, setSearchResults]);

  useEffect(() => {
    fetch("https://ipapi.co/json/")  // Can use http://ip-api.co/json/ but this is not easy for deploying as it is not https. 
      .then((res) => res.json())
      .then((data) => {
        // console.log("Data from ipapi.com :", data)
        if (data.lat && data.lon) {
          setMapCenter({ lat: data.lat, lng: data.lon });
        } else if(data.latitude && data.longitude) {
          setMapCenter({ lat: data.latitude, lng: data.longitude });
        }
        else{
          setMapCenter({ lat: 0, lng: 0 });
        }
      })
      .catch((err) => {
        console.error("getting error:", err, " when using API service.")
        setMapCenter({ lat: 0, lng: 0 });
      });
    // called = true;
    // }
  }, []);

  return <div id="map" style={{ height: "100%", width: "100%" }} />;
};

export default MapView;
