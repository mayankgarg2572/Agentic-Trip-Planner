import React, { useContext, useEffect, useRef } from 'react';
import { MapContext } from '../context/MapContext';
import api from '../api/api';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import 'leaflet-control-geocoder/dist/Control.Geocoder.css';
import 'leaflet-control-geocoder';

const MapView = () => {
  const mapRef = useRef(null);
  const { mapCenter, setMapCenter, setSearchResults } = useContext(MapContext);

  useEffect(() => {
    if (!mapRef.current) {
      mapRef.current = L.map('map', { zoomControl: false }).setView([mapCenter.lat, mapCenter.lng], 21);
      L.control.zoom({ position: 'bottomright' }).addTo(mapRef.current);
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
      }).addTo(mapRef.current);

      mapRef.current.on('contextmenu', (e) => {
        L.popup()
          .setLatLng(e.latlng)
          .setContent('<button id="addMarker">Mark this Location</button>')
          .openOn(mapRef.current);

        document.getElementById('addMarker').onclick = () => {
          L.marker(e.latlng).addTo(mapRef.current);
          console.log("The saving object", e.latlng)

          api.saveMarkerLocation(e.latlng.lat, e.latlng.lng);
          mapRef.current.closePopup();
        };
      });
    } else if (mapCenter.lat && mapCenter.lng) {
      mapRef.current.setView([mapCenter.lat, mapCenter.lng], 21);
    }
  }, [mapCenter, setMapCenter, setSearchResults]);

    useEffect(() => {
    fetch('https://ipapi.co/json/') 
      .then(res => res.json())
      .then(data => {
        if (data.latitude && data.longitude) {
          setMapCenter({ lat: data.latitude, lng: data.longitude });
        } else {
          // Fallback: e.g. default to [0,0]
          setMapCenter({ lat: 0, lng: 0 });
        }
      })
      .catch(() => {
        setMapCenter({ lat: 0, lng: 0 });
      });
  }, []);

  return <div id="map" style={{ height: '100%', width: '100%' }} />;
};

export default MapView;
