import React, {useState, useContext} from 'react'
import { MapContext } from '../context/MapContext'
import api from '../api/api'

import 'leaflet/dist/leaflet.css';
import 'leaflet-control-geocoder/dist/Control.Geocoder.css';
import 'leaflet-control-geocoder';
import classes from './CustomSearchBar.module.css'


const CustomSearchBar = () => {
    const [query, setQuery] = useState('')
    const {setSearchResults} = useContext(MapContext)

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

        // console.log("Direct Nominatim API results obtained:", data);

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
        // console.log("INSIDE THE handleSearch with query:", query)
        try{
            const [nominatimResults,  geoapifyResponse] = await Promise.all([
                fetchNominationResults(query),
                api.searchLocationMultiple(query)
            ])
            const geoapifyResults = (geoapifyResponse?.data?.results ?? []).map(r => ({
                ...r,
                source: 'Geoapify'
                }));
            // console.log("results, geo:", geoapifyResults, "\n\n\n Nomination:", nominatimResults)
            setSearchResults([...nominatimResults, ...geoapifyResults])
        }
        catch(err){
            console.error('Search error:', err)
            setSearchResults([])
        }
        finally{
            // console.log("results:", searchResults)
        }
    } 
  return (
    <div className={classes.serachBarForm} >
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