import React, { useContext, useEffect, useRef } from "react";
import { MapContext } from "../context/MapContext";
// import api from "../api/api";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import "leaflet-control-geocoder/dist/Control.Geocoder.css";
import "leaflet-control-geocoder";
import api from "../api/api";

const MapView = () => {
  // console.log("MapView is Mounting");
  const mapRef = useRef(null);
  const overlayRef = useRef(null);
  const { mapCenter, setMapCenter, setSelectedLocations, itinerary } =
    useContext(MapContext);

  useEffect(() => {
    if (!mapRef.current) {
      return;
    }

    if (mapCenter.lat && mapCenter.lng) {
      mapRef.current.setView([mapCenter.lat, mapCenter.lng], 16);
    }
  }, [mapCenter]);

  useEffect(() => {
    // console.log("Inside Set Itineary use effect in MapView.jsx")
    if (!overlayRef.current || !mapRef.current) return;
    overlayRef.current.clearLayers();

    if (!itinerary) return;

    const route = L.geoJSON(itinerary).addTo(overlayRef.current);

    itinerary?.properties?.waypoints?.forEach?.(
      (wp) =>
        
        L.marker([wp?.location?.[1], wp?.location?.[0]]).addTo(
          overlayRef.current
        )
    );
    try {
      mapRef.current.fitBounds(route.getBounds(), { padding: [20, 20] });
    } catch (error) {
      console.log("Getting Error in applying bound in Route:", route);
    }

    // console.log("Inside the useEffect for itineary", itinerary.geometry.coordinates?.[0]?.[0])
  }, [itinerary]);

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
                const btn = document.getElementById(
                  `removeMarker-${newMarkerTitle}`
                );
                if (btn) {
                  btn.onclick = () => {
                    mapRef.current.removeLayer(marker);
                    setSelectedLocations((prev) =>
                      prev.filter(
                        (loc) =>
                          !(
                            loc.lat === e.latlng.lat && loc.lng === e.latlng.lng
                          )
                      )
                    );
                  };
                }
              }, 0);
            });
            marker.addTo(mapRef.current);
            return [...prevLocations, newMarker];
          });

          mapRef.current.closePopup();
        };
      });
    }

    if (!overlayRef.current) {
      overlayRef.current = L.layerGroup().addTo(mapRef.current);
    }

    L.Icon.Default.mergeOptions({
      iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
      iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
      shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
    })

    const func = async () => {
      try {
        const data = await api.getLatLongForIP();
        // console.log("Data from ipapi.com :", data)
        if (data.lat && data.lon) {
          setMapCenter({ lat: data.lat, lng: data.lon });
        } else if (data.latitude && data.longitude) {
          setMapCenter({ lat: data.latitude, lng: data.longitude });
        } else {
          setMapCenter({ lat: 0, lng: 0 });
        }
      } catch (error) {
        console.error(error);
      }
      try {
        await api.startServer();
      } catch (error) {
        console.error(error);
      }
    };
    func();
    // called = true;
    // }

    return () => {
      mapRef.current?.remove();
      overlayRef.current = null;
    };
  }, []);

  return <div id="map" style={{ height: "100%", width: "100%" }} />;
};

export default MapView;
