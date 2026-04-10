import React from 'react'

import {
    CCol,
    CRow,
    CContainer,
    CCard
} from '@coreui/react'

import { DocsComponents, DocsExample } from 'src/components'

import markers from 'src/assets/json/map/markers.json'
import mapNL from 'src/assets/images/nl_map.svg'
// takes markers that specify location of assets
// markers also unique id - passed as props to 
// retrieval function that loads asset information when marker is clicked
const Map = (markers) => {
  return (
    <>
    <CContainer>
        <CCol className="mb-4">
            <div style={{ height: '400px', width: '100%', backgroundColor: '#e9ecef' }}>
                <img src={mapNL} alt="Netherlands Map" style={{ width: '100%', height: '100%' }} />
            </div>
        </CCol>
    </CContainer>
    </>
  )
}

const MapContainer = () => {
  return (
    <div>
      <h1>Map of Assets</h1>
      <CCard className="mb-4">
        <CRow className="mb-4">
            <CCol>
                <div>
                    here, keywords and filters will be displayed
                </div>
            </CCol>
                <div style={{ height: '400px', width: '100%', backgroundColor: '#e9ecef' }}>
                <Map markers={markers} />
                </div>
                <div>
                    here, information relating to a selected asset will be displayed.
                </div>
        </CRow>
    </CCard>
    </div>
  )
}

export default MapContainer