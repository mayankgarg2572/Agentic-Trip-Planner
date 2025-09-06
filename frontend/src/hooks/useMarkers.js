import { useCallback } from "react";
import L from "leaflet";

export const useMarkers = (mapRef, setSelectedLocations) => {
  const addMarker = useCallback((latlng, title) => {
    const marker = L.marker(latlng, {
      icon: L.icon({
        iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowUrl:
          "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
        shadowSize: [41, 41],
      }),
      title,
    });

    marker.bindTooltip(title, {
      permanent: true,
      direction: "top",
      offset: [0, -10],
    });

    return marker;
  }, []);

  const handleMarkerRemoval = useCallback(
    (marker, latlng) => {
      mapRef.current.removeLayer(marker);
      setSelectedLocations((prev) =>
        prev.filter(
          (loc) => !(loc.lat === latlng.lat && loc.lng === latlng.lng)
        )
      );
    },
    [mapRef, setSelectedLocations]
  );

  return { addMarker, handleMarkerRemoval };
};
