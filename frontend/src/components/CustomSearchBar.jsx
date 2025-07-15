import React, {useState, useContext} from 'react'
import { MapContext } from '../context/MapContext'
import api from '../api/api'
// import { fetchNominationResults } from '../utils/mapUtils'

import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import 'leaflet-control-geocoder/dist/Control.Geocoder.css';
import 'leaflet-control-geocoder';



const CustomSearchBar = () => {
    const [query, setQuery] = useState('')
    const {setSearchResults, searchResults} = useContext(MapContext)
    
      // const geocoderControl = L.Control.geocoder({ defaultMarkGeocode: false })
      //   .on('markgeocode', async (e) => {
      //     const { name, center } = e.geocode;

      //     const nominatimResults = e.geocode ? [{
      //       address: name,
      //       lat: center.lat,
      //       lng: center.lng,
      //       source: 'Nominatim'
      //     }] : [];

    const fetchNominationResults = async (query) => {
    const endpoint = `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}`;

    try {
        const response = await fetch(endpoint, {
            method: 'GET',
            headers: {
                'Accept': 'application/json'
            }
        });

        if (!response.ok) {
            console.error("Network response was not OK", response.statusText);
            return [];
        }

        const data = await response.json();

        console.log("Direct Nominatim API results obtained:", data);

        return data.map(res => ({
            address: res.display_name,
            lat: parseFloat(res.lat),
            lng: parseFloat(res.lon),
            source: 'Nominatim'
        }));

    } catch (error) {
        console.error("Fetch Nominatim API error:", error);
        return [];
    }
};
    const handleSearch =  async() => {
        if(!query.trim()) return ;
        console.log("INSIDE THE handleSearch with query:", query)
        try{
            // const [ geoapifyResponse] = await Promise.all([
            //     // fetchNominationResults(query),
            //     api.searchLocationMultiple(query)
            // ])
            const [nominatimResults,  geoapifyResponse] = await Promise.all([
                fetchNominationResults(query),
                api.searchLocationMultiple(query)
            ])
            const geoapifyResults = geoapifyResponse.data.results.map(r => ({
                ...r,
                source: 'Geoapify'
            }))
            console.log("results, geo:", geoapifyResults, "\n\n\n Nomination:", nominatimResults)
            // console.log("results, geo:", geoapifyResults)
            setSearchResults([...nominatimResults, ...geoapifyResults])
            // setSearchResults([ ...geoapifyResults])
        }
        catch(err){
            console.error('Search error:', err)
            setSearchResults([])
        }
        finally{
            console.log("results:", searchResults)
        }
    } 
  return (
    <div style={{position: 'absolute', top: 10, left:80, zIndex: 1000}} >
        <input 
            value =  {query}
            onChange = {(e) => setQuery(e.target.value)}
            placeholder='Search Location ...'
        />
        <button onClick={handleSearch} >🔎</button>
    </div>
  )
}

export default CustomSearchBar