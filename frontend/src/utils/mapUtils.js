import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import 'leaflet-control-geocoder/dist/Control.Geocoder.css';
import 'leaflet-control-geocoder';


const fetchNominationResults = (query) => {
    return new Promise((resolve, reject)=> {
        const geocoder = new L.Control.Geocoder.Nominatim()
        geocoder.geocode(query, (results) => {
            if(results && results.length>0){
                resolve(results.map(res => ({
                    address: res.name,
                    lat: res.center.lat,
                    lng: res.center.lng,
                    source: 'Nominatim'
                })));
            }
            else{
                resolve([])
            }
        })
    }  )
}

export {fetchNominationResults}