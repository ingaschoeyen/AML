import React from 'react'

import {
    CContainer,
    CCard,
    CCardBody,
    CCardHeader,
} from '@coreui/react'

import graph_placeholder from 'src/assets/images/graph_placeholder.jpg'

const Network = () => {
    return (
        <CContainer>
            <h1>Network of Assets</h1>
            <CCard className="mb-4">
                <CCardHeader>
                    Network Visualization
                </CCardHeader>
                <CCardBody>
                    <img src={graph_placeholder} alt="Network Graph Placeholder" style={{ width: '100%' }} />
                </CCardBody>
            </CCard>
        </CContainer>
    )
}
    

export default Network