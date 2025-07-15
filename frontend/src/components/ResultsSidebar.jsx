import React, { useContext } from 'react';
import { MapContext } from '../context/MapContext';

const ResultsSidebar = ({ onClose }) => {
  const { searchResults, setMapCenter, setSearchResults } = useContext(MapContext);

  const removeResult =  (idx) => {
    const updatedResults = [...searchResults]
    updatedResults.splice(idx, 1)
    setSearchResults(updatedResults)
  }

  if (searchResults.length === 0) return null
   ;

  return (
    <div style={{ position: 'absolute', left: 0, top: 0, height: '100%', width: '300px', background: '#fff', overflowY: 'auto', zIndex: 1000 }}>
      <p>Search Results</p>
      <button onClick={onClose}>✖️</button>
      <ul style={{ listStyle: 'none', padding: 0 }}>
        {searchResults.map((result, idx) => (
          <li key={idx}
              style={{
                cursor: 'pointer', padding: '10px', borderBottom: '1px solid #ddd',
                backgroundColor: result.source === 'Geoapify' ? '#2d9dd6ff' : '#fafff0'
              }}
              >
                <div onClick={() => setMapCenter({ lat: result.lat, lng: result.lng })}>
                    <strong>{result.source}</strong>: {result.address}
                </div>
                <button onClick={() => removeResult(idx)} style={{ marginTop: '5px',
                  color: 'red'
                }}>
                  ❌ Remove
                </button>
            
          </li>
        ))}
      </ul>
    </div>
  );
};

export default ResultsSidebar;
