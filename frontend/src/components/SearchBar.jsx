import React, { useState, useContext } from 'react'
import api from '../api/api'
import { MapContext } from '../context/MapContext'

import classes from './SearchBar.module.css'
const SearchBar = () => {
    const [address, setAddress] =  useState('')
    const { setMapCenter } = useContext( MapContext );

    const handleSearch =  async(e) => {
        
        e.preventDefault()
        try{
            const result  =  await api.searchLocation(address)
            const { latitude, longitude } = result.data
            setMapCenter({lat: latitude, long: longitude})
        }
        catch(err){
            console.error(err)
        }
        
        // Pass the result to MapView by context ad state management
    }
  return (
    <form style={classes.serachBarForm} onSubmit={handleSearch}>
        <input 
            id='searchInput'
            name ='address'
            value = {address}
            onChange={(e) => setAddress(e.target.value)}
            placeholder="Search Address..."
        />
        <button type='submit'>🔎</button>
    </form>
  )
}

export default SearchBar