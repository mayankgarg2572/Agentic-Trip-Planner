// import React, {useContext, useEffect, useRef} from 'react'
// import { MapContext  } from '../context/MapContext'
// import api from '../api/api';
// import L from 'leaflet'
// import 'leaflet/dist/leaflet.css'
// import 'leaflet-control-geocoder/dist/Control.Geocoder.css';



// const MapView = () => {
//     const mapRef = useRef(null)
//     const { mapCenter } = useContext(MapContext)

//     useEffect(()=>{
//         if(!mapRef.current && mapCenter.lat !== undefined && mapCenter.lng !== undefined) {
//             mapRef.current =  L.map('map').setView(
//                 [mapCenter.lat, mapCenter.lng],
//                 4
//             );
//             L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
//                 attribution: '&copy; OpenStreetMap contributors'
//             }).addTo(mapRef.current)


//             mapRef.current.on('contextmenu', (e) => {
//                 L.popup()
//                     .setLatLng(e.latlng)
//                     .setContent('<button id="addMarker">Mark this Location</button>')
//                     .openOn(mapRef.current);
//                 document.getElementById('addMarker').onclick =  () => {
//                     L.marker(e.latlng).addTo(mapRef.current)
//                     api.saveMarkerLocation(e.latlng.lat, e.latlbg.lng);
//                     mapRef.current.closePopup()
//                 }
//             })
//         }
//         else if (mapCenter.lat !== undefined && mapCenter.lng !== undefined){
//             mapRef.current.setView([mapCenter.lat, mapCenter.lng], 13)
//         }
//     }, [mapCenter])
//     return (
//     <div id = "map" style={{ height: '100%', width: '100%' }} />
//   )
// }

// export default MapView

// import React, { useContext, useEffect, useRef } from 'react';
// import { MapContext } from '../context/MapContext';
// import api from '../api/api';
// import L from 'leaflet';
// import 'leaflet/dist/leaflet.css';
// import 'leaflet-control-geocoder/dist/Control.Geocoder.css';
// import 'leaflet-control-geocoder';

// const MapView = () => {
//   const mapRef = useRef(null);
//   const { mapCenter, setMapCenter } = useContext(MapContext);

//   useEffect(() => {
//     if (!mapRef.current) {
//       mapRef.current = L.map('map').setView([mapCenter.lat, mapCenter.lng], 5);
      
//       L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
//         attribution: '© OpenStreetMap contributors'
//       }).addTo(mapRef.current);

//       // Add Geocoder Control
//       const geocoderControl = L.Control.geocoder({
//         defaultMarkGeocode: true
//       })
//       .on('markgeocode', (e) => {
//         const { center, name } = e.geocode;
//         mapRef.current.setView(center, 13);

//         // Explicitly capture searched location to backend
//         api.searchLocation(name).then(response => {
//           console.log("Location stored successfully:", response.data);
//           setMapCenter({ lat: center.lat, lng: center.lng });
//         }).catch(err => {
//           console.error("Error storing location:", err);
//         });
//       })
//       .addTo(mapRef.current);

//       // Right-click to mark location explicitly
//       mapRef.current.on('contextmenu', (e) => {
//         L.popup()
//           .setLatLng(e.latlng)
//           .setContent('<button id="addMarker">Mark this Location</button>')
//           .openOn(mapRef.current);

//         document.getElementById('addMarker').onclick = () => {
//           L.marker(e.latlng).addTo(mapRef.current);
//           api.saveMarkerLocation(e.latlng.lat, e.latlng.lng);
//           mapRef.current.closePopup();
//         };
//       });
//     } else if (mapCenter.lat !== undefined && mapCenter.lng !== undefined) {
//         console.log(mapCenter)
//       mapRef.current.setView([mapCenter.lat, mapCenter.lng], 5);
//     }
//   }, [mapCenter, setMapCenter]);

//   return <div id="map" style={{ height: '100%', width: '100%' }} />;
// };

// export default MapView;


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
      mapRef.current = L.map('map').setView([mapCenter.lat, mapCenter.lng], 13);

      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
      }).addTo(mapRef.current);

      // const geocoderControl = L.Control.geocoder({ defaultMarkGeocode: false })
      //   .on('markgeocode', async (e) => {
      //     const { name, center } = e.geocode;

      //     const nominatimResults = e.geocode ? [{
      //       address: name,
      //       lat: center.lat,
      //       lng: center.lng,
      //       source: 'Nominatim'
      //     }] : [];

      //     let geoapifyResults = [];
      //     try {
      //       const res = await api.searchLocationMultiple(name);
      //       geoapifyResults = res.data.results.map(r => ({
      //         ...r,
      //         source: 'Geoapify'
      //       }));
      //     } catch (err) {
      //       console.error("Geoapify fetch error:", err);
      //     }

      //     setSearchResults([...nominatimResults, ...geoapifyResults]);
      //   })
      //   .addTo(mapRef.current);

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
      mapRef.current.setView([mapCenter.lat, mapCenter.lng], 13);
    }
  }, [mapCenter, setMapCenter, setSearchResults]);

  return <div id="map" style={{ height: '100%', width: '100%' }} />;
};

export default MapView;
